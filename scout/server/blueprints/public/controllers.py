import logging
from functools import reduce

from scout.constants import EVENTS_MAP
from scout.utils.date import pretty_date

LOG = logging.getLogger(__name__)
NOF_RECENT_EVENTS = 3


"""Controller module for first webview.

Requires: Python 3.7 or greater.
Reason: Implementation relies on dicts being able to maintain internal order.
This was previously only supported in OrderedDict().
"""

class CompactEvent():
    def __init__(self, verb, event_type, date):
        self.verb = verb
        self.event_type = event_type
        self.date = date
        self.count = 1

    def increment(self):
        self.count = self.count+1
        return self
        
    def __repr__(self):
        return self.verb + ":" + self.event_type + ":" + pretty_date(self.date)

def get_events_of_interest(store, user):
    """Read event database and compile a list of selected events of interest
    Args:
        store: scout.adapter.MongoAdapter
        user: store.user
    Returns:
        events_of_interest: list of dicts{'case', 'link', 'human_readable'}
        -where human_readable is a list of strings refering to users recent
         events of interest
    """
    events_of_interest = []
    events_per_case = []
    cases = recent_cases(user, store)
    LOG.debug("recent: {}".format(cases))
    for case in cases:
        event_list = events_in_case(store, user, case)
        LOG.debug("event_list: {}".format(event_list))
        events_per_case.append(event_list)

    for event_list in events_per_case:
        event = {}
        event["human_readable"] = compile_latest_events(event_list)
        head, *_tail = event_list
        event["link"] = head["link"]
        event["case"] = head["case"]
        events_of_interest.append(event)
    return events_of_interest


def recent_cases(user, store):
    """Return a list of recent cases order in increasing age. A case
    may appear only once."""
    return list(store.unique_cases_by_date({"_id": user.email}))


def events_in_case(store, user, case):
    """Return a list of events associated with a user's specific case."""

    # TODO: sort by 'updated_at'
    return list(store.user_events_by_case({"_id": user.email}, case))


def compile_latest_events(event_list):
    def compile_latest_events_aux(event_list, acc):
        """helper function"""
        if event_list == []:
            return acc
        head, *tail = event_list
        LOG.debug("acc: {}".format(acc))
        if len(acc) >=1 and head['verb'] == acc[0].verb and head['category'] == acc[0].event_type:
            try:
                compact_event = acc.pop()
                acc.append(compact_event.increment())
            except IndexError:
                compact_event = CompactEvent(head['verb'], head['category'], head['updated_at'])
                acc.append(compact_event)
        else:
            compact_event = CompactEvent(head['verb'], head['category'], head['updated_at'])
            acc.append(compact_event)
        return compile_latest_events_aux(tail, acc)
        
    myevents = compile_latest_events_aux(event_list, [])
    LOG.debug('myevents: {}'.format(myevents))
    
    return events_to_string(myevents[0:3])



def compile_important_events(event_list):
    """Compile a string of recent events, ordered by importance, together
    with the sum of the events occurences. Importance is determined by
    placement in the macro EVENTS_MAP.

        Args:
            event_list
        Returns:
            string, example: 'commented on 1 case. Pinned variant X 1.'
    """
    pairs = []
    for event in event_list:
        pairs.append((event["verb"], event["category"]))

    event_sum_list = sum_occurrences(pairs)
    top_events = get_important_events(event_sum_list)
    return events_to_string(top_events)


def get_important_events(all_events):
    """Sort tuple list accourding to macro EVENTS_MAP and return
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
    """Convert a list of event tuples to a readable string.

    Args:
        list_of_events: [((key, event_type), n_events)]

    Returns:
       string: a description of events, example:
       'Commented on 1 case. Pinned variant X3'
    """
    l = []

    LOG.debug("LIST: {}".format(list_of_events))

    def plural_s(n):
        """Return a possessive 's' to append if n is >1. This is used
        to make grammatically corrected strings."""
        if n > 1:
            return "s"
        return ""

    def is_repeated_verb(verb, event):
        """When the 'verb' is repeated in 'event' it would return
        strange sentences in a stylistic sence. This function is used
        to detect such a verb-event combination"""
        return event in EVENTS_MAP.get(verb)

    for compact_event in list_of_events:
        
        sentence = EVENTS_MAP.get(compact_event.verb)
        sentence2 = sentence.replace("nof", str(compact_event.count))
        sentence3 = sentence2.replace("event_type", compact_event.event_type + plural_s(compact_event.count))
        sentence4 = sentence3 + " (" +pretty_date(compact_event.date) + ")"
        LOG.debug("GOT:" + sentence4)
        l.append(sentence4)
    return reduce(lambda a, b: a + ". " + b, l)


def sum_occurrences(pairs):
    """Count tuples
    Args:
        pairs list of tuples (verb, category)

    Returns:
        Dict where each key is a tuple(verb, type), the value is numnber
        of occurances {('pin', 'variant'): 1,
    """

    def sum_occurrences_aux(pairs, accumulator):
        if pairs == []:
            return accumulator
        head, *tail = pairs
        if head in accumulator:
            accumulator[head] += 1
        else:
            accumulator[head] = 1
        return sum_occurrences_aux(tail, accumulator)

    return sum_occurrences_aux(pairs, {})


def verb_index(verb):
    """Return index of verb in EVENTS_MAP"""
    main, _rest = verb
    return list(EVENTS_MAP).index(main)
