from sipature_ml.config import load_config


def test_pipeline_config_loads() -> None:
    config = load_config("pipeline")
    assert config["project"] == "sipature"
    assert config["evaluation"]["group_key"] == "destination_id"


def test_taxonomy_is_multilabel() -> None:
    config = load_config("taxonomy")
    assert config["constraints"]["multilabel"] is True
    assert "sanitation" in config["aspects"]["environmental"]
