import logging

from scout.models import Individual

logger = logging.getLogger(__name__)

def build_individual(ind):
    """Build a mongoengine Individual object
    
        Args:
            ind(dict): A dictionary with individual information
    
        Returns:
            ind_obj(Individual): A mongoengine Individual object
    """
    logger.info("Building Individual with id:{0}".format(ind['individual_id']))
    
    ind_obj = Individual(
        individual_id=ind['individual_id']
    )
    ind_obj.display_name = ind.get('display_name')
    ind_obj.sex = ind.get('sex')
    ind_obj.phenotype = ind.get('phenotype')
    ind_obj.father = ind.get('father')
    ind_obj.mother = ind.get('mother')
    ind_obj.capture_kits = ind.get('capture_kits',[])
    ind_obj.bam_file = ind.get('bam_file')
    
    return ind_obj
