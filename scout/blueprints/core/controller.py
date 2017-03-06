# -*- coding: utf-8 -*-
from scout.constants import CASE_STATUSES


def institutes(store, institute_query):
    """Preprocess institute objects."""
    for institute in institute_query:
        case_count = store.cases(collaborator=institute.internal_id).count()
        yield (institute, case_count)


def cases(case_query):
    """Preprocess case objects."""
    case_groups = {status: [] for status in CASE_STATUSES}
    for case_obj in case_query:
        analysis_types = set(ind['analysis_type'] for ind in case_obj['individuals'])
        case_obj['analysis_types'] = list(analysis_types)
        case_groups[case_obj['status']].append(case_obj)

    data = {
        'prio_cases': case_groups['prioritized'],
        'cases': [(status, case_groups[status]) for status in CASE_STATUSES],
        'found_cases': case_query.count(),
    }
    return data
