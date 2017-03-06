# -*- coding: utf-8 -*-


def user_institutes(store, user_obj):
    """Preprocess institute objects."""
    institutes = (store.institute(inst_id) for inst_id in user_obj.institutes)
    for institute in institutes:
        case_count = store.cases(collaborator=institute['internal_id']).count()
        yield (institute, case_count)
