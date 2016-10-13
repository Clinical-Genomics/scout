from scout.build import build_case

def test_build_minimal_case():
    case = {
        'case_id': "337334",
        'display_name': "337334",
        'owner': 'cust000',
        'collaborators': ['cust000'],
        'individuals':[
            {
                'ind_id': 'ADM1136A1',
                'father': '0',
                'mother': '0',
                'display_name': 'ADM1136A1',
                'sex': '1',
                'phenotype': 1
            },
            {
                'ind_id': 'ADM1136A2',
                'father': 'ADM1136A1',
                'mother': 'ADM1136A3',
                'display_name': 'ADM1136A2',
                'sex': '1',
                'phenotype': 2
            },
            {
                'ind_id': 'ADM1136A3',
                'father': '0',
                'mother': '0',
                'display_name': 'ADM1136A3',
                'sex': '2',
                'phenotype': 1
            },
            
        ]
    }
    
    case_obj = build_case(case)
    
    assert case_obj.case_id == case['case_id']
    assert len(case_obj.individuals) == 3