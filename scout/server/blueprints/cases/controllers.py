# -*- coding: utf-8 -*-
from flask import url_for
import query_phenomizer

from scout.constants import CASE_STATUSES, PHENOTYPE_GROUPS
from scout.models.event import VERBS_MAP

STATUS_MAP = {'solved': 'bg-success', 'archived': 'bg-warning'}
SEX_MAP = {'1': 'male', '2': 'female'}
PHENOTYPE_MAP = {-9: 'missing', 0: 'missing', 1: 'unaffected', 2: 'affected'}


def user_institutes(store, user_obj):
    """Preprocess institute objects."""
    if user_obj.is_admin:
        institutes = store.institutes()
    else:
        institutes = (store.institute(inst_id) for inst_id in user_obj.institutes)
    for institute in institutes:
        case_count = store.cases(collaborator=institute['_id']).count()
        yield (institute, case_count)


def cases(store, case_query):
    """Preprocess case objects."""
    case_groups = {status: [] for status in CASE_STATUSES}
    for case_obj in case_query:
        analysis_types = set(ind['analysis_type'] for ind in case_obj['individuals'])
        case_obj['analysis_types'] = list(analysis_types)
        case_obj['assignees'] = [store.user(user_email) for user_email in
                                 case_obj.get('assignees', [])]
        case_groups[case_obj['status']].append(case_obj)

    data = {
        'prio_cases': case_groups['prioritized'],
        'cases': [(status, case_groups[status]) for status in CASE_STATUSES],
        'found_cases': case_query.count(),
    }
    return data


def case(store, institute_obj, case_obj):
    """Preprocess a single case."""
    for individual in case_obj['individuals']:
        individual['sex_human'] = SEX_MAP.get(individual['sex'], 'unknown')
        individual['phenotype_human'] = PHENOTYPE_MAP.get(individual['phenotype'])

    case_obj['assignees'] = [store.user(user_email) for user_email in
                             case_obj.get('assignees', [])]
    suspects = [store.variant(variant_id) for variant_id in
                case_obj.get('suspects', [])]
    causatives = [store.variant(variant_id) for variant_id in
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

    # other collaborators than the owner of the case
    case_obj['o_collaborators'] = [collab_id for collab_id in
                                   case_obj['collaborators'] if collab_id != ['owner']]

    irrelevant_ids = ('cust000', institute_obj['_id'])
    collab_ids = [collab['_id'] for collab in store.institutes() if
                  (collab['_id'] not in irrelevant_ids) and
                  (collab['_id'] not in case_obj['collaborators'])]

    events = list(store.events(institute_obj, case=case_obj))
    for event in events:
        event['verb'] = VERBS_MAP[event['verb']]

    data = {
        'status_class': STATUS_MAP.get(case_obj['status']),
        'other_causatives': store.check_causatives(case_obj),
        'comments': store.events(institute_obj, case=case_obj, comments=True),
        'hpo_groups': PHENOTYPE_GROUPS,
        'events': events,
        'suspects': suspects,
        'causatives': causatives,
        'collaborators': collab_ids,
    }
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
