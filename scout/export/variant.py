from pprint import pprint as pp

from scout.constants import (CHROMOSOMES, CHROMOSOME_INTEGERS)

def export_causatives(adapter, collaborator):
    """Export causative variants for a collaborator
    
    Args:
        adapter(MongoAdapter)
        collaborator(str)
    
    Yields:
        variant_obj(str): 
    """
    #put variants in a dict to get unique ones
    variant_string = ("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}")
    
    # Store the variants in a list for sorting
    variants = []
    
    for document_id in adapter.get_causatives(institute_id=collaborator):
        variant_obj = adapter.variant(document_id)
        
        chrom = variant_obj['chromosome']
        # Convert chromosome to integer for sorting
        chrom_int = CHROMOSOME_INTEGERS.get(chrom)
        if not chrom_int:
            LOG.info("Unknown chromosome %s", chrom)
            continue
        
        variants.append((chrom_int, variant_obj['position'], variant_obj))
    
    variants.sort(key=lambda x: (x[0], x[1]))
    for variant in variants:
        variant_obj = variant[2]
        yield variant_string.format(
                        variant_obj['chromosome'],
                        variant_obj['position'],
                        variant_obj['dbsnp_id'],
                        variant_obj['reference'],
                        variant_obj['alternative'],
                        variant_obj['quality'],
                        ';'.join(variant_obj['filters']),
                        '.'
                        )
    