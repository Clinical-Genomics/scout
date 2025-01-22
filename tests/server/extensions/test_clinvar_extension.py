import responses

from scout.server.app import create_app
from scout.server.extensions import clinvar_api

CLINVAR_TEST_API_URL = "https://test.clinvar.api.submissions/"
TEST_SUBMISSION_ID = "SUB1234567"
TEST_API_KEY = "test_key"


@responses.activate
def test_json_submission_status(processed_submission):
    """Test the function that retrieves the status of a submission to ClinVar."""

    # GIVEN a patched ClinVar API instance
    responses.add(
        responses.GET,
        f"{CLINVAR_TEST_API_URL}{TEST_SUBMISSION_ID}/actions/",
        json=processed_submission,
        status=200,
    )

    # WHEN app is created and contains the CLINVAR_API_URL param
    test_app = create_app(config=dict(TESTING=True, CLINVAR_API_URL=CLINVAR_TEST_API_URL))

    with test_app.app_context():

        # GIVEN a call to the json_submission_status function of the ClinVar extension
        submission_status_json = clinvar_api.json_submission_status(
            submission_id=TEST_SUBMISSION_ID, api_key=TEST_API_KEY
        )

        # THEN the extension function should return the expected json document
        assert submission_status_json == processed_submission
