import datetime
import logging
from functools import reduce
from scout.constants import VERBS_MAP
from scout.utils.date import pretty_date

LOG = logging.getLogger(__name__)


NOF_RECENT_EVENTS = 5


"""Controller module for first webview.



### Chiara's idea

-----------------------------------------------------
Case 1
-----------------------------------------------------
Edited synopsis. Marked 3 variants as causative, unmarked 1 variant as causative. Dismissed 27 variants.


-----------------------------------------------------
Case 2
-----------------------------------------------------
Commented on case. Commented on 2 variants, requested Sanger for one variant. Sent 1 variant to MatchMaker.


-----------------------------------------------------
Case 3
-----------------------------------------------------
Requested rerun for the case


"""


def verb_index(verb):
    """Return index of verb in VERBS_MAP"""
    a, b = verb
    return list(VERBS_MAP).index(a)


def get_events_of_interest(store, user):
    """Read event database and compile a list of selected events of interest"""
    LOG.debug(f"User: {user.email}")
    events_of_interest = []
    recent_events_by_case = []
    most_recent_cases = get_most_recent_cases(user, store)

    for case in most_recent_cases:
        event_list = list(store.user_events({"_id": user.email}, case=case))
        recent_events_by_case.append(event_list)

    for elem in recent_events_by_case:

        hd, *_ = elem
        event = {}
        event["human_readable"] = compile_important_events(elem)
        event["link"] = hd["link"]
        event["case"] = hd["case"]
        events_of_interest.append(event)

    LOG.debug(f"ELEMS: {events_of_interest}")
    return events_of_interest


def get_most_recent_cases(user, store):
    """Return a list of recent cases, unique by case. Order by newest first"""
    return list(store.distinct_user_case({"_id": user.email}))


def compile_important_events(event_list):
    """Compile lists of recent events, ordered by importance and supply count per event.
    Return as human readable string."""

    pairs = []
    for event in event_list:
        pairs.append((event["verb"], event["category"]))

    pairs_c = count_pairs(pairs)
    LOG.debug(f"EVENTS: {pairs_c}")
    order = sorted(pairs_c, key=verb_index)
    best = get_best(order, pairs_c, 4)
    LOG.debug(f"BEST: {best}")
    event_strings = events_to_string(best)
    LOG.debug(f"Events strings: {event_strings}")
    return reduce(lambda a, b: a + ", " + b, event_strings)


def get_events(user, store):
    """ """
    events = list(store.user_events({"_id": user.email}))
    distinct = list(
        store.distinct_user_events(
            {
                "_id": user.email,
            }
        )
    )
    asorted_events = list(store.user_events({"_id": user.email}, case="internal_id_2"))
    pairs = []

    LOG.debug(f"DISTINCT: {distinct}")
    LOG.debug(f"ASORTED: {asorted_events}")
    for event in events:
        pairs.append((event["verb"], event["category"]))

    pairs_c = count_pairs(pairs)
    LOG.debug(f"EVENTS: {events}")
    order = sorted(pairs_c, key=verb_index)
    best = get_best(order, pairs_c, 4)
    LOG.debug(f"BEST: {best}")
    event_strings = events_to_string(best)
    return event_strings


def events_to_string(list_of_events):
    """List of tuples: [(Key, kombo), n_events]]"""
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
            l.append(VERBS_MAP.get(verb) + " " + str(n) + " " + event_type + possessive_s(n))
    return l


def get_best(order, all, n):
    """Compile list of first n elements"""
    i = 0
    l = []
    LOG.debug(f"ORDER: {order}")
    while i < n and i < len(order):
        key = order[i]
        l.append((key, all[key]))
        i += 1
    return l


def count_pairs(pairs):
    """Count tuples
    Args:
        pairs list of tuples (verb, category)

    Returns:
        Dict where each key is a pair, the value is numnber of occurances
    """

    def count_pairs_aux(pairs, acc):
        if pairs == []:
            return acc
        head, *tail = pairs
        if head in acc:
            acc[head] += 1
        else:
            acc[head] = 1
        return count_pairs_aux(tail, acc)

    a = count_pairs_aux(pairs, {})
    LOG.debug(f"GOT: {a}")
    return a


def count_event(event_list, event_name):
    """Counts occurences of event_name in event_list, returns tuple"""
    count = 0

    for event in event_list:
        if event == event_name:
            count += 1
    return (event_name, count)


def get_event(events):
    """Get events for user

    Args:
    * user(Dict)

    Returns:
    * List: list of events sorted newest first
    """
    for event in events:
        event_outp = {}
        event_outp["case"] = event["case"]
        event_outp["category"] = event["category"]
        event_outp["link"] = event["link"]
        event_outp["subject"] = event["subject"]
        event_outp["updated_at"] = event["updated_at"]
        event_outp["verb"] = event["verb"]
        event_list.append(event_outp)

    return sorted(event_list, key=lambda d: d["updated_at"], reverse=True)


def drop_uninteresting_events(event_list):
    """Drop events from list"""
    unintersting_verbs = []
    interesting_list = []
    for event in event_list:
        if event["verb"] not in unintersting_verbs:
            interesting_list.append(event)
    return interesting_list


def prepare_pretty(event_list):
    """Pretty print dates, truncate long lines, map single verbs into sentances"""
    for event in event_list:
        event["verb"] = VERBS_MAP.get(event["verb"]).capitalize()
        event["updated_at"] = pretty_date(event["updated_at"])
        if len(event["subject"]) > 25:
            event["subject"] = event["subject"][0:25] + "..."
