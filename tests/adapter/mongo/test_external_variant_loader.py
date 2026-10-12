from pathlib import Path

from flask import Flask

from scout.adapter.mongo.external_variant_loader import ExternalVariantLoader


def test_run_scout_loader(monkeypatch, tmp_path):
    """Test that the external scout_loader runs with the correct arguments and MongoDB configuration."""
    app = Flask(__name__)
    app.config.update(
        VARIANTS_LOADER="/opt/scout_loader/scout_loader",
        MONGO_URI="mongodb://localhost:27017",
        MONGO_DBNAME="scout_test",
    )
    case_config = tmp_path / "case.yaml"
    case_config.write_text("family: test\n", encoding="utf-8")
    captured = {}

    def mock_run(command, check):
        captured["command"] = command
        captured["check"] = check
        captured["config_path"] = Path(command[-1])
        captured["config"] = captured["config_path"].read_text(encoding="utf-8")

    monkeypatch.setattr(
        "scout.adapter.mongo.external_variant_loader.subprocess.run",
        mock_run,
    )

    with app.app_context(), case_config.open(encoding="utf-8") as config:
        ExternalVariantLoader().run_scout_loader(config)

    assert captured["command"] == [
        "/opt/scout_loader/scout_loader",
        "--case-config",
        str(case_config),
        "--config",
        str(captured["config_path"]),
    ]
    assert captured["check"] is True
    assert captured["config"] == (
        'mongo_uri = "mongodb://localhost:27017"\n'
        'mongo_dbname = "scout_test"\n'
    )
    assert not captured["config_path"].exists()
