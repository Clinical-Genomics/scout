# -*- coding: utf-8 -*-
from flask import url_for

from scout import __version__
from scout.server.blueprints.public.controllers import (
    events_to_string,
    get_important_events,
    sum_occurrences,
    verb_index,
)


def test_verb_index():
    # GIVEN a subset of VERBS_MACRO
    verbs_map = {
        "mark_causative": "marked causative for",
        "update_diagnosis": "updated diagnosis for",
        "rerun": "requested rerun of",
        "status": "updated the status for",
        "comment": "commented on",
        "comment_update": "updated a comment for",
        "pin": "pinned variant",
        "assign": "was assigned to",

    }

    # THEN calling `verb_index` will return the correct index
    assert verb_index(("assign", "sadf")) == 7
    assert verb_index(("status", "sadf")) == 3


def test_sum_occurences():
    # GIVEN list of events
    test_list = [
        ("pin", "variant"),
        ("pin", "variant"),
        ("pin", "variant"),
        ("pin", "case"),
        ("assign", "variant"),
    ]
    # THEN calling `sum_occurrences()` will return a dict
    # where the keys are events and values the number of occurences
    # of each event respectively
    sums = sum_occurrences(test_list)
    assert sums[("pin", "variant")] == 3
    assert sums[("pin", "case")] == 1


def test_get_important_events():
    # GIVEN a dict where keys are verb-tuples
    test = {("pin", "case"): 1, ("assign", "variant"): 1, ("pin", "variant"): 3, }

    # WHEN calling `get_important_events(...)`
    importants = get_important_events(test)

    # THEN the result is ordered according to VERBS_MAP
    (key, _value) = importants[0]
    print(importants)
    assert list(test)[0] == key


def test_events_to_string():
    # GIVEN a list of test tuples
    test = [(("assign", "variant"), 1), (("pin", "variant"), 3), (("pin", "case"), 1)]

    # THEN expanding the test list into sentences via the
    # VERBS_MAP macro, the correct and enumerated events are
    # found
    events_string = events_to_string(test)
    assert "Was assigned to 1 variant" in events_string
    assert "Pinned variant X3" in events_string
    assert "Pinned variant 1 case" in events_string
