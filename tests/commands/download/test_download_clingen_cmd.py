"""Tests for download commands"""

import pathlib
import tempfile

from scout.commands.download.clingen import clingen as clingen_cmd


def test_download_clingen_cmd(mocker, empty_mock_app):
    """Test download clingen command"""

    # GIVEN a mock app
    mock_app = empty_mock_app
    runner = mock_app.test_cli_runner()
    mocker.patch("scout.utils.scout_requests.fetch_resource")

    # GIVEN a temporary directory
    with tempfile.TemporaryDirectory() as dir_name:
        tempdir = pathlib.Path(dir_name)
        # WHEN running the command
        result = runner.invoke(clingen_cmd, ["-o", tempdir])

        # THEN check it exits without problems
        assert result.exit_code == 0
        assert "Download ClinGen" in result.output
