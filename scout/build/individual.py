import logging

from scout.models import Individual
from scout.constants import REV_PHENOTYPE_MAP, REV_SEX_MAP

log = logging.getLogger(__name__)


def build_individual(ind):
    """Build a mongoengine Individual object

        Args:
            ind (dict): A dictionary with individual information

        Returns:
            ind_obj (Individual): A mongoengine Individual object
    """
    log.info("Building Individual with id:{0}".format(ind['individual_id']))

    ind_obj = Individual(
        individual_id=ind['individual_id']
    )
    ind_obj.display_name = ind['display_name']
    ind_obj.sex = str(REV_SEX_MAP[ind['sex']])
    ind_obj.phenotype = REV_PHENOTYPE_MAP[ind['phenotype']]
    ind_obj.father = ind.get('father')
    ind_obj.mother = ind.get('mother')
    ind_obj.capture_kits = ind.get('capture_kits', [])
    ind_obj.bam_file = ind.get('bam_file')
    ind_obj.analysis_type = ind.get('analysis_type')
    
    return ind_obj
