import logging

LOG = logging.getLogger(__name__)

def frequency(variant_obj):
    """Returns a judgement on the overall frequency of the variant.

    Combines multiple metrics into a single call.
    
    Args:
        variant_obj(scout.models.Variant)
    
    Returns:
        str in ['common','uncommon','rare']
    """
    most_common_frequency = max(variant_obj.get('thousand_genomes_frequency') or 0,
                                variant_obj.get('exac_frequency') or 0,
                                variant_obj.get('gnomad_frequency') or 0
                                )

    if most_common_frequency > .05:
        return 'common'
    if most_common_frequency > .01:
        return 'uncommon'
    
    return 'rare'


def end_position(variant_obj):
    """Calculate end position for a variant.
    
    Args:
        variant_obj(scout.models.Variant)
    
    Returns:
        end_position(int)
    """
    alt_bases = len(variant_obj['alternative'])
    num_bases = max(len(variant_obj['reference']), alt_bases)
    return variant_obj['position'] + (num_bases - 1)

def default_panels(store, case_obj):
    """Return the panels that are decided to be default for a case.
    
    Check what panels that are default, fetch those and add them to a list.
    
    Args:
        store(scout.adapter.MongoAdapter)
        case_obj(scout.models.Case)
    
    Returns:
        default_panels(list(dict))
        
    """
    default_panels = []
    # Add default panel information to variant
    for panel in case_obj.get('panels',[]):
        if not panel.get('is_default'):
            continue
        panel_obj = store.gene_panel(panel['panel_name'], panel.get('version'))
        if not panel_obj:
            LOG.warning("Panel {0} version {1} could not be found".format(
                panel['panel_name'], panel.get('version')))
            continue
        default_panels.append(panel_obj)
    return default_panels

def update_hgncsymbol(variant_obj):
    """Check if the HGNC symbols have changed since the variant was loaded"""
    pass