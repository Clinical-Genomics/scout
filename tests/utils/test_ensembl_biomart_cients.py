from typing import Iterator

import pytest
from schug.demo import (
    EXONS_37_FILE_PATH,
    EXONS_38_FILE_PATH,
    GENES_37_FILE_PATH,
    GENES_38_FILE_PATH,
    TRANSCRIPTS_37_FILE_PATH,
    TRANSCRIPTS_38_FILE_PATH,
)
from schug.models.common import Build

from scout.utils.ensembl_biomart_clients import EnsemblBiomartHandler
from scout.utils.handle import get_file_handle

MOCKED_RESPONSE = "requests.get"

SCHUG_BUILD_GENES_PATHS = [
    (Build.build_37, GENES_37_FILE_PATH),
    (Build.build_38, GENES_38_FILE_PATH),
]

SCHUG_BUILD_TRANSCRIPTS_PATHS = [
    (Build.build_37, TRANSCRIPTS_37_FILE_PATH),
    (Build.build_38, TRANSCRIPTS_38_FILE_PATH),
]

SCHUG_BUILD_EXONS_PATHS = [
    (Build.build_37, EXONS_37_FILE_PATH),
    (Build.build_38, EXONS_38_FILE_PATH),
]


@pytest.mark.parametrize("build, path", SCHUG_BUILD_GENES_PATHS)
def test_stream_resource_genes(build, path, mocker):
    """Test the stream_resource Biomart client for downloading genes in both builds."""

    # GIVEN an Ensembl biomart client
    client = EnsemblBiomartHandler(build=build)

    # GIVEN a patched response from Ensembl Biomart, via schug
    mocker.patch.object(
        EnsemblBiomartHandler, "biomart_get", return_value=get_file_handle(str(path))
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
        EnsemblBiomartHandler, "biomart_get", return_value=get_file_handle(str(path))
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
        EnsemblBiomartHandler, "biomart_get", return_value=get_file_handle(str(path))
    )

    # THEN it should stream the gene resource when stream_resource in invoked
    resource_lines: Iterator = client.stream_resource(interval_type="exons")
    # THEN the first line should be the header
    assert list(resource_lines)[0].startswith("Chromosome")
