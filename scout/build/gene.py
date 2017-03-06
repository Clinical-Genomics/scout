import logging

from . import (build_transcript)

from scout.constants import (CONSEQUENCE, FEATURE_TYPES, SO_TERM_KEYS)

log = logging.getLogger(__name__)

def build_gene(gene):
    """Build a gene object
        
        Has to build the transcripts for the genes to
    
    Args:
        gene(dict)

    Returns:
        gene_obj(dict)
    
    gene = dict(
        # The hgnc gene id
        hgnc_id = int, # required
        # A list of Transcript objects
        transcripts = list, # list of <transcript>
        # This is the worst functional impact of all transcripts
        functional_annotation = str, # choices=SO_TERM_KEYS
        # This is the region of the most severe functional impact
        region_annotation = str, # choices=FEATURE_TYPES
        # This is most severe sift prediction of all transcripts
        sift_prediction = str, # choices=CONSEQUENCE
        # This is most severe polyphen prediction of all transcripts
        polyphen_prediction = str, # choices=CONSEQUENCE
    )
    
    """
    gene_obj = dict()

    gene_obj['hgnc_id'] = int(gene['hgnc_id'])

    transcripts = []
    for transcript in gene['transcripts']:
        transcript_obj = build_transcript(transcript)
        transcripts.append(transcript_obj)
    gene_obj['transcripts'] = transcripts

    functional_annotation = gene['most_severe_consequence']
    if not functional_annotation in SO_TERM_KEYS:
        log.warning("Invalid functional annotation %s", functional_annotation)
    else:
        gene_obj['functional_annotation'] = functional_annotation
    
    region_annotation = gene['region_annotation']
    if not region_annotation in FEATURE_TYPES:
        log.warning("Invalid region annotation %s", region_annotation)
    else:
        gene_obj['region_annotation'] = region_annotation
 
    sift_prediction = gene['most_severe_sift']
    if not sift_prediction in CONSEQUENCE:
        log.warning("Invalid sift prediction %s", sift_prediction)
    else:
        gene_obj['sift_prediction'] = sift_prediction

    polyphen_prediction = gene['most_severe_polyphen']
    if not polyphen_prediction in CONSEQUENCE:
        log.warning("Invalid polyphen prediction %s", polyphen_prediction)
    else:
        gene_obj['polyphen_prediction'] = polyphen_prediction
 
    return gene_obj