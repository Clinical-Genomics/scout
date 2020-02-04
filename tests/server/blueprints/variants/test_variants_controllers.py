import copy
import logging

from scout.server.blueprints.variants.controllers import (
    variants_export_header,
    variant_export_lines,
    variants,
    sv_variants,
)

LOG = logging.getLogger(__name__)


def test_variants_research_no_shadow_clinical_assessments(
    real_variant_database, institute_obj, case_obj
):
    # GIVEN a db with variants,
    adapter = real_variant_database
    case_id = case_obj["_id"]

    # GIVEN a clinical variant from one case
    variant_clinical = adapter.variant_collection.find_one(
        {"case_id": case_id, "variant_type": "clinical"}
    )

    # GIVEN a copy of that variant marked research
    variant_research = copy.deepcopy(variant_clinical)
    variant_research["_id"] = "research_version"
    variant_research["variant_type"] = "research"
    adapter.variant_collection.insert_one(variant_research)

    # WHEN filtering for that variant in research
    variants_query = {"variant_type": "research"}
    variants_query_res = adapter.variants(
        case_obj["_id"], query=variants_query, category=variant_clinical["category"]
    )

    res = variants(adapter, institute_obj, case_obj, variants_query_res)
    res_variants = res["variants"]

    LOG.debug("Variants: {}".format(res_variants))
    # THEN it is returned
    assert any([variant["_id"] == variant_research["_id"] for variant in res_variants])

    # THEN no previous annotations are reported back for the reseach case..
    assert not any([variant.get("clinical_assessments") for variant in res_variants])


def test_variants_research_shadow_clinical_assessments(
    real_variant_database, institute_obj, case_obj
):
    # GIVEN a db with variants,
    adapter = real_variant_database
    case_id = case_obj["_id"]

    # GIVEN a clinical variant from one case
    variant_clinical = adapter.variant_collection.find_one(
        {"case_id": case_id, "variant_type": "clinical"}
    )

    # GIVEN a copy of that variant marked research
    variant_research = copy.deepcopy(variant_clinical)
    variant_research["_id"] = "research_version"
    variant_research["variant_type"] = "research"
    adapter.variant_collection.insert_one(variant_research)

    # WHEN updating the manual assessments of the clinical variant
    adapter.variant_collection.update_one(
        {"_id": variant_clinical["_id"]},
        {
            "$set": {
                "manual_rank": 2,
                "mosaic_tags": ["1"],
                "dismiss_variant": ["2", "3"],
                "acmg_classification": 0,
            }
        },
    )

    # WHEN filtering for that variant in research
    variants_query = {"variant_type": "research"}
    variants_query_res = adapter.variants(
        case_obj["_id"], query=variants_query, category=variant_clinical["category"]
    )

    res = variants(adapter, institute_obj, case_obj, variants_query_res)
    res_variants = res["variants"]

    # THEN it is returned
    assert any([variant["_id"] == variant_research["_id"] for variant in res_variants])

    # THEN previous annotations are reported back for the reseach case.
    assert any([variant.get("clinical_assessments") for variant in res_variants])


def test_sv_variants_research_shadow_clinical_assessments(
    real_variant_database, institute_obj, case_obj
):
    # GIVEN a db with variants,
    adapter = real_variant_database
    case_id = case_obj["_id"]

    # GIVEN a clinical variant from one case
    variant_clinical = adapter.variant_collection.find_one(
        {"case_id": case_id, "variant_type": "clinical"}
    )
    # GIVEN the variant is an SV
    adapter.variant_collection.update_one(
        {"_id": variant_clinical["_id"]},
        {"$set": {"category": "sv", "sub_category": "dup"}},
    )

    # GIVEN a copy of that variant marked research
    variant_research = copy.deepcopy(variant_clinical)
    variant_research["_id"] = "research_version"
    variant_research["variant_type"] = "research"
    variant_research["category"] = "sv"
    variant_research["sub_category"]: "dup"
    adapter.variant_collection.insert_one(variant_research)

    # WHEN updating the manual assessments of the clinical variant
    adapter.variant_collection.update_one(
        {"_id": variant_clinical["_id"]},
        {
            "$set": {
                "manual_rank": 2,
                "mosaic_tags": ["1"],
                "dismiss_variant": ["2", "3"],
            }
        },
    )

    # WHEN filtering for that variant in research
    variants_query = {"variant_type": "research"}
    variants_query_res = adapter.variants(
        case_obj["_id"], query=variants_query, category="sv"
    )
    assert variants_query_res

    res = sv_variants(adapter, institute_obj, case_obj, variants_query_res)
    res_variants = res["variants"]

    LOG.debug("Variants: {}".format(res_variants))

    # THEN it is returned
    assert any([variant["_id"] == variant_research["_id"] for variant in res_variants])

    # THEN previous annotations are reported back for the reseach case.
    assert any([variant.get("clinical_assessments") for variant in res_variants])


def test_variant_csv_export(real_variant_database, case_obj):
    adapter = real_variant_database
    case_id = case_obj["_id"]

    # Given a database with variants from a case
    snv_variants = adapter.variant_collection.find(
        {"case_id": case_id, "category": "snv"}
    )

    # Given 5 variants to be exported
    variants_to_export = []
    for variant in snv_variants.limit(5):
        assert type(variant) is dict
        variants_to_export.append(variant)
    n_vars = len(variants_to_export)
    assert n_vars == 5

    # Collect export header from variants controller
    export_header = variants_export_header(case_obj)

    # Assert that exported document has n fields:
    # n = (EXPORT_HEADER items in variants_export.py) + (3 * number of individuals analysed for the case)
    assert len(export_header) == 8 + 3 * len(case_obj["individuals"])

    # Given the lines of the document to be exported
    export_lines = variant_export_lines(adapter, case_obj, variants_to_export)

    # Assert that all five variants are going to be exported to CSV
    assert len(export_lines) == 5

    # Assert that all of 5 variants contain the fields specified by the document header
    for export_line in export_lines:
        export_cols = export_line.split(",")
        assert len(export_cols) == len(export_header)
