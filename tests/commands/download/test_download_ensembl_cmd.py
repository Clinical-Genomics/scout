"""Tests for download commands"""

import pathlib
import tempfile

import pytest

from scout.commands.download.ensembl import ensembl as ensembl_cmd
from scout.commands.download.ensembl import print_ensembl


def test_download_ensembl_cmd(mocker, empty_mock_app):
    """Test download ensembl command"""
    # GIVEN a temporary directory
    mock_app = empty_mock_app
    runner = mock_app.test_cli_runner()

    mocker.patch("scout.commands.download.ensembl.print_ensembl")
    with tempfile.TemporaryDirectory() as dir_name:
        the_dir = pathlib.Path(dir_name)
        # WHEN running the command
        result = runner.invoke(ensembl_cmd, ["-o", the_dir, "--skip-tx", "--build", "37"])
        # THEN check it exits without problems
        assert result.exit_code == 0
        assert "Download ensembl results" in result.output


def test_print_ensembl_genes(mocker, transcripts_handle):
    """Test print ensembl function"""
    # GIVEN a temporary directory and some exac lines
    build = "37"
    tx_file_name = "ensembl_genes_{}.txt".format(build)
    tx_lines = [line.strip() for line in transcripts_handle]
    mocker.patch("scout.utils.scout_requests.fetch_ensembl_biomart", return_value=tx_lines)
    dir_name = tempfile.TemporaryDirectory()
    the_dir = pathlib.Path(dir_name.name)
    # WHEN fetching and printing the exac data
    print_ensembl(the_dir, resource_type="genes", genome_build=build)
    i = 0
    for i, line in enumerate(open(the_dir / tx_file_name)):
        if len(line) > 10 and i > 0:
            assert line.split("\t")[1].startswith("ENSG")
    # THEN check some lines where produced
    assert i > 0


def test_print_ensembl_transcripts(mocker, transcripts_handle):
    """Test print ensembl function"""
    # GIVEN a temporary directory and some exac lines
    build = "37"
    tx_file_name = "ensembl_transcripts_{}.txt".format(build)
    tx_lines = [line.strip() for line in transcripts_handle]
    mocker.patch("scout.utils.scout_requests.fetch_ensembl_biomart", return_value=tx_lines)
    dir_name = tempfile.TemporaryDirectory()
    the_dir = pathlib.Path(dir_name.name)
    # WHEN fetching and printing the exac data
    print_ensembl(the_dir, resource_type="transcripts", genome_build=build)
    i = 0
    for i, line in enumerate(open(the_dir / tx_file_name)):
        if len(line) > 10 and i > 0:
            assert line.split("\t")[1].startswith("ENSG")
    # THEN check some lines where produced
    assert i > 0


def test_print_ensembl_exons(mocker, transcripts_handle):
    """Test print ensembl function"""
    # GIVEN a temporary directory and some exac lines
    build = "37"
    tx_file_name = "ensembl_exons_{}.txt".format(build)
    tx_lines = [line.strip() for line in transcripts_handle]
    mocker.patch("scout.utils.scout_requests.fetch_ensembl_biomart", return_value=tx_lines)
    dir_name = tempfile.TemporaryDirectory()
    the_dir = pathlib.Path(dir_name.name)
    # WHEN fetching and printing the exac data
    print_ensembl(the_dir, resource_type="exons", genome_build=build)
    i = 0
    for i, line in enumerate(open(the_dir / tx_file_name)):
        if len(line) > 10 and i > 0:
            assert line.split("\t")[1].startswith("ENSG")
    # THEN check some lines where produced
    assert i > 0


def test_print_ensembl_unknown_resource(mocker, transcripts_handle):
    """Test print ensembl function"""
    # GIVEN a temporary directory and some exac lines
    build = "37"
    tx_file_name = "ensembl_exons_{}.txt".format(build)
    tx_lines = [line.strip() for line in transcripts_handle]
    mocker.patch("scout.utils.scout_requests.fetch_ensembl_biomart", return_value=tx_lines)
    dir_name = tempfile.TemporaryDirectory()
    the_dir = pathlib.Path(dir_name.name)
    # WHEN fetching and printing the exac data
    with pytest.raises(SyntaxError):
        print_ensembl(the_dir, resource_type="unknown", genome_build=build)
