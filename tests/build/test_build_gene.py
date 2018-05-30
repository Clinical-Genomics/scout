"""tests/build/test_build_gene.py

Tests for genes that are built on the variants

"""

from scout.build.variant.gene import build_gene

def test_build_gene():
    ## GIVEN information about a gene and a transcripts
    
    ## WHEN adding gene and transcript information and building variant
    transcript_info = {
        'functional_annotations': ['transcript_ablation'],
        'transcript_id': 'ENST00000249504',
        'hgnc_id': 5134,
        'sift_prediction': 'deleterious'
    }
    gene_info = {
        'transcripts': [transcript_info],
        'most_severe_transcript': transcript_info,
        'most_severe_consequence': 'transcript_ablation',
        'most_severe_sift': 'deleterious',
        'most_severe_polyphen': None,
        'hgnc_id': 5134,
        'region_annotation': 'exonic',
    }
    
    gene_obj = build_gene(gene_info)
    
    assert gene_obj['hgnc_id'] == gene_info['hgnc_id']
    assert 'hgnc_symbol' not in gene_obj

def test_build_gene_hgnc_info():
    ## GIVEN information about a gene and some hgnc information
    
    ## WHEN adding gene and transcript information and building variant
    transcript_info = {
        'functional_annotations': ['transcript_ablation'],
        'transcript_id': 'ENST00000249504',
        'hgnc_id': 5134,
        'sift_prediction': 'deleterious'
    }
    gene_info = {
        'transcripts': [transcript_info],
        'most_severe_transcript': transcript_info,
        'most_severe_consequence': 'transcript_ablation',
        'most_severe_sift': 'deleterious',
        'most_severe_polyphen': None,
        'hgnc_id': 5134,
        'region_annotation': 'exonic',
    }

    transcript_1 = {
            'ensembl_transcript_id': 'ENST00000498438',
            'is_primary': False,
            'start': 176968944,
            'end': 176974482
        }

    transcript_2 = {
            'ensembl_transcript_id': 'ENST00000249504',
            'is_primary': True,
            'refseq_id': 'NM_021192',
            'start': 176972014,
            'end': 176974722,
        }

    hgnc_transcripts = [
        transcript_1,
        transcript_2
    ]
    
    hgnc_gene = {
        'hgnc_id': 5134,
        'hgnc_symbol': 'HOXD11',
        'ensembl_id': 'ENSG00000128713',
        'chromosome': '2',
        'start': 176968944,
        'end': 176974722,
        'build': 37,
        'description': 'homeobox D11',
        'aliases': ['HOX4', 'HOXD11', 'HOX4F'],
        'entrez_id': 3237,
        'omim_ids': 142986,
        'pli_score': 0.0131898476206074,
        'primary_transcripts': ['NM_021192'],
        'ucsc_id': 'uc010fqx.4',
        'uniprot_ids': ['P31277'],
        'vega_id': 'OTTHUMG00000132510',
        'transcripts': hgnc_transcripts,
        'incomplete_penetrance': False,
        'ad': True,
        'ar': False,
        'xd': False,
        'xr': False,
        'x': False,
        'y': False,
        'transcripts_dict': {
            'ENST00000498438': transcript_1,
            'ENST00000249504': transcript_2,
        }
    }
    
    hgncid_to_gene = {5134: hgnc_gene}
    
    gene_obj = build_gene(gene_info, hgncid_to_gene=hgncid_to_gene)
    
    assert gene_obj['hgnc_symbol'] == hgnc_gene['hgnc_symbol']
    assert gene_obj['inheritance'] == ['AD']
