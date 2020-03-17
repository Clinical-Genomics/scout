"""Tests for updating HPO terms from CLI"""

from scout.commands import cli


def test_update_hpo_no_confirm(mock_app):
    """Tests the CLI that updates HPO terms in the database"""

    runner = mock_app.test_cli_runner()
    # GIVEN a CLI runner
    assert runner

    # WHEN running CLI without arguments arguments
    result = runner.invoke(cli, ["update", "hpo"])
    # THEN assert that the program exits
    assert result.exit_code == 1
    # THEN assert that an error message is printed
    assert "Are you sure you want to drop the hpo terms?" in result.output


def test_update_hpo(mock_app, demo_files):
    """Tests the CLI that updates HPO terms in the database"""

    runner = mock_app.test_cli_runner()
    # GIVEN a CLI runner
    assert runner
    # GIVEN the demo hpo terms
    hpoterms = demo_files["hpoterms_path"]
    # GIVEN the demo hpo to genes file
    hpo_to_genes = demo_files["hpo_to_genes_path"]
    # WHEN running CLI with arguments arguments
    result = runner.invoke(
        cli,
        ["update", "hpo", "--hpoterms", hpoterms, "--hpo-to-genes", hpo_to_genes],
        input="y",
    )
    # THEN assert that the program exits without problems
    assert result.exit_code == 0
    # THEN assert that the correct info is logged
    assert "INFO Time to load terms" in result.output
