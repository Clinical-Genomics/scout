import requests
from flask import Blueprint

from scout.server.extensions import chanjo_report


def test_chanjo_mt_coverage_stats(app, monkeypatch):
    """Test the function that sends requests to Chanjo to get MT vs autosomal coverage stats"""

    # GIVEN a mock connection to chanjo and an available json_chrom_coverage endpoint
    bp = Blueprint("report", __name__)

    @bp.route("/chanjo_endpoint", methods=["POST"])
    def json_chrom_coverage():
        """This is the mocker function"""
        pass

    app.register_blueprint(bp)

    def mock_post(*args, **kwargs):
        return MockResponse()

    # AND a mock response from chanjo API with coverage stats for some samples
    class MockResponse:
        def __init__(self):
            self.text = '{"sample1":36, "sample2": 32, "sample3": 34}'

    monkeypatch.setattr(requests, "post", mock_post)

    # Given a case with the same samples
    individuals = []
    samples = ["sample1", "sample2", "sample3"]
    for sample in samples:
        individuals.append({"individual_id": sample})

    with app.app_context():
        # WHEN the function to get the MT vs autosome coverage stats is invoked
        coverage_stats = chanjo_report.mt_coverage_stats(individuals=individuals)
        expected_keys = ["mt_coverage", "autosome_cov", "mt_copy_number"]
        # THEN it should return stats for each sample, and all expected key/values for each sample
        for sample in samples:
            assert sample in coverage_stats
            for key in expected_keys:
                assert key in coverage_stats[sample]
