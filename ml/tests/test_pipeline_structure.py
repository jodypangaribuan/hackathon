from sipature_ml.paths import PATHS
from sipature_ml.stages import PIPELINE_ORDER, Stage


def test_pipeline_stage_order_is_complete() -> None:
    assert PIPELINE_ORDER[0] is Stage.INVENTORY
    assert PIPELINE_ORDER[-1] is Stage.EXPORT_APP
    assert len(PIPELINE_ORDER) == len(Stage)


def test_required_project_directories_exist() -> None:
    required = (
        PATHS.root / "configs",
        PATHS.root / "contracts",
        PATHS.root / "notebooks",
        PATHS.root / "src" / "sipature_ml",
        PATHS.root / "tests",
    )
    assert all(path.is_dir() for path in required)
