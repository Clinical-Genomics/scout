from datetime import datetime
from pprint import pprint as pp

import pytest

from scout.constants import REV_SEX_MAP
from scout.exceptions import ConfigError, PedigreeError
from scout.parse.case import (
    parse_case,
    parse_case_data,
    parse_custom_images,
    parse_individual,
    parse_individuals,
    parse_ped,
    removeNoneValues,
)


def test_parse_case_no_date(scout_config):
    # GIVEN a load config without a date
    scout_config.pop("analysis_date")
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the todays date should have been set
    assert "analysis_date" not in scout_config
    assert isinstance(case_data["analysis_date"], datetime)


def test_parse_case_wrong_date_string(scout_config):
    # GIVEN you load info thats not a date
    scout_config["analysis_date"] = "not a date"
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the todays date should have been set
    assert isinstance(scout_config["analysis_date"], str)
    assert isinstance(case_data["analysis_date"], datetime)


def test_parse_case_date_string(scout_config):
    # GIVEN a load config with date string
    # WHEN case is parsed
    scout_config["analysis_date"] = "2019-11-05"
    case_data = parse_case(scout_config)
    # THEN the case should have a datetime object
    assert isinstance(scout_config["analysis_date"], str)
    assert isinstance(case_data["analysis_date"], datetime)


def test_parse_case_date(scout_config):
    # GIVEN you load sample information from a scout config
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the case should have an analysis_date
    assert isinstance(scout_config["analysis_date"], datetime)
    assert isinstance(case_data["analysis_date"], datetime)


@pytest.mark.parametrize(
    "param_name",
    [
        "analysis_date",
        "cohorts",
        "delivery_report",
        "gene_panels",
        "gene_fusion_report",
        "lims_id",
        "owner",
        "peddy_check",
        "peddy_ped",
        "peddy_sex",
        "phenotype_terms",
        "rank_model_version",
        "rank_score_threshold",
        "smn_tsv",
        "sv_rank_model_version",
    ],
)
def test_parse_case_parsing(scout_config, param_name):
    # GIVEN you load sample information from a scout config
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the case should have a the parameter
    assert case_data[param_name] == scout_config[param_name]


@pytest.mark.parametrize(
    ("param_name", "alias_name"),
    ([("case_id", "family"), ("default_panels", "default_gene_panels")]),
)
def test_parse_case_aliases(scout_config, param_name, alias_name):
    """Certain configuration parameters have an alias externally"""
    # GIVEN you load sample information from a scout config
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the case a correct case id
    assert case_data[param_name] == scout_config[alias_name]


def test_parse_case_madeline(scout_config):
    # GIVEN you load sample information from a scout config
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the case a correct case id
    assert case_data["madeline_info"]


def test_parse_case_custom_images(scout_config):
    """Test parsing of case"""
    # Given you load custom images info from scout config
    custom_images = parse_custom_images(scout_config)
    # WHEN images is parsed
    # THEN custom_images should have the same sections
    cnf_img = scout_config["custom_images"]
    assert cnf_img.keys() == custom_images.keys()
    # THEN custom_images should have the same number of images
    assert all(len(custom_images[section]) == len(cnf_img[section]) for section in custom_images)
    # Given that some custom images are of not supported formats
    custom_images = parse_custom_images(
        {
            "custom_images": {
                "section_one": [
                    {
                        "title": "A png image",
                        "description": "desc",
                        "path": "scout/demo/images/custom_images/640x480_one.png",
                    },
                    {
                        "title": "A bitmap image",
                        "description": "desc",
                        "path": "scout/demo/images/custom_images/640x480_one.bnp",
                    },
                ],
                "section_two": [
                    {
                        "title": "A pdf image",
                        "description": "desc",
                        "path": "scout/demo/images/custom_images/640x480_one.pdf",
                    },
                ],
            }
        }
    )
    # THEN check that non valid image formats are being rejected
    assert len(custom_images["section_one"]) == 1
    assert "section_two" not in custom_images


def test_parse_case_collaborators(scout_config):
    # GIVEN you load sample information from a scout config
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the case should have a list with collaborators
    assert case_data["collaborators"] == [scout_config["owner"]]


@pytest.mark.parametrize(
    "vcf_file", ["vcf_snv", "vcf_sv", "vcf_str", "vcf_snv_research", "vcf_sv_research"]
)
def test_parse_case_vcf_files(scout_config, vcf_file):
    # GIVEN you load sample information from a scout config
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the case should the same vcf files as specified in the
    assert case_data["vcf_files"][vcf_file] == scout_config[vcf_file]


@pytest.mark.parametrize("bam_name", ["alignment_path", "bam_file", "bam_path"])
def test_parse_case_bams(scout_config, bam_name):
    # GIVEN a load config with bam_path as key to bam/cram files
    bam_path = "a bam"
    for sample in scout_config["samples"]:
        sample[bam_name] = bam_path
    # WHEN case is parsed
    case_data = parse_case(scout_config)

    # THEN assert that bam files are added correct
    for ind in case_data["individuals"]:
        assert ind["bam_file"] == bam_path


def test_parse_case_multiple_alignment_files(scout_config):
    # GIVEN a load config with both cram and bam files
    bam_path = "a bam"
    for sample in scout_config["samples"]:
        sample["bam_file"] = bam_path

    cram_path = "a cram"
    for sample in scout_config["samples"]:
        sample["alignment_path"] = cram_path

    # WHEN case is parsed
    case_data = parse_case(scout_config)

    # THEN assert that cram files are added correctly, ignoring bam
    for ind in case_data["individuals"]:
        assert ind["bam_file"] == cram_path


def test_parse_ped_file(ped_file):
    # GIVEN a pedigree with three samples
    with open(ped_file, "r") as case_lines:
        # WHEN parsing out relevant sample info
        family_id, samples = parse_ped(case_lines)
    # THEN it should return correct family id
    assert family_id == "643594"
    # THEN it should return correct number of individuals
    assert len(samples) == 3
    # THEN assert the sex has been converted
    for sample in samples:
        assert sample["sex"] in REV_SEX_MAP


def test_parse_case_ped_file(ped_file):
    # GIVEN a pedigree with three samples
    with open(ped_file, "r") as case_lines:
        # WHEN parsing out relevant sample info
        config_data = parse_case_data(ped=case_lines, owner="cust000")
    # THEN it should return correct family id
    assert config_data["family"] == "643594"
    # THEN it should return correct number of individuals
    assert len(config_data["samples"]) == 3


def test_parse_case_minimal_config(minimal_config):
    # GIVEN a minimal config
    # WHEN parsing the config
    case_data = parse_case(minimal_config)
    # THEN assert is was parsed correct
    assert case_data


def test_parse_ped():
    # GIVEN a pedigree with three samples
    case_lines = [
        "#Family ID\tIndividual ID\tPaternal ID\tMaternal ID\tSex\tPhenotype",
        "636808\tADM1059A1\t0\t0\t1\t1",
        "636808\tADM1059A2\tADM1059A1\tADM1059A3\t1\t2",
        "636808\tADM1059A3\t0\t0\t2\t1",
    ]

    # WHEN parsing out relevant sample info
    family_id, samples = parse_ped(case_lines)
    # THEN it should return correct family id
    assert family_id == "636808"
    # THEN it should return correct number of individuals
    assert len(samples) == 3


# ## Test how problems are handeled when parsing a case


def test_parse_case_two_cases_ped():
    # GIVEN ped lines from multiple families
    case_lines = [
        "#Family ID\tIndividual ID\tPaternal ID\tMaternal ID\tSex\tPhenotype",
        "636808\tADM1059A1\t0\t0\t1\t1",
        "636808\tADM1059A2\tADM1059A1\tADM1059A3\t1\t2",
        "636808\tADM1059A3\t0\t0\t2\t1",
        "636809\tADM1059A3\t0\t0\t2\t1",
    ]
    # WHEN parsing case info
    with pytest.raises(PedigreeError):
        # THEN it should raise since there are multiple families
        parse_ped(case_lines)


def test_no_individuals():
    # GIVEN a list with no indioviduals
    samples = []
    # WHEN parsing the individuals
    with pytest.raises(PedigreeError):
        # THEN error should be raised since a family has to have individuals
        parse_individuals(samples)


def test_parse_missing_id():
    # GIVEN a individual without sample_id
    sample_info = {"sex": "male", "phenotype": "affected"}
    # WHEN a individual is parsed
    with pytest.raises(PedigreeError):
        # THEN a PedigreeError should be raised
        parse_individual(sample_info)


def test_parse_missing_sex():
    # GIVEN a individual without sex
    sample_info = {"sample_id": "1", "phenotype": "affected"}
    # WHEN a individual is parsed
    with pytest.raises(PedigreeError):
        # THEN a PedigreeError should be raised
        parse_individual(sample_info)


def test_parse_missing_phenotype():
    # GIVEN a individual without phenotype
    sample_info = {"sample_id": "1", "sex": "male"}
    # WHEN a individual is parsed
    with pytest.raises(PedigreeError):
        # THEN a PedigreeError should be raised
        parse_individual(sample_info)


def test_parse_wrong_phenotype():
    # GIVEN a individual with wrong phenotype format
    sample_info = {"sample_id": "1", "sex": "male", "phenotype": "not-affected"}
    # WHEN a individual is parsed
    with pytest.raises(PedigreeError):
        # THEN a PedigreeError should be raised
        parse_individual(sample_info)


def test_parse_wrong_sex():
    # GIVEN a individual with wrong sex format
    sample_info = {"sample_id": "1", "sex": "flale", "phenotype": "affected"}
    # WHEN a individual is parsed
    with pytest.raises(PedigreeError):
        # THEN a PedigreeError should be raised
        parse_individual(sample_info)


def test_wrong_relations(scout_config):
    # GIVEN a individual with correct family info
    # Nothing should happend here
    assert parse_case(scout_config)

    # WHEN changing mother id in proband to non-existing id
    samples_list = scout_config["samples"]
    erronous_config = []
    for sample in samples_list:
        if sample["sample_id"] == "ADM1059A2":
            sample["mother"] = "ID_miss"
            erronous_config.append(sample)
        else:
            erronous_config.append(sample)
    scout_config["samples"] = erronous_config

    # THEN a PedigreeError should be raised
    with pytest.raises(PedigreeError):
        parse_case(scout_config)


def test_removeNoneValues():
    # WHEN a dict *not* containing a None value
    d = {"a": "1", "b": 2, "c": 3}

    # THEN calling removeNoneValues(dict) will not change dict
    assert d == removeNoneValues(d)


def test_removeNoneValues():
    # WHEN a dict containing a value which is None
    d = {"a": "1", "b": 2, "c": None}

    # THEN calling removeNoneValues(dict) will remove key-value pair
    # where value=None
    assert {"a": "1", "b": 2} == removeNoneValues(d)


def test_parse_optional_igv_param(scout_config):
    # GIVEN a dict contains optional igv params
    # i.e. rhocall_wig
    samples = scout_config["samples"]

    # WHEN optional parameters are added to config
    for sample in samples:
        sample["rhocall_bed"] = "path/to/rb"
        sample["rhocall_wig"] = "path/to/rw"
        sample["upd_regions_bed"] = "path/to/up"
        sample["upd_sites_bed"] = "path/to/us"
        sample["tiddit_coverage_wig"] = "path/to/tc"
        sample["chromograph_images"] = "path/to/ci"
    scout_config["samples"] = samples

    # THEN parsing the config will add those to case data
    case_data = parse_case(scout_config)
    case_list = []
    config_list = []
    for individual in case_data["individuals"]:
        case_list.append(
            (
                individual["rhocall_wig"],
                individual["rhocall_bed"],
                individual["upd_regions_bed"],
                individual["upd_sites_bed"],
                individual["tiddit_coverage_wig"],
                individual["chromograph_images"],
            )
        )

    for sample in samples:
        config_list.append(
            (
                sample["rhocall_wig"],
                sample["rhocall_bed"],
                sample["upd_regions_bed"],
                sample["upd_sites_bed"],
                sample["tiddit_coverage_wig"],
                sample["chromograph_images"],
            )
        )

    assert config_list == case_list


def test_missing_optional_igv_param(scout_config):
    # WHEN a dict is missing optinal wig param (later passed to igv.js)
    # i.e. rhocall_wig
    scout_config.pop("rhocall_bed", "ignore_return")
    scout_config.pop("rhocall_wig", "ignore_return")
    scout_config.pop("upd_regions_bed", "ignore_return")
    scout_config.pop("upd_sites_bed", "ignore_return")
    scout_config.pop("tiddit_coverage_wig", "ignore_return")

    # THEN parsing the config will not raise an exception
    case_data = parse_case(scout_config)
    assert case_data


@pytest.mark.parametrize("key", ["owner", "family"])
def test_missing_mandatory_config_key(scout_config, key):
    ## GIVEN a scout_config (dict) containing user case information

    ## WHEN deleting key
    scout_config.pop(key)
    ## THEN calling parse_case() will raise ConfigError
    with pytest.raises(ConfigError):
        parse_case(scout_config)
