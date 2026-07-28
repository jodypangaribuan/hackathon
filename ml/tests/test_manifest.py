import hashlib

from sipature_ml.manifest import build_manifest, sha256_file, write_manifest


def test_sha256_file(tmp_path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("sipature\n", encoding="utf-8")
    expected = hashlib.sha256(b"sipature\n").hexdigest()
    assert sha256_file(source) == expected


def test_manifest_round_trip(tmp_path) -> None:
    source = tmp_path / "source.csv"
    source.write_text("id,value\n1,test\n", encoding="utf-8")
    manifest = build_manifest(
        artifact_version="test-v1",
        pipeline_version="0.1.0",
        config={"seed": 42},
        source_files=[source],
    )
    output = tmp_path / "manifest.json"
    write_manifest(output, manifest)
    assert output.is_file()
    assert manifest["sources"][0]["sha256"] == sha256_file(source)
