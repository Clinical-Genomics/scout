import logging
from flask import url_for
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


class CompactEvent:
    """Class to represent a minimal event to be displayed on Scout's frontpage."""

    def __init__(self, verb, event_type, date):
        self.verb = verb
        self.event_type = event_type
        self.date = date
        self.count = 1

    def increment_by_one(self):
        """Increment internal counter by one

        Args: none
        Returns:
            CompactEvent()
        """
        self.count = self.count + 1
        return self

    def __eq__(self, other):
        if not isinstance(other, CompactEvent):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return (
            self.verb == other.verb
            and self.event_type == other.event_type
            and pretty_date(self.date) == pretty_date(other.date)
            and self.count == other.count
        )

    def __repr__(self):
        return (
            self.verb + ":" + self.event_type + ":" + str(self.count) + ":" + pretty_date(self.date)
        )


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
    cases = list(store.unique_cases_by_date(user.email))
    for case in cases:
        event_list = list(store.user_events_by_case({"_id": user.email}, case))
        # only add non-empty event_lists
        if event_list:
            events_per_case.append(event_list)
        else:
            LOG.debug("no events found for case: {} / {}".format(case, user.email))

    for events in events_per_case:
        compact_events = get_compact_events(events)
        event = {}
        event["human_readable"] = events_to_string(compact_events)
        head, *_tail = events
        event["link"] = case_page_link(head["case"], store)
        event["name"] = store.get_display_name(head["case"])
        events_of_interest.append(event)
    return events_of_interest


def case_page_link(case, store):
    """Create a relative link to the case page
    Args:
        case: string
        store: scout.adapter.MongoAdapter
    Returns:
       link: string:
    """
    institute = store.get_institute(case)
    display_name = store.get_display_name(case)
    link = url_for("cases.case", institute_id=institute, case_name=display_name)
    return link


def get_compact_events(event_list):
    """Compile a list of of events in a compact format, ready to be
    displayed on a Scout webpage. Subsequent events of the same type and verb will
    increment a counter. Return NOF_RECENT_EVENTS events.

    Args:
        event_list(list of events)
    Returns:
           list of CompactEvents
    """

    def compile_latest_events_aux(event_list, acc):
        """Auxiliary function for list recurssion
        Args:
            event_list(list of events)
            acc(empty list)
        Returns:
           list of CompactEvents
        """
        if event_list == []:
            return acc
        head, *tail = event_list
        if (
            len(acc) >= 1
            and head["verb"] == acc[-1].verb
            and head["category"] == acc[-1].event_type
        ):
            try:
                compact_event = acc.pop()
                acc.append(compact_event.increment_by_one())
            except IndexError:
                compact_event = CompactEvent(head["verb"], head["category"], head["updated_at"])
                acc.append(compact_event)
        else:
            compact_event = CompactEvent(head["verb"], head["category"], head["updated_at"])
            acc.append(compact_event)
        return compile_latest_events_aux(tail, acc)

    compiled_events = compile_latest_events_aux(event_list, [])
    top_events = compiled_events[0:NOF_RECENT_EVENTS]
    return top_events


def events_to_string(list_of_events):
    """Convert a list of event tuples to a readable string.

    Args:
        list_of_events: [CompactEvent()]

    Returns:
       string: a description of events, example:
       'Commented on 1 case (1 day ago). Pinned 3 variants (2 weeks ago)'
    """
    sentence_list = []

    def plural_s(n):
        """Return a possessive 's' to append if n is >1. This is used
        to make grammatically corrected strings."""
        if n > 1:
            return "s"
        return ""

    for compact_event in list_of_events:
        sentence = EVENTS_MAP.get(compact_event.verb)
        sentence2 = sentence.replace("nof", str(compact_event.count))
        sentence3 = sentence2.replace(
            "event_type", compact_event.event_type + plural_s(compact_event.count)
        )
        sentence4 = sentence3 + " (" + pretty_date(compact_event.date) + "). "
        sentence_list.append(sentence4)
    return reduce(lambda a, b: a + b, sentence_list, "")
