

def export_causatives(adapter, collaborator):
    """docstring for export_causatives"""
    #put variants in a dict to get unique ones
    variants = {}
    
    for variant in adapter.get_causatives(institute_id=collaborator):
        variant_id = '_'.join(variant.variant_id.split('_')[:-1])
        variants[variant_id] = variant
    
    variant_string = ("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}")
    
    for variant_id in variants:
        variant = variants[variant_id]
        yield variant_string.format(
            variant.chromosome,
            str(variant.position),
            ';'.join(variant.db_snp_ids),
            variant.reference,
            variant.alternative,
            str(variant.quality),
            ';'.join(variant.filters),
            '.',
            )
    