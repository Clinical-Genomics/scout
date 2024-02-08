"""Tests for download commands"""

import pathlib
import tempfile

from scout.commands.download.exac import exac as exac_cmd
from scout.commands.download.exac import print_constraint
from scout.constants import GNOMAD_CONSTRAINT_FILENAME


def test_download_constraints_cmd(mocker, empty_mock_app):
    """Test download ExAC / GnomAD constraint command"""
    # GIVEN a temporary directory
    mock_app = empty_mock_app
    runner = mock_app.test_cli_runner()

    mocker.patch("scout.commands.download.exac.print_constraint")
    with tempfile.TemporaryDirectory() as dir_name:
        out_dir = pathlib.Path(dir_name)
        # WHEN running the command
        result = runner.invoke(exac_cmd, ["-o", out_dir])
        # THEN check it exits without problems
        assert result.exit_code == 0
        assert "Download ExAC" in result.output


def test_print_constraint_cmd(mocker, exac_handle):
    """Test print EXaC / GnomAD constraint function"""
    # GIVEN a temporary directory and some GnomAD constraints lines
    exac_lines = [line.strip() for line in exac_handle]
    mocker.patch("scout.utils.scout_requests.fetch_resource", return_value=exac_lines)
    dir_name = tempfile.TemporaryDirectory()
    out_dir = pathlib.Path(dir_name.name)

    # WHEN fetching and printing the EXaC / GnomAD data
    print_constraint(out_dir)
    i = 0
    for i, line in enumerate(open(out_dir / GNOMAD_CONSTRAINT_FILENAME)):
        if len(line) > 10 and i > 0:
            assert line.startswith("A")
            break
    # THEN check some lines where produced
    assert i > 0
