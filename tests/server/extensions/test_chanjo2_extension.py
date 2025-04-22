import responses

from scout.server.app import create_app
from scout.server.extensions import chanjo2

CHANJO2_BASE_URL = "https://chanjo2.se"


@responses.activate
def test_chanjo2_mt_coverage_stats(case_obj):
    """Test the function that sends requests to Chanjo2 to get MT vs autosomal coverage stats"""

    # GIVEN a case with individuals containing d4 files
    for ind in case_obj["individuals"]:
        assert ind["d4_file"]

    # GIVEN a patched chanjo2 instance
    # GIVEN a mocked Chanjo2 server dataset add endpoint
    url = f"{CHANJO2_BASE_URL}/coverage/d4/interval/"
    responses.add(
        responses.POST,
        url,
        json={"mean_coverage": 32},
        status=200,
    )

    # WHEN app is created and contains the CHANJO2_URL param
    test_app = create_app(config=dict(TESTING=True, CHANJO2_URL=CHANJO2_BASE_URL))

    with test_app.app_context():
        # WHEN POST requests are sent to chanjo2 to retrieve MT vs autosomal coverage stats
        coverage_stats = chanjo2.mt_coverage_stats(case_obj=case_obj)

        # THEN coverage stats should contain the expected key/values
        for ind in case_obj["individuals"]:
            ind_id = ind["individual_id"]
            assert isinstance(coverage_stats[ind_id]["autosome_cov"], int)
            assert isinstance(coverage_stats[ind_id]["mt_coverage"], int)
            assert isinstance(coverage_stats[ind_id]["mt_copy_number"], float)


@responses.activate
def test_chanjo2_get_complete_coverage(case_obj):
    """Test the function that sends requests to Chanjo2 to get MT vs autosomal coverage stats"""

    # GIVEN a case with individuals containing d4 files
    for ind in case_obj["individuals"]:
        assert ind["d4_file"]

    # GIVEN a response that is ok for each individual
    json_response = {}
    for ind in case_obj["individuals"]:
        json_response[ind["individual_id"]] = {
            "mean_coverage": 30,
            "coverage_completeness_percent": 100,
        }

    # GIVEN a patched chanjo2 instance
    # GIVEN a mocked Chanjo2 server dataset add endpoint
    url = f"{CHANJO2_BASE_URL}/coverage/d4/genes/summary"
    responses.add(
        responses.POST,
        url,
        json=json_response,
        status=200,
    )

    # WHEN app is created and contains the CHANJO2_URL param
    test_app = create_app(config=dict(TESTING=True, CHANJO2_URL=CHANJO2_BASE_URL))

    with test_app.app_context():
        # WHEN POST requests are sent to chanjo2 to retrieve MT vs autosomal coverage stats
        full_coverage = chanjo2.get_gene_complete_coverage(
            hgnc_id=17284, threshold=10, individuals=case_obj["individuals"]
        )

        assert full_coverage
