"""Tests for download commands"""

import pathlib
import tempfile

from scout.commands.download.omim import omim as omim_cmd


def test_download_omim_cmd(mocker, empty_mock_app):
    """Test download omim command"""
    # GIVEN a temporary directory
    mock_app = empty_mock_app
    runner = mock_app.test_cli_runner()

    mocker.patch("scout.commands.download.omim.print_omim")
    with tempfile.TemporaryDirectory() as dir_name:
        the_dir = pathlib.Path(dir_name)
        # WHEN running the command
        result = runner.invoke(omim_cmd, ["-o", the_dir, "--api-key", "a key"])
        # THEN check it exits without problems
        assert result.exit_code == 0
        assert "Download OMIM" in result.output
