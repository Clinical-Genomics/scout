import logging
from pprint import pprint as pp
from vcf_parser import VCFParser

from scout.parse import parse_variant
from scout.build import build_variant
from scout.exceptions import IntegrityError

logger = logging.getLogger(__name__)

def delete_variants(adapter, case_obj, variant_type='clinical'):
    """Delete all variants for a case of a certain variant type
    
        Args:
            case_obj(Case)
            variant_type(str)
    """
    adapter.delete_variants(
        case_id=case_obj['case_id'], 
        variant_type=variant_type
    )

def load_variants(adapter, variant_file, case_obj, variant_type='clinical'):
    """Load all variantt in variants
    
        Args:
            adapter(MongoAdapter)
            variant_file(str): Path to variant file
            case(Case)
            variant_type(str)
    
    """
    variants = VCFParser(infile=variant_file)
    
    try:
        for variant in variants:
            load_variant(
                adapter=adapter,
                variant=variant,
                case_obj=case_obj,
                variant_type=variant_type
            )
    except Exception as e:
        logger.error(e.message)
        logger.info("Deleting inserted variants")
        delete_variants(adapter, case_obj, variant_type)

def load_variant(adapter, variant, case_obj, variant_type='clinical'):
    """Load a variant into the database
    
        Parse the variant, create a mongoengine object and load it into 
        the database.
    
        Args:
            adapter(MongoAdapter)
            variant(vcf_parser.Variant)
            case_obj(Case)
            variant_type(str)
        
        Returns:
            variant_obj(Variant): mongoengine Variant object
    """
    institute_obj = adapter.institute(institute_id=case_obj['owner'])
    
    if not institute_obj:
        raise IntegrityError("Institute {0} does not exist in"\
                             " database.".format(case_obj['owner']))
    
    parsed_variant = parse_variant(
        variant_dict=variant, 
        case=case_obj, 
        variant_type=variant_type
    )
    
    variant_obj = build_variant(
        variant=parsed_variant, 
        institute=institute_obj
    )
    
    adapter.load_variant(variant_obj)
    
    return variant_obj