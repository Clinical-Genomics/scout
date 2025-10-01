from flask import Blueprint

from scout.server.extensions import chanjo_report


def test_chanjo_mt_coverage_stats(app, monkeypatch):
    """Test MT vs autosomal coverage stats fetching with mocked requests"""

    # GIVEN a mock blueprint with the Chanjo endpoint
    bp = Blueprint("report", __name__)

    @bp.route("/chanjo_endpoint", methods=["POST"])
    def json_chrom_coverage():
        """Mock endpoint"""
        return ""

    app.register_blueprint(bp)

    # Mock requests.post to return a fake JSON response
    class MockResponse:
        def json(self):
            # Return some random coverage numbers
            return {"sample1": 36, "sample2": 32, "sample3": 34}

    def mock_post(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("requests.post", mock_post)

    # GIVEN a case with the same samples
    individuals = [{"individual_id": s} for s in ["sample1", "sample2", "sample3"]]

    # Flask needs a test request context for url_for(_external=True)
    with app.test_request_context():
        # Use the existing instance
        coverage_stats = chanjo_report.mt_coverage_stats(individuals=individuals)

        expected_keys = ["mt_coverage", "autosome_cov", "mt_copy_number"]
        for sample in ["sample1", "sample2", "sample3"]:
            assert sample in coverage_stats
            for key in expected_keys:
                assert key in coverage_stats[sample]
