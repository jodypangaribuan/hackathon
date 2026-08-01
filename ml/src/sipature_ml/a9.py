"""A9 full-corpus inference, aggregation, priority, and safe export."""

from __future__ import annotations

import json
import math
import re
from collections.abc import Iterable
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import sklearn

from .baselines import CONTRASTS, NEGATIVE_CUES, POSITIVE_CUES
from .config import ML_ROOT, load_config
from .manifest import sha256_file

REVIEW_COLUMNS = {
    "review_id", "destination_id", "review_text_raw", "has_text", "rating",
    "published_date_estimate", "duplicate_group_id", "source_file", "source_row",
}
DESTINATION_COLUMNS = {
    "destination_id", "canonical_name", "kind", "latitude", "longitude", "address",
    "category", "canonical_status",
}


def _write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _preflight_output(output_dir: Path) -> None:
    if output_dir.exists():
        raise FileExistsError(f"Immutable output directory already exists: {output_dir}")


def _require_columns(frame: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{name} is missing columns: {missing}")


def _artifact_hashes(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): sha256_file(path)
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.name != "manifest.json"
    }


def _manifest(stage: str, config: dict[str, Any], sources: Iterable[Path]) -> dict[str, Any]:
    contract_sources = [
        ML_ROOT / "configs" / "a9.yaml",
        ML_ROOT / "configs" / "scoring.yaml",
        ML_ROOT / "configs" / "taxonomy.yaml",
        Path(__file__),
    ]
    return {
        "a9_version": config["a9_version"],
        "stage": stage,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sources": {str(path): sha256_file(path) for path in [*sources, *contract_sources]},
    }


def _contains(text: str, term: str) -> bool:
    return bool(re.search(rf"(?<!\w){re.escape(term.casefold())}(?!\w)", text.casefold()))


def classify_polarity(text: str, aspect: str, taxonomy: dict[str, Any]) -> str:
    """Return an explicitly lexical aspect-conditioned polarity fallback."""

    lowered = text.casefold()
    terms = taxonomy["aspect_definitions"][aspect]["seed_terms"]
    positions = [lowered.find(term.casefold()) for term in terms if _contains(lowered, term)]
    if positions:
        position = min(item for item in positions if item >= 0)
        local = lowered[max(0, position - 70): position + 120]
    else:
        local = lowered
    for marker in CONTRASTS:
        if marker in local:
            clauses = re.split(rf"\b{re.escape(marker)}\b", local, maxsplit=1)
            local = next((clause for clause in clauses if any(term in clause for term in terms)), local)
            break
    negative = sum(_contains(local, cue) for cue in NEGATIVE_CUES)
    positive = sum(_contains(local, cue) for cue in POSITIVE_CUES)
    if negative > positive:
        return "negative"
    if positive > negative:
        return "positive"
    return "neutral"


def _evidence_span(text: str, aspect: str, taxonomy: dict[str, Any], max_chars: int) -> str:
    lowered = text.casefold()
    positions = [
        lowered.find(term.casefold())
        for term in taxonomy["aspect_definitions"][aspect]["seed_terms"]
        if _contains(lowered, term)
    ]
    center = min((value for value in positions if value >= 0), default=0)
    start = max(0, center - max_chars // 3)
    return text[start:start + max_chars].strip()


def load_tfidf_contract(model_dir: Path, config: dict[str, Any]) -> dict[str, Any]:
    """Verify and load the exact TF-IDF artifact selected after A8."""

    section = config["models"]["aspect"]
    model_path, manifest_path = model_dir / "model.joblib", model_dir / "manifest.json"
    if sklearn.__version__ != section["required_sklearn_version"]:
        raise RuntimeError(
            f"scikit-learn {section['required_sklearn_version']} is required; "
            f"found {sklearn.__version__}"
        )
    if sha256_file(model_path) != section["model_sha256"]:
        raise ValueError("TF-IDF model hash mismatch")
    if sha256_file(manifest_path) != section["manifest_sha256"]:
        raise ValueError("TF-IDF manifest hash mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["model_version"] != section["version"]:
        raise ValueError("TF-IDF model version mismatch")
    if manifest["taxonomy_sha256"] != sha256_file(ML_ROOT / "configs" / "taxonomy.yaml"):
        raise ValueError("TF-IDF taxonomy hash mismatch")
    artifact = joblib.load(model_path)
    expected = sorted(load_config("taxonomy")["aspect_definitions"])
    if artifact["aspects"] != expected:
        raise ValueError("TF-IDF aspect order differs from taxonomy")
    return artifact


def infer_frame(
    reviews: pd.DataFrame,
    artifact: dict[str, Any],
    config: dict[str, Any],
    generated_at: str,
) -> pd.DataFrame:
    """Infer restricted review-level records from canonical textual reviews."""

    _require_columns(reviews, REVIEW_COLUMNS, "canonical reviews")
    textual = reviews.loc[reviews["has_text"]].copy()
    if textual["review_id"].duplicated().any() or textual["destination_id"].isna().any():
        raise ValueError("Text reviews require unique review_id and destination_id")
    texts = textual["review_text_raw"].fillna("").astype(str).tolist()
    probabilities = np.asarray(
        artifact["model"].predict_proba(artifact["vectorizer"].transform(texts)), dtype=float
    )
    aspects = artifact["aspects"]
    thresholds = np.asarray(artifact["thresholds"], dtype=float)
    if probabilities.shape != (len(textual), len(aspects)):
        raise ValueError("TF-IDF probability shape mismatch")
    taxonomy = load_config("taxonomy")
    polarity_version = config["models"]["polarity"]["version"]
    records: list[dict[str, Any]] = []
    for row_index, (_, row) in enumerate(textual.iterrows()):
        text = texts[row_index]
        predictions = []
        for aspect_index, aspect in enumerate(aspects):
            probability = float(probabilities[row_index, aspect_index])
            if probability < thresholds[aspect_index]:
                continue
            predictions.append({
                "aspect": aspect,
                "aspect_probability": probability,
                "polarity": classify_polarity(text, aspect, taxonomy),
                "polarity_probability": None,
                "polarity_model_version": polarity_version,
                "severity": None,
                "severity_probability": None,
                "severity_status": config["models"]["severity"]["status"],
            })
        records.append({
            "review_id": row["review_id"],
            "destination_id": row["destination_id"],
            "generated_at": generated_at,
            "model_version": config["a9_version"],
            "rating": None if pd.isna(row["rating"]) else float(row["rating"]),
            "published_date_estimate": row["published_date_estimate"],
            "duplicate_group_id": row["duplicate_group_id"],
            "source_file": row["source_file"],
            "source_row": int(row["source_row"]),
            "review_text": text,
            "predictions": predictions,
        })
    return pd.DataFrame(records)


def run_inference(
    reviews_path: Path, model_dir: Path, output_dir: Path,
) -> dict[str, Any]:
    """Run immutable, restricted full-corpus aspect and polarity inference."""

    _preflight_output(output_dir)
    config = load_config("a9")
    artifact = load_tfidf_contract(model_dir, config)
    reviews = pd.read_parquet(reviews_path)
    generated_at = datetime.now(timezone.utc).isoformat()
    predictions = infer_frame(reviews, artifact, config, generated_at)
    output_dir.mkdir(parents=True)
    prediction_path = output_dir / "review-predictions.parquet"
    predictions.to_parquet(prediction_path, index=False)
    summary = {
        "a9_version": config["a9_version"],
        "generated_at": generated_at,
        "text_reviews": len(predictions),
        "reviews_with_predictions": int(predictions["predictions"].map(bool).sum()),
        "aspect_predictions": int(predictions["predictions"].map(len).sum()),
        "aspect_model": config["models"]["aspect"]["version"],
        "polarity_model": config["models"]["polarity"]["version"],
        "severity_status": config["models"]["severity"]["status"],
        "restricted": True,
    }
    _write_json(output_dir / "summary.json", summary)
    manifest = _manifest("infer", config, [reviews_path, model_dir / "model.joblib",
                                             model_dir / "manifest.json"])
    manifest["artifact_hashes"] = _artifact_hashes(output_dir)
    _write_json(output_dir / "manifest.json", manifest)
    return summary


def freshness_weight(value: Any, reference_date: date, half_life_days: int) -> float:
    if value is None or pd.isna(value):
        return 0.5
    parsed = pd.Timestamp(value).date()
    age = max(0, (reference_date - parsed).days)
    return float(0.5 ** (age / half_life_days))


def bayesian_rate(negative: float, mentions: float, global_rate: float, alpha: float) -> float:
    if mentions < 0 or negative < 0 or negative > mentions or alpha <= 0:
        raise ValueError("Invalid Bayesian rate inputs")
    return float((negative + alpha * global_rate) / (mentions + alpha))


def _confidence(mentions: int, levels: dict[str, int], missing_components: int = 0) -> str:
    if mentions < levels["low"]:
        return "insufficient"
    level = "high" if mentions >= levels["high"] else "medium" if mentions >= levels["medium"] else "low"
    order = ["low", "medium", "high"]
    return order[max(0, order.index(level) - missing_components)]


def aggregate_frames(
    predictions: pd.DataFrame,
    reviews: pd.DataFrame,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aggregate review predictions into destination-aspect signals and evidence."""

    required = {"review_id", "destination_id", "predictions", "review_text",
                "published_date_estimate", "duplicate_group_id", "source_file", "source_row"}
    _require_columns(predictions, required, "review predictions")
    _require_columns(reviews, {"destination_id", "has_text"}, "canonical reviews")
    section = config["aggregation"]
    parsed_dates = pd.to_datetime(predictions["published_date_estimate"], errors="coerce")
    reference = parsed_dates.max().date() if parsed_dates.notna().any() else datetime.now(timezone.utc).date()
    duplicate_sizes = predictions["duplicate_group_id"].value_counts()
    flat: list[dict[str, Any]] = []
    for _, row in predictions.iterrows():
        for prediction in row["predictions"]:
            freshness = freshness_weight(
                row["published_date_estimate"], reference, section["freshness_half_life_days"]
            )
            duplicate = (
                section["duplicate_discount"]
                if duplicate_sizes.get(row["duplicate_group_id"], 0) > 1
                else 1.0
            )
            flat.append({
                **prediction,
                "review_id": row["review_id"], "destination_id": row["destination_id"],
                "review_text": row["review_text"], "source_file": row["source_file"],
                "source_row": row["source_row"], "published_date_estimate": row["published_date_estimate"],
                "duplicate_group_id": row["duplicate_group_id"], "freshness_weight": freshness,
                "duplicate_discount": duplicate,
                "weight": prediction["aspect_probability"] * freshness * duplicate,
            })
    columns = ["destination_id", "aspect", "mention_count", "negative_count",
               "severe_count", "complaint_rate", "smoothed_complaint_rate",
               "mean_confidence", "persistence", "freshness", "unique_review_count",
               "text_review_count", "all_review_count", "data_confidence", "severity_status"]
    if not flat:
        return pd.DataFrame(columns=columns), pd.DataFrame()
    frame = pd.DataFrame(flat)
    global_rates = frame.groupby("aspect")["polarity"].apply(lambda x: (x == "negative").mean())
    text_counts = reviews.loc[reviews["has_text"]].groupby("destination_id").size()
    all_counts = reviews.groupby("destination_id").size()
    signals, evidence = [], []
    for (destination_id, aspect), group in frame.groupby(["destination_id", "aspect"]):
        negative = group["polarity"].eq("negative")
        weighted_mentions = float(group["weight"].sum())
        weighted_negative = float(group.loc[negative, "weight"].sum())
        recent = pd.to_datetime(group["published_date_estimate"], errors="coerce")
        cutoff = pd.Timestamp(reference) - pd.Timedelta(days=section["persistence_recent_days"])
        old_negative = bool((negative & (recent < cutoff)).any())
        recent_negative = bool((negative & (recent >= cutoff)).any())
        signal = {
            "destination_id": destination_id, "aspect": aspect,
            "mention_count": len(group), "negative_count": int(negative.sum()),
            "severe_count": None,
            "complaint_rate": 0.0 if not weighted_mentions else weighted_negative / weighted_mentions,
            "smoothed_complaint_rate": bayesian_rate(
                weighted_negative, weighted_mentions, float(global_rates[aspect]), section["bayesian_alpha"]
            ),
            "mean_confidence": float(group["aspect_probability"].mean()),
            "persistence": float(old_negative and recent_negative),
            "freshness": float(group["freshness_weight"].mean()),
            "unique_review_count": int(group["review_id"].nunique()),
            "text_review_count": int(text_counts.get(destination_id, 0)),
            "all_review_count": int(all_counts.get(destination_id, 0)),
            "data_confidence": _confidence(len(group), section["minimum_mentions"], 1),
            "severity_status": config["models"]["severity"]["status"],
        }
        signals.append(signal)
        eligible = group.loc[
            negative & (group["aspect_probability"] >= config["inference"]["evidence_min_aspect_probability"])
        ].sort_values(["aspect_probability", "freshness_weight"], ascending=False)
        seen: set[str] = set()
        for _, item in eligible.iterrows():
            duplicate_key = item["duplicate_group_id"] or item["review_id"]
            if duplicate_key in seen or len(seen) >= section["evidence_per_issue"]:
                continue
            seen.add(duplicate_key)
            evidence.append({
                "destination_id": destination_id, "aspect": aspect,
                "review_id": item["review_id"], "source_file": item["source_file"],
                "source_row": int(item["source_row"]),
                "text": _evidence_span(item["review_text"], aspect, load_config("taxonomy"),
                                        section["evidence_max_chars"]),
                "aspect_probability": float(item["aspect_probability"]),
                "published_date_estimate": item["published_date_estimate"],
            })
    return pd.DataFrame(signals), pd.DataFrame(evidence)


def run_aggregation(
    predictions_dir: Path, reviews_path: Path, output_dir: Path,
) -> dict[str, Any]:
    _preflight_output(output_dir)
    config = load_config("a9")
    predictions_path = predictions_dir / "review-predictions.parquet"
    predictions = pd.read_parquet(predictions_path)
    reviews = pd.read_parquet(reviews_path)
    signals, evidence = aggregate_frames(predictions, reviews, config)
    output_dir.mkdir(parents=True)
    signals.to_parquet(output_dir / "destination-aspect-signals.parquet", index=False)
    evidence.to_parquet(output_dir / "evidence.parquet", index=False)
    summary = {"a9_version": config["a9_version"], "signals": len(signals),
               "evidence_items": len(evidence), "destinations": int(signals["destination_id"].nunique()),
               "severity_status": config["models"]["severity"]["status"], "restricted": True}
    _write_json(output_dir / "summary.json", summary)
    manifest = _manifest("aggregate", config, [predictions_path, predictions_dir / "manifest.json", reviews_path])
    manifest["artifact_hashes"] = _artifact_hashes(output_dir)
    _write_json(output_dir / "manifest.json", manifest)
    return summary


def priority_score(components: dict[str, float | None], weights: dict[str, float]) -> dict[str, Any]:
    """Renormalize available priority components and expose every contribution."""

    available = {key: value for key, value in components.items() if value is not None}
    available_weight = sum(weights[key] for key in available)
    if not available or available_weight <= 0:
        return {"score": None, "available_weight": 0.0, "components": {}}
    details = {}
    score = 0.0
    for key, value in available.items():
        normalized_weight = weights[key] / available_weight
        contribution = float(value) * normalized_weight
        score += contribution
        details[key] = {"value": float(value), "original_weight": weights[key],
                        "effective_weight": normalized_weight, "contribution": contribution}
    return {"score": score, "available_weight": available_weight, "components": details}


def _priority_label(score: float | None, available_weight: float, config: dict[str, Any]) -> str:
    if score is None or available_weight < config["priority"]["minimum_available_weight"]:
        return "Insufficient Data"
    for label, cutoff in config["priority"]["labels"].items():
        if score >= cutoff:
            return label
    raise AssertionError("Priority labels must include a zero cutoff")


def validate_export(payload: dict[str, Any]) -> None:
    """Enforce the operational A9 gate without adding a runtime schema dependency."""

    required = {"schema_version", "model_version", "generated_at", "source_manifest",
                "limitations", "destinations"}
    if required - payload.keys():
        raise ValueError("A9 export is missing required top-level fields")
    if not re.fullmatch(r"[a-f0-9]{64}", payload["source_manifest"]):
        raise ValueError("A9 export source manifest must be a SHA-256 digest")
    seen = set()
    for destination in payload["destinations"]:
        if destination["destination_id"] in seen:
            raise ValueError("A9 export destination IDs must be unique")
        seen.add(destination["destination_id"])
        for issue in destination["issues"]:
            if issue["priority"] != "Insufficient Data" and not issue["evidence"]:
                raise ValueError("Every actionable A9 issue must contain evidence")
            if issue["severity_status"] != "unavailable_no_supported_model":
                raise ValueError("A9 severity status is not the frozen unavailable state")
            if not issue["explanation"] or not issue["recommended_verification"]:
                raise ValueError("Every A9 issue needs an explanation and verification action")


def prioritize_frames(
    signals: pd.DataFrame, destinations: pd.DataFrame, config: dict[str, Any],
) -> pd.DataFrame:
    _require_columns(destinations, DESTINATION_COLUMNS, "canonical destinations")
    weights = load_config("scoring")["priority_weights"]
    max_exposure = max(1, int(signals["all_review_count"].max())) if len(signals) else 1
    records = []
    for _, destination in destinations.iterrows():
        rows = signals.loc[signals["destination_id"] == destination["destination_id"]].copy()
        issues = []
        for _, signal in rows.iterrows():
            components = {
                "severity": None,
                "complaint_frequency": float(signal["smoothed_complaint_rate"]),
                "model_confidence": float(signal["mean_confidence"]),
                "persistence": float(signal["persistence"]),
                "visitor_exposure": min(1.0, math.log1p(signal["all_review_count"]) / math.log1p(max_exposure)),
                "facility_gap": None,
                "feasibility": None,
            }
            scored = priority_score(components, weights)
            label = _priority_label(scored["score"], scored["available_weight"], config)
            if signal["mention_count"] < config["priority"]["minimum_issue_mentions"]:
                label = "Insufficient Data"
            if destination["canonical_status"] != "metadata_anchor":
                label = "Insufficient Data"
            mapping = config["interventions"][signal["aspect"]]
            issues.append({
                **signal.to_dict(), "priority_score": scored["score"], "priority": label,
                "priority_components": scored["components"],
                "available_weight": scored["available_weight"],
                "recommended_verification": mapping["verification"],
                "candidate_intervention": mapping["candidate"],
                "explanation": (
                    "Priority uses available components only; severity, facility gap, and feasibility are unavailable."
                    if destination["canonical_status"] == "metadata_anchor"
                    else "Destination identity is unresolved; operational priority is withheld."
                ),
            })
        issues.sort(key=lambda item: (-1 if item["priority_score"] is None else -item["priority_score"], item["aspect"]))
        top = issues[:config["priority"]["top_issues_per_destination"]]
        usable = [item for item in top if item["priority"] != "Insufficient Data"]
        overall = usable[0]["priority"] if usable else "Insufficient Data"
        overall_score = usable[0]["priority_score"] if usable else None
        records.append({
            "destination_id": destination["destination_id"], "name": destination["canonical_name"],
            "kind": destination["kind"], "latitude": destination["latitude"],
            "longitude": destination["longitude"], "address": destination["address"],
            "category": destination["category"], "canonical_status": destination["canonical_status"],
            "data_confidence": usable[0]["data_confidence"] if usable else "insufficient",
            "priority": overall, "priority_score": overall_score,
            "health_score": None if not usable else 100 * (1 - np.mean([item["smoothed_complaint_rate"] for item in usable])),
            "issues": top,
        })
    return pd.DataFrame(records)


def run_prioritization(
    aggregation_dir: Path, destinations_path: Path, output_dir: Path,
) -> dict[str, Any]:
    _preflight_output(output_dir)
    config = load_config("a9")
    signals_path = aggregation_dir / "destination-aspect-signals.parquet"
    prioritized = prioritize_frames(pd.read_parquet(signals_path), pd.read_parquet(destinations_path), config)
    output_dir.mkdir(parents=True)
    prioritized.to_parquet(output_dir / "prioritized-destinations.parquet", index=False)
    summary = {"a9_version": config["a9_version"], "destinations": len(prioritized),
               "with_priority": int(prioritized["priority"].ne("Insufficient Data").sum()),
               "severity_status": config["models"]["severity"]["status"]}
    _write_json(output_dir / "summary.json", summary)
    manifest = _manifest("prioritize", config, [signals_path, aggregation_dir / "manifest.json", destinations_path])
    manifest["artifact_hashes"] = _artifact_hashes(output_dir)
    _write_json(output_dir / "manifest.json", manifest)
    return summary


def run_export(prioritization_dir: Path, aggregation_dir: Path, output_dir: Path) -> dict[str, Any]:
    """Write a privacy-safe aggregate export without overwriting app baseline data."""

    _preflight_output(output_dir)
    config = load_config("a9")
    prioritized_path = prioritization_dir / "prioritized-destinations.parquet"
    evidence_path = aggregation_dir / "evidence.parquet"
    destinations = pd.read_parquet(prioritized_path)
    evidence = pd.read_parquet(evidence_path)
    generated_at = datetime.now(timezone.utc).isoformat()
    exported = []
    for _, destination in destinations.iterrows():
        issues = []
        for issue in destination["issues"]:
            safe_evidence = evidence.loc[
                (evidence["destination_id"] == destination["destination_id"])
                & (evidence["aspect"] == issue["aspect"])
            ]
            priority = issue["priority"] if len(safe_evidence) else "Insufficient Data"
            issues.append({
                "aspect": issue["aspect"], "mention_count": int(issue["mention_count"]),
                "negative_count": int(issue["negative_count"]), "severe_count": None,
                "text_review_count": int(issue["text_review_count"]),
                "all_review_count": int(issue["all_review_count"]),
                "smoothed_complaint_rate": float(issue["smoothed_complaint_rate"]),
                "mean_confidence": float(issue["mean_confidence"]),
                "data_confidence": issue["data_confidence"], "priority": priority,
                "priority_score": issue["priority_score"], "priority_components": issue["priority_components"],
                "severity_status": issue["severity_status"], "explanation": issue["explanation"],
                "recommended_verification": issue["recommended_verification"],
                "candidate_intervention": issue["candidate_intervention"],
                "evidence": [{"text": row["text"], "aspect_probability": float(row["aspect_probability"]),
                              "published_date_estimate": row["published_date_estimate"]}
                             for _, row in safe_evidence.iterrows()],
            })
        actionable = [item for item in issues if item["priority"] != "Insufficient Data"]
        exported.append({
            "destination_id": destination["destination_id"], "name": destination["name"],
            "kind": destination["kind"],
            "latitude": None if pd.isna(destination["latitude"]) else float(destination["latitude"]),
            "longitude": None if pd.isna(destination["longitude"]) else float(destination["longitude"]),
            "data_confidence": actionable[0]["data_confidence"] if actionable else "insufficient",
            "priority": actionable[0]["priority"] if actionable else "Insufficient Data",
            "priority_score": actionable[0]["priority_score"] if actionable else None,
            "health_score": destination["health_score"] if actionable else None,
            "issues": issues,
        })
    payload = {
        "schema_version": config["schema_version"], "model_version": config["a9_version"],
        "generated_at": generated_at,
        "source_manifest": sha256_file(prioritization_dir / "manifest.json"),
        "limitations": [config["models"]["polarity"]["limitation"],
                        "Severity and facility-gap components are unavailable.",
                        "Evidence is anonymized but remains restricted pending privacy review."],
        "destinations": exported,
    }
    validate_export(payload)
    output_dir.mkdir(parents=True)
    _write_json(output_dir / "app-export.json", payload)
    manifest = _manifest("export-app", config, [prioritized_path, prioritization_dir / "manifest.json",
                                                 evidence_path, aggregation_dir / "manifest.json"])
    manifest["artifact_hashes"] = _artifact_hashes(output_dir)
    _write_json(output_dir / "manifest.json", manifest)
    return {"a9_version": config["a9_version"], "destinations": len(exported),
            "output": str(output_dir / "app-export.json"), "restricted": True}


def build_expert_review_queue(
    prioritized: pd.DataFrame, evidence: pd.DataFrame, size: int = 25,
) -> pd.DataFrame:
    """Build a deterministic restricted queue without fabricating human judgments."""

    candidates = prioritized.loc[
        prioritized["priority"].ne("Insufficient Data")
        & prioritized["canonical_status"].eq("metadata_anchor")
    ].sort_values(["priority_score", "destination_id"], ascending=[False, True])
    rows = []
    for _, destination in candidates.head(size).iterrows():
        issue = next(
            item for item in destination["issues"] if item["priority"] != "Insufficient Data"
        )
        snippets = evidence.loc[
            (evidence["destination_id"] == destination["destination_id"])
            & (evidence["aspect"] == issue["aspect"])
        ]
        rows.append({
            "destination_id": destination["destination_id"],
            "destination_name": destination["name"],
            "aspect": issue["aspect"],
            "priority": issue["priority"],
            "priority_score": issue["priority_score"],
            "evidence": snippets["text"].tolist(),
            "recommended_verification": issue["recommended_verification"],
            "candidate_intervention": issue["candidate_intervention"],
            "issue_correct": None,
            "evidence_supported": None,
            "intervention_relevant": None,
            "misleading_risk": None,
            "reviewer_notes": None,
        })
    return pd.DataFrame(rows)


def weight_sensitivity(
    prioritized: pd.DataFrame, weights: dict[str, float], delta: float = 0.2,
) -> dict[str, Any]:
    """Measure top-destination stability under one-at-a-time weight perturbations."""

    base_rows = prioritized.loc[prioritized["priority"].ne("Insufficient Data")]
    base_top = set(base_rows.nlargest(20, "priority_score")["destination_id"])
    scenarios = {}
    for component in weights:
        perturbed = dict(weights)
        perturbed[component] *= 1 + delta
        scores = []
        for _, destination in base_rows.iterrows():
            issue = next(item for item in destination["issues"] if item["priority"] != "Insufficient Data")
            values = {key: None for key in weights}
            values.update({key: value["value"] for key, value in issue["priority_components"].items()})
            scores.append((destination["destination_id"], priority_score(values, perturbed)["score"]))
        top = {item[0] for item in sorted(scores, key=lambda item: (-item[1], item[0]))[:20]}
        scenarios[f"{component}_plus_{int(delta * 100)}pct"] = {
            "top20_overlap": len(base_top & top), "top20_jaccard": len(base_top & top) / len(base_top | top)
        }
    return {"base_top20_count": len(base_top), "scenarios": scenarios}
