from scout.models.variant.gene import Gene

from . import (build_transcript)

def build_gene(gene):
    """Build a mongoengine Gene object
        
        Has to build the transcripts for the genes to
    
        Args:
            gene(dict)
    
        Returns:
            gene_obj(Gene)
    """
    gene_obj = Gene(
        hgnc_id = gene['hgnc_id']
    )

    transcripts = []
    for transcript in gene['transcripts']:
        transcript_obj = build_transcript(transcript)
        transcripts.append(transcript_obj)
    gene_obj.transcripts = transcripts

    gene_obj.functional_annotation = gene['most_severe_consequence']
    gene_obj.region_annotation = gene['region_annotation']
    gene_obj.sift_prediction = gene['most_severe_sift']
    gene_obj.polyphen_prediction = gene['most_severe_polyphen']

    return gene_obj