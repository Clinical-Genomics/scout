import logging
from datetime import datetime

from vcf_parser import VCFParser

from scout.ext.backend.utils import get_mongo_case
from scout.ext.backend.utils import get_mongo_variant

logger = logging.getLogger(__name__)

def load_variants(adapter, vcf_file, variant_type, case_lines, owner, 
                  case_type='mip', rank_score_threshold=0, scout_configs={}):
    """Load a case together with it's variants into the database
    
        Args:
            adapter(MongoAdapter)
            vcf_file(str): Path to a vcf file
            variant_type(str): 'clinical' or research
            case_lines(Iterable): ped like strings
            owner(str): The owner of the variants
            case_type(str): The format of the variants
            rank_score_threshold(int)
            scout_configs(dict): A dictionary with configs
    """

    # Make sure that the current institute exists
    if not adapter.institute(institute_id=owner):
        logger.warning("Institute {0} does not exist in database".format(
            owner))
        logger.info("Creating new institute")
        adapter.add_institute(internal_id=owner, display_name=owner)

    case_obj = get_mongo_case(
        case_lines = case_lines,
        owner=owner,
        case_type=case_type,
        collaborators=scout_configs.get('collaborators') or set(),
        analysis_type=scout_configs.get('analysis_type', 'unknown').lower(),
        scout_configs=scout_configs,
    )

    adapter.add_case(case_obj)

    case_id = case_obj.case_id

    logger.info("Setting up a variant parser")
    variant_parser = VCFParser(infile=vcf_file)
    nr_of_variants = 0
    variants_inserted = 0
    
    #Delete all old variants
    adapter.delete_variants(case_id, variant_type)
    #Fetch the institute
    institute = adapter.institute(institute_id=case_obj.owner)
    start_inserting_variants = datetime.now()

    # Check which individuals that exists in the vcf file.
    # Save the individuals in a dictionary with individual ids as keys
    # and display names as values
    individuals = {}
    # loop over keys (internal ids)
    logger.info("Checking which individuals in ped file exists in vcf")
    for ind in case_obj.individuals:
        ind_id = ind.individual_id
        display_name = ind.display_name
        logger.debug("Checking individual {0}".format(ind_id))
        if ind_id in variant_parser.individuals:
            logger.debug("Individual {0} found".format(ind_id))
            individuals[ind_id] = display_name
        else:
            logger.warning("Individual {0} is present in ped file but"\
                            " not in vcf".format(ind_id))

    logger.info('Start parsing variants')

    # If a rank score threshold is used, check if below that threshold
    for variant in variant_parser:
        logger.debug("Parsing variant %s" % variant['variant_id'])
        nr_of_variants += 1

        if float(variant['rank_scores'][case.display_name]) > rank_score_threshold:
            variants_inserted += 1
            mongo_variant = get_mongo_variant(
                variant=variant,
                variant_type=variant_type,
                individuals=individuals,
                case=case_obj,
                institute=institute,
            )
            adapter.add_snv(mongo_variant)
        
        if nr_of_variants % 10000 == 0:
            logger.info('{0} variants parsed'.format(nr_of_variants))
    
    logger.info("Parsing variants done")
    logger.info("{0} variants parsed".format(nr_of_variants))
    logger.info("{0} variants inserted".format(variants_inserted))
    logger.info("Time to insert variants: {0}".format(
                datetime.now() - start_inserting_variants))
    
def load_svs(adapter, sv_file, variant_type, case_lines, owner, case_type='mip'):
    """Load structural variants into the database"""
    pass