"""
Test Phenopacket API extension
"""

from scout.server.extensions import phenopacketapi


def test_phenopacket_from_case(phenopackets_app, test_case, hpo_term):
    """Test phenopacket JSON export for case individuals with HPO terms assigned."""

    # GIVEN that the test case has an affected individual
    affected_ind = test_case["individuals"][0]
    assert affected_ind["phenotype"] == 2

    # GIVEN that the test case has an associated phenotype term
    test_case["phenotype_terms"] = [
        {
            "phenotype_id": hpo_term["hpo_id"],
            "feature": hpo_term["description"],
            "individuals": [{"individual_id": affected_ind["individual_id"]}],
        }
    ]

    with phenopackets_app.app_context():
        # WHEN asking for a phenopacket JSON
        phenopacket_json = phenopacketapi.phenopacket_from_case(test_case)

        # THEN the HPO term ID should appear in the produced JSON string
        assert hpo_term["hpo_id"] in phenopacket_json
