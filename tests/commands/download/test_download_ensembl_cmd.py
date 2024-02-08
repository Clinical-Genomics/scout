"""Tests for download commands"""

import pathlib
import tempfile

import pytest

from scout.commands.download.ensembl import ensembl as ensembl_cmd
from scout.commands.download.ensembl import print_ensembl
from scout.utils.ensembl_biomart_clients import EnsemblBiomartHandler


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


def test_print_ensembl_genes(mocker, genes37_handle):
    """Test print ensembl genes function."""

    # GIVEN a patched call to schug
    # GIVEN a patched response from Ensembl Biomart, via schug
    mocker.patch.object(EnsemblBiomartHandler, "stream_get", return_value=genes37_handle)

    # GIVEN a temporary directory where the ensembl genes will be saved
    dir_name = tempfile.TemporaryDirectory()
    save_path = pathlib.Path(dir_name.name)

    # GIVEN the genes file that will be downloaded from Ensembl
    build = "37"
    genes_file_name: str = "ensembl_genes_{}.txt".format(build)

    # THEN the genes file should contain lines
    print_ensembl(save_path, resource_type="genes", genome_build=build)
    genes_file = open(save_path / genes_file_name)
    assert genes_file.readlines()


def test_print_ensembl_transcripts(mocker, transcripts_handle):
    """Test print ensembl transcripts function."""

    # GIVEN a patched call to schug
    mocker.patch.object(EnsemblBiomartHandler, "stream_get", return_value=transcripts_handle)

    # GIVEN a temporary directory where the ensembl genes will be saved
    dir_name = tempfile.TemporaryDirectory()
    save_path = pathlib.Path(dir_name.name)

    # GIVEN the transcripts file that will be downloaded from Ensembl
    build = "37"
    tx_file_name: str = "ensembl_transcripts_{}.txt".format(build)

    # THEN the transcripts file should contain lines
    print_ensembl(save_path, resource_type="transcripts", genome_build=build)
    tx_file = open(save_path / tx_file_name)
    assert tx_file.readlines()


def test_print_ensembl_exons(mocker, exons_handle):
    """Test print ensembl exons function."""

    # GIVEN a patched call to schug
    mocker.patch.object(EnsemblBiomartHandler, "stream_get", return_value=exons_handle)

    # GIVEN a temporary directory where the ensembl genes will be saved
    dir_name = tempfile.TemporaryDirectory()
    save_path = pathlib.Path(dir_name.name)

    # GIVEN the transcripts file that will be downloaded from Ensembl
    build = "37"
    exons_file_name: str = "ensembl_exons_{}.txt".format(build)

    # THEN the exons file should contain lines
    print_ensembl(save_path, resource_type="exons", genome_build=build)
    exons_file = open(save_path / exons_file_name)
    assert exons_file.readlines()


def test_print_ensembl_unknown_resource(mocker, transcripts_handle):
    """Test print ensembl function"""

    # GIVEN a temporary directory to save resource to
    dir_name = tempfile.TemporaryDirectory()
    save_path = pathlib.Path(dir_name.name)

    # WHEN print_ensembl is invoked with resource_type not in ["genes","transcripts","exons"]
    # THEN it should raise error
    with pytest.raises(SyntaxError):
        print_ensembl(save_path, resource_type="unknown", genome_build="37")
