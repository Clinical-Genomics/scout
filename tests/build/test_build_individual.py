# -*- coding: utf-8 -*-
from scout.build import build_individual
from scout.exceptions import PedigreeError
import pytest


def test_build_individual():
    ## GIVEN information about a individual
    ind_info = {
        "individual_id": "1",
        "father": "2",
        "mother": "3",
        "display_name": "1-1",
        "sex": "male",
        "phenotype": "affected",
        "bam_file": "scout/demo/reduced_mt.bam",
        "capture_kits": ["Agilent"],
    }

    ## WHEN parsing the information
    ind_obj = build_individual(ind_info)

    ## THEN assert that information was parsed in the correct way
    assert ind_obj["individual_id"] == ind_info["individual_id"]
    assert ind_obj["display_name"] == ind_info["display_name"]
    assert ind_obj["capture_kits"] == ind_info["capture_kits"]
    assert ind_obj["mother"] == ind_info["mother"]
    assert ind_obj["sex"] == "1"
    assert ind_obj["phenotype"] == 2
    assert ind_obj["bam_file"].endswith(ind_info["bam_file"])
    assert ind_obj["analysis_type"] == "unknown"


def test_build_individual_no_individual_id():
    ## GIVEN information about a individual without individual_id
    ind_info = {
        "father": "2",
        "mother": "3",
        "display_name": "1-1",
        "sex": "male",
        "phenotype": "affected",
        "bam_file": "a.bam",
        "capture_kits": ["Agilent"],
    }
    ## WHEN parsing the information
    ## THEN assert exception is raised since individual_id is required
    with pytest.raises(PedigreeError):
        ind_obj = build_individual(ind_info)


def test_build_individual_no_display_name():
    ## GIVEN information about a individual without display_name
    ind_info = {
        "individual_id": "1",
        "father": "2",
        "mother": "3",
        "sex": "male",
        "phenotype": "affected",
        "bam_file": "a.bam",
        "capture_kits": ["Agilent"],
    }
    ## WHEN parsing the information
    ind_obj = build_individual(ind_info)
    ## THEN assert that individual_id was used as display name
    assert ind_obj["display_name"] == ind_info["individual_id"]


def test_build_individual_no_sex():
    ## GIVEN information about a individual without sex
    ind_info = {
        "individual_id": "1",
        "father": "2",
        "mother": "3",
        "phenotype": "affected",
        "bam_file": "a.bam",
        "capture_kits": ["Agilent"],
    }
    ## WHEN parsing the information
    ind_obj = build_individual(ind_info)
    ## THEN assert that sex was set to other
    assert ind_obj["sex"] == "0"


def test_build_individual_wrong_sex():
    ## GIVEN information about a individual with malformed sex information
    ind_info = {
        "individual_id": "1",
        "father": "2",
        "mother": "3",
        "sex": "random",
        "phenotype": "affected",
        "bam_file": "a.bam",
        "capture_kits": ["Agilent"],
    }
    ## WHEN parsing the information
    ## THEN assert exception is raised since we can not determin sex
    with pytest.raises(PedigreeError):
        ind_obj = build_individual(ind_info)


def test_build_individual_no_phenotype():
    ## GIVEN information about a individual without phenotype
    ind_info = {
        "individual_id": "1",
        "father": "2",
        "mother": "3",
        "sex": "male",
        "bam_file": "a.bam",
        "capture_kits": ["Agilent"],
    }
    ## WHEN parsing the information
    ind_obj = build_individual(ind_info)
    ## THEN assert phenitype was set to unknown (0)
    assert ind_obj["phenotype"] == 0


def test_build_individual_wrong_phenotype():
    ## GIVEN information about a individual with malformed phenotype information
    ind_info = {
        "individual_id": "1",
        "father": "2",
        "mother": "3",
        "sex": "male",
        "phenotype": "scrabble",
        "bam_file": "a.bam",
        "capture_kits": ["Agilent"],
    }
    ## WHEN parsing the information
    ## THEN assert exception is raised since we can not determin phenotype
    with pytest.raises(PedigreeError):
        ind_obj = build_individual(ind_info)


def test_build_individual_no_analysis_type():
    ## GIVEN information about a individual without analysis type
    ind_info = {"individual_id": "1"}
    ## WHEN parsing the information
    ind_obj = build_individual(ind_info)
    ## THEN assert analysis type was set to unknown
    assert ind_obj["analysis_type"] == "unknown"


def test_build_individual_wrong_analysis_type():
    ## GIVEN information about a individual with malformed analysis type
    ind_info = {"individual_id": "1", "analysis_type": "hello"}
    ## WHEN parsing the information
    ## THEN assert exception is raised since we can not determin analysis type
    with pytest.raises(PedigreeError):
        ind_obj = build_individual(ind_info)


def test_build_individuals(parsed_case):
    ## GIVEN a case with multiple individuals
    for ind_info in parsed_case["individuals"]:
        ## WHEN building the ind_objs
        ind_obj = build_individual(ind_info)
        ## THEN assert they succeded
        assert ind_obj["individual_id"] == ind_info["individual_id"]
        assert ind_obj["display_name"] == ind_info["display_name"]
        assert ind_obj["capture_kits"] == ind_info["capture_kits"]


# Cancer stuff


def test_build_individual_tmb():
    ## GIVEN information about a individual
    ind_info = {
        "individual_id": "1",
        "father": "2",
        "mother": "3",
        "display_name": "1-1",
        "sex": "male",
        "phenotype": "affected",
        "bam_file": "a.bam",
        "capture_kits": ["Agilent"],
        "tmb": "0.1",
    }

    ## WHEN parsing the information
    ind_obj = build_individual(ind_info)

    ## THEN assert that information was parsed in the correct way
    assert ind_obj["tmb"] == ind_info["tmb"]


def test_build_individual_msi():
    ## GIVEN information about a individual
    ind_info = {
        "individual_id": "1",
        "father": "2",
        "mother": "3",
        "display_name": "1-1",
        "sex": "male",
        "phenotype": "affected",
        "bam_file": "a.bam",
        "capture_kits": ["Agilent"],
        "tmb": "0.1",
        "msi": "13",
    }

    ## WHEN parsing the information
    ind_obj = build_individual(ind_info)

    ## THEN assert that information was parsed in the correct way
    assert ind_obj["msi"] == ind_info["msi"]


def test_build_individual_tumor_purity():
    ## GIVEN information about a individual
    ind_info = {
        "individual_id": "1",
        "father": "2",
        "mother": "3",
        "display_name": "1-1",
        "sex": "male",
        "phenotype": "affected",
        "bam_file": "a.bam",
        "capture_kits": ["Agilent"],
        "tmb": "0.1",
        "msi": "13",
        "tumor_purity": "0.013",
    }

    ## WHEN parsing the information
    ind_obj = build_individual(ind_info)

    ## THEN assert that information was parsed in the correct way
    assert ind_obj["tumor_purity"] == ind_info["tumor_purity"]


def test_build_individual_tumor_type():
    ## GIVEN information about a individual
    ind_info = {
        "individual_id": "1",
        "father": "2",
        "mother": "3",
        "display_name": "1-1",
        "sex": "male",
        "phenotype": "affected",
        "bam_file": "a.bam",
        "capture_kits": ["Agilent"],
        "tmb": "0.1",
        "msi": "13",
        "tumor_type": "melanoma",
    }

    ## WHEN parsing the information
    ind_obj = build_individual(ind_info)

    ## THEN assert that information was parsed in the correct way
    assert ind_obj["tumor_type"] == ind_info["tumor_type"]
    assert ind_obj["tissue_type"] == "unknown"


def test_build_individual_tissue_type():
    ## GIVEN information about a individual
    ind_info = {
        "individual_id": "1",
        "father": "2",
        "mother": "3",
        "display_name": "1-1",
        "sex": "male",
        "phenotype": "affected",
        "bam_file": "a.bam",
        "capture_kits": ["Agilent"],
        "tmb": "0.1",
        "msi": "13",
        "tissue_type": "blood",
    }

    ## WHEN parsing the information
    ind_obj = build_individual(ind_info)

    ## THEN assert that information was parsed in the correct way
    assert ind_obj["tissue_type"] == ind_info["tissue_type"]
