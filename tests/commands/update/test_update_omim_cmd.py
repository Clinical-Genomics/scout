"""Tests for scout update omim"""

import responses

from scout.commands import cli

MIM2GENE_URL = "https://omim.org/static/omim/data/mim2gene.txt"
INVALID_KEY_GENEMAP2_URL = "https://data.omim.org/downloads/not_a_valid_key/genemap2.txt"


def test_update_omim_non_existing_institute(empty_mock_app):
    """Tests the CLI that updates OMIM terms in database"""
    mock_app = empty_mock_app

    # GIVEN a cli runner
    runner = mock_app.test_cli_runner()
    assert runner

    # WHEN updating omim-auto with no institute specified
    result = runner.invoke(cli, ["update", "omim"])
    # THEN warns that institute does not exist
    assert "WARNING Please specify an existing institute" in result.output
    # THEN command raises error because institute did not exist
    assert result.exit_code != 0


def test_update_omim_existing_institute_no_omim_key(mock_app):
    """Tests the CLI that updates OMIM terms in database"""
    # GIVEN a cli runner
    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, provide non valid API key
    result = runner.invoke(
        cli,
        ["update", "omim", "--institute", "cust000"],
    )
    assert result.exit_code != 0
    assert "WARNING Please provide a omim api key to load the omim gene panel" in result.output


@responses.activate
def test_update_omim_wrong_omim_key(mock_app):
    """Tests the CLI that updates OMIM terms in database"""

    # GIVEN that OMIM rejects the API key (mocked, so no real request is sent)
    responses.add(responses.GET, MIM2GENE_URL, body="", status=200)
    responses.add(responses.GET, INVALID_KEY_GENEMAP2_URL, status=403)

    # GIVEN a cli runner
    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, provide non valid API key
    result = runner.invoke(
        cli,
        ["update", "omim", "--institute", "cust000", "--api-key", "not_a_valid_key"],
    )
    # THEN assert exit code is non zero since the kwy did not work
    assert result.exit_code != 0
    # THEN it should have stopped at the OMIM download with the invalid key
    assert responses.calls[-1].request.url == INVALID_KEY_GENEMAP2_URL


def test_update_omim_file_paths(mock_app, genemap_file, mim2gene_file):
    """Tests the CLI that updates OMIM terms in database"""

    # GIVEN a cli runner
    runner = mock_app.test_cli_runner()
    assert runner

    # Test CLI base, with paths to ommim resources specified
    result = runner.invoke(
        cli,
        [
            "update",
            "omim",
            "--institute",
            "cust000",
            "--genemap2",
            genemap_file,
            "--mim2genes",
            mim2gene_file,
        ],
    )
    assert result.exit_code == 0
