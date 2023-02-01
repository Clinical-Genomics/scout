import uuid

import responses
from flask import url_for
from werkzeug.datastructures import ImmutableMultiDict

from scout.server.app import create_app
from scout.server.extensions import beacon, store

BEACON_BASE_URL = "http://localhost:6000/apiv1.0"


def test_beacon_create_app():
    """Test initiating the Beacon extensions when app config file contains right params"""

    # GIVEN an app initialized with BEACON_URL and BEACON_TOKEN params
    test_app = create_app(
        config=dict(
            TESTING=True,
            BEACON_TOKEN=str(uuid.uuid4()),
            BEACON_URL=BEACON_BASE_URL,
        )
    )

    # THEN it should contain the expected Beacon extension class attributes:
    with test_app.app_context():
        assert beacon.add_variants_url
        assert beacon.delete_variants_url
        assert beacon.token


@responses.activate
def test_add_dataset(app, institute_obj):
    """Test the function that sends a POST request to the Beacon with the info to create a new dataset"""

    # GIVEN a mocked Beacon server dataset add endpoint
    url = f"{BEACON_BASE_URL}/add_dataset"
    responses.add(
        responses.POST,
        url,
        json={"message": "Dataset collection was successfully updated"},
        status=200,
    )
    # invoking add_dataset function with expected params
    resp_code = beacon.add_dataset(institute_obj, "cust000_GRCh37")
    # Should return a success response code (200)
    assert resp_code == 200


def test_add_variants_unauthorized_user(app):
    """Test add_variants function when user has not a beacon_submitter role"""

    # GIVEN a user with no beacon_submitter role
    user_obj = store.user_collection.find_one()
    assert "beacon_submitter" not in user_obj["roles"]

    # AND a case with no associated submission object
    case_obj = store.case_collection.find_one()
    assert "beacon" not in case_obj

    with app.test_client() as client:
        # GIVEN that the user is logged in
        client.get(url_for("auto_login"))

        # WHEN user submits variants from a case to the Beacon
        beacon.add_variants(store, case_obj, None)

        # THEN case will not be updated with submission data
        updated_case = store.case_collection.find_one(case_obj)
        assert "beacon" not in updated_case


@responses.activate
def test_add_variants_wrong_dataset(app, user_obj, case_obj):
    """Testing add_variants function when no dataset corresponding to customer and
    case genome build is available in Beacon"""

    # GIVEN a mocked Beacon server info endpoint
    url = f"{BEACON_BASE_URL}/add"
    responses.add(
        responses.GET,
        url,
        json={"datasets": [{"id": "custX_GRCh37"}, {"id": "custY_GRCh38"}]},
        status=200,
    )

    # GIVEN a user with beacon_submitter role
    store.user_collection.find_one_and_update(
        {"_id": user_obj["email"]}, {"$set": {"roles": ["beacon_submitter"]}}
    )

    with app.test_client() as client:
        # GIVEN that the user is logged in
        client.get(url_for("auto_login"))

        # WHEN user submits variants from a case to the Beacon
        form_data = ImmutableMultiDict({"case": "internal_id", "vcf_files": "vcf_snv"})
        beacon.add_variants(store, case_obj, form_data)

        # THEN case will NOT be updated with submission data
        updated_case = store.case_collection.find_one()
        assert "beacon" not in updated_case


@responses.activate
def test_add_variants(app, user_obj, case_obj):
    """Test add_variants function when user is authorized"""

    # GIVEN a mocked Beacon server add endpoint
    url = f"{BEACON_BASE_URL}/add"
    responses.add(responses.POST, url, json={"foo": "bar"}, status=202)

    # GIVEN a mocked Beacon server info endpoint
    url = f"{BEACON_BASE_URL}/"
    responses.add(
        responses.GET,
        url,
        json={"datasets": [{"id": "cust000_GRCh37"}]},
        status=200,
    )

    # GIVEN a user with beacon_submitter role
    store.user_collection.find_one_and_update(
        {"_id": user_obj["email"]}, {"$set": {"roles": ["beacon_submitter"]}}
    )

    with app.test_client() as client:
        # GIVEN that the user is logged in
        client.get(url_for("auto_login"))

        # WHEN user submits variants from a case to the Beacon
        form_data = ImmutableMultiDict({"case": "internal_id", "vcf_files": "vcf_snv"})
        beacon.add_variants(store, case_obj, form_data)

        # THEN case will be updated with submission data
        updated_case = store.case_collection.find_one()
        assert "beacon" in updated_case

        # AND the relative event should be saved in the database:
        beacon_event = store.event_collection.find_one()
        assert beacon_event["verb"] == "beacon_add"
        assert beacon_event["link"] == f"/{case_obj['owner']}/{case_obj['display_name']}"


@responses.activate
def test_remove_variants(app, user_obj, institute_obj, case_obj):
    """Test remove_variants function when user is authorized to edit a beacon submission"""

    url = f"{BEACON_BASE_URL}/delete"
    responses.add(responses.DELETE, url, json={"foo": "bar"}, status=202)

    # GIVEN a case with Beacon submission data:
    store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"beacon": "this is a test"}}
    )

    # GIVEN a user with beacon_submitter role
    store.user_collection.find_one_and_update(
        {"_id": user_obj["email"]}, {"$set": {"roles": ["beacon_submitter"]}}
    )

    with app.test_client() as client:
        # GIVEN that the user is logged in
        client.get(url_for("auto_login"))

        # WHEN user calls the endpoint to remove a Beacon submission for a case
        beacon.remove_variants(store, institute_obj["_id"], case_obj)

        # THEN Beacon data should be removed from case document
        updated_case = store.case_collection.find_one()
        assert "beacon" not in updated_case

        # AND the relative event should be saved in the database:
        beacon_event = store.event_collection.find_one()
        assert beacon_event["verb"] == "beacon_remove"
        assert beacon_event["link"] == f"/{case_obj['owner']}/{case_obj['display_name']}"
