import json

import responses

from scout.server.app import create_app
from scout.server.extensions import clinvar_api

CLINVAR_TEST_API_URL = "https://test.clinvar.api.submissions/"
CLINVAR_TEST_SUBMISSION_SUMMARY_URL = "https://submit.ncbi.nlm.nih.gov/api/2.0/files/xxxxxxxx/sub999999-summary-report.json/?format=attachment"
TEST_SUBMISSION_ID = "SUB1234567"
TEST_API_KEY = "test_key"
TEST_CLINVAR_ACCESSION = "SCV000839746"


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

    # WHEN an app is created and contains the CLINVAR_API_URL param
    test_app = create_app(config=dict(TESTING=True, CLINVAR_API_URL=CLINVAR_TEST_API_URL))

    with test_app.app_context():

        # GIVEN a call to the json_submission_status function of the ClinVar extension
        submission_status_json = clinvar_api.json_submission_status(
            submission_id=TEST_SUBMISSION_ID, api_key=TEST_API_KEY
        )

        # THEN the extension function should return the expected json document
        assert submission_status_json == processed_submission


@responses.activate
def test_get_clinvar_scv_accession(successful_submission_summary_file_content):
    """Tests the ClinVar extension function that collects the ClinVar accession ID (SCV) after downloading a submission summary file."""

    # GIVEN a downloadable submission summary from ClinVar
    file_content = json.dumps(successful_submission_summary_file_content).encode("utf-8")

    # GIVEN a patched response from ClinVar
    responses.add(
        method=responses.GET,
        url=CLINVAR_TEST_SUBMISSION_SUMMARY_URL,
        body=file_content,
        status=200,
        stream=True,
        content_type="application/json",
    )

    # WHEN an app is created and contains the CLINVAR_API_URL param
    test_app = create_app(config=dict(TESTING=True, CLINVAR_API_URL=CLINVAR_TEST_API_URL))

    with test_app.app_context():

        # THEN the extension function should return the expected ClinVar accession ID
        clinvar_accession = clinvar_api.get_clinvar_scv_accession(
            url=CLINVAR_TEST_SUBMISSION_SUMMARY_URL
        )
        assert clinvar_accession == TEST_CLINVAR_ACCESSION
