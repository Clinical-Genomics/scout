from scout.constants.clinvar import CLINVAR_API_URL_DEFAULT
from scout.server.app import create_app

CLINVAR_TEST_API_URL = "https://submit.ncbi.nlm.nih.gov/apitest/v1/submissions/"
TEST_SUBMISSION_ID = "SUB1234567"
TEST_API_KEY = "test_key"


@responses.activate
def test_json_submission_status(processed_submission):
    """Test the function that retrieves the status of a submission to ClinVar."""

    # GIVEN a mocked submitted response from ClinVar:
    actions: list[dict] = [
        {
            "id": f"{CLINVAR_TEST_API_URL}-1",
            "responses": [],
            "status": "submitted",
            "targetDb": "clinvar",
            "updated": "2024-04-29T13:39:24.384085Z",
        }
    ]

    responses.add(
        responses.GET,
        f"{CLINVAR_API_URL_DEFAULT}{CLINVAR_TEST_API_URL}/actions/",
        json=processed_submission,
        status=200,
    )

    test_app = create_app(config=dict(TESTING=True, CLINVAR_API_URL=CLINVAR_TEST_API_URL))
