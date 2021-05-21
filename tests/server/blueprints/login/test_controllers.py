"""Tests for login controllers"""

from scout.server.blueprints.login.controllers import event_rank, users


def test_event_rank_zero():
    """Test the newcomer status"""
    # GIVEN 0 events
    nr_events = 0
    # WHEN fetching the rank
    invetigator_status = event_rank(nr_events)
    # THEN assert that the user is a aspirant
    assert invetigator_status == "aspirant"


def test_event_rank_50():
    """Test the newcomer status"""
    # GIVEN 50 events
    nr_events = 50
    # WHEN fetching the rank
    invetigator_status = event_rank(nr_events)
    # THEN assert that the user is still a aspirant
    assert invetigator_status == "aspirant"


def test_event_rank_150():
    """Test the constable status"""
    # GIVEN 150 events
    nr_events = 150
    # WHEN fetching the rank
    invetigator_status = event_rank(nr_events)
    # THEN assert that the user is a constable
    assert invetigator_status == "constable"


def test_event_rank_550():
    """Test the sergant status"""
    # GIVEN 550 events
    nr_events = 550
    # WHEN fetching the rank
    invetigator_status = event_rank(nr_events)
    # THEN assert that the user is a constable
    assert invetigator_status == "constable"


def test_event_rank_1050():
    """Test the sergant status"""
    # GIVEN 1050 events
    nr_events = 1050
    # WHEN fetching the rank
    invetigator_status = event_rank(nr_events)
    # THEN assert that the user is a sergant
    assert invetigator_status == "sergeant"


def test_event_rank_6000():
    """Test the inspector status"""
    # GIVEN 6000 events
    nr_events = 6000
    # WHEN fetching the rank
    invetigator_status = event_rank(nr_events)
    # THEN assert that the user is still a inspector
    assert invetigator_status == "inspector"


def test_users_controller(user_adapter):
    """Test the uses controller"""
    res = users(user_adapter)
    user = res["users"][0]
    assert user["events_rank"] == "aspirant"
