import logging
from typing import Iterable, Iterator, Optional

from scout.constants import GENE_CONSTRAINT_LABELS

logger = logging.getLogger(__name__)


def _check_na(value: str) -> Optional[float]:
    """GnomAD gene constraint files will contain NA values for certain genes/transcripts."""

    if not value or value == "NA":
        return None
    return float(value)


def parse_constraint_line(line: str, header: list) -> Optional[dict]:
    """Parse a GnomAD constraint formatted line

    In contrast to old ExAC constraint files, these have one line per transcript.
    We keep only the MANE select ones as representative for the gene, and will in practice only retain one (there will commonly be
    at least one ENSEMBL and one RefSeq) as these are later aggregated per gene.
    """
    split_line = line.rstrip().split("\t")
    gene_constraint = dict(zip(header, split_line))

    if gene_constraint["mane_select"] == "false":
        return

    gene_constraint["hgnc_symbol"] = gene_constraint["gene"]

    for key, header_key in GENE_CONSTRAINT_LABELS.items():
        gene_constraint[key] = _check_na(gene_constraint[header_key])

    gene_constraint["raw"] = line

    return gene_constraint


def parse_constraint_genes(lines: Iterable[str]) -> Iterator[dict]:
    """Parse lines with GnomAD constraint

    This is designed to dump a file with constraint values from GnomAD
    This is downloaded from:

    Args:
        lines(iterable(str)): An iterable with GnomAD constraint tsv formatted lines
    Yields:
        gene_constraint(dict): A dictionary with the relevant constraint information
    """
    header = []
    logger.info("Parsing GnomAD gene constraint...")
    for index, line in enumerate(lines):
        if index == 0:
            header = line.rstrip().split("\t")
        elif len(line) > 10:
            gene_constraint = parse_constraint_line(line, header)
            if gene_constraint:
                yield gene_constraint
