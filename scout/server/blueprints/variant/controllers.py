import logging
from datetime import datetime

from flask_login import current_user

from scout.server.utils import (institute_and_case, variant_case, user_institutes)
from scout.constants import (CALLERS, MANUAL_RANK_OPTIONS, DISMISS_VARIANT_OPTIONS, VERBS_MAP, 
                             ACMG_MAP, MOSAICISM_OPTIONS, ACMG_OPTIONS, ACMG_COMPLETE_MAP)

from scout.server.links import (ensembl, add_variant_links)
from .utils import (end_position, default_panels, frequency, callers, evaluation, 
                    is_affected, predictions, sv_frequencies, add_gene_info, clinsig_human)

from scout.parse.variant.ids import parse_document_id

LOG = logging.getLogger(__name__)

def variant(store, institute_id, case_name, variant_id=None, variant_obj=None, add_case=True,
            add_other=True, get_overlapping=True, add_compounds=True, variant_type=None):
    """Pre-process a single variant for the detailed variant view.

    Adds information from case and institute that is not present on the variant
    object

    Args:
        store(scout.adapter.MongoAdapter)
        institute_obj(scout.models.Institute)
        case_obj(scout.models.Case)
        variant_id(str)
        variant_obj(dict)
        add_case(bool): If info about files case should be added
        add_other(bool): If information about other causatives should be added
        get_overlapping(bool): If overlapping variants should be collected
        variant_type(str): in ['snv', 'str', 'sv', 'cancer']

    Returns:
        variant_info(dict): {
            'variant': <variant_obj>,
            'causatives': <list(other_causatives)>,
            'events': <list(events)>,
            'overlapping_svs': <list(overlapping svs)>,
            'manual_rank_options': MANUAL_RANK_OPTIONS,
            'dismiss_variant_options': DISMISS_VARIANT_OPTIONS,
            'ACMG_OPTIONS': ACMG_OPTIONS,
            'evaluations': <list(evaluations)>,
        }

    """
    variant_type = variant_type or 'snv'
    start = datetime.now()
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    # If the variant is already collected we skip this part
    if not variant_obj:
        # NOTE this will query with variant_id == document_id, not the variant_id.
        variant_obj = store.variant(variant_id)

    if variant_obj is None:
        return None

    variant_id = variant_obj['variant_id']

    genome_build = case_obj.get('genome_build', '37')
    if genome_build not in ['37','38']:
        genome_build = '37'

    panels = default_panels(store, case_obj)
    variant_obj = add_gene_info(store, variant_obj, gene_panels=panels, genome_build=genome_build)
    # Add information about bam files and create a region vcf
    if add_case:
        variant_case(store, case_obj, variant_obj)

    # Collect all the events for the variant
    events = store.events(institute_obj, case=case_obj, variant_id=variant_id)
    for event in events:
        event['verb'] = VERBS_MAP[event['verb']]
    
    # Comments are not on case level so these needs to be fetched on their own
    variant_obj['comments'] = store.events(institute_obj, case=case_obj,
                                           variant_id=variant_id, comments=True)

    # Adds information about other causative variants
    other_causatives = []
    if add_other:
        other_causatives = [causative for causative in 
                            store.other_causatives(case_obj, variant_obj)]

    # Gather display information for the genes
    variant_obj.update(predictions(variant_obj.get('genes',[])))

    # sort compounds on combined rank score
    compounds = variant_obj.get('compounds', [])
    if compounds and add_compounds:
    # Gather display information for the compounds
        for compound_obj in compounds:
            compound_obj.update(predictions(compound_obj.get('genes', [])))
        
        variant_obj['compounds'] = sorted(variant_obj['compounds'],
                                          key=lambda compound: -compound['combined_score'])

    variant_obj['end_position'] = end_position(variant_obj)
    if variant_type == 'sv':
        variant_obj['frequencies'] = sv_frequencies(variant_obj)
    elif variant_type in ['snv', 'cancer']:
        # This is to convert a summary of frequencies to a string
        variant_obj['frequency'] = frequency(variant_obj)
    # Format clinvar information
    variant_obj['clinsig_human'] = (clinsig_human(variant_obj) if variant_obj.get('clnsig')
                                    else None)
    # Add general variant links
    add_variant_links(variant_obj, int(genome_build))
    
    # Add display information about callers
    variant_obj['callers'] = callers(variant_obj, category=variant_type)
    
    # Convert affection status to strings for the template
    is_affected(variant_obj, case_obj)

    if variant_obj.get('genetic_models'):
        variant_models = set(model.split('_', 1)[0] for model in variant_obj['genetic_models'])
        all_models = variant_obj.get('all_models', set())
        variant_obj['is_matching_inheritance'] = set.intersection(variant_models,all_models)

    # Prepare classification information for visualisation
    classification = variant_obj.get('acmg_classification')
    if isinstance(classification, int):
        acmg_code = ACMG_MAP[variant_obj['acmg_classification']]
        variant_obj['acmg_classification'] = ACMG_COMPLETE_MAP[acmg_code]
    
    evaluations = []
    for evaluation_obj in store.get_evaluations(variant_obj):
        evaluation(store, evaluation_obj)
        evaluations.append(evaluation_obj)

    case_clinvars = store.case_to_clinVars(case_obj.get('display_name'))

    if variant_id in case_clinvars:
        variant_obj['clinvar_clinsig'] = case_clinvars.get(variant_id)['clinsig']

    overlapping_vars = []
    if get_overlapping:
        for var in store.overlapping(variant_obj):
            var.update(predictions(var.get('genes',[])))
            overlapping_vars.append(var)
    variant_obj['end_chrom'] = variant_obj.get('end_chrom', variant_obj['chromosome'])

    return {
        'institute': institute_obj,
        'case': case_obj,
        'variant': variant_obj,
        'causatives': other_causatives,
        'events': events,
        'overlapping_vars': overlapping_vars,
        'manual_rank_options': MANUAL_RANK_OPTIONS,
        'dismiss_variant_options': DISMISS_VARIANT_OPTIONS,
        'mosaic_variant_options': MOSAICISM_OPTIONS,
        'ACMG_OPTIONS': ACMG_OPTIONS,
        'evaluations': evaluations,
    }

def observations(store, loqusdb, case_obj, variant_obj):
    """Query observations for a variant.
    
    Check if variant_obj have been observed before ni the loqusdb instance.
    If not return {}
    
    We need to add links to the variant in other cases where the variant has been observed.
    First we need to make sure that the user has access to these cases. The user_institute_ids holds
    information about what institutes the user has access to.
    
    Loop over the case ids from loqusdb and check if they exist in the scout instance.
    Also make sure that we do not link to the observation that is the current variant.
    
    Args:
        store (scout.adapter.MongoAdapter)
        loqusdb (scout.server.extensions.LoqusDB)
        case_obj (scout.models.Case)
        variant_obj (scout.models.Variant)
    
    Returns:
        obs_data(dict)
    """
    chrom = variant_obj['chromosome']
    pos = variant_obj['position']
    ref = variant_obj['reference']
    alt = variant_obj['alternative']
    var_case_id = variant_obj['case_id']
    var_type = variant_obj.get('variant_type', 'clinical')

    composite_id = ("{0}_{1}_{2}_{3}".format(chrom, pos, ref, alt))
    obs_data = loqusdb.get_variant({'_id': composite_id}) or {}
    if not obs_data:
        LOG.debug("Could not find any observations for %s", composite_id)
        return obs_data

    obs_data['total'] = loqusdb.case_count()
    user_institutes_ids = set([inst['_id'] for inst in user_institutes(store, current_user)])

    obs_data['cases'] = []
    institute_id = variant_obj['institute']
    for case_id in obs_data.get('families', []):
        if case_id == var_case_id:
            continue
        # other case might belong to same institute, collaborators or other institutes
        other_case = store.case(case_id)
        if not other_case:
            # Case could have been removed
            LOG.debug("Case %s could not be found in database", case_id)
            continue
        other_institutes = set([other_case.get('owner')])
        other_institutes.update(set(other_case.get('collaborators', [])))
        
        if user_institutes_ids.isdisjoint(other_institutes):
            # If the user does not have access to the information we skip it
            continue
        document_id = parse_document_id(chrom, str(pos), ref, alt, var_type, case_id)
        other_variant = store.variant(document_id=document_id)
        obs_data['cases'].append(dict(case=other_case, variant=other_variant))

    return obs_data
