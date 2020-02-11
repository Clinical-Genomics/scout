"""Tests for download commands"""

import pathlib
import tempfile

from scout.commands.download.hgnc import hgnc as hgnc_cmd
from scout.commands.download.hgnc import print_hgnc


def test_download_hgnc_cmd(mocker, empty_mock_app):
    """Test download hgnc command"""
    # GIVEN a temporary directory
    mock_app = empty_mock_app
    runner = mock_app.test_cli_runner()

    mocker.patch("scout.commands.download.hgnc.print_hgnc")
    with tempfile.TemporaryDirectory() as dir_name:
        the_dir = pathlib.Path(dir_name)
        # WHEN running the command
        result = runner.invoke(hgnc_cmd, ["-o", the_dir])
        # THEN check it exits without problems
        assert result.exit_code == 0
        assert "Download HGNC" in result.output


def test_print_hgnc_cmd(mocker, hgnc_handle):
    """Test print hgnc function"""
    # GIVEN a temporary directory and some exac lines
    hgnc_file_name = "hgnc.txt"
    hgnc_lines = [line.strip() for line in hgnc_handle]
    mocker.patch("scout.utils.scout_requests.fetch_resource", return_value=hgnc_lines)
    dir_name = tempfile.TemporaryDirectory()
    the_dir = pathlib.Path(dir_name.name)
    # WHEN fetching and printing the exac data
    print_hgnc(the_dir)
    i = 0
    # THEN assert that the lines where printed to the correct file
    for i, line in enumerate(open(the_dir / hgnc_file_name)):
        if len(line) > 10 and i > 0:
            assert line.startswith("HGNC")
    # THEN check some lines where produced
    assert i > 0
