from scout.models import (HpoTerm, DiseaseTerm)

def build_hpo_term(hpo_info):
    """Build a mongoengine HpoTerm object
    
        Args:
            hpo_info(dict)
    
        Returns:
            hpo_obj(HpoTerm)
    """
    hpo_obj = HpoTerm(
        hpo_id = hpo_info['hpo_id'],
        description = hpo_info['description'],
    )
    
    return hpo_obj

def build_disease_term(disease_info):
    """docstring for build_disease_term"""
    disease_obj = DiseaseTerm(
        disease_id = disease_info['disease_nr'],
        source = disease_info['source'],
        hpo_terms = list(disease_info['hpo_terms'])
    )

    return disease_obj