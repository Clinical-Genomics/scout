from scout.parse.variant.conservation import (parse_conservation_info, parse_conservations)

def test_parse_conservation(cyvcf2_variant):
    variant = cyvcf2_variant
    ## GIVEN a variant with some GERP information
    variant.INFO['dbNSFP_GERP___RS'] = 3.7
    ## WHEN parsing conservation
    ## THEN assert that the field is parsed correct
    assert parse_conservation_info(variant, 'dbNSFP_GERP___RS', 'gerp') == ['Conserved']

def test_parse_conservation_multiple_terms(cyvcf2_variant):
    variant = cyvcf2_variant
    ## GIVEN a variant with multiple GERP annotations
    variant.INFO['dbNSFP_GERP___RS'] = 3.7, -0.34

    ## WHEN parsing conservation
    ## THEN assert that all terms are returned
    assert parse_conservation_info(variant, 'dbNSFP_GERP___RS', 'gerp') == ['Conserved', 'NotConserved']

def test_parse_conservations(cyvcf2_variant):
    variant = cyvcf2_variant
    ## GIVEN a variant with multiple conservation annotations
    variant.INFO['dbNSFP_GERP___RS'] = 4.6,0
    variant.INFO['dbNSFP_phastCons100way_vertebrate'] = 0.8
    variant.INFO['dbNSFP_phyloP100way_vertebrate'] = 2.4

    ## WHEN parsing conservation
    ## THEN assert that all terms are returned

    conservations = parse_conservations(variant)

    assert conservations['gerp'] == ['Conserved', 'NotConserved']
    assert conservations['phast'] == ['Conserved']
    assert conservations['phylop'] == ['NotConserved']


def test_parse_conservation_csq(cyvcf2_variant):

    ## GIVEN a variant with multiple conservation annotations
    csq_entry="""0&4.6|0.8|2.4,0&4.6|0.8|2.4"""
    vep_header="""GERP++_RS|phastCons100way_vertebrate|phyloP100way_vertebrate"""

    cyvcf2_variant.INFO['CSQ'] = csq_entry

    # variant consists of 2 transcrips, each one of them with gerp, phast and phylop values
    raw_transcripts =  list((dict(zip(vep_header.split('|'), transcript_info.split('|')))
                       for transcript_info in csq_entry.split(',')))

    assert len(raw_transcripts) == 2

    ## WHEN parsing conservation
    conservations = parse_conservations(cyvcf2_variant, True, raw_transcripts)

    ## THEN assert that all terms are returned
    assert conservations['gerp'] == ['NotConserved','Conserved']
    assert conservations['phast'] == ['Conserved']
    assert conservations['phylop'] == ['NotConserved']
