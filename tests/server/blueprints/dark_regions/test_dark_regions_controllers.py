import datetime

from scout.server.blueprints.dark_regions.controllers import sma_case
from scout.server.blueprints.dark_regions.helpers import SMN_HGNC_IDS, _get_paraphrase_regions


def test_get_paraphrase(real_populated_database, app):

    case_obj = real_populated_database.case_collection.find_one({"_id": "internal_id"})

    assert "paraphrase" in case_obj
    assert case_obj["paraphrase"]

    assert "paraphrase" in case_obj["individuals"][0]
    assert case_obj["individuals"][0]["paraphrase"]

    regions = _get_paraphrase_regions(case_obj=case_obj)

    assert "rccx" in regions
    assert "6" in regions["rccx"]["phase_region"]["chrom"]


def test_sma_case_panel_filtered_paraphrase_regions(real_populated_database, app):
    """Only dark regions with genes on selected panel should be shown."""

    case_obj = real_populated_database.case_collection.find_one({"_id": "internal_id"})
    institute_obj = real_populated_database.institute(case_obj["owner"])
    all_regions = _get_paraphrase_regions(case_obj=case_obj)

    region_with_genes = next(
        (
            region
            for region in all_regions.values()
            if region.get("genes_in_region") and len(region["genes_in_region"]) > 0
        ),
        None,
    )
    assert region_with_genes is not None

    target_gene = region_with_genes["genes_in_region"][0]
    panel_name = "sma-dark-test-panel"
    real_populated_database.panel_collection.insert_one(
        {
            "panel_name": panel_name,
            "display_name": "SMA Dark Test Panel",
            "version": 1.0,
            "institute": case_obj["owner"],
            "date": datetime.datetime.now(),
            "genes": [{"hgnc_id": target_gene["hgnc_id"], "symbol": target_gene["hgnc_symbol"]}],
        }
    )
    case_obj["panels"] = [
        {
            "panel_name": panel_name,
            "display_name": "SMA Dark Test Panel",
            "version": 1.0,
            "is_default": True,
        }
    ]

    with app.app_context():
        data = sma_case(
            store=real_populated_database,
            institute_obj=institute_obj,
            case_obj=case_obj,
            selected_gene_panels=[panel_name],
        )

    assert data["selected_gene_panels"] == [panel_name]
    assert data["paraphrase_regions"]
    for region in data["paraphrase_regions"].values():
        for gene in region.get("genes_in_region", []):
            assert gene["hgnc_id"] == target_gene["hgnc_id"]
    assert "show_smn_section" in data


def test_sma_case_smn_visibility_by_selected_panel_genes(real_populated_database, app):
    """SMN section visibility should follow selected panel HGNC IDs."""

    case_obj = real_populated_database.case_collection.find_one({"_id": "internal_id"})
    institute_obj = real_populated_database.institute(case_obj["owner"])

    non_smn_panel_name = "sma-dark-non-smn-panel"
    real_populated_database.panel_collection.insert_one(
        {
            "panel_name": non_smn_panel_name,
            "display_name": "SMA Dark Non-SMN Panel",
            "version": 1.0,
            "institute": case_obj["owner"],
            "date": datetime.datetime.now(),
            "genes": [{"hgnc_id": 123456, "symbol": "NONSMN"}],
        }
    )
    case_obj["panels"] = [
        {
            "panel_name": non_smn_panel_name,
            "display_name": "SMA Dark Non-SMN Panel",
            "version": 1.0,
            "is_default": True,
        }
    ]

    with app.app_context():
        filtered_data = sma_case(
            store=real_populated_database,
            institute_obj=institute_obj,
            case_obj=case_obj,
            selected_gene_panels=[non_smn_panel_name],
        )
        unfiltered_data = sma_case(
            store=real_populated_database,
            institute_obj=institute_obj,
            case_obj=case_obj,
            selected_gene_panels=[],
        )

    assert filtered_data["show_smn_section"] is False
    assert unfiltered_data["show_smn_section"] is True


def test_sma_case_hpo_panel_uses_dynamic_gene_list(real_populated_database, app):
    """Selecting the virtual HPO panel should filter by case dynamic HPO genes."""

    case_obj = real_populated_database.case_collection.find_one({"_id": "internal_id"})
    institute_obj = real_populated_database.institute(case_obj["owner"])
    all_regions = _get_paraphrase_regions(case_obj=case_obj)

    region_with_genes = next(
        (
            region
            for region in all_regions.values()
            if region.get("genes_in_region") and len(region["genes_in_region"]) > 0
        ),
        None,
    )
    assert region_with_genes is not None

    target_hgnc_id = region_with_genes["genes_in_region"][0]["hgnc_id"]
    case_obj["dynamic_gene_list"] = [{"hgnc_id": target_hgnc_id}]

    with app.app_context():
        data = sma_case(
            store=real_populated_database,
            institute_obj=institute_obj,
            case_obj=case_obj,
            selected_gene_panels=["hpo"],
        )

    assert data["selected_gene_panels"] == ["hpo"]
    assert data["paraphrase_regions"]
    for region in data["paraphrase_regions"].values():
        for gene in region.get("genes_in_region", []):
            assert gene["hgnc_id"] == target_hgnc_id
    assert data["show_smn_section"] == (target_hgnc_id in SMN_HGNC_IDS)
