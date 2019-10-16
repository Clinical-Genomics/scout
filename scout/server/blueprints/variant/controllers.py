from scout.server.utils import (institute_and_case, variant_case)
from scout.constants import (CALLERS, MANUAL_RANK_OPTIONS, DISMISS_VARIANT_OPTIONS)

from scout.server.links import (ensembl)

# def variant(store, institute_obj, case_obj, variant_id=None, variant_obj=None, add_case=True,
#             add_other=True, get_overlapping=True):
#     """Pre-process a single variant for the detailed variant view.
#
#     Adds information from case and institute that is not present on the variant
#     object
#
#     Args:
#         store(scout.adapter.MongoAdapter)
#         institute_obj(scout.models.Institute)
#         case_obj(scout.models.Case)
#         variant_id(str)
#         variant_obj(dict)
#         add_case(bool): If info about files case should be added
#         add_other(bool): If information about other causatives should be added
#         get_overlapping(bool): If overlapping svs should be collected
#
#     Returns:
#         variant_info(dict): {
#             'variant': <variant_obj>,
#             'causatives': <list(other_causatives)>,
#             'events': <list(events)>,
#             'overlapping_svs': <list(overlapping svs)>,
#             'manual_rank_options': MANUAL_RANK_OPTIONS,
#             'dismiss_variant_options': DISMISS_VARIANT_OPTIONS,
#             'ACMG_OPTIONS': ACMG_OPTIONS,
#             'evaluations': <list(evaluations)>,
#         }
#
#     """
#     # If the variant is already collected we skip this part
#     if not variant_obj:
#         default_panels = []
#         # Add default panel information to variant
#         for panel in case_obj['panels']:
#             if not panel.get('is_default'):
#                 continue
#             panel_obj = store.gene_panel(panel['panel_name'], panel.get('version'))
#             if not panel:
#                 LOG.warning("Panel {0} version {1} could not be found".format(
#                     panel['panel_name'], panel.get('version')))
#                 continue
#             default_panels.append(panel_obj)
#
#         # NOTE this will query with variant_id == document_id, not the variant_id.
#         variant_obj = store.variant(variant_id, gene_panels=default_panels)
#
#     genome_build = case_obj.get('genome_build', '37')
#     if genome_build not in ['37','38']:
#         genome_build = '37'
#
#     if variant_obj is None:
#         return None
#     # Add information to case_obj
#     if add_case:
#         variant_case(store, case_obj, variant_obj)
#
#     # Collect all the events for the variant
#     events = list(store.events(institute_obj, case=case_obj, variant_id=variant_obj['variant_id']))
#     for event in events:
#         event['verb'] = VERBS_MAP[event['verb']]
#
#     other_causatives = set()
#     # Adds information about other causative variants
#     if add_other:
#         for other_causative in store.other_causatives(case_obj, variant_obj):
#             # avoid adding other causatives duplicates
#             other_causatives.add(tuple(other_causative.items()))
#         # convert set of tuples into list of dictionaries
#         other_causatives = [ dict(item) for item in list(other_causatives)]
#
#     variant_obj = parse_variant(store, institute_obj, case_obj, variant_obj, genome_build=genome_build)
#
#     variant_obj['end_position'] = end_position(variant_obj)
#     variant_obj['frequency'] = frequency(variant_obj)
#     variant_obj['clinsig_human'] = (clinsig_human(variant_obj) if variant_obj.get('clnsig')
#                                     else None)
#     variant_obj['thousandg_link'] = thousandg_link(variant_obj, genome_build)
#     variant_obj['exac_link'] = exac_link(variant_obj)
#     variant_obj['gnomad_link'] = gnomad_link(variant_obj)
#     variant_obj['swegen_link'] = swegen_link(variant_obj)
#     variant_obj['cosmic_link'] = cosmic_link(variant_obj)
#     variant_obj['beacon_link'] = beacon_link(variant_obj, genome_build)
#     variant_obj['ucsc_link'] = ucsc_link(variant_obj, genome_build)
#     variant_obj['alamut_link'] = alamut_link(variant_obj)
#     variant_obj['spidex_human'] = spidex_human(variant_obj)
#     variant_obj['expected_inheritance'] = expected_inheritance(variant_obj)
#     variant_obj['callers'] = callers(variant_obj, category='snv')
#
#     individuals = {individual['individual_id']: individual for individual in
#                    case_obj['individuals']}
#     for sample_obj in variant_obj['samples']:
#         individual = individuals[sample_obj.get('sample_id')]
#         if not individual:
#             return None
#         sample_obj['is_affected'] = True if individual['phenotype'] == 2 else False
#
#     gene_models = set()
#     variant_obj['disease_associated_transcripts'] = []
#
#     # Parse the gene models, both from panels and genes
#     for gene_obj in variant_obj.get('genes', []):
#         # Adds gene level links
#         parse_gene(gene_obj, genome_build)
#         omim_models = set()
#         for disease_term in gene_obj.get('disease_terms', []):
#             omim_models.update(disease_term.get('inheritance', []))
#         gene_obj['omim_inheritance'] = list(omim_models)
#
#         # Build strings for the disease associated transcripts from gene panel
#         for refseq_id in gene_obj.get('disease_associated_transcripts', []):
#             hgnc_symbol = (gene_obj['common']['hgnc_symbol'] if gene_obj.get('common') else
#                            gene_obj['hgnc_id'])
#             transcript_str = "{}:{}".format(hgnc_symbol, refseq_id)
#             variant_obj['disease_associated_transcripts'].append(transcript_str)
#
#         gene_models = gene_models | omim_models
#
#     if variant_obj.get('genetic_models'):
#         variant_models = set(model.split('_', 1)[0] for model in variant_obj['genetic_models'])
#         variant_obj['is_matching_inheritance'] = variant_models & gene_models
#
#     evaluations = []
#     for evaluation_obj in store.get_evaluations(variant_obj):
#         evaluation(store, evaluation_obj)
#         evaluations.append(evaluation_obj)
#
#     case_clinvars = store.case_to_clinVars(case_obj.get('display_name'))
#
#     if variant_id in case_clinvars:
#         variant_obj['clinvar_clinsig'] = case_clinvars.get(variant_id)['clinsig']
#
#     svs = []
#     if get_overlapping:
#         svs = (parse_variant(store, institute_obj, case_obj, variant_obj) for
#                             variant_obj in store.overlapping(variant_obj))
#
#     return {
#         'variant': variant_obj,
#         'causatives': other_causatives,
#         'events': events,
#         'overlapping_svs': svs,
#         'manual_rank_options': MANUAL_RANK_OPTIONS,
#         'dismiss_variant_options': DISMISS_VARIANT_OPTIONS,
#         'mosaic_variant_options': MOSAICISM_OPTIONS,
#         'ACMG_OPTIONS': ACMG_OPTIONS,
#         'evaluations': evaluations,
#     }


def sv_variant(store, institute_id, case_name, variant_id=None, variant_obj=None, add_case=True,
               get_overlapping=True):
    """Pre-process an SV variant entry for detail page.

    Adds information to display variant.
    Since information from the views comes from urls we need to fetch the actual objects from the 
    database. That includes institute, case and the variant itself

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
    variant_obj['frequencies'] = frequencies(variant_obj)
    variant_obj['callers'] = callers(variant_obj, category='sv')

    overlapping_snvs = []
    if get_overlapping:
        overlapping_snvs = [var.update(predictions(var.get('genes',[]))) for var in store.overlapping(variant_obj)]

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

    variant_obj['end_chrom'] = variant_obj.get('end_chrom', variant_obj['chromosome'])

    return {
        'institute': institute_obj,
        'case': case_obj,
        'variant': variant_obj,
        'overlapping_snvs': overlapping_snvs,
        'manual_rank_options': MANUAL_RANK_OPTIONS,
        'dismiss_variant_options': DISMISS_VARIANT_OPTIONS
    }

def predictions(genes):
    """Adds information from variant specific genes to display.
    
    Args:
        genes(list[dict])
    
    Returns:
        data(dict)
    """
    data = {
        'sift_predictions': [],
        'polyphen_predictions': [],
        'region_annotations': [],
        'functional_annotations': []
    }
    for gene_obj in genes:
        for pred_key in data:
            gene_key = pred_key[:-1]
            if len(genes) == 1:
                value = gene_obj.get(gene_key, '-')
            else:
                gene_id = gene_obj.get('hgnc_symbol') or str(gene_obj['hgnc_id'])
                value = ':'.join([gene_id, gene_obj.get(gene_key, '-')])
            data[pred_key].append(value)

    return data

def frequencies(variant_obj):
    """Add frequencies in the correct way for the template
    
    Args:
        variant_obj(scout.models.Variant)
    
    Returns:
        frequencies(list(tuple)): A list of frequencies to display
    """
    
    # Mandatory frequencies
    
    frequencies = [
        ('GnomAD', variant_obj.get('gnomad_frequency')),
    ]

    if 'clingen_cgh_benign' in variant_obj:
        frequencies.append(('ClinGen CGH (benign)', variant_obj['clingen_cgh_benign']))
    if 'clingen_cgh_pathogenic' in variant_obj:
        frequencies.append(('ClinGen CGH (pathogenic)', variant_obj['clingen_cgh_pathogenic']))
    if 'clingen_ngi' in variant_obj:
        frequencies.append(('ClinGen NGI', variant_obj['clingen_ngi']))
    if 'clingen_mip' in variant_obj:
        frequencies.append(('ClinGen MIP', variant_obj['clingen_mip']))
    if 'swegen' in variant_obj:
        frequencies.append(('SweGen', variant_obj['swegen']))
    if 'decipher' in variant_obj:
        frequencies.append(('Decipher', variant_obj['decipher']))
    
    return frequencies

def callers(variant_obj, category='snv'):
    """Return info about callers.
    
    Args:
        variant_obj(scout.models.Variant)
        category(str)
    
    Returns:
        calls(list(str)): A list of the callers that identified the variant
    """
    calls = set()
    for caller in CALLERS[category]:
        if variant_obj.get(caller['id']):
            calls.add((caller['name'], variant_obj[caller['id']]))

    return list(calls)

def str_variant(store, institute_id, case_name, variant_id):
    """Pre-process an STR variant entry for detail page.

    Adds information to display variant

    Args:
        store(scout.adapter.MongoAdapter)
        institute_id(str)
        case_name(str)
        variant_id(str)

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
    variant_obj =  store.variant(variant_id)

    # fill in information for pilup view
    variant_case(store, case_obj, variant_obj)

    variant_obj['callers'] = callers(variant_obj, category='str')

    # variant_obj['str_ru']
    # variant_obj['str_repid']
    # variant_obj['str_ref']

    variant_obj['comments'] = store.events(institute_obj, case=case_obj,
                                           variant_id=variant_obj['variant_id'], comments=True)

    return {
        'institute': institute_obj,
        'case': case_obj,
        'variant': variant_obj,
        'overlapping_snvs': overlapping_snvs,
        'manual_rank_options': MANUAL_RANK_OPTIONS,
        'dismiss_variant_options': DISMISS_VARIANT_OPTIONS
    }
