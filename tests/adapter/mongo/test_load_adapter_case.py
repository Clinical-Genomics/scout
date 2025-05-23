from pprint import pprint as pp

import pytest

from scout.exceptions import IntegrityError


def test_load_case(real_panel_database, parsed_case):
    adapter = real_panel_database
    ## GIVEN an empty database
    existing_case = adapter.case_collection.find_one()
    assert existing_case is None

    ## WHEN loading a case
    adapter.load_case(parsed_case)

    ## THEN assert that the case was loaded
    existing_case = adapter.case_collection.find_one()

    assert existing_case["_id"] == parsed_case["family"]


def test_load_case_no_institute(adapter, case_obj):
    ## GIVEN an empty database
    existing_case = adapter.case_collection.find_one()
    assert existing_case is None

    ## WHEN loading a case

    ## THEN assert that loading fails since there where no institute
    with pytest.raises(IntegrityError):
        adapter.load_case(case_obj)


def test_load_case_empty_vcf(real_panel_database, parsed_case, empty_sv_clinical_file):
    adapter = real_panel_database
    ## GIVEN an empty database
    existing_case = adapter.case_collection.find_one()
    assert existing_case is None

    parsed_case["vcf_files"]["vcf_sv"] = empty_sv_clinical_file

    ## WHEN loading a case with a empty sv vcf
    adapter.load_case(parsed_case)

    ## THEN assert that the case was loaded
    existing_case = adapter.case_collection.find_one()

    ## THEN assert that the empty VCF was used
    assert existing_case["vcf_files"]["vcf_sv"] == empty_sv_clinical_file


def test_get_load_order(adapter, cancer_case_obj):
    ### GIVEN a database adapter and a parsed case

    ### WHEN determining variant load order
    load_type_cat = adapter.get_load_type_categories(cancer_case_obj)

    ### THEN cancer SNVs are taken before cancer SVs
    assert load_type_cat == [("clinical", "cancer"), ("clinical", "cancer_sv")]
