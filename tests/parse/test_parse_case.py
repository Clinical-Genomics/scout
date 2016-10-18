import pytest
from scout.parse import parse_case
from scout.exceptions import PedigreeError

def test_parse_case(case_lines, scout_configs):
    owner = scout_configs['owner']
    
    case = parse_case(case_lines, owner)
    
    assert case['owner'] == owner


def test_parse_case_two_cases():
    """Should raise SyntaxError if there are multiple families in the ped file"""
    case_lines = [
        "#Family ID	Individual ID	Paternal ID	Maternal ID	Sex	Phenotype",
        "636808	ADM1059A1	0	0	1	1",
        "636808	ADM1059A2	ADM1059A1	ADM1059A3	1	2",
        "636808	ADM1059A3	0	0	2	1",
        "636809	ADM1059A3	0	0	2	1",
    ]
    #Should raise since there are multiple families
    with pytest.raises(PedigreeError):
        parse_case(case_lines, 'test_institute')