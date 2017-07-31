# -*- coding: utf-8 -*-


def event_rank(count):
    """Determine event ranking."""
    if count < 10:
        return 'constable'
    elif count < 100:
        return 'sergeant'
    elif count < 250:
        return 'inspector'
    elif count < 500:
        return 'superintendent'
    elif count < 1000:
        return 'commander'
    else:
        return 'commissioner'


def users(store):
    """Display a list of all users and which institutes they belong to."""
    user_objs = list(store.users())
    total_events = store.user_events().count()
    for user_obj in user_objs:
        user_obj['institutes'] = [store.institute(inst_id) for inst_id in user_obj['institutes']]
        user_obj['events'] = store.user_events(user_obj).count()
        user_obj['events_rank'] = event_rank(user_obj['events'])
    return dict(
        users=sorted(user_objs, key=lambda user: -user['events']),
        total_events=total_events,
    )
