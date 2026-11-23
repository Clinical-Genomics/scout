# -*- coding: utf-8 -*-
import responses

from scout.commands import cli

MIM2GENE_URL = "https://omim.org/static/omim/data/mim2gene.txt"
INVALID_KEY_GENEMAP2_URL = "https://data.omim.org/downloads/not_a_valid_key/genemap2.txt"


@responses.activate
def test_setup_database_invalid_omim_key(mock_app):
    """Testing the cli to setup a full scale database"""

    # GIVEN that OMIM rejects the API key (mocked, so no real request is sent)
    responses.add(responses.GET, MIM2GENE_URL, body="", status=200)
    responses.add(responses.GET, INVALID_KEY_GENEMAP2_URL, status=403)

    runner = mock_app.test_cli_runner()
    assert runner

    # test the CLI command with non-valid API key
    result = runner.invoke(cli, ["setup", "database", "--api-key", "not_a_valid_key", "--yes"])
    # Make sure that setup enters in setup function correctly but stops because
    # there is no valid OMIM API KEY
    assert result.exit_code != 0
    # THEN it should have stopped at the OMIM download with the invalid key
    assert responses.calls[-1].request.url == INVALID_KEY_GENEMAP2_URL


def test_setup_database(mock_app):
    """Testing the cli to setup a full scale database"""

    runner = mock_app.test_cli_runner()
    assert runner

    # test the CLI command for seting up scout
    result = runner.invoke(cli, ["setup", "demo"])

    # Make sure that setup function works correctly
    assert result.exit_code == 0
    assert "Scout instance setup successful" in result.output
