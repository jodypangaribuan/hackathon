"""Annotation sampling, validation, agreement, adjudication, and gold freezing."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score

from .config import ML_ROOT, load_config
from .manifest import sha256_file

ANNOTATOR_IDS = ("A1", "A2", "A3")
NEGATIVE_SEED_TERMS = (
    "kotor", "jorok", "sampah", "limbah", "rusak", "berbahaya", "bahaya", "pungli",
    "pungutan", "kasar", "tidak terawat", "air mati", "terbengkalai", "kecewa",
)
POSITIVE_TERMS = (
    "bagus", "baik", "bersih", "indah", "cantik", "nyaman", "aman", "ramah", "mudah",
    "luas", "jelas", "terawat", "sejuk", "cepat", "membantu", "recommended", "good",
    "beautiful", "clean", "comfortable", "friendly", "safe",
)
NEGATIVE_TERMS = (
    "tidak", "kurang", "buruk", "jelek", "kotor", "jorok", "rusak", "mahal", "kasar",
    "lambat", "sempit", "bahaya", "berbahaya", "rawan", "licin", "pungli", "pungutan",
    "sampah", "bau", "kecewa", "terbengkalai", "tutup", "sulit", "bising", "pengap",
    "bad", "dirty", "broken", "dangerous", "expensive", "rude", "closed",
)
HIGH_SEVERITY_TERMS = (
    "sangat berbahaya", "tidak bisa dipakai", "tidak dapat digunakan", "tidak ada air",
    "pungli", "dipalak", "pemalakan", "maling", "copet", "keracunan", "ancaman",
    "dangerous", "unusable",
)
MEDIUM_SEVERITY_TERMS = (
    "rusak", "kotor", "jorok", "kasar", "antre", "antri", "tidak terawat", "terbengkalai",
    "berlubang", "sulit", "sempit", "bau", "lambat", "tutup",
)
NEGATION_PATTERNS = ("tidak ", "tak ", "bukan ", "belum ", "gak ", "nggak ")
PASS_PROFILES = {
    "strict": {"context_chars": 65, "require_polarity_cue": True, "allow_neutral": False},
    "balanced": {"context_chars": 100, "require_polarity_cue": False, "allow_neutral": True},
    "recall": {"context_chars": 150, "require_polarity_cue": False, "allow_neutral": True},
}
INDONESIAN_MARKERS = ("yang", "dan", "tidak", "tempat", "bagus", "jalan", "dengan", "untuk")
ENGLISH_MARKERS = ("the", "and", "not", "place", "good", "road", "with", "for")


def _contains_term(text: str, terms: list[str] | tuple[str, ...]) -> bool:
    lowered = text.casefold()
    return any(
        re.search(rf"(?<!\w){re.escape(term.casefold())}(?!\w)", lowered) is not None
        for term in terms
    )


def _language_marker(text: str) -> str:
    lowered = f" {text.casefold()} "
    has_id = any(f" {term} " in lowered for term in INDONESIAN_MARKERS)
    has_en = any(f" {term} " in lowered for term in ENGLISH_MARKERS)
    if has_id and has_en:
        return "mixed"
    if has_id:
        return "id_marker"
    if has_en:
        return "en_marker"
    return "undetermined"


def build_sampling_frame(canonical_reviews: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    taxonomy = load_config("taxonomy")
    aspects = taxonomy["aspect_definitions"]
    frame = canonical_reviews.loc[canonical_reviews["has_text"]].copy()
    frame["word_count"] = frame["review_text_raw"].str.split().str.len()
    frame["length_band"] = pd.cut(
        frame["word_count"],
        bins=[0, 3, 10, 25, 60, math.inf],
        labels=["very_short", "short", "medium", "long", "very_long"],
        include_lowest=True,
    ).astype(str)
    frame["rating_band"] = frame["rating"].map(
        lambda value: "missing" if pd.isna(value) else "low_1_2" if value <= 2 else "mid_3" if value <= 3 else "high_4_5"
    )
    frame["language_marker"] = frame["review_text_raw"].map(_language_marker)
    frame["recency_band"] = np.select(
        [
            frame["published_date_estimate"].isna(),
            pd.to_datetime(frame["published_date_estimate"], errors="coerce") >= pd.Timestamp("2024-01-01"),
            pd.to_datetime(frame["published_date_estimate"], errors="coerce") >= pd.Timestamp("2022-01-01"),
        ],
        ["unknown", "recent", "mid"],
        default="older",
    )
    aspect_columns: list[str] = []
    for aspect, details in aspects.items():
        column = f"candidate_{aspect}"
        frame[column] = frame["review_text_raw"].map(
            lambda text, terms=details["seed_terms"]: _contains_term(text, terms)
        )
        aspect_columns.append(column)
    frame["candidate_complaint"] = frame["review_text_raw"].map(
        lambda text: _contains_term(text, NEGATIVE_SEED_TERMS)
    )
    frame["candidate_aspect_count"] = frame[aspect_columns].sum(axis=1)
    frame["candidate_aspects"] = frame.apply(
        lambda row: [column.removeprefix("candidate_") for column in aspect_columns if row[column]],
        axis=1,
    )
    return frame, aspect_columns


def _sampling_weights(frame: pd.DataFrame, aspect_columns: list[str]) -> pd.Series:
    destination_count = frame.groupby("destination_id")["review_id"].transform("size")
    weights = 1 / np.sqrt(destination_count)
    weights *= frame["rating_band"].map({"low_1_2": 3.0, "mid_3": 2.0, "high_4_5": 1.0, "missing": 1.5})
    weights *= frame["language_marker"].map({"mixed": 2.5, "en_marker": 1.4, "id_marker": 1.0, "undetermined": 1.2})
    weights *= frame["length_band"].map({"very_short": 1.3, "short": 1.0, "medium": 1.1, "long": 1.5, "very_long": 2.0}).astype(float)
    weights *= np.where(frame["candidate_complaint"], 2.5, 1.0)
    taxonomy = load_config("taxonomy")
    for column in aspect_columns:
        aspect = column.removeprefix("candidate_")
        if taxonomy["aspect_definitions"][aspect]["rare_sampling"]:
            weights *= np.where(frame[column], 3.0, 1.0)
    return weights.astype(float)


def stratified_sample(
    frame: pd.DataFrame,
    aspect_columns: list[str],
    size: int,
    seed: int,
    excluded_review_ids: set[str] | None = None,
) -> pd.DataFrame:
    pool = frame.loc[~frame["review_id"].isin(excluded_review_ids or set())].copy()
    if size > len(pool):
        raise ValueError(f"Sample size {size} exceeds pool size {len(pool)}")
    pool["sampling_weight"] = _sampling_weights(pool, aspect_columns)
    sample = pool.sample(n=size, weights="sampling_weight", random_state=seed, replace=False)
    return sample.sort_values("review_id").reset_index(drop=True)


def _annotation_template(review_id: str, row: pd.Series, annotator_id: str) -> dict[str, Any]:
    return {
        "review_id": review_id,
        "destination_id": row["destination_id"],
        "text": row["review_text_raw"],
        "rating_context": None if pd.isna(row["rating"]) else float(row["rating"]),
        "labels": [],
        "annotator_id": annotator_id,
        "annotation_version": "1.0.0-rc1",
        "annotation_status": "pending",
        "review_notes": None,
    }


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _assignment_rows(
    sample: pd.DataFrame,
    phase: str,
    double_rate: float,
    all_annotators: bool,
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows: list[dict[str, Any]] = []
    shuffled_ids = sample["review_id"].sample(frac=1, random_state=seed).tolist()
    double_count = len(sample) if all_annotators else round(len(sample) * double_rate)
    double_ids = set(shuffled_ids[:double_count])
    for position, review_id in enumerate(shuffled_ids):
        if review_id in double_ids:
            annotators = ANNOTATOR_IDS if all_annotators else tuple(
                rng.choice(ANNOTATOR_IDS, size=2, replace=False).tolist()
            )
        else:
            annotators = (ANNOTATOR_IDS[position % len(ANNOTATOR_IDS)],)
        for annotator_id in annotators:
            rows.append(
                {
                    "phase": phase,
                    "review_id": review_id,
                    "annotator_id": annotator_id,
                    "is_double_annotated": len(annotators) > 1,
                }
            )
    return pd.DataFrame(rows).sort_values(["annotator_id", "review_id"]).reset_index(drop=True)


def run_annotation_sampling(
    processed_dir: Path,
    annotation_dir: Path,
    report_dir: Path,
) -> dict[str, Any]:
    annotation_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    reviews = pd.read_parquet(processed_dir / "canonical_reviews.parquet")
    frame, aspect_columns = build_sampling_frame(reviews)
    config = load_config("taxonomy")
    sampling = config["sampling"]
    pilot = stratified_sample(frame, aspect_columns, sampling["pilot_size"], sampling["seed"])
    main = stratified_sample(
        frame,
        aspect_columns,
        sampling["main_size"],
        sampling["seed"] + 1,
        excluded_review_ids=set(pilot["review_id"]),
    )

    audit_columns = [
        "review_id", "destination_id", "source_kind", "rating", "word_count", "length_band",
        "rating_band", "language_marker", "recency_band", "candidate_complaint",
        "candidate_aspect_count", "candidate_aspects", "sampling_weight",
    ]
    pilot[audit_columns].to_csv(annotation_dir / "pilot_sampling_audit.csv", index=False)
    main[audit_columns].to_csv(annotation_dir / "main_sampling_audit.csv", index=False)

    pilot_assignments = _assignment_rows(pilot, "pilot", 1.0, True, sampling["seed"])
    main_assignments = _assignment_rows(
        main,
        "main",
        sampling["double_annotation_rate"],
        False,
        sampling["seed"] + 2,
    )
    assignments = pd.concat([pilot_assignments, main_assignments], ignore_index=True)
    assignments.to_csv(annotation_dir / "annotation_assignments.csv", index=False)

    lookup = pd.concat([pilot, main]).set_index("review_id")
    for phase, phase_assignments in assignments.groupby("phase"):
        for annotator_id, annotator_assignments in phase_assignments.groupby("annotator_id"):
            records = [
                _annotation_template(review_id, lookup.loc[review_id], annotator_id)
                for review_id in annotator_assignments["review_id"]
            ]
            _write_jsonl(annotation_dir / f"{phase}_{annotator_id}_annotations.jsonl", records)

    support_rows: list[dict[str, Any]] = []
    for column in aspect_columns:
        aspect = column.removeprefix("candidate_")
        support_rows.append(
            {
                "aspect": aspect,
                "clean_pool_candidate_support": int(frame[column].sum()),
                "clean_pool_candidate_share": float(frame[column].mean()),
                "pilot_candidate_support": int(pilot[column].sum()),
                "main_candidate_support": int(main[column].sum()),
                "rare_sampling": bool(config["aspect_definitions"][aspect]["rare_sampling"]),
            }
        )
    support = pd.DataFrame(support_rows).sort_values("clean_pool_candidate_support", ascending=False)
    support.to_csv(report_dir / "annotation_candidate_support.csv", index=False)

    summary = {
        "annotation_version": config["taxonomy_version"],
        "clean_text_pool": len(frame),
        "pilot_unique_reviews": len(pilot),
        "pilot_annotation_tasks": len(pilot_assignments),
        "main_unique_reviews": len(main),
        "main_annotation_tasks": len(main_assignments),
        "main_double_annotated_reviews": int(
            main_assignments.loc[main_assignments["is_double_annotated"], "review_id"].nunique()
        ),
        "main_single_annotated_reviews": int(
            main_assignments.loc[~main_assignments["is_double_annotated"], "review_id"].nunique()
        ),
        "sample_overlap": len(set(pilot["review_id"]) & set(main["review_id"])),
        "destinations_in_pilot": int(pilot["destination_id"].nunique()),
        "destinations_in_main": int(main["destination_id"].nunique()),
        "assignment_files": sorted(path.name for path in annotation_dir.glob("*.jsonl")),
        "taxonomy_sha256": sha256_file(ML_ROOT / "configs" / "taxonomy.yaml"),
        "schema_sha256": sha256_file(ML_ROOT / "contracts" / "annotation.schema.json"),
    }
    (report_dir / "annotation_sampling_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as error:
                    raise ValueError(f"Invalid JSON at {path}:{line_number}: {error}") from error
    return records


def validate_annotation_record(record: dict[str, Any]) -> list[str]:
    taxonomy = load_config("taxonomy")
    errors: list[str] = []
    required = {
        "review_id", "destination_id", "text", "labels", "annotator_id",
        "annotation_version", "annotation_status",
    }
    missing = required - set(record)
    if missing:
        errors.append(f"missing fields: {sorted(missing)}")
        return errors
    if record["annotation_version"] != taxonomy["taxonomy_version"]:
        errors.append("annotation_version mismatch")
    if not str(record["annotator_id"]).startswith("A"):
        errors.append("invalid annotator_id")
    seen: set[str] = set()
    for label in record["labels"]:
        aspect = label.get("aspect")
        polarity = label.get("polarity")
        severity = label.get("severity")
        if aspect not in taxonomy["aspect_definitions"]:
            errors.append(f"invalid aspect: {aspect}")
        if aspect in seen:
            errors.append(f"duplicate aspect: {aspect}")
        seen.add(aspect)
        if polarity not in taxonomy["polarity_labels"]:
            errors.append(f"invalid polarity: {polarity}")
        if polarity == "negative" and severity not in taxonomy["severity_labels"]:
            errors.append(f"negative label requires severity: {aspect}")
        if polarity != "negative" and severity is not None:
            errors.append(f"nonnegative label severity must be null: {aspect}")
        evidence = label.get("evidence_text")
        if evidence and evidence not in record["text"]:
            errors.append(f"evidence is not verbatim substring: {aspect}")
    return errors


def validate_annotation_files(paths: list[Path], require_completed: bool = False) -> dict[str, Any]:
    total = 0
    invalid: list[dict[str, Any]] = []
    seen_assignments: set[tuple[str, str]] = set()
    for path in paths:
        for record in load_jsonl(path):
            total += 1
            key = (record.get("review_id", ""), record.get("annotator_id", ""))
            errors = validate_annotation_record(record)
            if key in seen_assignments:
                errors.append("duplicate review/annotator assignment")
            seen_assignments.add(key)
            if require_completed and record.get("annotation_status") not in {"completed", "adjudicated"}:
                errors.append("annotation is not completed")
            if errors:
                invalid.append({"file": str(path), "review_id": key[0], "errors": errors})
    return {"records": total, "invalid_records": len(invalid), "errors": invalid}


def _label_map(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {label["aspect"]: label for label in record["labels"]}


def evaluate_agreement(paths: list[Path], output_path: Path) -> dict[str, Any]:
    validation = validate_annotation_files(paths, require_completed=True)
    if validation["invalid_records"]:
        raise ValueError(f"Invalid annotations: {validation['invalid_records']}")
    records = [record for path in paths for record in load_jsonl(path)]
    by_review: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_review.setdefault(record["review_id"], []).append(record)
    double = {key: value for key, value in by_review.items() if len(value) >= 2}
    if not double:
        raise ValueError("No double-annotated reviews found")

    jaccards: list[float] = []
    polarity_pairs: list[bool] = []
    severity_a: list[int] = []
    severity_b: list[int] = []
    severity_map = {"low": 0, "medium": 1, "high": 2}
    per_label: dict[str, list[tuple[int, int]]] = {
        aspect: [] for aspect in load_config("taxonomy")["aspect_definitions"]
    }
    disagreement_ids: set[str] = set()
    for review_id, review_records in double.items():
        for left, right in combinations(review_records, 2):
            left_map, right_map = _label_map(left), _label_map(right)
            left_set, right_set = set(left_map), set(right_map)
            union = left_set | right_set
            jaccard = len(left_set & right_set) / len(union) if union else 1.0
            jaccards.append(jaccard)
            if jaccard < 1:
                disagreement_ids.add(review_id)
            for aspect, pair_values in per_label.items():
                pair_values.append((int(aspect in left_set), int(aspect in right_set)))
            for aspect in left_set & right_set:
                polarity_same = left_map[aspect]["polarity"] == right_map[aspect]["polarity"]
                polarity_pairs.append(polarity_same)
                if not polarity_same:
                    disagreement_ids.add(review_id)
                if left_map[aspect]["polarity"] == right_map[aspect]["polarity"] == "negative":
                    severity_a.append(severity_map[left_map[aspect]["severity"]])
                    severity_b.append(severity_map[right_map[aspect]["severity"]])
                    if severity_a[-1] != severity_b[-1]:
                        disagreement_ids.add(review_id)

    per_label_metrics: dict[str, Any] = {}
    for aspect, pairs in per_label.items():
        left, right = zip(*pairs, strict=True)
        agreement = sum(a == b for a, b in pairs) / len(pairs)
        if len(set(left) | set(right)) < 2:
            kappa = float("nan")
        else:
            kappa = float(cohen_kappa_score(left, right))
        per_label_metrics[aspect] = {"agreement": round(agreement, 4), "kappa": None if math.isnan(kappa) else round(kappa, 4)}

    weighted_kappa = (
        float(cohen_kappa_score(severity_a, severity_b, weights="quadratic"))
        if severity_a and len(set(severity_a) | set(severity_b)) >= 2
        else float("nan")
    )
    metrics = {
        "double_annotated_reviews": len(double),
        "pairwise_comparisons": len(jaccards),
        "aspect_jaccard_mean": round(float(np.mean(jaccards)), 4),
        "polarity_agreement": round(float(np.mean(polarity_pairs)), 4) if polarity_pairs else None,
        "severity_weighted_kappa": None if math.isnan(weighted_kappa) else round(weighted_kappa, 4),
        "per_label": per_label_metrics,
        "disagreement_review_ids": sorted(disagreement_ids),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return metrics


def freeze_gold(
    annotation_paths: list[Path],
    adjudicated_path: Path,
    metrics_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    metrics = json.loads(metrics_path.read_text())
    gates = load_config("taxonomy")["agreement_gates"]
    if metrics["aspect_jaccard_mean"] < gates["aspect_jaccard"]:
        raise ValueError("Aspect agreement gate not met")
    if metrics["polarity_agreement"] is None or metrics["polarity_agreement"] < gates["polarity_agreement"]:
        raise ValueError("Polarity agreement gate not met")
    if metrics["severity_weighted_kappa"] is None or metrics["severity_weighted_kappa"] < gates["severity_weighted_kappa"]:
        raise ValueError("Severity agreement gate not met")

    records = [record for path in annotation_paths for record in load_jsonl(path)]
    adjudicated = load_jsonl(adjudicated_path)
    adjudicated_ids = {record["review_id"] for record in adjudicated}
    missing_adjudication = set(metrics.get("disagreement_review_ids", [])) - adjudicated_ids
    if missing_adjudication:
        raise ValueError(
            f"Missing adjudication for {len(missing_adjudication)} disagreement reviews"
        )
    final_by_review: dict[str, dict[str, Any]] = {}
    for record in records:
        if record["annotation_status"] != "completed":
            continue
        gold_record = {
            "review_id": record["review_id"],
            "destination_id": record["destination_id"],
            "text": record["text"],
            "rating_context": record.get("rating_context"),
            "labels": sorted(record["labels"], key=lambda label: label["aspect"]),
            "annotation_version": record["annotation_version"],
            "annotation_status": "adjudicated" if record["review_id"] in adjudicated_ids else "completed",
            "review_notes": None,
        }
        existing = final_by_review.get(record["review_id"])
        if existing and existing["labels"] != gold_record["labels"] and record["review_id"] not in adjudicated_ids:
            raise ValueError(f"Unadjudicated label disagreement: {record['review_id']}")
        final_by_review[record["review_id"]] = gold_record
    for record in adjudicated:
        if record["annotation_status"] != "adjudicated":
            raise ValueError("Adjudication records must have status adjudicated")
        final_by_review[record["review_id"]] = {
            "review_id": record["review_id"],
            "destination_id": record["destination_id"],
            "text": record["text"],
            "rating_context": record.get("rating_context"),
            "labels": sorted(record["labels"], key=lambda label: label["aspect"]),
            "annotation_version": record["annotation_version"],
            "annotation_status": "adjudicated",
            "review_notes": record.get("review_notes"),
        }
    validation = validate_annotation_files([adjudicated_path], require_completed=True)
    if validation["invalid_records"]:
        raise ValueError("Invalid adjudication records")
    output = sorted(final_by_review.values(), key=lambda record: record["review_id"])
    _write_jsonl(output_path, output)
    manifest = {
        "gold_records": len(output),
        "annotation_version": load_config("taxonomy")["taxonomy_version"],
        "gold_sha256": sha256_file(output_path),
        "metrics_sha256": sha256_file(metrics_path),
    }
    output_path.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def _term_matches(text: str, terms: list[str]) -> list[re.Match[str]]:
    matches: list[re.Match[str]] = []
    for term in terms:
        matches.extend(
            re.finditer(rf"(?<!\w){re.escape(term.casefold())}(?!\w)", text.casefold())
        )
    return sorted(matches, key=lambda match: (match.start(), -len(match.group())))


def _evidence_span(text: str, match: re.Match[str], radius: int = 70) -> str:
    start = max(0, match.start() - radius)
    end = min(len(text), match.end() + radius)
    left_boundary = max(text.rfind(".", 0, match.start()), text.rfind("!", 0, match.start()), text.rfind("?", 0, match.start()))
    if left_boundary >= start:
        start = left_boundary + 1
    right_boundaries = [position for delimiter in ".!?" if (position := text.find(delimiter, match.end())) != -1]
    if right_boundaries and min(right_boundaries) < end:
        end = min(right_boundaries) + 1
    return text[start:end].strip()


def _local_polarity(context: str, matched_term: str, profile: dict[str, Any]) -> str | None:
    lowered = context.casefold()
    if matched_term.casefold() in {"pungli", "pungutan"} and re.search(
        r"(?:tidak ada|ga ada|gak ada|nggak ada|gadak|tanpa|bebas|aman\s+(?:dari|dri)|menghindari|gak banyak|nggak banyak).{0,30}(?:pungli|pungutan)",
        lowered,
    ):
        return "positive"
    if matched_term.casefold() in {"pungli", "pungutan"} and "?" in context:
        return "neutral"
    positive = _contains_term(lowered, POSITIVE_TERMS)
    negative = _contains_term(lowered, NEGATIVE_TERMS)
    term_position = lowered.find(matched_term.casefold())
    prefix = lowered[max(0, term_position - 15) : term_position]
    term_is_positive = matched_term.casefold() in POSITIVE_TERMS
    term_is_negative = matched_term.casefold() in NEGATIVE_TERMS

    if term_is_positive and any(pattern in prefix for pattern in NEGATION_PATTERNS):
        negative, positive = True, False
    elif term_is_negative and any(pattern in prefix for pattern in NEGATION_PATTERNS):
        positive, negative = True, False
    elif term_is_positive:
        positive = True
    elif term_is_negative:
        negative = True

    if negative and not positive:
        return "negative"
    if positive and not negative:
        return "positive"
    if negative and positive:
        negative_positions = [match.start() for match in _term_matches(lowered, list(NEGATIVE_TERMS))]
        positive_positions = [match.start() for match in _term_matches(lowered, list(POSITIVE_TERMS))]
        nearest_negative = min((abs(position - term_position) for position in negative_positions), default=10_000)
        nearest_positive = min((abs(position - term_position) for position in positive_positions), default=10_000)
        return "negative" if nearest_negative <= nearest_positive else "positive"
    if profile["require_polarity_cue"]:
        return None
    return "neutral" if profile["allow_neutral"] else None


def _negative_severity(context: str, aspect: str) -> str:
    high_terms = list(HIGH_SEVERITY_TERMS)
    if aspect != "sanitation":
        high_terms = [term for term in high_terms if term != "tidak ada air"]
    if _contains_term(context, high_terms):
        return "high"
    if _contains_term(context, MEDIUM_SEVERITY_TERMS):
        return "medium"
    return "low"


def label_review_pass(text: str, profile_name: str) -> list[dict[str, Any]]:
    taxonomy = load_config("taxonomy")
    profile = PASS_PROFILES[profile_name]
    labels: list[dict[str, Any]] = []
    for aspect, details in taxonomy["aspect_definitions"].items():
        matches = _term_matches(text, details["seed_terms"])
        if not matches:
            continue
        best_label: dict[str, Any] | None = None
        for match in matches:
            context = _evidence_span(text, match, profile["context_chars"])
            context_lower = context.casefold()
            if aspect == "maintenance" and match.group().casefold() == "rusak":
                maintenance_objects = (
                    "fasilitas", "gazebo", "bangunan", "kamar", "toilet", "wc", "kursi",
                    "lampu", "jembatan", "wahana", "pondok", "atap", "pagar",
                )
                if _contains_term(context_lower, ("jalan", "akses")) and not _contains_term(
                    context_lower, maintenance_objects
                ):
                    continue
            if aspect == "cleanliness" and _contains_term(
                context_lower, ("toilet", "wc", "kamar mandi")
            ) and not _contains_term(
                context_lower, ("area", "tempat", "lantai", "meja", "kamar", "lingkungan")
            ):
                continue
            if aspect == "public_facilities" and _contains_term(
                context_lower, ("toilet", "wc", "kamar mandi")
            ) and not _contains_term(
                context_lower,
                ("gazebo", "kursi", "tempat duduk", "penerangan", "lampu", "mushola", "masjid", "gereja", "difabel"),
            ):
                continue
            if aspect == "maintenance" and match.group().casefold() in {
                "perawatan",
                "maintenance",
            } and re.search(r"(?:dana|pembangunan|untuk).{0,35}(?:perawatan|maintenance)", context_lower):
                polarity = "neutral"
            else:
                polarity = _local_polarity(context, match.group(), profile)
            if polarity is None:
                continue
            candidate = {
                "aspect": aspect,
                "polarity": polarity,
                "severity": _negative_severity(context, aspect) if polarity == "negative" else None,
                "evidence_text": context,
            }
            if best_label is None or (
                candidate["polarity"] == "negative" and best_label["polarity"] != "negative"
            ):
                best_label = candidate
        if best_label:
            labels.append(best_label)
    return sorted(labels, key=lambda label: label["aspect"])


def _consensus_labels(pass_labels: dict[str, list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], float, list[dict[str, Any]]]:
    votes: dict[str, list[dict[str, Any]]] = {}
    for profile, labels in pass_labels.items():
        for label in labels:
            votes.setdefault(label["aspect"], []).append({**label, "profile": profile})

    consensus: list[dict[str, Any]] = []
    disagreements: list[dict[str, Any]] = []
    for aspect, aspect_votes in sorted(votes.items()):
        if len(aspect_votes) < 2:
            disagreements.append({"aspect": aspect, "reason": "single_pass_only", "votes": aspect_votes})
            continue
        polarity_counts = Counter(vote["polarity"] for vote in aspect_votes)
        polarity, polarity_votes = polarity_counts.most_common(1)[0]
        if polarity_votes < 2:
            disagreements.append({"aspect": aspect, "reason": "polarity_disagreement", "votes": aspect_votes})
            continue
        matching_votes = [vote for vote in aspect_votes if vote["polarity"] == polarity]
        severity = None
        if polarity == "negative":
            severity_counts = Counter(vote["severity"] for vote in matching_votes)
            severity = severity_counts.most_common(1)[0][0]
        evidence_vote = min(
            matching_votes,
            key=lambda vote: (len(vote["evidence_text"]), vote["profile"]),
        )
        vote_count = len(matching_votes)
        consensus.append(
            {
                "aspect": aspect,
                "polarity": polarity,
                "severity": severity,
                "evidence_text": evidence_vote["evidence_text"],
                "vote_count": vote_count,
                "confidence": round(vote_count / 3, 4),
            }
        )
        if vote_count < 3 or len(aspect_votes) < 3:
            disagreements.append({"aspect": aspect, "reason": "partial_consensus", "votes": aspect_votes})

    aspect_sets = [{label["aspect"] for label in labels} for labels in pass_labels.values()]
    pairwise = []
    for left, right in combinations(aspect_sets, 2):
        union = left | right
        pairwise.append(len(left & right) / len(union) if union else 1.0)
    return consensus, round(float(np.mean(pairwise)), 4), disagreements


def run_silver_annotation(
    processed_dir: Path,
    annotation_dir: Path,
    report_dir: Path,
) -> dict[str, Any]:
    annotation_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    reviews = pd.read_parquet(processed_dir / "canonical_reviews.parquet").set_index("review_id")
    pilot_ids = pd.read_csv(annotation_dir / "pilot_sampling_audit.csv")["review_id"].tolist()
    main_ids = pd.read_csv(annotation_dir / "main_sampling_audit.csv")["review_id"].tolist()

    pass_outputs: dict[str, list[dict[str, Any]]] = {profile: [] for profile in PASS_PROFILES}
    silver_records: list[dict[str, Any]] = []
    disagreement_records: list[dict[str, Any]] = []
    for phase, review_ids in (("pilot", pilot_ids), ("main", main_ids)):
        for review_id in review_ids:
            row = reviews.loc[review_id]
            text = row["review_text_raw"]
            pass_labels = {
                profile: label_review_pass(text, profile) for profile in PASS_PROFILES
            }
            for profile, labels in pass_labels.items():
                pass_outputs[profile].append(
                    {"phase": phase, "review_id": review_id, "labels": labels}
                )
            labels, agreement, disagreements = _consensus_labels(pass_labels)
            status = (
                "no_supported_aspect"
                if not labels and not disagreements
                else "review_recommended"
                if disagreements or agreement < 0.80
                else "consensus"
            )
            silver_records.append(
                {
                    "review_id": review_id,
                    "destination_id": row["destination_id"],
                    "text": text,
                    "rating_context": None if pd.isna(row["rating"]) else float(row["rating"]),
                    "labels": labels,
                    "annotation_version": "silver-1.0.0",
                    "label_source": "ai_assisted_weak_supervision",
                    "silver_status": status,
                    "pass_agreement": agreement,
                }
            )
            if disagreements:
                disagreement_records.append(
                    {
                        "phase": phase,
                        "review_id": review_id,
                        "destination_id": row["destination_id"],
                        "pass_agreement": agreement,
                        "disagreements": disagreements,
                    }
                )

    silver_path = annotation_dir / "silver-v1.0.0.jsonl"
    _write_jsonl(silver_path, sorted(silver_records, key=lambda record: record["review_id"]))
    for profile, records in pass_outputs.items():
        _write_jsonl(annotation_dir / f"silver-pass-{profile}.jsonl", records)
    _write_jsonl(annotation_dir / "silver-disagreement-queue.jsonl", disagreement_records)

    main_records = [record for record in silver_records if record["review_id"] in set(main_ids)]
    aspect_support = Counter(
        label["aspect"] for record in main_records for label in record["labels"]
    )
    polarity_support = Counter(
        label["polarity"] for record in main_records for label in record["labels"]
    )
    severity_support = Counter(
        label["severity"]
        for record in main_records
        for label in record["labels"]
        if label["severity"] is not None
    )
    status_counts = Counter(record["silver_status"] for record in silver_records)
    summary = {
        "silver_version": "silver-1.0.0",
        "label_source": "ai_assisted_weak_supervision",
        "pilot_records": len(pilot_ids),
        "main_records": len(main_ids),
        "total_records": len(silver_records),
        "status_counts": dict(status_counts),
        "mean_pass_agreement": round(float(np.mean([record["pass_agreement"] for record in silver_records])), 4),
        "disagreement_queue_records": len(disagreement_records),
        "main_aspect_support": dict(sorted(aspect_support.items())),
        "main_polarity_support": dict(sorted(polarity_support.items())),
        "main_severity_support": dict(sorted(severity_support.items())),
        "silver_sha256": sha256_file(silver_path),
        "taxonomy_sha256": sha256_file(ML_ROOT / "configs" / "taxonomy.yaml"),
        "limitations": [
            "Silver labels are AI-assisted weak-supervision outputs, not human gold labels.",
            "Pass agreement measures rule consistency, not inter-annotator agreement.",
            "Confidence is vote agreement and is not calibrated probability.",
            "Seed lexicons may miss implicit, sarcastic, or domain-specific statements.",
        ],
    }
    (report_dir / "silver_annotation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "artifact": str(silver_path),
        "sha256": summary["silver_sha256"],
        "records": len(silver_records),
        "annotation_version": "silver-1.0.0",
        "label_source": summary["label_source"],
        "taxonomy_sha256": summary["taxonomy_sha256"],
    }
    (annotation_dir / "silver-v1.0.0.manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def validate_silver_records(path: Path) -> dict[str, Any]:
    taxonomy = load_config("taxonomy")
    records = load_jsonl(path)
    errors: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for record in records:
        record_errors: list[str] = []
        review_id = record.get("review_id", "")
        if review_id in seen_ids:
            record_errors.append("duplicate review_id")
        seen_ids.add(review_id)
        if record.get("annotation_version") != "silver-1.0.0":
            record_errors.append("invalid silver version")
        if record.get("label_source") != "ai_assisted_weak_supervision":
            record_errors.append("invalid label source")
        seen_aspects: set[str] = set()
        for label in record.get("labels", []):
            aspect = label.get("aspect")
            polarity = label.get("polarity")
            severity = label.get("severity")
            if aspect not in taxonomy["aspect_definitions"]:
                record_errors.append(f"invalid aspect: {aspect}")
            if aspect in seen_aspects:
                record_errors.append(f"duplicate aspect: {aspect}")
            seen_aspects.add(aspect)
            if polarity not in taxonomy["polarity_labels"]:
                record_errors.append(f"invalid polarity: {polarity}")
            if polarity == "negative" and severity not in taxonomy["severity_labels"]:
                record_errors.append(f"negative label requires severity: {aspect}")
            if polarity != "negative" and severity is not None:
                record_errors.append(f"nonnegative severity must be null: {aspect}")
            if label.get("evidence_text") not in record.get("text", ""):
                record_errors.append(f"non-verbatim evidence: {aspect}")
            if label.get("vote_count") not in {2, 3}:
                record_errors.append(f"invalid vote count: {aspect}")
        if record_errors:
            errors.append({"review_id": review_id, "errors": record_errors})
    return {"records": len(records), "invalid_records": len(errors), "errors": errors}
