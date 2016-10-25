from scout.models import (HpoTerm, DiseaseTerm)

def build_hpo_term(adapter, hpo_info):
    """Build a mongoengine HpoTerm object
    
        Args:
            hpo_info(dict)
    
        Returns:
            hpo_obj(HpoTerm)
    """
    hpo_obj = HpoTerm(
        hpo_id = hpo_info['hpo_id'],
        description = hpo_info['description']
        )
    
    # List with HgncGene objects
    hgnc_genes = []
    for hgnc_symbol in hpo_info['hgnc_symbols']:
        gene_obj = adapter.hgnc_gene(hgnc_symbol)
        if gene_obj:
            hgnc_genes.append(gene_obj)
    
    hpo_obj.genes = hgnc_genes
    
    return hpo_obj

def build_disease_term(adapter, disease_info):
    """docstring for build_disease_term"""
    disease_obj = DiseaseTerm(
        disease_id = disease_info['mim_nr']
    )

    # List with HgncGene objects
    hgnc_genes = []
    for hgnc_symbol in disease_info.get('hgnc_symbols', []):
        gene_obj = adapter.hgnc_gene(hgnc_symbol)
        if gene_obj:
            hgnc_genes.append(gene_obj)
    
    disease_obj.genes = hgnc_genes
    
    hpo_terms = []
    for hpo_id in disease_info.get('hpo_terms', []):
        hpo_obj = adapter.hpo_term(hpo_id)
        if hpo_obj:
            hpo_terms.append(hpo_obj)
    
    disease_obj.hpo_terms = hpo_terms
    
    return disease_obj