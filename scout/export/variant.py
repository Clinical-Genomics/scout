from pprint import pprint as pp

from scout.constants import (CHROMOSOMES, CHROMOSOME_INTEGERS)

def export_variants(adapter, collaborator, document_id=None):
    """Export causative variants for a collaborator
    
    Args:
        adapter(MongoAdapter)
        collaborator(str)
        document_id(str): Search for a specific variant
    
    Yields:
        variant_obj(scout.Models.Variant): Variants marked as causative ordered by position. 
    """
    
    # Store the variants in a list for sorting
    variants = []
    if document_id:
        yield adapter.variant(document_id)
        return
    
    ##TODO add check so that same variant is not included more than once
    for document_id in adapter.get_causatives(institute_id=collaborator):
        variant_obj = adapter.variant(document_id)
        
        chrom = variant_obj['chromosome']
        # Convert chromosome to integer for sorting
        chrom_int = CHROMOSOME_INTEGERS.get(chrom)
        if not chrom_int:
            LOG.info("Unknown chromosome %s", chrom)
            continue
        
        # Add chromosome and position to prepare for sorting
        variants.append((chrom_int, variant_obj['position'], variant_obj))
    
    # Sort varants based on position
    variants.sort(key=lambda x: (x[0], x[1]))
    
    for variant in variants:
        variant_obj = variant[2]
        yield variant_obj
    