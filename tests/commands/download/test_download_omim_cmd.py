"""Tests for download commands"""

import os
import pathlib
import tempfile

import responses

from scout.commands.download.omim import omim as omim_cmd
from scout.commands.download.omim import print_omim
from scout.demo.resources import genemap2_reduced_path, mim2gene_reduced_path


@responses.activate
def test_download_omim_cmd(empty_mock_app):
    """Test download omim command"""

    runner = empty_mock_app.test_cli_runner()

    # GIVEN a patched response from OMIM to obtain genemap2 file
    url = "https://data.omim.org/downloads/a%20key/genemap2.txt"
    with open(genemap2_reduced_path, "r") as hpo_file:
        content = hpo_file.read()
    responses.add(
        responses.GET,
        url,
        body=content,
        status=200,
    )

    # GIVEN a patched response from OMIM to obtain mim2gene file
    url = "https://omim.org/static/omim/data/mim2gene.txt"
    with open(mim2gene_reduced_path, "r") as hpo_file:
        content = hpo_file.read()
    responses.add(
        responses.GET,
        url,
        body=content,
        status=200,
    )

    # GIVEN a temporary directory
    with tempfile.TemporaryDirectory() as dir_name:
        the_dir = pathlib.Path(dir_name)
        # WHEN running the command
        result = runner.invoke(omim_cmd, ["-o", the_dir, "--api-key", "a key"])
        # THEN command should run successfully
        assert result.exit_code == 0
        assert "Download OMIM" in result.output

        # AND the directory should contain the 2 expected files
        downloaded_files = os.listdir(dir_name)
        assert "genemap2.txt" in downloaded_files
        assert "mim2genes.txt" in downloaded_files
