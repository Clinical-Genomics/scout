import responses

from scout.utils.hgvs import VALIDATOR_URL, validate_hgvs


@responses.activate
def test_validate_hgvs_failed():
    """Test the API that validates a variant descriptor when the descriptor is NOT valid"""

    # GIVEN a variant descriptor expression
    desc = "NM_001145436.2:c.1840C>T"
    build = "GRCh37"

    # GIVEN a mocked warning (failed validation) response from the VariantValidator API
    resp_content = {
        "flag": "warning",
        "validation_warnings": [
            "NM_001145436.2:c.1840C>T: Variant reference (C) does not agree with reference sequence (G)"
        ],
    }
    responses.add(
        responses.GET,
        VALIDATOR_URL.format(build, desc),
        json=resp_content,
        status=200,
    )
    # THEN validation should fail
    assert validate_hgvs(build, desc) is False


@responses.activate
def test_validate_hgvs_success():
    """Test the API that validates a variant descriptor when the descriptor is valid"""

    # GIVEN a variant descriptor expression
    desc = "NM_001145437.2:c.1600C>T"
    build = "GRCh37"

    # GIVEN a mocked success response from the VariantValidator API
    resp_content = {"flag": "gene_variant"}
    responses.add(
        responses.GET,
        VALIDATOR_URL.format(build, desc),
        json=resp_content,
        status=200,
    )
    # THEN validation should return True
    assert validate_hgvs(build, desc)
