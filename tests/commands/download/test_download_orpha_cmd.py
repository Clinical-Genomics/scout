"""Tests for download commands"""

import os
import pathlib
import tempfile
from typing import List

import click.testing
import responses
from flask import app

from scout.commands.download.orpha import orpha as orpha_cmd
from scout.constants import ORPHA_URLS
from scout.demo.resources import (
    orphadata_en_product4_reduced_path,
    orphadata_en_product6_reduced_path,
)


@responses.activate
def test_download_orpha_cmd(empty_mock_app: app.Flask):
    """Test download orpha command"""

    runner: app.FlaskCliRunner = empty_mock_app.test_cli_runner()

    # GIVEN a patched response from Orphadata to obtain orphadata_en_product4 and orphadata_en_product6 files

    with open(orphadata_en_product4_reduced_path, "r") as orphadata_en_product4_file:
        content: str = orphadata_en_product4_file.read()

    responses.add(
        responses.GET,
        ORPHA_URLS["orpha_to_hpo"],
        body=content,
        status=200,
    )

    with open(orphadata_en_product6_reduced_path, "r") as orphadata_en_product6_file:
        content: str = orphadata_en_product6_file.read()

    responses.add(
        responses.GET,
        ORPHA_URLS["orpha_to_genes"],
        body=content,
        status=200,
    )

    # GIVEN a temporary directory
    with tempfile.TemporaryDirectory() as dir_name:
        the_dir: pathlib.Path = pathlib.Path(dir_name)
        # WHEN running the command
        result: click.testing.Result = runner.invoke(orpha_cmd, ["-o", the_dir])
        # THEN command should run successfully
        assert result.exit_code == 0
        assert "Download ORPHA" in result.output

        # AND the directory should contain the expected file
        downloaded_files: List = os.listdir(dir_name)
        assert "orphadata_en_product4.xml" in downloaded_files
        assert "orphadata_en_product6.xml" in downloaded_files
