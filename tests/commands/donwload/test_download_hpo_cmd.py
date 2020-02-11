"""Tests for download commands"""

import pathlib
import tempfile

from scout.commands.download.hpo import hpo as hpo_cmd


def test_download_hpo_cmd(mocker, empty_mock_app):
    """Test download hpo command"""
    # GIVEN a temporary directory
    mock_app = empty_mock_app
    runner = mock_app.test_cli_runner()

    mocker.patch("scout.commands.download.hpo.print_hpo")
    with tempfile.TemporaryDirectory() as dir_name:
        the_dir = pathlib.Path(dir_name)
        # WHEN running the command
        result = runner.invoke(hpo_cmd, ["-o", the_dir])
        # THEN check it exits without problems
        assert result.exit_code == 0
        assert "Download HPO" in result.output
