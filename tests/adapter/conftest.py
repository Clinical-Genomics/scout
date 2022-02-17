from copy import deepcopy

import pytest


@pytest.fixture
def real_oldcase_database(real_panel_database, parsed_case):
    # add case with old case id construct
    config_data = deepcopy(parsed_case)
    config_data["case_id"] = "-".join([config_data["owner"], config_data["display_name"]])
    case_obj = real_panel_database.load_case(config_data)
    # add suspect and causative!
    institute_obj = real_panel_database.institute(case_obj["owner"])
    user_obj = real_panel_database.users()[0]
    variant_obj = real_panel_database.variant_collection.find_one()

    real_panel_database.pin_variant(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="",
        variant=variant_obj,
    )
    real_panel_database.mark_causative(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="",
        variant=variant_obj,
    )
    # add ACMG evaluation
    real_panel_database.submit_evaluation(
        variant_obj=variant_obj,
        user_obj=user_obj,
        institute_obj=institute_obj,
        case_obj=case_obj,
        link="",
        criteria=[{"term": "PS1"}, {"term": "PM1"}],
    )
    # add comment on a variant
    real_panel_database.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="",
        variant=variant_obj,
        comment_level="specific",
    )
    yield {
        "adapter": real_panel_database,
        "variant": variant_obj,
        "case": real_panel_database.case(case_obj["_id"]),
    }


@pytest.fixture
def parsed_gene():
    gene_info = {
        "hgnc_id": 1,
        "hgnc_symbol": "AAA",
        "ensembl_id": "ENSG1",
        "chrom": "1",
        "start": 10,
        "end": 100,
        "build": "37",
    }
    return gene_info


@pytest.fixture
def omim_term():
    """Returns a test OMIM term as it is saved in the database"""
    disease_term = dict(
        _id="OMIM:1",
        disease_id="OMIM:1",
        disease_nr=1,
        source="OMIM",
        description="First disease",
        genes=[1],  # List with integers that are hgnc_ids
    )
    return disease_term
