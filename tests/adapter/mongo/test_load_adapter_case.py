from pprint import pprint as pp

import pytest

from scout.exceptions import IntegrityError


def test_load_case(real_panel_database, scout_config):
    adapter = real_panel_database
    ## GIVEN an empty database
    existing_case = adapter.case_collection.find_one()
    assert existing_case is None

    ## WHEN loading a case
    adapter.load_case(scout_config)

    ## THEN assert that the case was loaded
    existing_case = adapter.case_collection.find_one()

    assert existing_case["_id"] == scout_config["family"]


def test_load_case_no_institute(adapter, case_obj):
    ## GIVEN an empty database
    existing_case = adapter.case_collection.find_one()
    assert existing_case is None

    ## WHEN loading a case

    ## THEN assert that loading fails since there where no institute
    with pytest.raises(IntegrityError):
        adapter.load_case(case_obj)


def test_load_case_empty_vcf(real_panel_database, scout_config, empty_sv_clinical_file):
    adapter = real_panel_database
    ## GIVEN an empty database
    existing_case = adapter.case_collection.find_one()
    assert existing_case is None

    scout_config["vcf_sv"] = empty_sv_clinical_file

    ## WHEN loading a case with a empty sv vcf
    adapter.load_case(scout_config)

    ## THEN assert that the case was loaded
    existing_case = adapter.case_collection.find_one()

    ## THEN assert that the empty VCF was used
    assert existing_case["vcf_files"]["vcf_sv"] == empty_sv_clinical_file
