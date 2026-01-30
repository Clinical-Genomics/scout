import pytest
import responses
from flask import url_for

from scout.constants.clinvar import ASSERTION_CRITERIA_GERM_ID, ASSERTION_GERM_GERM_DB
from scout.server.extensions import store

GERMLINE = "germline"
ONCOGENICITY = "oncogenicity"

CLINVAR_API_URL_TEST = "https://submit.ncbi.nlm.nih.gov/apitest/v1/submissions/"
STATUS_ENDPOINT = "clinvar.clinvar_submission_status"
UPDATE_ENDPOINT = "clinvar.clinvar_update_submission"
VAR_SAVE_ENDPOINT = "clinvar.clinvar_variant_save"
SEND_API_SUBMISSION = "clinvar.send_api_submission"
DEMO_SUBMISSION_ID = "SUB12345678"
DEMO_API_KEY = "TESTTEST1111AAAA2222BBBB3333CCCC4444DDDD5555EEEE6666FFFF"


@responses.activate
def test_clinvar_api_status(app):
    """Test the endpoint used to check the status of a ClinVar submission."""

    # GIVEN a mocked submitted response from ClinVar:
    actions: list[dict] = [
        {
            "id": f"{DEMO_SUBMISSION_ID}-1",
            "responses": [],
            "status": "submitted",
            "targetDb": "clinvar",
            "updated": "2024-04-29T13:39:24.384085Z",
        }
    ]

    responses.add(
        responses.GET,
        f"{CLINVAR_API_URL_TEST}{DEMO_SUBMISSION_ID}/actions/",
        json={"actions": actions},
        status=200,
    )

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # GIVEN a call to the status endpoint
        response = client.post(
            url_for(STATUS_ENDPOINT, submission_id=DEMO_SUBMISSION_ID),
            data={"apiKey": DEMO_API_KEY},
        )

        # THEN the response should redirect
        assert response.status_code == 302


@pytest.mark.parametrize(
    "endpoint",
    [
        "clinvar.clinvar_add_germline_variant",
        "clinvar.clinvar_add_onc_variant",
    ],
)
def test_clinvar_multistep_add_variant_page(app, institute_obj, case_obj, variant_obj, endpoint):
    """Test endpoints that display the multistep form to add a ClinVar variant (germline or oncogenic)."""
    # GIVEN a database with a variant
    assert store.variant_collection.find_one()

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # WHEN sending a post request to add a variant to ClinVar
        data = {"var_id": variant_obj["_id"]}
        resp = client.post(
            url_for(
                endpoint,
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=data,
        )

        # THEN the form page should work as expected
        assert resp.status_code == 200


@pytest.mark.parametrize(
    "submissions_endpoint",
    [
        "clinvar.clinvar_germline_submissions",
        "clinvar.clinvar_onc_submissions",
    ],
)
def test_clinvar_submissions_page(
    app,
    institute_obj,
    case_obj,
    submissions_endpoint,
):
    """Test the pages that shows ClinVar submissions (germline or oncogenicity) for an institute."""

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # THEN the submissions page should work
        resp = client.get(
            url_for(
                submissions_endpoint,
                institute_id=institute_obj["internal_id"],
            ),
        )

        assert resp.status_code == 200


ACTIONS = [
    ("closed", "status", "closed"),
    ("open", "status", "open"),
    ("submitted", "status", "submitted"),
]


@pytest.mark.parametrize(
    "submission_type",
    [
        GERMLINE,
        ONCOGENICITY,
    ],
)
@pytest.mark.parametrize("update_action, status_key, status_value", ACTIONS)
def test_clinvar_update_submission_status(
    app,
    institute_obj,
    case_obj,
    user_obj,
    submission_type,
    update_action,
    status_key,
    status_value,
):
    """Test the endpoint responsible for updating the status of ClinVar submissions (either germline or oncogenicity)."""

    # GIVEN a database with a submission
    subm_obj = store.get_open_clinvar_submission(
        institute_id=institute_obj["_id"], user_id=user_obj["_id"], type=submission_type
    )
    assert subm_obj[status_key] == "open"
    assert store.clinvar_submission_collection.find_one()

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # WHEN submission status is changed via the endpoint
        data = {"update_submission": update_action}
        resp = client.post(
            url_for(
                UPDATE_ENDPOINT,
                institute_id=institute_obj["internal_id"],
                submission=subm_obj["_id"],
            ),
            data=data,
        )

        # THEN response should redirect back
        assert resp.status_code == 302

        # AND submission status should have changed
        updated = store.clinvar_submission_collection.find_one()
        assert updated[status_key] == status_value


@pytest.mark.parametrize(
    "submission_type",
    [
        GERMLINE,
        ONCOGENICITY,
    ],
)
def test_clinvar_update_submission_delete(app, institute_obj, user_obj, submission_type):
    """Test deleting one submission document using the status update endpoint."""

    # GIVEN a database with a submission
    subm_obj = store.get_open_clinvar_submission(
        institute_id=institute_obj["_id"], user_id=user_obj["_id"], type=submission_type
    )

    assert store.clinvar_submission_collection.find_one()

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # WHEN submission is removed via the 'clinvar_update_submission' endpoint
        data = {"update_submission": "delete"}
        client.post(
            url_for(
                UPDATE_ENDPOINT,
                institute_id=institute_obj["internal_id"],
                submission=subm_obj["_id"],
            ),
            data=data,
        )

        # THEN the submission should be removed
        assert store.clinvar_submission_collection.find_one() is None


@pytest.mark.parametrize(
    "submission_type",
    [
        GERMLINE,
        ONCOGENICITY,
    ],
)
def test_get_submission_as_json(institute_obj, user_obj, app, submission_type):
    """Test the endpoint that returns the submission object as a json file."""

    # GIVEN a database with a submission
    subm_obj = store.get_open_clinvar_submission(
        institute_id=institute_obj["_id"], user_id=user_obj["_id"], type=submission_type
    )

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # THEN the submission should be viewable as json
        resp = client.get(
            url_for(
                "clinvar.get_submission_as_json",
                submission=subm_obj["_id"],
                subm_type=submission_type,
            )
        )

        assert resp.status_code == 200
        assert resp.is_json


def test_clinvar_save(app, institute_obj, case_obj, clinvar_snv_form):
    """Test the endpoint that parses the multistep user form and adds a germline variant to a germline submission."""

    EXPECTED_SUBMISSION_KEYS = [
        "recordStatus",
        "variantSet",
        "conditionSet",
        "observedIn",
        "institute_id",
        "case_name",
        "variant_id",
    ]

    # GIVEN a database with no ClinVar submission documents
    assert store.clinvar_submission_collection.find_one() is None

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # WHEN a variant is included in a germline submission via the 'clinvar_germline_save' endpoint
        client.post(
            url_for(
                VAR_SAVE_ENDPOINT,
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                subm_type=GERMLINE,
            ),
            data=clinvar_snv_form,
        )

        # THEN a submission should exist
        subm_obj = store.clinvar_submission_collection.find_one()
        # Of the specified type
        assert subm_obj["type"] == GERMLINE

        # WHICH contains assertion criteria
        assert subm_obj["assertionCriteria"]["db"] == ASSERTION_GERM_GERM_DB
        assert subm_obj["assertionCriteria"]["id"] == ASSERTION_CRITERIA_GERM_ID

        # AND the submitted variant with the expected keys
        for var in subm_obj[f"{GERMLINE}Submission"]:
            for key in EXPECTED_SUBMISSION_KEYS + [f"{GERMLINE}Classification"]:
                assert key in var


@pytest.mark.parametrize(
    "submission_type",
    [
        GERMLINE,
        ONCOGENICITY,
    ],
)
def test_send_api_submission(app, institute_obj, user_obj, submission_type):
    """Test sending a submission to the ClinVar API."""

    # GIVEN a mocked ClinVar API service
    responses.add(
        responses.POST,
        CLINVAR_API_URL_TEST,
        json={"id": "SUB1234567"},
        status=201,
    )

    # GIVEN a ClinVar submission document present in the database
    subm_obj = store.get_open_clinvar_submission(
        institute_id=institute_obj["_id"], user_id=user_obj["_id"], type=submission_type
    )

    assert subm_obj["status"] == "open"

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # Then a request to the "send_api_submission" endpoint
        resp = client.post(
            url_for(
                SEND_API_SUBMISSION,
                institute_id=institute_obj["internal_id"],
                submission=subm_obj["_id"],
                subm_type=submission_type,
            )
        )
        # SHOULD result in a redirect to submissions page (code 302)
        assert resp.status_code == 302

        # AND the submission object in database should be marked as submitted
        updated_submission = store.clinvar_submission_collection.find_one({"_id": subm_obj["_id"]})
        assert updated_submission["status"] == "submitted"
