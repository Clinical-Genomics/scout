import logging
from functools import reduce
from scout.constants import VERBS_MAP

LOG = logging.getLogger(__name__)
NOF_RECENT_EVENTS = 4


"""Controller module for first webview.

Requires: Python 3.7 or greater.
Reason: Implementation relies on normal dicts able to maintain
internal order.
"""


def get_events_of_interest(store, user):
    """Read event database and compile a list of selected events of interest
    Args:
        store: scout.adapter.MongoAdapter
        user: store.user
    Returns:
        events_of_interest: list of dicts{'Case', 'link', 'human_readable'}
        -where human_readable is a list of strings refering to users recent events of interest
    """
    events_of_interest = []
    events_per_case = []
    cases = recent_cases(user, store)

    for case in cases:
        event_list = events_in_case(store, user, case)
        events_per_case.append(event_list)

    for event_list in events_per_case:
        event = {}
        event["human_readable"] = compile_important_events(event_list)
        head, *_tail = event_list
        event["link"] = head["link"]
        event["case"] = head["case"]
        events_of_interest.append(event)
    return events_of_interest


def recent_cases(user, store):
    """Return a list of recent cases order in increasing age. A case may appear only once."""
    return list(store.unique_cases_by_date({"_id": user.email}))


def events_in_case(store, user, case):
    """Return a list of events associated with a user's specific case"""
    return list(store.user_events({"_id": user.email}, case=case))


def compile_important_events(event_list):
    """Compile a string of recent events, ordered by importance, together with the sum of the events occurences.
    Importance is determined by placement in the macro VERBS_MAP.
        Args:
            event_list
        Returns:
            string, example: 'commented on 1 case. Pinned variant X 1.'
    """
    pairs = []
    for event in event_list:
        pairs.append((event["verb"], event["category"]))

    event_sum_list = sum_occurrences(pairs)
    LOG.debug(f"EVENTS: {event_sum_list}")
    top_events = get_important_events(event_sum_list)
    LOG.debug(f"BEST: {top_events}")
    return events_to_string(top_events)


def get_important_events(all_events):
    """Sort tuple list accourding to macro VERBS_MAP and return
    a list of length(NOF_RECENT_EVENTS).

    Args:
        all_events:Dict()

    Returns:
        tuple_list: (verb, count)
    """
    events_by_importance = sorted(all_events, key=verb_index)
    i = 0
    l = []
    while i < NOF_RECENT_EVENTS and i < len(events_by_importance):
        key = events_by_importance[i]
        l.append((key, all_events[key]))
        i += 1
    return l


def events_to_string(list_of_events):
    """List of tuples: [(Key, kombo), n_events]


    Returns:"""
    l = []

    def possessive_s(n):
        if n > 1:
            return "s"
        return ""

    def tautology(verb, event):
        return event in VERBS_MAP.get(verb)

    for event in list_of_events:
        (verb, event_type), n = event
        if tautology(verb, event_type):
            l.append(VERBS_MAP.get(verb) + " X" + str(n))
        else:
            l.append(
                VERBS_MAP.get(verb) + " " + str(n) + " " + event_type + possessive_s(n)
            )
    return reduce(lambda a, b: a + ", " + b, l)


def sum_occurrences(pairs):
    """Count tuples
    Args:
        pairs list of tuples (verb, category)

    Returns:
        Dict where each key is a tuple(verb, type), the value is numnber of occurances {('pin', 'variant'): 1,
    """

    def sum_occurrences_aux(pairs, acc):
        if pairs == []:
            return acc
        head, *tail = pairs
        if head in acc:
            acc[head] += 1
        else:
            acc[head] = 1
        return sum_occurrences_aux(tail, acc)

    return sum_occurrences_aux(pairs, {})


def verb_index(verb):
    """Return index of verb in VERBS_MAP"""
    main, _rest = verb
    return list(VERBS_MAP).index(main)
