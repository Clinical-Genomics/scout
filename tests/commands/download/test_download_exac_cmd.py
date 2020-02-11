"""Tests for download commands"""

import pathlib
import tempfile

from scout.commands.download.exac import exac as exac_cmd
from scout.commands.download.exac import print_exac


def test_download_exac_cmd(mocker, empty_mock_app):
    """Test download exac command"""
    # GIVEN a temporary directory
    mock_app = empty_mock_app
    runner = mock_app.test_cli_runner()

    mocker.patch("scout.commands.download.exac.print_exac")
    with tempfile.TemporaryDirectory() as dir_name:
        the_dir = pathlib.Path(dir_name)
        # WHEN running the command
        result = runner.invoke(exac_cmd, ["-o", the_dir])
        # THEN check it exits without problems
        assert result.exit_code == 0
        assert "Download ExAC" in result.output


def test_print_exac_cmd(mocker, exac_handle):
    """Test print exac function"""
    # GIVEN a temporary directory and some exac lines
    exac_file_name = "fordist_cleaned_exac_r03_march16_z_pli_rec_null_data.txt"
    exac_lines = [line.strip() for line in exac_handle]
    mocker.patch("scout.utils.scout_requests.fetch_resource", return_value=exac_lines)
    dir_name = tempfile.TemporaryDirectory()
    the_dir = pathlib.Path(dir_name.name)
    # WHEN fetching and printing the exac data
    print_exac(the_dir)
    i = 0
    for i, line in enumerate(open(the_dir / exac_file_name)):
        if len(line) > 10 and i > 0:
            assert line.startswith("ENST")
    # THEN check some lines where produced
    assert i > 0
