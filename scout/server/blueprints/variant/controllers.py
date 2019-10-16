from scout.server.utils import (institute_and_case, variant_case)

def sv_variant(store, institute_id, case_name, variant_id=None, variant_obj=None, add_case=True,
               get_overlapping=True):
    """Pre-process an SV variant entry for detail page.

    Adds information to display variant

    Args:
        store(scout.adapter.MongoAdapter)
        institute_id(str)
        case_name(str)
        variant_id(str)
        variant_obj(dcit)
        add_case(bool): If information about case files should be added

    Returns:
        detailed_information(dict): {
            'institute': <institute_obj>,
            'case': <case_obj>,
            'variant': <variant_obj>,
            'overlapping_snvs': <overlapping_snvs>,
            'manual_rank_options': MANUAL_RANK_OPTIONS,
            'dismiss_variant_options': DISMISS_VARIANT_OPTIONS
        }
    """
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)

    if not variant_obj:
        variant_obj = store.variant(variant_id)

    if add_case:
        # fill in information for pilup view
        variant_case(store, case_obj, variant_obj)

    # frequencies
    variant_obj['frequencies'] = [
        ('1000G', variant_obj.get('thousand_genomes_frequency')),
        ('1000G (left)', variant_obj.get('thousand_genomes_frequency_left')),
        ('1000G (right)', variant_obj.get('thousand_genomes_frequency_right')),
        ('GnomAD', variant_obj.get('gnomad_frequency')),
    ]

    if 'clingen_cgh_benign' in variant_obj:
        variant_obj['frequencies'].append(('ClinGen CGH (benign)', variant_obj['clingen_cgh_benign']))
    if 'clingen_cgh_pathogenic' in variant_obj:
        variant_obj['frequencies'].append(('ClinGen CGH (pathogenic)', variant_obj['clingen_cgh_pathogenic']))
    if 'clingen_ngi' in variant_obj:
        variant_obj['frequencies'].append(('ClinGen NGI', variant_obj['clingen_ngi']))
    if 'clingen_mip' in variant_obj:
        variant_obj['frequencies'].append(('ClinGen MIP', variant_obj['clingen_mip']))
    if 'swegen' in variant_obj:
        variant_obj['frequencies'].append(('SweGen', variant_obj['swegen']))
    if 'decipher' in variant_obj:
        variant_obj['frequencies'].append(('Decipher', variant_obj['decipher']))

    variant_obj['callers'] = callers(variant_obj, category='sv')

    overlapping_snvs = []
    if get_overlapping:
        overlapping_snvs = (parse_variant(store, institute_obj, case_obj, variant) for variant in
                            store.overlapping(variant_obj))

    # parse_gene function is not called for SVs, but a link to ensembl gene is required
    for gene_obj in variant_obj.get('genes', []):
        if gene_obj.get('common'):
            ensembl_id = gene_obj['common']['ensembl_id']
            try:
                build = int(gene_obj['common'].get('build','37'))
            except Exception:
                build = 37
            gene_obj['ensembl_link'] = ensembl(ensembl_id, build=build)

    variant_obj['comments'] = store.events(institute_obj, case=case_obj,
                                           variant_id=variant_obj['variant_id'], comments=True)

    case_clinvars = store.case_to_clinVars(case_obj.get('display_name'))
    if variant_id in case_clinvars:
        variant_obj['clinvar_clinsig'] = case_clinvars.get(variant_id)['clinsig']

    if not 'end_chrom' in variant_obj:
        variant_obj['end_chrom'] = variant_obj['chromosome']

    return {
        'institute': institute_obj,
        'case': case_obj,
        'variant': variant_obj,
        'overlapping_snvs': overlapping_snvs,
        'manual_rank_options': MANUAL_RANK_OPTIONS,
        'dismiss_variant_options': DISMISS_VARIANT_OPTIONS
    }