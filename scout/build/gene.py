from scout.models import Gene

from . import (build_transcript, build_phenotype)

def build_gene(gene):
    """Build a mongoengine Gene object
        
        Has to build the transcripts for the genes to
    
        Args:
            gene(dict)
    
        Returns:
            gene_obj(Gene)
    """
    gene_obj = Gene(
        hgnc_symbol = gene['hgnc_symbol']
    )
    gene_obj.ensembl_gene_id = gene['ensembl_gene_id']
    
    transcripts = []
    for transcript in gene['transcripts']:
        transcript_obj = build_transcript(transcript)
        transcripts.append(transcript_obj)
    gene_obj.transcripts = transcripts
    
    gene_obj.functional_annotation = gene['most_severe_consequence']
    gene_obj.region_annotation = gene['region_annotation']
    gene_obj.sift_prediction = gene['most_severe_sift']
    gene_obj.polyphen_prediction = gene['most_severe_polyphen']
    
    gene_obj.omim_gene_entry = gene['omim_gene_id']
    
    phenotypes = []
    if gene['phenotype_terms']:
        for phenotype in gene['phenotype_terms']:
            phenotype_obj = build_phenotype(phenotype)
            phenotypes.append(phenotype_obj)
    gene_obj.omim_phenotypes = phenotypes
    
    gene_obj.description = gene['description']
    
    gene_obj.reduced_penetrance = gene['reduced_penetrance']
    
    if gene['disease_associated']:
        gene_obj.disease_associated_transcripts = gene['disease_associated']
    
    return gene_obj