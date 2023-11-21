import logging

from typing import Dict, Iterator
from schug.load.biomart import EnsemblBiomartClient
from schug.models.common import Build as SchugBuild

LOG = logging.getLogger(__name__)

BUILD_37 = "GRCh37"
BUILD_38 = "GRCh38"

BUILDS: Dict(str, str) = {
    "37" : BUILD_37,
    "38" : BUILD_38,
}

CHROMOSOME_NAME_37: str = "Chromosome Name"
CHROMOSOME_NAME_38: str = "Chromosome/scaffold name"
ENSEMBL_GENE_ID_37: str = "Ensembl Gene ID"
ENSEMBL_GENE_ID_38: str = "Gene stable ID"

GENES_FILE_HEADER: Dict[str, List[str]] = {
    BUILD_37: [
        CHROMOSOME_NAME_37,
        "Gene Start (bp)",
        "Gene End (bp)",
        ENSEMBL_GENE_ID_37,
        "HGNC symbol",
        "HGNC ID(s)",
    ],
    BUILD_38: [
        CHROMOSOME_NAME_38,
        "Gene start (bp)",
        "Gene end (bp)",
        ENSEMBL_GENE_ID_38,
        "HGNC symbol",
        "HGNC ID",
    ],
}

TRANSCRIPTS_FILE_HEADER: Dict[str, List[str]] = {
    BUILD_37: [
        CHROMOSOME_NAME_37,
        ENSEMBL_GENE_ID_37,
        "Ensembl Transcript ID",
        "Transcript Start (bp)",
        "Transcript End (bp)",
        "RefSeq mRNA [e.g. NM_001195597]",
        "RefSeq mRNA predicted [e.g. XM_001125684]",
        "RefSeq ncRNA [e.g. NR_002834]",
    ],
    BUILD_38: [
        CHROMOSOME_NAME_38,
        ENSEMBL_GENE_ID_38,
        "Transcript stable ID",
        "Transcript start (bp)",
        "Transcript end (bp)",
        "RefSeq mRNA ID",
        "RefSeq mRNA predicted ID",
        "RefSeq ncRNA ID",
        "RefSeq match transcript (MANE Select)",
        "RefSeq match transcript (MANE Plus Clinical)",
    ],
}

EXONS_FILE_HEADER: Dict[str, List[str]] = {
    BUILD_37: [
        CHROMOSOME_NAME_37,
        ENSEMBL_GENE_ID_37,
        "Ensembl Transcript ID",
        "Ensembl Exon ID",
        "Exon Chr Start (bp)",
        "Exon Chr End (bp)",
        "5' UTR Start",
        "5' UTR End",
        "3' UTR Start",
        "3' UTR End",
        "Strand",
        "Exon Rank in Transcript",
    ],
    BUILD_38: [
        CHROMOSOME_NAME_38,
        ENSEMBL_GENE_ID_38,
        "Transcript stable ID",
        "Exon stable ID",
        "Exon region start (bp)",
        "Exon region end (bp)",
        "5' UTR start",
        "5' UTR end",
        "3' UTR start",
        "3' UTR end",
        "Strand",
        "Exon rank in transcript",
    ],
}

class EnsemblBiomartHandler:
    """A class that handles Ensembl genes, transcripts and exons downloads via schug."""

    def __init__(self, build:str = "37"):

    def read_resource_lines(build: str, interval_type: IntervalType) -> Iterator[str]:
        """Returns lines of a remote Ensembl Biomart resource (genes, transcripts or exons) in a given genome build."""

        shug_client: EnsemblBiomartClient = ENSEMBL_RESOURCE_CLIENT[interval_type](
            build=SchugBuild(build)
        )
        url: str = shug_client.build_url(xml=shug_client.xml)
        response: requests.models.responses = requests.get(url, stream=True)
        return response.iter_lines(decode_unicode=True)




