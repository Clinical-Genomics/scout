# -*- coding: utf-8 -*-
import datetime

import pymongo
from flask import url_for

from scout import __version__
from scout.server.blueprints.public.controllers import (
    CompactEvent,
    events_to_string,
    get_compact_events,
)


def test_get_compact_events(real_variant_database, institute_obj, case_obj, user_obj, variant_obj):
    # GIVEN A event database with two events
    adapter = real_variant_database

    adapter.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="variant_link",
        variant=variant_obj,
        content="Hello, locally",
        comment_level="specific",
    )

    # and a global comment
    adapter.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="variant_link",
        variant=variant_obj,
        content="Hello, globally",
        comment_level="global",
    )

    # WHEN quering the database for all events and calling `get_compact_events()`
    query = dict()
    query["user_id"] = "john@doe.com"
    query["case"] = "internal_id"
    events_list = list(adapter.event_collection.find(query).sort("updated_at", pymongo.DESCENDING))
    compact_events = get_compact_events(events_list)

    # THEN the returned event will behave as a simulated CompactEvent()
    test_a = CompactEvent("comment", "variant", datetime.datetime.now())
    test_a.increment()
    assert compact_events[0] == test_a


def test_events_to_string():
    # GIVEN a list fo CompactEvents. Where one is incremented.
    # Note that date attribute is ignored when testing
    test_a = CompactEvent("assign", "variant", 1)
    test_b = CompactEvent("pin", "variant", 1)
    test_c = CompactEvent("pin", "case", 1)
    test_c.increment()
    test_c.increment()
    test = [test_a, test_b, test_c]

    # THEN expanding the test list into sentences via the
    # VERBS_MAP macro, the correct and enumerated events are
    # found
    events_string = events_to_string(test)
    assert "Assigned 1 variant" in events_string
    assert "Pinned 1 variant" in events_string
    assert "Pinned 3 cases" in events_string


def test_events_to_string_empty_string():
    # GIVEN an empty list
    test_list = []

    # THEN the empty string is returned
    assert "" == events_to_string(test_list)
