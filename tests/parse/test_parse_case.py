import pytest
from scout.parse.case import parse_case
from scout.parse.case import parse_ped
from scout.exceptions import PedigreeError


def test_parse_case(scout_config):
    # GIVEN you load sample information from a scout config
    # WHEN case is parsed
    case_data = parse_case(scout_config)
    # THEN the case should have a owner
    assert case_data['owner'] == scout_config['owner']


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


def test_parse_ped(ped_lines):
    # GIVEN a pedigree with three samples
    assert len(ped_lines) == 4
    # WHEN parsing out relevant sample info
    family_id, samples = parse_ped(ped_lines)
    # THEN it should return stuff
    assert family_id == '643594'
    assert len(samples) == 3
    # assert samples[0]['sample_id'] == 'ADM1136A1'
    # assert samples[0]['sex'] == 'male'
    # assert samples[0]['phenotype'] == 'unaffected'
