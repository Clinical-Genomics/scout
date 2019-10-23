from scout.server.blueprints.variant.utils import (predictions, sv_frequencies, is_affected, 
evaluation, transcript_str, frequency, end_position)

def test_end_position_old_indel():
    ## GIVEN a small indel
    var = {'alternative':'TCTC', 'reference': 'AGAG', 'position': 100}
    ## WHEN getting the end position
    end = end_position(var)
    ## THEN assert that the end position is 10 bases
    assert end == 103

def test_end_position_indel():
    ## GIVEN a single nucleotide variant
    var = {'alternative':'TCTCTCTCACA', 'reference': 't', 'position': 100}
    ## WHEN getting the end position
    end = end_position(var)
    ## THEN assert that the end position is 10 bases
    assert end == 110

def test_end_position_snv():
    ## GIVEN a single nucleotide variant
    var = {'alternative':'A', 'reference': 'C', 'position': 100}
    ## WHEN getting the end position
    end = end_position(var)
    ## THEN assert that the end position is correct
    assert end == 100

def test_frequency_rare():
    ## GIVEN a variant which is uncommon gnomad frequency
    var = {'gnomad_frequency':0.001}
    ## WHEN converting frequencies to string
    freq_str = frequency(var)
    ## THEN assert that the variant is common
    assert freq_str == 'rare'

def test_frequency_uncommon():
    ## GIVEN a variant which is uncommon gnomad frequency
    var = {'gnomad_frequency':0.03}
    ## WHEN converting frequencies to string
    freq_str = frequency(var)
    ## THEN assert that the variant is common
    assert freq_str == 'uncommon'

def test_frequency_common():
    ## GIVEN a variant with a common gnomad frequency
    var = {'gnomad_frequency':0.5}
    ## WHEN converting frequencies to string
    freq_str = frequency(var)
    ## THEN assert that the variant is common
    assert freq_str == 'common'
    
def test_tx_str():
    ## GIVEN a transcript object with an exon change and a gene name
    gene_name = 'NCDN'
    tx_obj = {
        'exon': '8/8',
        'refseq_id': 'NM_001014839',
        'coding_sequence_name': 'c.*156C>T',
    }
    ## WHEN Converting the information to a string for the template
    change_str = transcript_str(tx_obj, gene_name)
    
    ## THEN assert the string is on expected format
    assert change_str == "NCDN:NM_001014839:exon8:c.*156C>T:NA"
    
def test_evaluation(real_variant_database):
    ## GIVEN a populated database
    store = real_variant_database
    var = store.variant_collection.find_one()
    user = store.user_collection.find_one()
    institute = store.institute_collection.find_one()
    case = store.case_collection.find_one()
    link = 'a link'
    classification = 'pathogenic'
    
    ## WHEN adding an evaluation to the database
    store.submit_evaluation(var, user, institute, case, link, classification=classification)
    
    eval_obj = store.acmg_collection.find_one()
    assert eval_obj['institute_id'] == institute['_id']
    assert 'institute' not in eval_obj
    
    updated_eval = evaluation(store, eval_obj)
    ## THEN assert that the correct information was added to display evaluation
    assert updated_eval['institute'] == institute
    

def test_is_affected_healthy():
    ## GIVEN a variant and a case
    case_obj = {
        'individuals': [{'individual_id': '1', 'phenotype': 1}]
    }
    variant_obj = {
        'samples': [{'sample_id': '1'}]
    }
    ## WHEN converting affection status to string
    is_affected(variant_obj, case_obj)
    ## THEN assert that affection status is healthy
    updated_sample = variant_obj['samples'][0]
    assert 'is_affected' in updated_sample
    assert updated_sample['is_affected'] == False

def test_is_affected_affected():
    ## GIVEN a variant and a case
    case_obj = {
        'individuals': [{'individual_id': '1', 'phenotype': 2}]
    }
    variant_obj = {
        'samples': [{'sample_id': '1'}]
    }
    ## WHEN converting affection status to string
    is_affected(variant_obj, case_obj)
    ## THEN assert that affection status is healthy
    updated_sample = variant_obj['samples'][0]
    assert updated_sample['is_affected'] == True

def test_gene_predictions_no_info():
    ## GIVEN a empty list of genes
    genes = []
    
    ## WHEN parsing the gene predictions
    res = predictions(genes)
    ## THEN assert the result is not filled
    assert res == {'sift_predictions': [],
                   'polyphen_predictions': [],
                   'region_annotations': [],
                   'functional_annotations': []}

def test_gene_predictions_one_gene():
    ## GIVEN a empty list of genes
    gene = {
        'sift_prediction': 'deleterious',
        'polyphen_prediction': 'probably_damaging',
        'region_annotation': 'exonic',
        'functional_annotation': 'missense_variant',
    }
    genes = [gene]
    
    ## WHEN parsing the gene predictions
    res = predictions(genes)
    ## THEN assert the result is not filled
    assert res == {
                   'sift_predictions': ['deleterious'],
                   'polyphen_predictions': ['probably_damaging'],
                   'region_annotations': ['exonic'],
                   'functional_annotations': ['missense_variant']
               }

def test_gene_predictions_one_gene_no_sift():
    ## GIVEN a empty list of genes
    gene = {
        'hgnc_symbol': 'AAA',
        'polyphen_prediction': 'probably_damaging',
        'region_annotation': 'exonic',
        'functional_annotation': 'missense_variant',
    }
    genes = [gene]
    
    ## WHEN parsing the gene predictions
    res = predictions(genes)
    ## THEN assert the result is not filled
    assert res == {
                   'sift_predictions': ['-'],
                   'polyphen_predictions': ['probably_damaging'],
                   'region_annotations': ['exonic'],
                   'functional_annotations': ['missense_variant']
               }

def test_gene_predictions_two_genes():
    ## GIVEN a empty list of genes
    gene = {
        'hgnc_symbol': 'AAA',
        'sift_prediction': 'deleterious',
        'polyphen_prediction': 'probably_damaging',
        'region_annotation': 'exonic',
        'functional_annotation': 'missense_variant',
    }
    gene2 = {
        'hgnc_symbol': 'BBB',
        'sift_prediction': 'tolerated',
        'polyphen_prediction': 'unknown',
        'region_annotation': 'exonic',
        'functional_annotation': 'synonymous_variant',
    }
    genes = [gene, gene2]
    
    ## WHEN parsing the gene predictions
    res = predictions(genes)
    ## THEN assert the result is not filled
    assert set(res['sift_predictions']) == set(['AAA:deleterious', 'BBB:tolerated'])

def test_sv_frequencies_empty():
    ## GIVEN a variant object with gnomad annotation
    var = {}
    ## WHEN parsing the sv frequencies
    freq = sv_frequencies(var)
    ## THEN assert the correct tuple is returned
    assert len(freq) == 1
    assert freq[0] == ('GnomAD', var.get('gnomad_frequency'))

def test_sv_frequencies_gnomad():
    ## GIVEN a variant object with gnomad annotation
    var = {'gnomad_frequency': 0.01}
    ## WHEN parsing the sv frequencies
    freq = sv_frequencies(var)
    ## THEN assert the correct tuple is returned
    assert len(freq) == 1
    assert freq[0] == ('GnomAD', var.get('gnomad_frequency'))


def test_sv_frequencies_all():
    ## GIVEN a variant object with gnomad annotation
    var = {
            'gnomad_frequency': 0.02,
            'clingen_cgh_benign': 0.02,
            'clingen_cgh_pathogenic': 0.02,
            'clingen_ngi': 0.02,
            'clingen_mip': 0.02,
            'swegen': 0.02,
            'decipher': 0.02,
        }
    ## WHEN parsing the sv frequencies
    freq = sv_frequencies(var)
    ## THEN assert the correct tuple is returned
    assert len(freq) == 7
    for annotation in freq:
        assert annotation[1] == 0.02
