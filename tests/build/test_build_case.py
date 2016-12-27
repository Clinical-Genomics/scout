# -*- coding: utf-8 -*-
from scout.build import build_case

def test_build_case(parsed_case):
    #GIVEN a parsed case
    #WHEN bulding a case model
    case_obj = build_case(parsed_case)
    
    #THEN make sure it is built in the proper way
    assert case_obj.case_id == parsed_case['case_id']
    assert case_obj.display_name == parsed_case['display_name']
    assert case_obj.owner == parsed_case['owner']
    assert case_obj.collaborators == parsed_case['collaborators']
    assert case_obj.assignee == None
    assert len(case_obj.individuals) == len(parsed_case['individuals'])
    assert len(case_obj.suspects) == 0
    assert len(case_obj.causatives) == 0
    assert case_obj.synopsis == ''
    
    assert case_obj.status == 'inactive'
    assert case_obj.is_research == False
    assert case_obj.research_requested == False
    assert case_obj.rerun_requested == False
    
    assert case_obj.analysis_date == parsed_case['analysis_date']
    assert case_obj.analysis_dates == [parsed_case['analysis_date']]

    assert len(case_obj.dynamic_gene_list) == 0
    
    assert case_obj.genome_build == parsed_case['genome_build']
    
    assert case_obj.rank_model_version == parsed_case['rank_model_version']
    assert case_obj.rank_score_treshold == parsed_case['rank_score_treshold']
    
    assert case_obj.phenotype_terms == []
    assert case_obj.phenotype_groups == []
    
    assert case_obj.madeline_info == parsed_case['madeline_info']
    
    for vcf in case_obj.vcf_files:
         assert vcf in parsed_case['vcf_files']
         
    assert case_obj.diagnosis_phenotypes == []
    assert case_obj.diagnosis_genes == []
    
    if (parsed_case['vcf_files'].get('vcf_sv') or parsed_case['vcf_files'].get('vcf_sv_research')):
        assert case_obj.has_svvariants == True
    else:
        assert case_obj.has_svvariants == False

# def test_build_case_config(parsed_case):
#     case_obj = build_case(parsed_case)
#     print(case_obj.to_json())
#     assert False
