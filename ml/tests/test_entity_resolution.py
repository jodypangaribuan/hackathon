import pandas as pd

from sipature_ml.entity_resolution import (
    _review_name_sources,
    apply_reviewed_decisions,
    build_canonical_anchors,
    haversine_meters,
)


def test_haversine_is_zero_for_same_point() -> None:
    assert haversine_meters(2.35, 99.07, 2.35, 99.07) == 0


def test_anchor_merge_requires_same_name_kind_and_nearby_coordinates() -> None:
    frame = pd.DataFrame(
        [
            {
                "source_record_id": "a",
                "source_file": "x",
                "source_row": 2,
                "source_kind": "wisata",
                "is_anchor": True,
                "name_raw": "Bukit Toba",
                "name_normalized": "bukit toba",
                "category_raw": "Wisata",
                "address_raw": "A",
                "latitude": 2.35,
                "longitude": 99.07,
                "status_raw": "beroperasi",
            },
            {
                "source_record_id": "b",
                "source_file": "y",
                "source_row": 3,
                "source_kind": "wisata",
                "is_anchor": True,
                "name_raw": "BUKIT TOBA",
                "name_normalized": "bukit toba",
                "category_raw": "Wisata",
                "address_raw": "B",
                "latitude": 2.3501,
                "longitude": 99.0701,
                "status_raw": "beroperasi",
            },
        ]
    )
    canonical, links = build_canonical_anchors(frame)
    assert len(canonical) == 1
    assert len(links) == 2


def test_review_name_sources_collapse_normalization_collisions() -> None:
    reviews = pd.DataFrame(
        [
            {"source_kind": "wisata", "place_name_raw": "Family-Resto", "place_name_normalized": "family resto"},
            {"source_kind": "wisata", "place_name_raw": "Family Resto", "place_name_normalized": "family resto"},
        ]
    )
    result = _review_name_sources(reviews)
    assert len(result) == 1
    assert result.iloc[0]["name_normalized"] == "family resto"


def test_reviewed_decisions_correct_false_match_and_alias(tmp_path) -> None:
    links = pd.DataFrame(
        [
            {"source_record_id": "false_auto", "destination_id": "d1", "match_status": "auto_match", "match_rule": "fuzzy"},
            {"source_record_id": "missed_alias", "destination_id": None, "match_status": "manual_review", "match_rule": "candidate"},
        ]
    )
    ambiguous = pd.DataFrame(
        [{"source_record_id": "missed_alias", "candidate_destination_id": "d2"}]
    )
    review = tmp_path / "review.csv"
    review.write_text(
        "source_record_id,ground_truth,predicted_auto_match,review_batch\n"
        "false_auto,NO_MATCH,true,test\n"
        "missed_alias,MATCH,false,test\n",
        encoding="utf-8",
    )
    corrected, metrics = apply_reviewed_decisions(links, ambiguous, review)
    assert corrected.loc[0, "destination_id"] is None
    assert corrected.loc[1, "destination_id"] == "d2"
    assert metrics["pre_adjudication"]["fp"] == 1
    assert metrics["pre_adjudication"]["fn"] == 1
