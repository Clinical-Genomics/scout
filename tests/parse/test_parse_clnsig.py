from scout.parse.variant.clnsig import parse_clnsig

def test_parse_clnsig_():

    ## Test parsing classical clnsig representation
    variant = {
        'info_dict':{
            'CLNACC': "RCV000014440.17|RCV000014441.25|RCV000014442.25|RCV000014443.17|RCV000184011.1|RCV000188658.1",
            'CLNSIG': "5|5|5|5|5|5",
            'CLNREVSTAT': "conf|single|single|single|conf|conf",
            }
    }

    ## WHEN parsing the clinical significance
    clnsig_annotations = parse_clnsig(
        acc=variant['info_dict']['CLNACC'],
        sig=variant['info_dict']['CLNSIG'],
        revstat=variant['info_dict']['CLNREVSTAT'],
        transcripts=[]
    )

    ## THEN assert that they where parsed correct
    assert len(clnsig_annotations) == 6

    for entry in clnsig_annotations:
        if entry['accession'] == "RCV000014440.17":
            assert entry['value'] == 5
            assert entry['revstat'] == 'conf'


    ## Test parsing clnsig combination of values from different submitters:
    variant = {
        'info_dict':{
            'CLNACC': "265359",
            'CLNSIG': "Pathogenic/Likely pathogenic",
            'CLNREVSTAT': "criteria_provided,_multiple_submitters,_no_conflicts",
            }
    }
    clinrevstat = variant['info_dict']['CLNREVSTAT']
    revstat_groups = [rev.lstrip('_') for rev in clinrevstat.split(',')]

    clnsig_annotations = parse_clnsig(
        acc=variant['info_dict']['CLNACC'],
        sig=variant['info_dict']['CLNSIG'],
        revstat=variant['info_dict']['CLNREVSTAT'],
        transcripts=[]
    )

    ## assert that they where parsed correct
    assert len(clnsig_annotations) == 2

    for entry in clnsig_annotations:
        assert entry['accession'] ==  int(variant['info_dict']['CLNACC'])
        assert entry['value'] in ['Pathogenic', 'Likely pathogenic']
        assert entry['revstat'] == ', '.join(revstat_groups)
