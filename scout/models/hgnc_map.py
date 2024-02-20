from __future__ import unicode_literals

from typing import List, Optional


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


class HgncGene(dict):
    """HgncGene dictionary

    'hgnc_id': int, # This is the hgnc id, required:
    'hgnc_symbol': str, # The primary symbol, required
    'ensembl_id': str, # required
    'build': str, # '37' or '38', defaults to '37', required

    'chromosome': str, # required
    'start': int, # required
    'end': int, # required

    'description': str, # Gene description
    'aliases': list(), # Gene symbol aliases, includes hgnc_symbol, str
    'entrez_id': int,
    'omim_id': int,
    'pli_score': float,
    'primary_transcripts': list(), # List of refseq transcripts (str)
    'ucsc_id': str,
    'uniprot_ids': list(), # List of str
    'vega_id': str,

    # Inheritance information
    'inheritance_models': list(), # List of model names
    'incomplete_penetrance': bool, # Acquired from HPO

    # Phenotype information
    'phenotypes': list(), # List of dictionaries with phenotype information
    """

    def __init__(
        self,
        hgnc_id,
        hgnc_symbol,
        ensembl_id,
        chrom,
        start,
        end,
        description=None,
        aliases=None,
        entrez_id=None,
        omim_id=None,
        pli_score=None,
        primary_transcripts=None,
        ucsc_id=None,
        uniprot_ids=None,
        vega_id=None,
        inheritance_models=None,
        incomplete_penetrance=False,
        phenotypes=None,
        build="37",
    ):
        super(HgncGene, self).__init__()
        self["hgnc_id"] = int(hgnc_id)
        self["hgnc_symbol"] = hgnc_symbol
        self["ensembl_id"] = ensembl_id

        self["chromosome"] = chrom
        self["start"] = int(start)
        self["end"] = int(end)
        self["length"] = self["end"] - self["start"]

        self["description"] = description
        self["aliases"] = aliases
        self["primary_transcripts"] = primary_transcripts
        self["inheritance_models"] = inheritance_models
        self["phenotypes"] = phenotypes

        self["entrez_id"] = entrez_id
        if entrez_id:
            self["entrez_id"] = int(entrez_id)

        self["omim_id"] = omim_id
        if omim_id:
            self["omim_id"] = int(omim_id)

        self["ucsc_id"] = ucsc_id
        self["uniprot_ids"] = uniprot_ids
        self["vega_id"] = vega_id

        self["pli_score"] = pli_score
        if pli_score:
            self["pli_score"] = float(pli_score)

        self["incomplete_penetrance"] = incomplete_penetrance

        self["build"] = build
