from scout.models import PhenotypeTerm

def build_phenotype(phenotype):
    """Build a mongoengine PhenotypeTerm object
    
        Args:
            phenotype(dict)
    
        Returns:
            phenotype_obj(PheotypeTerm)
    """
    phenotype_obj = PhenotypeTerm(
        phenotype_id = phenotype['phenotype_id'],
        disease_models = phenotype['disease_models']
    )
    
    return phenotype_obj
