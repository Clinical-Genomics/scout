# -*- coding: utf-8 -*-


def institutes(store, institute_query):
    """Preprocess institute objects."""
    for institute in institute_query:
        case_count = store.cases(collaborator=institute['internal_id']).count()
        yield (institute, case_count)
