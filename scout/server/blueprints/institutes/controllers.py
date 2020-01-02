# -*- coding: utf-8 -*-

def institute(store, institute_id):
    """ Process institute data.

    Args:
        store(adapter.MongoAdapter)
        institute_id(str)

    Returns
        data(dict): includes institute obj and specific settings
    """

    institute_obj = store.institute(institute_id)
    users = store.users(institute_id)

    data = {
        'institute' : institute_obj,
        'users': users,
    }
    return data
