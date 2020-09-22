"""Tests for scout update omim"""

from scout.commands import cli


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


def test_update_omim_wrong_omim_key(mock_app):
    """Tests the CLI that updates OMIM terms in database"""

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
