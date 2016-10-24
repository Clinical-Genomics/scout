# -*- coding: utf-8 -*-
from scout.build import build_individual


def test_build_individual():
    ind_info = {
        'individual_id': '1',
        'father': '2',
        'mother': '3',
        'display_name': '1-1',
        'sex': 'male',
        'phenotype': 'affected',
        'bam_file': 'a.bam',
        'capture_kits': ['Agilent']
    }
    ind_obj = build_individual(ind_info)

    assert ind_obj.individual_id == ind_info['individual_id']
    assert ind_obj.display_name == ind_info['display_name']
    assert ind_obj.capture_kits == ind_info['capture_kits']


def test_build_individuals(parsed_case):
    for ind_info in parsed_case['individuals']:
        print(ind_info)
        ind_obj = build_individual(ind_info)

        assert ind_obj.individual_id == ind_info['individual_id']
        assert ind_obj.display_name == ind_info['display_name']
        assert ind_obj.capture_kits == ind_info['capture_kits']
