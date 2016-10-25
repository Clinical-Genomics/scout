import pytest
from scout.parse import parse_case
from scout.parse.case import parse_ped
from scout.exceptions import PedigreeError


def test_parse_case(scout_config, case_lines):
    # GIVEN you load sample information from PED file
    case_data = parse_case(scout_config, ped=case_lines)
    assert case_data['owner'] == scout_config['institute']


def test_parse_case_two_cases():
    # GIVEN ped lines from multiple families
    case_lines = [
        "#Family ID	Individual ID	Paternal ID	Maternal ID	Sex	Phenotype",
        "636808	ADM1059A1	0	0	1	1",
        "636808	ADM1059A2	ADM1059A1	ADM1059A3	1	2",
        "636808	ADM1059A3	0	0	2	1",
        "636809	ADM1059A3	0	0	2	1",
    ]
    # WHEN parsing case info
    config = {'institute': 'test_institute'}
    # THEN it should raise since there are multiple families
    with pytest.raises(PedigreeError):
        parse_case(config, ped=case_lines)


def test_parse_ped(case_lines):
    # GIVEN a pedigree with three samples
    assert len(case_lines) == 4
    # WHEN parsing out relevant sample info
    family_id, samples = parse_ped(case_lines)
    # THEN it should return stuff
    assert family_id == '337334-testset'
    assert len(samples) == 3
    # assert samples[0]['sample_id'] == 'ADM1136A1'
    # assert samples[0]['sex'] == 'male'
    # assert samples[0]['phenotype'] == 'unaffected'
