from pprint import pprint as pp


def export_causatives(adapter, collaborator):
    """Export causative variants
    
    Args:
        adapter(MongoAdapter)
        collaborator(str)
    """
    #put variants in a dict to get unique ones
    variant_string = ("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}")
    
    for document_id in adapter.get_causatives(institute_id=collaborator):
        variant_obj = adapter.variant(document_id)
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
    