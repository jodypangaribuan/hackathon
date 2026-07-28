from sipature_ml.split import (
    assign_components,
    build_leakage_components,
    validate_split_records,
)


def _record(review: str, destination: str, duplicate: str, aspect: str) -> dict:
    return {
        "review_id": review,
        "destination_id": destination,
        "duplicate_group_id": duplicate,
        "repeated_text_group_id": f"text-{review}",
        "labels": [{"aspect": aspect}],
    }


def test_components_connect_destinations_through_duplicate_group() -> None:
    records = [
        _record("r1", "d1", "dup-shared", "access"),
        _record("r2", "d2", "dup-shared", "access"),
        _record("r3", "d3", "dup-other", "safety"),
    ]
    components = build_leakage_components(records)
    assert sorted(len(component["destinations"]) for component in components) == [1, 2]


def test_components_connect_destinations_through_repeated_text() -> None:
    records = [
        _record("r1", "d1", "dup1", "access"),
        _record("r2", "d2", "dup2", "safety"),
    ]
    records[0]["repeated_text_group_id"] = "same-text"
    records[1]["repeated_text_group_id"] = "same-text"
    assert len(build_leakage_components(records)) == 1


def test_assignment_is_deterministic_and_leakage_free() -> None:
    records = [
        _record(f"r{i}", f"d{i}", f"dup{i}", "access" if i % 2 else "safety")
        for i in range(20)
    ]
    components = build_leakage_components(records)
    algorithm = {
        "candidates": 20,
        "missing_label_penalty": 25.0,
        "record_balance_weight": 2.0,
        "label_balance_weight": 4.0,
    }
    first = assign_components(
        components, {"train": 0.7, "validation": 0.15, "test": 0.15},
        ["access", "safety"], 42, algorithm
    )
    second = assign_components(
        components, {"train": 0.7, "validation": 0.15, "test": 0.15},
        ["access", "safety"], 42, algorithm
    )
    assert first == second
    split_records = {name: [] for name in ("train", "validation", "test")}
    for component in components:
        split_records[first[component["component_id"]]].extend(component["records"])
    assert validate_split_records(split_records)["valid"]


def test_validation_rejects_destination_leakage() -> None:
    records = {
        "train": [_record("r1", "d1", "dup1", "access")],
        "validation": [_record("r2", "d1", "dup2", "safety")],
        "test": [_record("r3", "d3", "dup3", "access")],
    }
    try:
        validate_split_records(records)
    except ValueError as error:
        assert "Leakage detected" in str(error)
    else:
        raise AssertionError("Destination leakage must fail validation")
