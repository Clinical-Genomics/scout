# -*- coding: utf-8 -*-
import itertools
import datetime

from flask import url_for
from flask_mail import Message
import query_phenomizer

from scout.constants import (CASE_STATUSES, PHENOTYPE_GROUPS, COHORT_TAGS, ACMG_OPTIONS)
from scout.constants.variant_tags import MANUAL_RANK_OPTIONS, DISMISS_VARIANT_OPTIONS, GENETIC_MODELS
from scout.models.event import VERBS_MAP
from scout.server.utils import institute_and_case
from scout.server.blueprints.variants.controllers import variants_description, variants_filter_by_field

STATUS_MAP = {'solved': 'bg-success', 'archived': 'bg-warning'}
SEX_MAP = {'1': 'male', '2': 'female'}
PHENOTYPE_MAP = {-9: 'missing', 0: 'missing', 1: 'unaffected', 2: 'affected'}


def cases(store, case_query):
    """Preprocess case objects."""
    limit = 100
    case_groups = {status: [] for status in CASE_STATUSES}
    for case_obj in case_query.limit(limit):
        analysis_types = set(ind['analysis_type'] for ind in case_obj['individuals'])
        case_obj['analysis_types'] = list(analysis_types)
        case_obj['assignees'] = [store.user(user_email) for user_email in
                                 case_obj.get('assignees', [])]
        case_groups[case_obj['status']].append(case_obj)
        case_obj['is_rerun'] = len(case_obj.get('analyses', [])) > 0

    data = {
        'cases': [(status, case_groups[status]) for status in CASE_STATUSES],
        'found_cases': case_query.count(),
        'limit': limit,
    }
    return data


def case(store, institute_obj, case_obj):
    """Preprocess a single case."""
    case_obj['individual_ids'] = []
    for individual in case_obj['individuals']:
        individual['sex_human'] = SEX_MAP.get(individual['sex'], 'unknown')
        individual['phenotype_human'] = PHENOTYPE_MAP.get(individual['phenotype'])
        case_obj['individual_ids'].append(individual['individual_id'])

    case_obj['assignees'] = [store.user(user_email) for user_email in
                             case_obj.get('assignees', [])]
    suspects = [store.variant(variant_id) or variant_id for variant_id in
                case_obj.get('suspects', [])]
    causatives = [store.variant(variant_id) or variant_id for variant_id in
                  case_obj.get('causatives', [])]

    distinct_genes = set()
    case_obj['panel_names'] = []
    for panel_info in case_obj.get('panels', []):
        if panel_info.get('is_default'):
            panel_obj = store.panel(panel_info['panel_id'])
            distinct_genes.update([gene['hgnc_id'] for gene in panel_obj['genes']])
            full_name = "{} ({})".format(panel_obj['display_name'], panel_obj['version'])
            case_obj['panel_names'].append(full_name)
    case_obj['default_genes'] = list(distinct_genes)

    for hpo_term in itertools.chain(case_obj.get('phenotype_groups', []),
                                    case_obj.get('phenotype_terms', [])):
        hpo_term['hpo_link'] = ("http://compbio.charite.de/hpoweb/showterm?id={}"
                                .format(hpo_term['phenotype_id']))

    # other collaborators than the owner of the case
    o_collaborators = [store.institute(collab_id) for collab_id in case_obj['collaborators'] if
                       collab_id != case_obj['owner']]
    case_obj['o_collaborators'] = [(collab_obj['_id'], collab_obj['display_name']) for
                                   collab_obj in o_collaborators]

    irrelevant_ids = ('cust000', institute_obj['_id'])
    collab_ids = [(collab['_id'], collab['display_name']) for collab in store.institutes() if
                  (collab['_id'] not in irrelevant_ids) and
                  (collab['_id'] not in case_obj['collaborators'])]

    events = list(store.events(institute_obj, case=case_obj))
    for event in events:
        event['verb'] = VERBS_MAP[event['verb']]

    data = {
        'status_class': STATUS_MAP.get(case_obj['status']),
        'other_causatives': store.check_causatives(case_obj=case_obj),
        'comments': store.events(institute_obj, case=case_obj, comments=True),
        'hpo_groups': PHENOTYPE_GROUPS,
        'events': events,
        'suspects': suspects,
        'causatives': causatives,
        'collaborators': collab_ids,
        'cohort_tags': COHORT_TAGS,
    }
    return data


def case_report_content(store, institute_obj, case_obj):
    """Gather contents to be visualized in a case report"""

    data = case(store, institute_obj, case_obj)

    data.update({'manual_rank_options': MANUAL_RANK_OPTIONS})
    data.update({'dismissed_options': DISMISS_VARIANT_OPTIONS})
    data.update({'genetic_models': dict(GENETIC_MODELS)})
    data.update({'report_created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})

    #get detailed info for the causatives:
    causatives = variants_description(store, data['causatives'], case_obj, institute_obj)
    data.update({'causatives_detailed': causatives})

    #get detailed info for the pinned:
    pinned = variants_description(store, data['suspects'], case_obj, institute_obj)
    data.update({'pinned_detailed': pinned})

    ## get variants for this case that are either classified, commented, tagged or dismissed.
    all_variants = list(store.variants(case_id=case_obj['_id'], nr_of_variants=-1)) #all snv variants
    all_variants = all_variants + list(store.variants(case_id=case_obj['_id'], nr_of_variants=-1, category='sv')) # add structural variants to the list

    # get complete info for the acmg classified variants
    classified_detailed = variants_filter_by_field(store, all_variants, 'acmg_classification', case_obj, institute_obj)
    data.update({'classified_detailed': classified_detailed})

    # get complete info for tagged variants
    tagged_detailed = variants_filter_by_field(store, all_variants, 'manual_rank', case_obj, institute_obj)
    data.update({'tagged_detailed': tagged_detailed})

    # get complete info for dismissed variants
    dismissed_detailed = variants_filter_by_field(store, all_variants, 'dismiss_variant', case_obj, institute_obj)
    data.update({'dismissed_detailed': dismissed_detailed})

    # get variants with any comment
    commented_ids=[]
    for variant in all_variants:
        events = list(store.events(institute_obj, case=case_obj, variant_id=variant['variant_id'], comments=True))
        if len(events) > 0:
            commented_ids.append(variant['_id'])

    commented_detailed = variants_description(store, commented_ids, case_obj, institute_obj)
    data.update({'commented_detailed': commented_detailed})

    return data



def update_synopsis(store, institute_obj, case_obj, user_obj, new_synopsis):
    """Update synopsis."""
    # create event only if synopsis was actually changed
    if new_synopsis and case_obj['synopsis'] != new_synopsis:
        link = url_for('cases.case', institute_id=institute_obj['_id'],
                       case_name=case_obj['display_name'])
        store.update_synopsis(institute_obj, case_obj, user_obj, link,
                              content=new_synopsis)


def hpo_diseases(username, password, hpo_ids, p_value_treshold=1):
    """Return the list of HGNC symbols that match annotated HPO terms.

    Args:
        username (str): username to use for phenomizer connection
        password (str): password to use for phenomizer connection

    Returns:
        query_result: a generator of dictionaries on the form
        {
            'p_value': float,
            'disease_source': str,
            'disease_nr': int,
            'gene_symbols': list(str),
            'description': str,
            'raw_line': str
        }
    """
    # skip querying Phenomizer unless at least one HPO terms exists
    try:
        results = query_phenomizer.query(username, password, *hpo_ids)
        diseases = [result for result in results
                    if result['p_value'] <= p_value_treshold]
        return diseases
    except SystemExit:
        return None


def rerun(store, mail, current_user, institute_id, case_name, sender, recipient):
    """Request a rerun by email."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for('cases.case', institute_id=institute_id, case_name=case_name)
    store.request_rerun(institute_obj, case_obj, user_obj, link)

    # this should send a JSON document to the SuSy API in the future
    html = """
        <p>{institute}: {case} ({case_id})</p>
        <p>Re-run requested by: {name}</p>
    """.format(institute=institute_obj['display_name'],
               case=case_obj['display_name'], case_id=case_obj['_id'],
               name=user_obj['name'].encode())

    # compose and send the email message
    msg = Message(subject=("SCOUT: request RERUN for {}"
                           .format(case_obj['display_name'])),
                  html=html, sender=sender, recipients=[recipient],
                  # cc the sender of the email for confirmation
                  cc=[user_obj['email']])
    mail.send(msg)


def update_default_panels(store, current_user, institute_id, case_name, panel_ids):
    """Update default panels for a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    user_obj = store.user(current_user.email)
    link = url_for('cases.case', institute_id=institute_id, case_name=case_name)
    panel_objs = [store.panel(panel_id) for panel_id in panel_ids]
    store.update_default_panels(institute_obj, case_obj, user_obj, link, panel_objs)
