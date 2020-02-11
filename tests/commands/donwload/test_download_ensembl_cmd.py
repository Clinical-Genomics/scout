"""Tests for download commands"""

import pathlib
import tempfile

from scout.commands.download.ensembl import ensembl as ensembl_cmd


def test_download_ensembl_cmd(mocker, empty_mock_app):
    """Test download ensembl command"""
    # GIVEN a temporary directory
    mock_app = empty_mock_app
    runner = mock_app.test_cli_runner()

    mocker.patch("scout.commands.download.ensembl.print_ensembl")
    with tempfile.TemporaryDirectory() as dir_name:
        the_dir = pathlib.Path(dir_name)
        # WHEN running the command
        result = runner.invoke(
            ensembl_cmd, ["-o", the_dir, "--skip-tx", "--build", "37"]
        )
        # THEN check it exits without problems
        assert result.exit_code == 0
        assert "Download ensembl results" in result.output
