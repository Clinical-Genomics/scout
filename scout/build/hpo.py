from scout.models import (HpoTerm, DiseaseTerm)

def build_hpo_term(hpo_info):
    """Build a hpo_term  object
    
        Args:
            hpo_info(dict)
    
        Returns:
            hpo_obj(dict)
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
    )

    return disease_obj