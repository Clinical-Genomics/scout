from typing import Iterator

import pytest

from scout.demo.resources import (
    exons37_reduced_path,
    exons38_reduced_path,
    genes37_reduced_path,
    genes38_reduced_path,
    transcripts37_reduced_path,
    transcripts38_reduced_path,
)
from scout.utils.ensembl_biomart_clients import EnsemblBiomartHandler
from scout.utils.handle import get_file_handle

SCHUG_BUILD_GENES_PATHS = [
    ("37", genes37_reduced_path),
    ("38", genes38_reduced_path),
]

SCHUG_BUILD_TRANSCRIPTS_PATHS = [
    ("37", transcripts37_reduced_path),
    ("38", transcripts38_reduced_path),
]

SCHUG_BUILD_EXONS_PATHS = [
    ("37", exons37_reduced_path),
    ("38", exons38_reduced_path),
]


@pytest.mark.parametrize("build, path", SCHUG_BUILD_GENES_PATHS)
def test_stream_resource_genes(build, path, mocker):
    """Test the stream_resource Biomart client for downloading genes in both builds."""

    # GIVEN an Ensembl biomart client
    client = EnsemblBiomartHandler(build=build)

    # GIVEN a patched response from Ensembl Biomart, via schug
    mocker.patch.object(
        EnsemblBiomartHandler, "stream_get", return_value=get_file_handle(str(path))
    )

    # THEN it should stream the gene resource when stream_resource in invoked
    resource_lines: Iterator = client.stream_resource(interval_type="genes")
    # THEN the first line should be the header
    assert list(resource_lines)[0].startswith("Chromosome")


@pytest.mark.parametrize("build, path", SCHUG_BUILD_TRANSCRIPTS_PATHS)
def test_stream_resource_transcripts(build, path, mocker):
    """Test the stream_resource Biomart client for downloading transcripts in both builds."""

    # GIVEN an Ensembl biomart client
    client = EnsemblBiomartHandler(build=build)

    # GIVEN a patched response from Ensembl Biomart, via schug
    mocker.patch.object(
        EnsemblBiomartHandler, "stream_get", return_value=get_file_handle(str(path))
    )

    # THEN it should stream the gene resource when stream_resource in invoked
    resource_lines: Iterator = client.stream_resource(interval_type="transcripts")
    # THEN the first line should be the header
    assert list(resource_lines)[0].startswith("Chromosome")


@pytest.mark.parametrize("build, path", SCHUG_BUILD_EXONS_PATHS)
def test_stream_resource_exons(build, path, mocker):
    """Test the stream_resource Biomart client for downloading exons in both builds."""

    # GIVEN an Ensembl biomart client
    client = EnsemblBiomartHandler(build=build)

    # GIVEN a patched response from Ensembl Biomart, via schug
    mocker.patch.object(
        EnsemblBiomartHandler, "stream_get", return_value=get_file_handle(str(path))
    )

    # THEN it should stream the gene resource when stream_resource in invoked
    resource_lines: Iterator = client.stream_resource(interval_type="exons")
    # THEN the first line should be the header
    assert list(resource_lines)[0].startswith("Chromosome")
