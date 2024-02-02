import logging
from typing import Iterator, Optional

logger = logging.getLogger(__name__)


def parse_constraint_line(line: str, header: list) -> Optional[dict]:
    """Parse a GnomAD constraint formatted line

    In contrast to old ExAC constraint files, these have one line per transcript.
    We keep only the MANE select ones as representative for the gene, and will in practice only retain one (there will commonly be
    at least one ENSEMBL and one RefSeq) as these are later aggregated per gene.
    """
    exac_gene = {}
    splitted_line = line.rstrip().split("\t")
    exac_gene = dict(zip(header, splitted_line))

    if exac_gene["mane_select"] == "false":
        return

    exac_gene["hgnc_symbol"] = exac_gene["gene"]
    exac_gene["pli_score"] = float(exac_gene["lof.pLI"])
    exac_gene["constraint_lof_oe"] = float(exac_gene["lof.oe"])
    exac_gene["constraint_lof_oe_ci_lower"] = float(exac_gene["lof.oe_ci.lower"])
    exac_gene["constraint_lof_oe_ci_upper"] = float(exac_gene["lof.oe_ci.upper"])
    exac_gene["constraint_lof_z"] = float(exac_gene["lof.z_score"])

    exac_gene["constraint_mis_oe"] = float(exac_gene["mis.oe"])
    exac_gene["constraint_mis_oe_ci_lower"] = float(exac_gene["mis.oe_ci.lower"])
    exac_gene["constraint_mis_oe_ci_upper"] = float(exac_gene["mis.oe_ci.upper"])
    exac_gene["constraint_mis_z"] = float(exac_gene["mis.z_score"])

    exac_gene["raw"] = line

    return exac_gene


def parse_constraint_genes(lines: Iterable[str]) -> Iterator[dict]:
    """Parse lines with GnomAD constraint

    This is designed to dump a file with constraint values from GnomAD
    This is downloaded from:

    Args:
        lines(iterable(str)): An iterable with ExAC formated genes
    Yields:
        exac_gene(dict): A dictionary with the relevant information
    """
    header = []
    logger.info("Parsing GnomAD constraint...")
    for index, line in enumerate(lines):
        if index == 0:
            header = line.rstrip().split("\t")
        elif len(line) > 10:
            exac_gene = parse_constraint_line(line, header)
            if exac_gene:
                yield exac_gene
