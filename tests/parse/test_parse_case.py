import pytest

from pprint import pprint as pp
from scout.parse.case import (parse_case, parse_ped, parse_individuals,
                              parse_individual, parse_case_data)
from scout.exceptions import PedigreeError
from scout.constants import REV_SEX_MAP

def test_parse_case(scout_config):
    # GIVEN you load sample information from a scout config
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the case should have a owner
    assert case_data['owner'] == scout_config['owner']


def test_parse_case(scout_config):
    # GIVEN you load sample information from a scout config
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the case a correct case id
    assert case_data['case_id'] == scout_config['family']


def test_parse_case_madeline(scout_config):
    # GIVEN you load sample information from a scout config
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the case a correct case id
    assert case_data['madeline_info']


def test_parse_case_collaborators(scout_config):
    # GIVEN you load sample information from a scout config
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the case should have a list with collaborators
    assert case_data['collaborators'] == [scout_config['owner']]


def test_parse_case_gene_panels(scout_config):
    # GIVEN you load sample information from a scout config
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the case should have the same panels like the config
    assert case_data['gene_panels'] == scout_config['gene_panels']


def test_parse_case_default_panels(scout_config):
    # GIVEN you load sample information from a scout config
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the case should have the same panels like the config
    assert case_data['default_panels'] == scout_config['default_gene_panels']


def test_parse_case_rank_threshold(scout_config):
    # GIVEN you load sample information from a scout config
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the case should have the same panels like the config
    assert case_data['rank_score_threshold'] == scout_config['rank_score_threshold']


def test_parse_case_rank_model_version(scout_config):
    # GIVEN you load sample information from a scout config
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the case should have the same rank model version like the config
    assert case_data['rank_model_version'] == scout_config['rank_model_version']


def test_parse_case_vcf_files(scout_config):
    # GIVEN you load sample information from a scout config
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the case should the same vcf files as specified in the
    assert case_data['vcf_files']['vcf_snv'] == scout_config['vcf_snv']
    assert case_data['vcf_files']['vcf_sv'] == scout_config['vcf_sv']
    assert case_data['vcf_files']['vcf_snv_research'] == scout_config['vcf_snv_research']
    assert case_data['vcf_files']['vcf_sv_research'] == scout_config['vcf_sv_research']


def test_parse_case_delivery_report(scout_config):
    # GIVEN you load sample information from a scout config

    # WHEN case is parsed
    case_data = parse_case(scout_config)

    # then we should find the delivery report in the parsed data
    assert case_data['delivery_report'] == scout_config['delivery_report']


def test_parse_ped_file(ped_file):
    # GIVEN a pedigree with three samples
    with open(ped_file, 'r') as case_lines:
        # WHEN parsing out relevant sample info
        family_id, samples = parse_ped(case_lines)
    # THEN it should return correct family id
    assert family_id == '643594'
    # THEN it should return correct number of individuals
    assert len(samples) == 3
    # THEN assert the sex has been converted
    for sample in samples:
        assert sample['sex'] in REV_SEX_MAP

def test_parse_case_ped_file(ped_file):
    # GIVEN a pedigree with three samples
    with open(ped_file, 'r') as case_lines:
        # WHEN parsing out relevant sample info
        config_data = parse_case_data(ped=case_lines, owner='cust000')
    # THEN it should return correct family id
    assert config_data['family'] == '643594'
    # THEN it should return correct number of individuals
    assert len(config_data['samples']) == 3


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
    assert family_id == '636808'
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
    sample_info = {
        'sex': 'male',
        'phenotype': 'affected',
    }
    # WHEN a individual is parsed
    with pytest.raises(PedigreeError):
        # THEN a PedigreeError should be raised
        parse_individual(sample_info)


def test_parse_missing_sex():
    # GIVEN a individual without sex
    sample_info = {
        'sample_id': '1',
        'phenotype': 'affected',
    }
    # WHEN a individual is parsed
    with pytest.raises(PedigreeError):
        # THEN a PedigreeError should be raised
        parse_individual(sample_info)


def test_parse_missing_phenotype():
    # GIVEN a individual without phenotype
    sample_info = {
        'sample_id': '1',
        'sex': 'male',
    }
    # WHEN a individual is parsed
    with pytest.raises(PedigreeError):
        # THEN a PedigreeError should be raised
        parse_individual(sample_info)


def test_parse_wrong_phenotype():
    # GIVEN a individual with wrong phenotype format
    sample_info = {
        'sample_id': '1',
        'sex': 'male',
        'phenotype': 'not-affected',
    }
    # WHEN a individual is parsed
    with pytest.raises(PedigreeError):
        # THEN a PedigreeError should be raised
        parse_individual(sample_info)


def test_parse_wrong_sex():
    # GIVEN a individual with wrong sex format
    sample_info = {
        'sample_id': '1',
        'sex': 'flale',
        'phenotype': 'affected',
    }
    # WHEN a individual is parsed
    with pytest.raises(PedigreeError):
        # THEN a PedigreeError should be raised
        parse_individual(sample_info)


def test_wrong_relations():
    """docstring for test_wrong_relations"""
    # GIVEN a individual with correct family info
    sample_info = {
        'sample_id': '1',
        'sex': 'male',
        'phenotype': 'affected',
        'mother': '3',
        'father': '2'
    }
    mother_info = {
        'sample_id': '3',
        'sex': 'female',
        'phenotype': 'unaffected',
        'mother': '0',
        'father': '0'
    }
    father_info = {
        'sample_id': '2',
        'sex': 'male',
        'phenotype': 'unaffected',
        'mother': '0',
        'father': '0'
    }
    samples = [sample_info, mother_info, father_info]
    # Nothong should happend here
    assert parse_individuals(samples)

    # WHEN changing mother id in proband
    sample_info['mother'] = '5'
    # THEN a PedigreeError should be raised
    with pytest.raises(PedigreeError):
        parse_individuals(samples)
