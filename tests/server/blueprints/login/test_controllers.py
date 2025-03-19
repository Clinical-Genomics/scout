"""Tests for login controllers"""

from scout.server.blueprints.login.controllers import event_rank, google_login, users


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


def test_google_login_user_logged_in(app):
    """Test that logged-in users are redirected to the login route, when the login is performed via Google Oauth 2.0"""

    # GIVEN an initialized app with LDAP config params
    with mock_app.test_client() as client:

        # GIVEN that the user is logged in
        with client.session_transaction() as sess:
            sess["email"] = "test@example.com"  # Simulate a logged-in user

            # THEN the function that checks the login should redirect to the login page
            resp = google_login()
            assert resp == "jksd"
