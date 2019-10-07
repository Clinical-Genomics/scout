from pprint import pprint as pp
from scout.parse.variant.clnsig import parse_clnsig

def test_parse_classic_clnsig(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "RCV000014440.17|RCV000014441.25|RCV000014442.25|RCV000014443.17|RCV000184011.1|RCV000188658.1"
    clnsig = "5|5|5|5|5|5"
    revstat = "conf|single|single|single|conf|conf"

    cyvcf2_variant.INFO['CLNACC'] = acc_nr
    cyvcf2_variant.INFO['CLNSIG'] = clnsig
    cyvcf2_variant.INFO['CLNREVSTAT'] = revstat
    
    ## WHEN parsing the annotations
    clnsig_annotations = parse_clnsig(cyvcf2_variant)
    
    ## THEN assert that they where parsed correct
    assert len(clnsig_annotations) == len(clnsig.split('|'))
    
    ## THEN assert that one of them is correct
    for entry in clnsig_annotations:
        if entry['accession'] == "RCV000014440.17":
            assert entry['value'] == 5
            assert entry['revstat'] == 'conf'
    


def test_parse_modern_clnsig(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "265359"
    clnsig = "Pathogenic/Likely pathogenic"
    revstat = "criteria_provided,_multiple_submitters,_no_conflicts"

    cyvcf2_variant.INFO['CLNACC'] = acc_nr
    cyvcf2_variant.INFO['CLNSIG'] = clnsig
    cyvcf2_variant.INFO['CLNREVSTAT'] = revstat
    
    ## WHEN parsing the annotations
    clnsig_annotations = parse_clnsig(cyvcf2_variant)
    
    ## THEN assert that they where parsed correct
    assert len(clnsig_annotations) == len(clnsig.split('|'))
    pp(clnsig_annotations)
    assert False
    

# def test_parse_clnsig_():
#
#     ## Test parsing clnsig combination of values from different submitters:
#     variant = {
#         'info_dict':{
#             'CLNACC': "265359",
#             'CLNSIG': "Pathogenic/Likely pathogenic",
#             'CLNREVSTAT': "criteria_provided,_multiple_submitters,_no_conflicts",
#             }
#     }
#     clinrevstat = variant['info_dict']['CLNREVSTAT']
#     revstat_groups = [rev.lstrip('_') for rev in clinrevstat.split(',')]
#
#     clnsig_annotations = parse_clnsig(
#         acc=variant['info_dict']['CLNACC'],
#         sig=variant['info_dict']['CLNSIG'],
#         revstat=variant['info_dict']['CLNREVSTAT'],
#         transcripts=[]
#     )
#
#     ## assert that they where parsed correct
#     assert len(clnsig_annotations) == 2
#
#     for entry in clnsig_annotations:
#         assert entry['accession'] ==  int(variant['info_dict']['CLNACC'])
#         assert entry['value'] in ['Pathogenic', 'Likely pathogenic']
#         assert entry['revstat'] == ', '.join(revstat_groups)
