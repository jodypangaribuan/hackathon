from sipature_ml.environment import build_environment_snapshot


def test_environment_snapshot_contains_reproducibility_fields() -> None:
    snapshot = build_environment_snapshot()
    assert snapshot["python"]
    assert snapshot["platform"]
    assert "pipeline.yaml" in snapshot["configs"]
    assert "numpy" in snapshot["packages"]
