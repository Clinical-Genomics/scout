"""Tests for download commands"""

import os
import pathlib
import tempfile

import responses

from scout.commands.download.orpha import orpha as orpha_cmd
from scout.demo.resources import orphadata_en_product6_reduced_path


@responses.activate
def test_download_orpha_cmd(empty_mock_app):
    """Test download orpha command"""

    runner = empty_mock_app.test_cli_runner()

    # GIVEN a patched response from Orphadata to obtain genes_to_orpha file
    url = "https://www.orphadata.com/data/xml/en_product6.xml"
    with open(orphadata_en_product6_reduced_path, "r") as orphadata_en_product6_file:
        content = orphadata_en_product6_file.read()
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
        result = runner.invoke(orpha_cmd, ["-o", the_dir])
        # THEN command should run successfully
        assert result.exit_code == 0
        assert "Download ORPHA" in result.output

        # AND the directory should contain the expected file
        downloaded_files = os.listdir(dir_name)
        assert "orphadata_en_product6.xml" in downloaded_files
