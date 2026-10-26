from pathlib import Path

import yaml

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
