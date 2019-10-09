from pprint import pprint as pp
from scout.parse.variant.clnsig import (parse_clnsig,is_pathogenic)

def test_parse_classic_clnsig(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "RCV000014440.17|RCV000014441.25|RCV000014442.25|RCV000014443.17|RCV000184011.1|RCV000188658.1"
    clnsig = "5|4|3|2|1|0"
    revstat = "conf|single|single|single|conf|conf"

    cyvcf2_variant.INFO['CLNACC'] = acc_nr
    cyvcf2_variant.INFO['CLNSIG'] = clnsig
    cyvcf2_variant.INFO['CLNREVSTAT'] = revstat
    
    ## WHEN parsing the annotations
    clnsig_annotations = parse_clnsig(cyvcf2_variant)
    
    ## THEN assert that they where parsed correct
    assert len(clnsig_annotations) == len(clnsig.split('|'))
    
    ## THEN assert that all accessions are there
    assert {term['accession'] for term in clnsig_annotations} == set(acc_nr.split('|'))
    ## THEN assert that all have been parsed as expected
    for entry in clnsig_annotations:
        if entry['accession'] == "RCV000014440.17":
            assert entry['value'] == 5
            assert entry['revstat'] == 'conf'

        if entry['accession'] == "RCV000014441.25":
            assert entry['value'] == 4
            assert entry['revstat'] == 'single'

        if entry['accession'] == "RCV000014442.25":
            assert entry['value'] == 3
            assert entry['revstat'] == 'single'

        if entry['accession'] == "RCV000014443.17":
            assert entry['value'] == 2
            assert entry['revstat'] == 'single'

        if entry['accession'] == "RCV000184011.1":
            assert entry['value'] == 1
            assert entry['revstat'] == 'conf'

        if entry['accession'] == "RCV000188658.1":
            assert entry['value'] == 0
            assert entry['revstat'] == 'conf'

def test_parse_modern_clnsig(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "265359"
    clnsig = "Pathogenic/Likely_pathogenic"
    revstat = "criteria_provided,_multiple_submitters,_no_conflicts"

    cyvcf2_variant.INFO['CLNACC'] = acc_nr
    cyvcf2_variant.INFO['CLNSIG'] = clnsig
    cyvcf2_variant.INFO['CLNREVSTAT'] = revstat
    
    ## WHEN parsing the annotations
    clnsig_annotations = parse_clnsig(cyvcf2_variant)
    
    ## THEN assert that the correct terms are parsed
    assert set(['pathogenic','likely_pathogenic']) == {term['value'] for term in clnsig_annotations}
    ## THEN assert that they where parsed correct
    assert len(clnsig_annotations) == len(clnsig.split('/'))

def test_parse_modern_clnsig_clnvid(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "265359"
    clnsig = "Pathogenic/Likely_pathogenic"
    revstat = "criteria_provided,_multiple_submitters,_no_conflicts"

    cyvcf2_variant.INFO['CLNVID'] = acc_nr
    cyvcf2_variant.INFO['CLNSIG'] = clnsig
    cyvcf2_variant.INFO['CLNREVSTAT'] = revstat
    
    ## WHEN parsing the annotations
    clnsig_annotations = parse_clnsig(cyvcf2_variant)
    
    ## THEN assert that the correct terms are parsed
    assert set(['pathogenic','likely_pathogenic']) == {term['value'] for term in clnsig_annotations}
    ## THEN assert that they where parsed correct
    assert len(clnsig_annotations) == len(clnsig.split('/'))

def test_parse_semi_modern_clnsig(cyvcf2_variant):
    ## GIVEN a variant with semi modern clinvar annotations
    # This means that there can be spaces between words
    acc_nr = "265359"
    clnsig = "Pathogenic/Likely pathogenic"
    revstat = "criteria_provided,_multiple_submitters,_no_conflicts"

    cyvcf2_variant.INFO['CLNACC'] = acc_nr
    cyvcf2_variant.INFO['CLNSIG'] = clnsig
    cyvcf2_variant.INFO['CLNREVSTAT'] = revstat
    
    ## WHEN parsing the annotations
    clnsig_annotations = parse_clnsig(cyvcf2_variant)
    
    ## THEN assert that the correct terms are parsed
    assert set(['pathogenic','likely_pathogenic']) == {term['value'] for term in clnsig_annotations}
    ## THEN assert that they where parsed correct
    assert len(clnsig_annotations) == len(clnsig.split('/'))
    for annotation in clnsig_annotations:
        assert annotation['accession'] == int(acc_nr)
        assert set(annotation['revstat'].split(',')) == set(["criteria_provided","multiple_submitters","no_conflicts"])

def test_parse_clnsig_all(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "265359"
    clnsig = "Pathogenic/Likely pathogenic"
    revstat = "criteria_provided,_multiple_submitters,_no_conflicts"

    cyvcf2_variant.INFO['CLNACC'] = acc_nr
    cyvcf2_variant.INFO['CLNSIG'] = clnsig
    cyvcf2_variant.INFO['CLNREVSTAT'] = revstat

    revstat_groups = [rev.lstrip('_') for rev in revstat.split(',')]

    clnsig_annotations = parse_clnsig(cyvcf2_variant)

    ## assert that they where parsed correct
    assert len(clnsig_annotations) == 2

    for entry in clnsig_annotations:
        assert entry['accession'] ==  int(acc_nr)
        assert entry['value'] in ['pathogenic', 'likely_pathogenic']
        assert entry['revstat'] == ','.join(revstat_groups)

def test_parse_complex_clnsig(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "265359"
    clnsig = "Benign/Likely_benign,_other"
    revstat = "criteria_provided,_multiple_submitters,_no_conflicts"

    cyvcf2_variant.INFO['CLNACC'] = acc_nr
    cyvcf2_variant.INFO['CLNSIG'] = clnsig
    cyvcf2_variant.INFO['CLNREVSTAT'] = revstat
    
    ## WHEN parsing the annotations
    clnsig_annotations = parse_clnsig(cyvcf2_variant)
    
    ## THEN assert that they where parsed correct
    assert len(clnsig_annotations) == 3

def test_parse_clnsig_transcripts(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    transcripts = [
        {
            'clnsig': ['likely_benign']
        }
    ]
    
    ## WHEN parsing the annotations
    clnsig_annotations = parse_clnsig(cyvcf2_variant, transcripts = transcripts)
    
    ## THEN assert that they where parsed correct
    assert len(clnsig_annotations) == 1
    assert clnsig_annotations[0]['value'] == 'likely_benign'


def test_is_pathogenic_pathogenic(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "265359"
    clnsig = "Pathogenic"
    revstat = "criteria_provided,_multiple_submitters,_no_conflicts"

    cyvcf2_variant.INFO['CLNVID'] = acc_nr
    cyvcf2_variant.INFO['CLNSIG'] = clnsig
    cyvcf2_variant.INFO['CLNREVSTAT'] = revstat
    
    ## WHEN checking if variants should be loaded
    pathogenic = is_pathogenic(cyvcf2_variant)
    
    ## THEN assert that The variant should be loaded
    assert pathogenic == True

def test_is_pathogenic_classic_pathogenic(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "RCV000014440.17|RCV000014441.25|RCV000014442.25|RCV000014443.17|RCV000184011.1|RCV000188658.1"
    clnsig = "5|4|3|2|1|0"
    revstat = "conf|single|single|single|conf|conf"

    cyvcf2_variant.INFO['CLNVID'] = acc_nr
    cyvcf2_variant.INFO['CLNSIG'] = clnsig
    cyvcf2_variant.INFO['CLNREVSTAT'] = revstat
    
    ## WHEN checking if variants should be loaded
    pathogenic = is_pathogenic(cyvcf2_variant)
    
    ## THEN assert that The variant should be loaded
    assert pathogenic == True

def test_is_pathogenic_benign(cyvcf2_variant):
    ## GIVEN a variant with classic clinvar annotations
    acc_nr = "265359"
    clnsig = "Likely_benign"
    revstat = "criteria_provided,_multiple_submitters,_no_conflicts"

    cyvcf2_variant.INFO['CLNVID'] = acc_nr
    cyvcf2_variant.INFO['CLNSIG'] = clnsig
    cyvcf2_variant.INFO['CLNREVSTAT'] = revstat
    
    ## WHEN checking if variants should be loaded
    pathogenic = is_pathogenic(cyvcf2_variant)
    
    ## THEN assert that The variant should be loaded
    assert pathogenic == False

def test_is_pathogenic_no_annotation(cyvcf2_variant):
    ## GIVEN a variant without clinvar annotations
    
    ## WHEN checking if variants should be loaded
    pathogenic = is_pathogenic(cyvcf2_variant)
    
    ## THEN assert that The variant should be loaded
    assert pathogenic == False
