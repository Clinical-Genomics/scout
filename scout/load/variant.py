import logging

from scout.parse import parse_variant
from scout.build import build_variant

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

def load_variants(adapter, variants, case, variant_type='clinical'):
    """Load all variantt in variants
    
        Args:
            adapter(MongoAdapter)
            variants(Iterable(dict))
            case(Case)
            variant_type(str)
    
    """
    for variant in variants:
        load_variant(
            adapter=adapter,
            variant=variant,
            case=case,
            variant_type=variant_type
        )

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
        logger.warning("Institute does not exist.")
        raise SyntaxError()
    
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