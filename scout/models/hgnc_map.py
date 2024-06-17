from __future__ import unicode_literals

from typing import List, Optional

from pydantic import BaseModel


class Exon(dict):
    """Exon dictionary

    "exon_id": str, # str(chrom-start-end)
    "chrom": str,
    "start": int,
    "end": int,
    "transcript": str, # ENST ID
    "hgnc_id": int,      # HGNC_id
    "rank": int, # Order of exon in transcript
    "strand": int, # 1 or -1
    "build": str, # Genome build

    """

    def __init__(self, exon_id, chrom, start, end, transcript, hgnc_id, rank, strand, build="37"):
        super(Exon, self).__init__()
        self["exon_id"] = exon_id
        self["chrom"] = chrom
        self["start"] = int(start)
        self["end"] = int(end)
        self["transcript"] = transcript
        self["hgnc_id"] = hgnc_id
        self["rank"] = int(rank)
        self["strand"] = int(strand)
        self["build"] = build


class HgncTranscript(dict):
    """Model for a transcript dictionary"""

    def __init__(
        self,
        transcript_id: str,
        hgnc_id: int,
        chrom: str,
        start: int,
        end: int,
        is_primary: bool = False,
        refseq_id: Optional[str] = None,
        refseq_identifiers: List[str] = None,
        build: str = "37",
        mane_select: Optional[str] = None,
        mane_plus_clinical: Optional[str] = None,
    ):
        super(HgncTranscript, self).__init__()
        self["ensembl_transcript_id"] = transcript_id
        self["hgnc_id"] = int(hgnc_id)
        self["chrom"] = chrom
        self["start"] = int(start)
        self["end"] = int(end)
        self["is_primary"] = is_primary
        self["refseq_id"] = refseq_id
        self["refseq_identifiers"] = refseq_identifiers
        self["build"] = build
        self["length"] = self["end"] - self["start"]
        if build == "38":
            if mane_select:
                self["mane_select"] = mane_select
            if mane_plus_clinical:
                self["mane_plus_clinical"] = mane_plus_clinical


class HgncGene(BaseModel):
    hgnc_id: int
    hgnc_symbol: str
    ensembl_id: str
    build: str
    chromosome: str
    start: int
    end: int
    length: int
    description: str
    aliases: List[str]
    entrez_id: int
    omim_id: int
    primary_transcripts: List[str]
    ucsc_id: str
    uniprot_ids: List[str]
    vega_id: str
    inheritance_models: Optional[str]
    incomplete_penetrance: bool
    phenotypes: List[dict]
    pli_score: float
    constraint_lof_oe: Optional[float]
    constraint_lof_oe_ci_lower: Optional[float]
    constraint_lof_oe_ci_upper: Optional[float]
    constraint_lof_z: Optional[float]
    constraint_mis_oe: Optional[float]
    constraint_mis_oe_ci_lower: Optional[float]
    constraint_mis_oe_ci_upper: Optional[float]
    constraint_mis_z: Optional[float]
