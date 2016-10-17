import logging
from codecs import open

from . import (load_case, load_variants, delete_variants)

logger = logging.getLogger(__name__)


def wipe_database():
    """docstring for wipe_database"""
    pass

def load_scout(adapter, case_file, snv_file, owner, sv_file=None, 
               case_type='mip', variant_type='clinical', update=False,
               scout_configs=None):
    """This function will load the database with a case and the variants
    
        Args:
            adapter(MongoAdapter)
            case_file(str): Path to ped like file
            snv_file(str): Path to a VCF with snvs
            owner(str): The institute that owns a case
            sv_file(str): Path to a VCF with SVs
            case_type(str): Format for case_file
            variant_type(str): 'clinical' or 'research'
            update(bool): Update case if it already exists
            scout_configs(dict): A dictionary with meta data
        
    """
    scout_configs = scout_configs or {}
    logger.info("Loading database")
    
    with open(case_file, 'r') as case_lines:
        case_obj = load_case(
            adapter=adapter, 
            case_lines=case_lines, 
            owner=owner, 
            case_type=case_type,
            analysis_type=scout_configs.get('analysis_type', 'unknown'), 
            scout_configs=scout_configs, 
            update=update
        )
    
    logger.info("Delete the variants for case {0}".format(case_obj.case_id))

    delete_variants(
        adapter=adapter, 
        case_obj=case_obj, 
        variant_type=variant_type
    )
    
    logger.info("Load the SNV variants for case {0}".format(case_obj.case_id))

    load_variants(
        adapter=adapter, 
        variant_file=snv_file, 
        case_obj=case_obj, 
        variant_type=variant_type,
        category='snv'
    )

    if sv_file:
        logger.info("Load the SV variants for case {0}".format(case_obj.case_id))
        load_variants(
            adapter=adapter, 
            variant_file=sv_file, 
            case_obj=case_obj, 
            variant_type=variant_type,
            category='sv'
        )

