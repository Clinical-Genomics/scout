import logging

from scout.constants import (REV_PHENOTYPE_MAP, REV_SEX_MAP, ANALYSIS_TYPES)
from scout.exceptions import PedigreeError

log = logging.getLogger(__name__)


def build_individual(ind):
    """Build a mongoengine Individual object

        Args:
            ind (dict): A dictionary with individual information

        Returns:
            ind_obj (dict): A Individual object
    
        dict(
            individual_id = str, # required
            display_name = str,
            sex = str, 
            phenotype = int, 
            father = str, # Individual id of father
            mother = str, # Individual id of mother
            capture_kits = list, # List of names of capture kits
            bam_file = str, # Path to bam file
            analysis_type = str, # choices=ANALYSIS_TYPES
        )
        
    """

    try:
        ind_obj = dict(
            individual_id=ind['individual_id']
        )
        log.info("Building Individual with id:{0}".format(ind['individual_id']))
    except KeyError as err:
        raise PedigreeError("Individual is missing individual_id")
        
    ind_obj['display_name'] = ind.get('display_name', ind_obj['individual_id'])
    
    sex = ind.get('sex', 'unknown')
    # Convert sex to .ped
    try:
        ind_obj['sex'] = str(REV_SEX_MAP[sex])
    except KeyError as err:
        raise(PedigreeError("Unknown sex: %s" % sex))

    phenotype = ind.get('phenotype', 'unknown')
    # Make the phenotype integers
    try:
        ped_phenotype = REV_PHENOTYPE_MAP[phenotype]
        if ped_phenotype == -9:
            ped_phenotype = 0
        ind_obj['phenotype'] = ped_phenotype 
    except KeyError as err:
        raise(PedigreeError("Unknown phenotype: %s" % phenotype))
    
    ind_obj['father'] = ind.get('father')
    ind_obj['mother'] = ind.get('mother')
    ind_obj['capture_kits'] = ind.get('capture_kits', [])
    ind_obj['bam_file'] = ind.get('bam_file')
    
    # Check if the analysis type is ok
    # Can be anyone of ('wgs', 'wes', 'mixed', 'unknown')
    analysis_type = ind.get('analysis_type', 'unknown')
    if not analysis_type in ANALYSIS_TYPES:
        raise PedigreeError("Analysis type %s not allowed", analysis_type)
    ind_obj['analysis_type'] = analysis_type
    
    return ind_obj
