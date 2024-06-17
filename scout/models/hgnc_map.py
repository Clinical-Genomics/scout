from __future__ import unicode_literals

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


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
    build: str
    chromosome: str
    start: int
    end: int
    length: int
    description: Optional[str] = None
    ensembl_id: Optional[str] = Field(None, alias="ensembl_gene_id")
    aliases: Optional[List[str]] = Field(None, alias="previous_symbols")
    entrez_id: Optional[int] = None
    omim_id: Optional[int] = None
    primary_transcripts: Optional[List[str]] = Field(None, alias="ref_seq")
    ucsc_id: Optional[str] = None
    uniprot_ids: Optional[List[str]] = None
    vega_id: Optional[str] = None
    inheritance_models: Optional[List[str]] = None
    incomplete_penetrance: Optional[bool] = False
    phenotypes: Optional[List[dict]] = None
    pli_score: Optional[float] = None
    constraint_lof_oe: Optional[float] = None
    constraint_lof_oe_ci_lower: Optional[float] = None
    constraint_lof_oe_ci_upper: Optional[float] = None
    constraint_lof_z: Optional[float] = None
    constraint_mis_oe: Optional[float] = None
    constraint_mis_oe_ci_lower: Optional[float] = None
    constraint_mis_oe_ci_upper: Optional[float] = None
    constraint_mis_z: Optional[float] = None

    @model_validator(mode="before")
    def set_gene_length(cls, values) -> "HgncGene":
        """Set gene length."""
        if None in [values.get("end"), values.get("start")]:
            values.update({"length": None})
        else:
            values.update({"length": values.get("end") - values.get("start")})
        return values

    @field_validator("phenotypes", mode="before")
    @classmethod
    def set_phenotypes_inheritance(cls, phenotypes) -> Optional[List[dict]]:
        """Convert field 'inheritance' of each phenotype in phenotypes from set to list."""
        for phenotype in phenotypes:
            phenotype["inheritance_models"] = list(phenotype.get("inheritance", {}))
            phenotype.pop("inheritance", None)

        return phenotypes
