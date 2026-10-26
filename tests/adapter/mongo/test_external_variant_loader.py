from pathlib import Path

import yaml
from flask import Flask

from scout.adapter.mongo.external_variant_loader import ExternalVariantLoader


def test_temp_case_config_from_case_dict_research():
    """Test that research configuration includes only available research VCF fields."""
    case_obj = {
        "case_id": "test",
        "owner": "cust000",
        "genome_build": "38",
        "rank_score_threshold": "5",
        "vcf_files": {
            "vcf_snv_research": "/data/snv.vcf.gz",
            "vcf_sv_research": "/data/sv.vcf.gz",
            "vcf_snv": "/data/clinical.vcf.gz",
        },
    }

    with ExternalVariantLoader().temp_case_config_from_case_dict(
        case_obj, is_research=True
    ) as yaml_file:
        config = yaml.safe_load(Path(yaml_file.name).read_text(encoding="utf-8"))

    assert config["family"] == "test"
    assert config["vcf_snv_research"] == "/data/snv.vcf.gz"
    assert config["vcf_sv_research"] == "/data/sv.vcf.gz"
    assert "vcf_snv" not in config
    assert "gene_panels" not in config


def test_temp_case_config_from_case_dict_clinical():
    """Test that clinical configuration includes gene panels and excludes research VCF fields."""
    case_obj = {
        "_id": "test",
        "owner": "cust000",
        "genome_build": "38",
        "rank_score_threshold": "5",
        "gene_panels": [{"panel_name": "OMIM-AUTO"}],
        "vcf_files": {
            "vcf_snv_research": "/data/snv.vcf.gz",
        },
    }

    with ExternalVariantLoader().temp_case_config_from_case_dict(
        case_obj, is_research=False
    ) as yaml_file:
        config = yaml.safe_load(Path(yaml_file.name).read_text(encoding="utf-8"))

    assert config["family"] == "test"
    assert config["gene_panels"] == [{"panel_name": "OMIM-AUTO"}]
    assert "vcf_snv_research" not in config


def test_run_external_scout_loader(monkeypatch):
    """Test that the external loader runs with the correct arguments and MongoDB configuration."""
    app = Flask(__name__)
    app.config.update(
        VARIANTS_LOADER="/opt/scout_loader/scout_loader",
        MONGO_URI="mongodb://localhost:27017",
        MONGO_DBNAME="scout_test",
    )
    case_obj = {
        "_id": "test",
        "owner": "cust000",
        "genome_build": "38",
        "rank_score_threshold": "5",
        "individuals": [{"individual_id": "sample1"}],
        "gene_panels": [{"panel_name": "OMIM-AUTO"}],
    }
    captured = {}

    def mock_run(command, check):
        captured["command"] = command
        captured["check"] = check
        captured["case_config_path"] = Path(command[2])
        captured["mongo_config_path"] = Path(command[4])
        captured["case_config"] = yaml.safe_load(
            captured["case_config_path"].read_text(encoding="utf-8")
        )
        captured["mongo_config"] = captured["mongo_config_path"].read_text(encoding="utf-8")

    monkeypatch.setattr(
        "scout.adapter.mongo.external_variant_loader.subprocess.run",
        mock_run,
    )

    with app.app_context():
        ExternalVariantLoader().run_external_scout_loader(case_obj)

    assert captured["command"][:2] == [
        "/opt/scout_loader/scout_loader",
        "--case-config",
    ]
    assert captured["command"][3] == "--config"
    assert captured["check"] is True
    assert captured["case_config"]["family"] == "test"
    assert captured["case_config"]["samples"] == [{"sample_id": "sample1"}]
    assert captured["case_config"]["gene_panels"] == [{"panel_name": "OMIM-AUTO"}]
    assert captured["mongo_config"] == (
        'mongo_uri = "mongodb://localhost:27017"\n' 'mongo_dbname = "scout_test"\n'
    )
    assert not captured["case_config_path"].exists()
    assert not captured["mongo_config_path"].exists()
