import json

from sipature_ml.inventory import inventory_dataset, write_inventory


def test_inventory_profiles_csv_and_hashes_source(tmp_path) -> None:
    dataset = tmp_path / "dataset"
    dataset.mkdir()
    source = dataset / "reviews.csv"
    source.write_text("place,rating\nA,5\nB,4\n", encoding="utf-8-sig")

    result = inventory_dataset(dataset)
    assert result["file_count"] == 1
    assert result["files"][0]["row_count_excluding_header"] == 2
    assert result["files"][0]["columns"] == ["place", "rating"]
    assert len(result["files"][0]["sha256"]) == 64


def test_write_inventory_creates_json_and_csv(tmp_path) -> None:
    result = {"dataset_dir": "/tmp/data", "file_count": 0, "files": []}
    json_path, csv_path = write_inventory(result, tmp_path / "reports")
    assert json.loads(json_path.read_text())["file_count"] == 0
    assert csv_path.read_text().startswith("filename,suffix,size_bytes")
