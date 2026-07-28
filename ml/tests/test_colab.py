from sipature_ml.colab import DRIVE_DIRECTORIES, bootstrap_drive


def test_bootstrap_drive_creates_persistent_layout(tmp_path) -> None:
    paths = bootstrap_drive(tmp_path / "SIPATURE")
    assert len(paths) == len(DRIVE_DIRECTORIES)
    assert all(path.is_dir() for path in paths)
