"""Destination-grouped, duplicate-safe split creation for silver annotations."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .config import ML_ROOT, load_config
from .manifest import sha256_file

SPLIT_NAMES = ("train", "validation", "test")


class _UnionFind:
    def __init__(self, values: list[str]) -> None:
        self.parent = {value: value for value in values}

    def find(self, value: str) -> str:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: str, right: str) -> None:
        left_root, right_root = self.find(left), self.find(right)
        if left_root != right_root:
            self.parent[max(left_root, right_root)] = min(left_root, right_root)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def load_split_source(
    annotation_path: Path,
    canonical_path: Path,
) -> list[dict[str, Any]]:
    """Join frozen silver records to canonical duplicate metadata with integrity checks."""

    records = _read_jsonl(annotation_path)
    canonical = pd.read_parquet(canonical_path)[
        ["review_id", "destination_id", "duplicate_group_id", "review_text_raw"]
    ]
    if canonical["review_id"].duplicated().any():
        raise ValueError("Canonical review_id must be unique")
    metadata = canonical.set_index("review_id").to_dict("index")
    joined: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records:
        review_id = record["review_id"]
        if review_id in seen:
            raise ValueError(f"Duplicate silver review_id: {review_id}")
        seen.add(review_id)
        if review_id not in metadata:
            raise ValueError(f"Silver review missing from canonical data: {review_id}")
        row = metadata[review_id]
        if record["destination_id"] != row["destination_id"]:
            raise ValueError(f"Destination mismatch for {review_id}")
        if record["text"] != row["review_text_raw"]:
            raise ValueError(f"Text mismatch for {review_id}")
        normalized_text = re.sub(
            r"\s+", " ", unicodedata.normalize("NFKC", record["text"]).casefold()
        ).strip()
        repeated_text_group_id = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()[:16]
        joined.append(
            {
                **record,
                "duplicate_group_id": row["duplicate_group_id"],
                "repeated_text_group_id": f"text_{repeated_text_group_id}",
            }
        )
    return joined


def build_leakage_components(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Connect destinations that share a technical duplicate group."""

    destinations = sorted({record["destination_id"] for record in records})
    union_find = _UnionFind(destinations)
    duplicate_destinations: dict[str, set[str]] = defaultdict(set)
    repeated_text_destinations: dict[str, set[str]] = defaultdict(set)
    for record in records:
        duplicate_destinations[record["duplicate_group_id"]].add(record["destination_id"])
        repeated_text_destinations[record["repeated_text_group_id"]].add(
            record["destination_id"]
        )
    for members in list(duplicate_destinations.values()) + list(
        repeated_text_destinations.values()
    ):
        ordered = sorted(members)
        for destination in ordered[1:]:
            union_find.union(ordered[0], destination)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[union_find.find(record["destination_id"])].append(record)
    components: list[dict[str, Any]] = []
    for component_id, members in sorted(grouped.items()):
        aspects = Counter(label["aspect"] for record in members for label in record["labels"])
        components.append(
            {
                "component_id": component_id,
                "records": members,
                "record_count": len(members),
                "destinations": sorted({record["destination_id"] for record in members}),
                "aspect_counts": aspects,
            }
        )
    return components


def _assignment_score(
    assignment: dict[str, str],
    components: list[dict[str, Any]],
    ratios: dict[str, float],
    aspects: list[str],
    config: dict[str, Any],
) -> float:
    destination_counts = Counter()
    record_counts = Counter()
    label_counts = {split: Counter() for split in SPLIT_NAMES}
    total_destinations = sum(len(component["destinations"]) for component in components)
    total_records = sum(component["record_count"] for component in components)
    total_labels = Counter()
    for component in components:
        split = assignment[component["component_id"]]
        destination_counts[split] += len(component["destinations"])
        record_counts[split] += component["record_count"]
        label_counts[split].update(component["aspect_counts"])
        total_labels.update(component["aspect_counts"])

    score = 0.0
    for split in SPLIT_NAMES:
        score += ((destination_counts[split] / total_destinations) - ratios[split]) ** 2 * 8
        score += (
            ((record_counts[split] / total_records) - ratios[split]) ** 2
            * config["record_balance_weight"]
        )
        for aspect in aspects:
            if total_labels[aspect]:
                actual = label_counts[split][aspect] / total_labels[aspect]
                score += (actual - ratios[split]) ** 2 * config["label_balance_weight"]
                if split != "train" and label_counts[split][aspect] == 0:
                    score += config["missing_label_penalty"]
    return score


def assign_components(
    components: list[dict[str, Any]],
    ratios: dict[str, float],
    aspects: list[str],
    seed: int,
    algorithm_config: dict[str, Any],
) -> dict[str, str]:
    """Select the best deterministic grouped assignment from seeded candidates."""

    rng = np.random.default_rng(seed)
    destination_total = sum(len(component["destinations"]) for component in components)
    target = {
        "validation": round(destination_total * ratios["validation"]),
        "test": round(destination_total * ratios["test"]),
    }
    target["train"] = destination_total - target["validation"] - target["test"]
    best: tuple[float, dict[str, str]] | None = None
    stable = sorted(components, key=lambda item: item["component_id"])
    for _ in range(algorithm_config["candidates"]):
        order = list(rng.permutation(len(stable)))
        assignment: dict[str, str] = {}
        counts = Counter()
        for index in order:
            component = stable[index]
            choices = [
                split
                for split in SPLIT_NAMES
                if counts[split] + len(component["destinations"]) <= target[split]
            ]
            if not choices:
                choices = list(SPLIT_NAMES)
            split = min(
                choices,
                key=lambda name: (counts[name] / max(target[name], 1), SPLIT_NAMES.index(name)),
            )
            assignment[component["component_id"]] = split
            counts[split] += len(component["destinations"])
        score = _assignment_score(assignment, stable, ratios, aspects, algorithm_config)
        signature = tuple(assignment[item["component_id"]] for item in stable)
        if best is None or (score, signature) < (
            best[0],
            tuple(best[1][item["component_id"]] for item in stable),
        ):
            best = (score, assignment)
    if best is None:
        raise ValueError("Unable to assign split components")
    return best[1]


def validate_split_records(split_records: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """Fail on review, destination, or duplicate-group leakage."""

    sets: dict[str, dict[str, set[str]]] = {}
    for split, records in split_records.items():
        sets[split] = {
            "reviews": {record["review_id"] for record in records},
            "destinations": {record["destination_id"] for record in records},
            "duplicates": {record["duplicate_group_id"] for record in records},
            "repeated_texts": {record["repeated_text_group_id"] for record in records},
        }
        if len(sets[split]["reviews"]) != len(records):
            raise ValueError(f"Duplicate review_id inside {split}")
    leakage: dict[str, int] = {}
    for index, left in enumerate(SPLIT_NAMES):
        for right in SPLIT_NAMES[index + 1 :]:
            for key in ("reviews", "destinations", "duplicates", "repeated_texts"):
                count = len(sets[left][key] & sets[right][key])
                leakage[f"{left}_{right}_{key}"] = count
                if count:
                    raise ValueError(f"Leakage detected: {left}/{right}/{key}={count}")
    return {"valid": True, "leakage_counts": leakage}


def _distribution(records: list[dict[str, Any]], aspects: list[str]) -> dict[str, Any]:
    aspect_counts = Counter(label["aspect"] for record in records for label in record["labels"])
    return {
        "records": len(records),
        "destinations": len({record["destination_id"] for record in records}),
        "duplicate_groups": len({record["duplicate_group_id"] for record in records}),
        "repeated_text_groups": len(
            {record["repeated_text_group_id"] for record in records}
        ),
        "empty_label_records": sum(not record["labels"] for record in records),
        "status_counts": dict(sorted(Counter(record["silver_status"] for record in records).items())),
        "aspect_support": {aspect: aspect_counts[aspect] for aspect in aspects},
    }


def run_split(
    processed_dir: Path,
    annotation_dir: Path,
    split_dir: Path,
    report_dir: Path,
) -> dict[str, Any]:
    """Create and lock split artifacts from frozen silver annotations."""

    config = load_config("split")
    taxonomy = load_config("taxonomy")
    aspects = sorted(taxonomy["aspect_definitions"])
    manifest_path = split_dir / "split_manifest_silver_v1.json"
    if manifest_path.exists():
        raise FileExistsError(f"Locked split manifest already exists: {manifest_path}")
    annotation_path = annotation_dir / config["annotation_file"]
    canonical_path = processed_dir / config["canonical_reviews_file"]
    records = load_split_source(annotation_path, canonical_path)
    components = build_leakage_components(records)
    assignment = assign_components(
        components, config["ratios"], aspects, config["seed"], config["algorithm"]
    )
    split_records = {split: [] for split in SPLIT_NAMES}
    for component in components:
        split = assignment[component["component_id"]]
        split_records[split].extend(
            {**record, "split": split} for record in component["records"]
        )
    for records_for_split in split_records.values():
        records_for_split.sort(key=lambda item: item["review_id"])
    validation = validate_split_records(split_records)

    split_dir.mkdir(parents=True, exist_ok=True)
    output_paths: dict[str, Path] = {}
    for split in SPLIT_NAMES:
        path = split_dir / f"{split}_silver_v1.jsonl"
        _write_jsonl(path, split_records[split])
        output_paths[split] = path
    manifest = {
        "split_version": config["split_version"],
        "algorithm": config["algorithm"],
        "seed": config["seed"],
        "ratios": config["ratios"],
        "annotation_version": "silver-1.0.0",
        "reference_label_type": "ai_assisted_weak_supervision_silver",
        "test_is_locked": True,
        "locked_at": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "silver_sha256": sha256_file(annotation_path),
            "canonical_reviews_sha256": sha256_file(canonical_path),
            "split_config_sha256": sha256_file(ML_ROOT / "configs" / "split.yaml"),
            "taxonomy_sha256": sha256_file(ML_ROOT / "configs" / "taxonomy.yaml"),
        },
        "component_count": len(components),
        "cross_destination_duplicate_groups": sum(
            len({record["destination_id"] for record in records if record["duplicate_group_id"] == group}) > 1
            for group in {record["duplicate_group_id"] for record in records}
        ),
        "multi_destination_components": sum(
            len(component["destinations"]) > 1 for component in components
        ),
        "cross_destination_repeated_text_groups": sum(
            len({record["destination_id"] for record in records if record["repeated_text_group_id"] == group}) > 1
            for group in {record["repeated_text_group_id"] for record in records}
        ),
        "distribution": {
            split: _distribution(split_records[split], aspects) for split in SPLIT_NAMES
        },
        "destination_ids": {
            split: sorted({record["destination_id"] for record in split_records[split]})
            for split in SPLIT_NAMES
        },
        "validation": validation,
        "outputs": {
            split: {"path": path.name, "sha256": sha256_file(path)}
            for split, path in output_paths.items()
        },
        "limitations": [
            "Labels are AI-assisted silver references, not human gold.",
            "duplicate_group_id represents technical exact duplicates, not semantic near-duplicates.",
            "Normalized exact repeated text is grouped across destinations; semantic paraphrases remain possible.",
            "Label balancing uses silver labels only for split stratification, not model selection.",
        ],
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "split_summary.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest
