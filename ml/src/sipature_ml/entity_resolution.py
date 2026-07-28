"""Conservative entity resolution for SIPATURE place and review records."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from rapidfuzz.fuzz import ratio, token_set_ratio

from .cleaning import normalize_name
from .config import ML_ROOT
from .manifest import sha256_file


def haversine_meters(
    latitude_a: float, longitude_a: float, latitude_b: float, longitude_b: float
) -> float:
    radius = 6_371_008.8
    lat_a, lon_a, lat_b, lon_b = map(
        math.radians, (latitude_a, longitude_a, latitude_b, longitude_b)
    )
    delta_lat, delta_lon = lat_b - lat_a, lon_b - lon_a
    value = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat_a) * math.cos(lat_b) * math.sin(delta_lon / 2) ** 2
    )
    return radius * 2 * math.asin(math.sqrt(value))


def _canonical_id(kind: str, normalized_name: str, suffix: str = "") -> str:
    payload = f"{kind}\x1f{normalized_name}\x1f{suffix}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:14]
    return f"dest_{kind}_{digest}"


def _compatible(source_kind: str, anchor_kind: str) -> bool:
    if source_kind == "wisata":
        return anchor_kind == "wisata"
    if source_kind in {"service", "resto", "hotel"}:
        return anchor_kind in {"resto", "hotel"}
    return True


def build_canonical_anchors(place_sources: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create canonical anchors, merging only same-kind exact names within 500 meters."""

    anchors = place_sources.loc[place_sources["is_anchor"]].copy().reset_index(drop=True)
    anchors["cluster_key"] = anchors.apply(
        lambda row: f"{row.source_kind}\x1f{row.name_normalized}", axis=1
    )
    canonical_records: list[dict[str, Any]] = []
    anchor_links: list[dict[str, Any]] = []
    for cluster_key, group in anchors.groupby("cluster_key", sort=True):
        kind, normalized_name = cluster_key.split("\x1f", 1)
        subclusters: list[list[int]] = []
        for index, row in group.iterrows():
            assigned = False
            for subcluster in subclusters:
                representative = anchors.loc[subcluster[0]]
                distance = haversine_meters(
                    float(row["latitude"]),
                    float(row["longitude"]),
                    float(representative["latitude"]),
                    float(representative["longitude"]),
                )
                if distance <= 500:
                    subcluster.append(index)
                    assigned = True
                    break
            if not assigned:
                subclusters.append([index])

        for position, indices in enumerate(subclusters):
            members = anchors.loc[indices]
            suffix = str(position) if len(subclusters) > 1 else ""
            destination_id = _canonical_id(kind, normalized_name, suffix)
            representative = members.sort_values(["source_file", "source_row"]).iloc[0]
            canonical_records.append(
                {
                    "destination_id": destination_id,
                    "canonical_name": representative["name_raw"],
                    "normalized_name": normalized_name,
                    "kind": kind,
                    "latitude": float(members["latitude"].mean()),
                    "longitude": float(members["longitude"].mean()),
                    "address": representative["address_raw"],
                    "category": representative["category_raw"],
                    "status": representative["status_raw"],
                    "source_record_count": len(members),
                    "canonical_status": "metadata_anchor",
                }
            )
            for _, member in members.iterrows():
                anchor_links.append(
                    {
                        "source_record_id": member["source_record_id"],
                        "destination_id": destination_id,
                        "match_status": "auto_match",
                        "match_rule": "metadata_anchor_exact_name_kind_distance",
                        "name_similarity": 1.0,
                        "address_similarity": 1.0,
                        "distance_meters": 0.0,
                        "candidate_count": 1,
                    }
                )
    return pd.DataFrame(canonical_records), pd.DataFrame(anchor_links)


def _rank_candidates(source: pd.Series, anchors: pd.DataFrame) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for anchor in anchors.itertuples(index=False):
        if not _compatible(str(source["source_kind"]), anchor.kind):
            continue
        name_similarity = max(
            ratio(source["name_normalized"], anchor.normalized_name),
            token_set_ratio(source["name_normalized"], anchor.normalized_name),
        ) / 100
        if name_similarity < 0.60:
            continue
        address_similarity = 0.0
        if source.get("address_normalized") and anchor.address:
            address_similarity = token_set_ratio(
                source["address_normalized"], normalize_name(anchor.address)
            ) / 100
        score = 0.85 * name_similarity + 0.15 * address_similarity
        candidates.append(
            {
                "destination_id": anchor.destination_id,
                "canonical_name": anchor.canonical_name,
                "name_similarity": name_similarity,
                "address_similarity": address_similarity,
                "score": score,
            }
        )
    return sorted(candidates, key=lambda item: (-item["score"], -item["name_similarity"]))


def resolve_sources(
    sources: pd.DataFrame,
    canonical: pd.DataFrame,
    *,
    allow_fuzzy_auto: bool,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Resolve source records; unresolved records receive no forced anchor match."""

    exact_lookup: dict[tuple[str, str], list[str]] = {}
    for row in canonical.itertuples(index=False):
        kinds = ("service", "resto", "hotel") if row.kind in {"resto", "hotel"} else ("wisata",)
        for kind in kinds:
            exact_lookup.setdefault((kind, row.normalized_name), []).append(row.destination_id)

    links: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    for _, source in sources.iterrows():
        exact_ids = exact_lookup.get((str(source["source_kind"]), source["name_normalized"]), [])
        if len(exact_ids) == 1:
            links.append(
                {
                    "source_record_id": source["source_record_id"],
                    "destination_id": exact_ids[0],
                    "match_status": "auto_match",
                    "match_rule": "exact_normalized_name_kind",
                    "name_similarity": 1.0,
                    "address_similarity": np.nan,
                    "distance_meters": np.nan,
                    "candidate_count": 1,
                }
            )
            continue

        candidates = _rank_candidates(source, canonical)
        best = candidates[0] if candidates else None
        second_score = candidates[1]["score"] if len(candidates) > 1 else 0.0
        margin = best["score"] - second_score if best else 0.0
        if (
            allow_fuzzy_auto
            and best
            and best["name_similarity"] >= 0.90
            and best["address_similarity"] >= 0.65
            and margin >= 0.08
        ):
            links.append(
                {
                    "source_record_id": source["source_record_id"],
                    "destination_id": best["destination_id"],
                    "match_status": "auto_match",
                    "match_rule": "fuzzy_name_address",
                    "name_similarity": best["name_similarity"],
                    "address_similarity": best["address_similarity"],
                    "distance_meters": np.nan,
                    "candidate_count": len(candidates),
                }
            )
        elif best and best["name_similarity"] >= 0.75:
            links.append(
                {
                    "source_record_id": source["source_record_id"],
                    "destination_id": None,
                    "match_status": "manual_review",
                    "match_rule": "ambiguous_fuzzy_candidate",
                    "name_similarity": best["name_similarity"],
                    "address_similarity": best["address_similarity"],
                    "distance_meters": np.nan,
                    "candidate_count": len(candidates),
                }
            )
            ambiguous.append(
                {
                    "source_record_id": source["source_record_id"],
                    "source_name": source["name_raw"],
                    "source_kind": source["source_kind"],
                    "candidate_destination_id": best["destination_id"],
                    "candidate_name": best["canonical_name"],
                    "name_similarity": best["name_similarity"],
                    "address_similarity": best["address_similarity"],
                    "score_margin": margin,
                }
            )
        else:
            links.append(
                {
                    "source_record_id": source["source_record_id"],
                    "destination_id": None,
                    "match_status": "unresolved",
                    "match_rule": "no_safe_candidate",
                    "name_similarity": best["name_similarity"] if best else 0.0,
                    "address_similarity": best["address_similarity"] if best else 0.0,
                    "distance_meters": np.nan,
                    "candidate_count": len(candidates),
                }
            )
            unresolved.append(
                {
                    "source_record_id": source["source_record_id"],
                    "source_name": source["name_raw"],
                    "source_kind": source["source_kind"],
                    "best_candidate_name": best["canonical_name"] if best else None,
                    "best_name_similarity": best["name_similarity"] if best else 0.0,
                }
            )
    return pd.DataFrame(links), pd.DataFrame(ambiguous), pd.DataFrame(unresolved)


def _review_name_sources(reviews: pd.DataFrame) -> pd.DataFrame:
    unique = (
        reviews[["source_kind", "place_name_raw", "place_name_normalized"]]
        .sort_values(["source_kind", "place_name_normalized", "place_name_raw"])
        .groupby(["source_kind", "place_name_normalized"], as_index=False)
        .agg(name_raw=("place_name_raw", "first"))
        .rename(columns={"place_name_normalized": "name_normalized"})
    )
    unique["source_record_id"] = unique.apply(
        lambda row: f"review_name_{hashlib.sha256(f'{row.source_kind}|{row.name_normalized}'.encode()).hexdigest()[:16]}",
        axis=1,
    )
    unique["source_file"] = "review_place_names"
    unique["source_row"] = np.nan
    unique["is_anchor"] = False
    unique["address_raw"] = ""
    unique["address_normalized"] = ""
    return unique


def _add_unresolved_canonicals(
    canonical: pd.DataFrame,
    sources: pd.DataFrame,
    links: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    needs_placeholder = links["destination_id"].isna()
    source_lookup = sources.set_index("source_record_id")
    new_records: list[dict[str, Any]] = []
    for index in links.index[needs_placeholder]:
        source = source_lookup.loc[links.at[index, "source_record_id"]]
        kind = str(source["source_kind"])
        destination_id = _canonical_id(f"unresolved_{kind}", source["name_normalized"])
        links.at[index, "destination_id"] = destination_id
        if destination_id not in canonical["destination_id"].values and not any(
            item["destination_id"] == destination_id for item in new_records
        ):
            new_records.append(
                {
                    "destination_id": destination_id,
                    "canonical_name": source["name_raw"],
                    "normalized_name": source["name_normalized"],
                    "kind": kind,
                    "latitude": np.nan,
                    "longitude": np.nan,
                    "address": source.get("address_raw", ""),
                    "category": "",
                    "status": "",
                    "source_record_count": 1,
                    "canonical_status": "unresolved_placeholder",
                }
            )
    if new_records:
        canonical = pd.concat([canonical, pd.DataFrame(new_records)], ignore_index=True)
    return canonical, links


def apply_reviewed_decisions(
    links: pd.DataFrame,
    ambiguous: pd.DataFrame,
    review_path: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Apply versioned human adjudication and report pre/post pair classification metrics."""

    reviewed = pd.read_csv(review_path, dtype=str)
    reviewed["predicted_auto_match"] = reviewed["predicted_auto_match"].map(
        {"true": True, "false": False}
    )
    candidate_lookup = ambiguous.set_index("source_record_id")["candidate_destination_id"].to_dict()
    links = links.copy()
    link_index = links.reset_index().set_index("source_record_id")["index"].to_dict()

    for decision in reviewed.itertuples(index=False):
        index = link_index.get(decision.source_record_id)
        if index is None:
            raise KeyError(f"Reviewed source record not found in links: {decision.source_record_id}")
        if decision.ground_truth == "MATCH" and not decision.predicted_auto_match:
            candidate_id = candidate_lookup.get(decision.source_record_id)
            if candidate_id is None:
                raise KeyError(f"Reviewed MATCH has no candidate: {decision.source_record_id}")
            links.at[index, "destination_id"] = candidate_id
            links.at[index, "match_status"] = "human_verified_match"
            links.at[index, "match_rule"] = "reviewed_alias_override"
        elif decision.ground_truth in {"NO_MATCH", "UNCERTAIN"}:
            links.at[index, "destination_id"] = None
            links.at[index, "match_status"] = (
                "human_verified_no_match"
                if decision.ground_truth == "NO_MATCH"
                else "manual_review"
            )
            links.at[index, "match_rule"] = (
                "reviewed_no_match_override"
                if decision.ground_truth == "NO_MATCH"
                else "reviewed_uncertain"
            )

    certain = reviewed.loc[reviewed["ground_truth"].isin(["MATCH", "NO_MATCH"])].copy()
    actual_match = certain["ground_truth"].eq("MATCH")
    predicted_match = certain["predicted_auto_match"]
    tp = int((actual_match & predicted_match).sum())
    fp = int((~actual_match & predicted_match).sum())
    fn = int((actual_match & ~predicted_match).sum())
    tn = int((~actual_match & ~predicted_match).sum())
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    post_matches = actual_match
    post_tp = int((actual_match & post_matches).sum())
    post_tn = int((~actual_match & ~post_matches).sum())
    metrics = {
        "review_file": str(review_path),
        "reviewed_pairs": len(reviewed),
        "certain_pairs": len(certain),
        "uncertain_pairs": int((reviewed["ground_truth"] == "UNCERTAIN").sum()),
        "pre_adjudication": {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "false_merge_rate_among_predicted_matches": round(fp / (tp + fp), 4)
            if tp + fp
            else 0.0,
        },
        "post_adjudication_on_reviewed_pairs": {
            "tp": post_tp,
            "fp": 0,
            "fn": 0,
            "tn": post_tn,
            "precision": 1.0,
            "recall": 1.0,
            "f1": 1.0,
            "false_merge_rate": 0.0,
            "scope_warning": "Human-corrected reviewed pairs only; not generalization performance.",
        },
    }
    return links, metrics


def run_entity_resolution(
    interim_dir: Path, processed_dir: Path, report_dir: Path
) -> dict[str, Any]:
    processed_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    place_sources = pd.read_parquet(interim_dir / "clean_place_sources.parquet")
    reviews = pd.read_parquet(interim_dir / "clean_reviews.parquet")

    canonical, anchor_links = build_canonical_anchors(place_sources)
    supporting = place_sources.loc[~place_sources["is_anchor"]].copy()
    supporting_links, supporting_ambiguous, supporting_unresolved = resolve_sources(
        supporting, canonical, allow_fuzzy_auto=True
    )
    review_sources = _review_name_sources(reviews)
    review_links, review_ambiguous, review_unresolved = resolve_sources(
        review_sources, canonical, allow_fuzzy_auto=False
    )

    all_links = pd.concat([anchor_links, supporting_links, review_links], ignore_index=True)
    ambiguous = pd.concat([supporting_ambiguous, review_ambiguous], ignore_index=True)
    unresolved = pd.concat([supporting_unresolved, review_unresolved], ignore_index=True)

    review_path = ML_ROOT / "configs" / "entity-review-v1.csv"
    all_links, evaluation_metrics = apply_reviewed_decisions(all_links, ambiguous, review_path)
    anchor_count = len(anchor_links)
    supporting_count = len(supporting_links)
    anchor_links = all_links.iloc[:anchor_count].copy()
    supporting_links = all_links.iloc[anchor_count : anchor_count + supporting_count].copy()
    review_links = all_links.iloc[anchor_count + supporting_count :].copy()

    canonical, supporting_links = _add_unresolved_canonicals(
        canonical, supporting, supporting_links
    )
    canonical, review_links = _add_unresolved_canonicals(canonical, review_sources, review_links)
    all_links = pd.concat([anchor_links, supporting_links, review_links], ignore_index=True)
    orphan_ids = set(canonical["destination_id"]) - set(all_links["destination_id"])
    if orphan_ids:
        raise ValueError(f"Canonical destinations without source links: {len(orphan_ids)}")

    review_name_map = review_links[["source_record_id", "destination_id", "match_status", "match_rule"]]
    review_sources_small = review_sources[["source_record_id", "source_kind", "name_normalized"]]
    review_name_map = review_name_map.merge(review_sources_small, on="source_record_id")
    reviews = reviews.merge(
        review_name_map.drop(columns=["source_record_id"]),
        left_on=["source_kind", "place_name_normalized"],
        right_on=["source_kind", "name_normalized"],
        how="left",
        validate="many_to_one",
    ).drop(columns=["name_normalized"])
    if reviews["destination_id"].isna().any():
        raise ValueError("All clean reviews must receive a destination_id")

    canonical.to_parquet(processed_dir / "canonical_destinations.parquet", index=False)
    all_links.to_parquet(processed_dir / "entity_links.parquet", index=False)
    reviews.to_parquet(processed_dir / "canonical_reviews.parquet", index=False)
    ambiguous.to_csv(report_dir / "entity_ambiguous_candidates.csv", index=False)
    unresolved.to_csv(report_dir / "entity_unresolved_sources.csv", index=False)

    link_counts = all_links["match_status"].value_counts()
    review_counts = reviews["match_status"].value_counts()
    summary = {
        "entity_resolution_version": "0.1.0",
        "canonical_destinations": len(canonical),
        "metadata_anchor_destinations": int(
            (canonical["canonical_status"] == "metadata_anchor").sum()
        ),
        "unresolved_placeholder_destinations": int(
            (canonical["canonical_status"] == "unresolved_placeholder").sum()
        ),
        "source_links": len(all_links),
        "link_status_counts": {str(key): int(value) for key, value in link_counts.items()},
        "review_records": len(reviews),
        "review_link_status_counts": {
            str(key): int(value) for key, value in review_counts.items()
        },
        "ambiguous_candidate_rows": len(ambiguous),
        "unresolved_source_rows": len(unresolved),
        "all_reviews_have_destination_id": bool(reviews["destination_id"].notna().all()),
        "outputs": {
            path.name: sha256_file(path) for path in sorted(processed_dir.glob("*.parquet"))
        },
    }
    (report_dir / "entity_resolution_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (report_dir / "entity_resolution_metrics.json").write_text(
        json.dumps(evaluation_metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary
