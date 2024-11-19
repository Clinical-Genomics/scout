"""Code to parse panel information"""

import logging
from datetime import datetime
from typing import List

from scout.constants import PANEL_GENE_INFO_MODELS, PANEL_GENE_INFO_TRANSCRIPTS
from scout.utils.date import get_date
from scout.utils.handle import get_file_handle

from .omim import get_mim_genes

LOG = logging.getLogger(__name__)


def get_panel_info(panel_lines=None, panel_id=None, institute=None, **kwargs):
    """Parse metadata for a gene panel

    For historical reasons it is possible to include all information about a gene panel in the
    header of a panel file. This function parses the header.

    Args:
        panel_lines(iterable(str))
        panel_id(str)
        institute(str)
        maintainer(list(user._id))

    Returns:
        panel_info(dict): Dictionary with panel information
    """
    panel_info = {
        "panel_id": panel_id,
        "institute": institute,
        "version": kwargs.get("version"),
        "maintainer": kwargs.get("maintainer"),
        "date": kwargs.get("date"),
        "display_name": kwargs.get("display_name"),
    }

    if panel_lines:
        for line in panel_lines:
            line = line.rstrip()
            if not line.startswith("##"):
                break

            info = line[2:].split("=")
            field = info[0]
            value = info[1]

            if not panel_info.get(field):
                panel_info[field] = value

    panel_info["date"] = get_date(panel_info["date"])

    return panel_info


def get_hgnc_identifier(gene_info, id_type="hgnc_id"):
    """Fetch the hgncid from a gene

    Args:
        gene_info(dict): Dictionary with gene information from a panel file
        id_type(str): in ['hgnc_id', 'hgnc_symbol']

    Returns:
        hgnc_identifier(str)
    """
    hgnc_id_identifiers = ["hgnc_id", "hgnc_idnumber", "hgncid"]
    hgnc_symbol_identifiers = ["hgnc_symbol", "hgncsymbol", "symbol"]

    identifiers = hgnc_id_identifiers
    if id_type == "hgnc_symbol":
        identifiers = hgnc_symbol_identifiers

    for identifier in identifiers:
        if identifier in gene_info:
            return gene_info[identifier]

    return None


def parse_gene(gene_info: dict) -> dict:
    """Parse a gene line with information from a panel file."""

    def get_alias_keys_value(alias_keys: list[str]) -> List[str]:
        """Collect list of strings from the alias keys present in gene_info."""
        return [
            item.strip()
            for alias_key in alias_keys
            if alias_key in gene_info
            for item in gene_info[alias_key].strip('"').split(",")
            if item
        ]

    gene = {}

    # Parse hgnc_id and handle errors
    hgnc_id = get_hgnc_identifier(gene_info, id_type="hgnc_id")
    if hgnc_id is not None:
        try:
            hgnc_id = int(hgnc_id)
        except ValueError:
            raise SyntaxError(f"Invalid hgnc id: {hgnc_id}")

    gene["hgnc_id"] = hgnc_id
    gene["hgnc_symbol"] = get_hgnc_identifier(gene_info, id_type="hgnc_symbol")
    gene["identifier"] = hgnc_id or gene["hgnc_symbol"]

    # Add list values from alias keys
    gene.update(
        {
            "disease_associated_transcripts": get_alias_keys_value(PANEL_GENE_INFO_TRANSCRIPTS),
            "inheritance_models": get_alias_keys_value(PANEL_GENE_INFO_MODELS),
            "custom_inheritance_models": get_alias_keys_value(["custom_inheritance_models"]),
        }
    )

    # Remove empty keys
    gene = {k: v for k, v in gene.items() if v}

    # Add boolean flags if they are True
    gene.update(
        {
            key: True
            for key in ["mosaicism", "reduced_penetrance"]
            if gene_info.get(key) and gene_info.get(key) != ""
        }
    )

    # Add optional fields
    gene.update(
        {
            key: gene_info[key]
            for key in ["database_entry_version", "comment"]
            if gene_info.get(key) and gene_info.get(key) != ""
        }
    )

    return gene


def get_delimiter(line):
    """Try to find out what delimiter to use"""
    delimiters = ["\t", ";"]
    line_length = 0
    delimiter = None

    for alt in delimiters:
        head_line = line.split(alt)
        if len(head_line) <= line_length:
            continue
        line_length = len(head_line)
        delimiter = alt
    return delimiter


def parse_genes(gene_lines):
    """Parse a file with genes and return the hgnc ids

    Args:
        gene_lines(iterable(str)): Stream with genes

    Returns:
        genes(list(dict)): Dictionaries with relevant gene info
    """
    genes = []
    header = []
    hgnc_identifiers = set()
    delimiter = "\t"
    # This can be '\t' or ';'

    # There are files that have '#' to indicate headers
    # There are some files that start with a header line without
    # any special symbol
    for i, line in enumerate(gene_lines):
        line = line.strip()
        if line.startswith("##") or len(line) < 1:
            continue

        if line.startswith("#"):
            # We need to try delimiters
            # We prefer ';' or '\t' byt should accept ' '
            delimiter = get_delimiter(line)
            header = [word.lower() for word in line[1:].split(delimiter)]
            continue
        # If no header symbol(#) assume first line is header
        if i == 0:
            delimiter = get_delimiter(line)

            if "hgnc" in line or "HGNC" in line:
                header = [word.lower() for word in line.split(delimiter)]
                continue
            # If first line is not a header try to sniff what the first
            # columns holds
            if line.split(delimiter)[0].isdigit():
                header = ["hgnc_id"]
            else:
                header = ["hgnc_symbol"]

        gene_info = dict(zip(header, line.split(delimiter)))

        # There are cases when excel exports empty lines that looks like
        # ;;;;;;;. This is a exception to handle these empty lines
        if not any(gene_info.values()):
            continue

        try:
            gene = parse_gene(gene_info)
        except Exception as err:
            LOG.warning(err)
            raise SyntaxError("Line {0} is malformed: {1}".format(i + 1, err))

        identifier = gene.pop("identifier")

        if identifier not in hgnc_identifiers:
            hgnc_identifiers.add(identifier)
            genes.append(gene)

    return genes


def parse_gene_panel(
    path,
    institute="cust000",
    panel_id="test",
    panel_type="clinical",
    genes=None,
    **kwargs,
):
    """Parse the panel info and return a gene panel

    Args:
        path(str): Path to panel file
        institute(str): Name of institute that owns the panel
        panel_id(str): Panel id
        date(datetime.datetime): Date of creation
        version(float)
        full_name(str): Option to have a long name

    Returns:
        gene_panel(dict)
    """
    LOG.info("Parsing gene panel %s", panel_id)
    gene_panel = {}

    gene_panel["path"] = path
    gene_panel["institute"] = institute
    gene_panel["panel_id"] = panel_id
    gene_panel["type"] = panel_type
    gene_panel["date"] = kwargs.get("date") or datetime.now()
    gene_panel["version"] = float(kwargs.get("version") or 1.0)
    gene_panel["display_name"] = kwargs.get("display_name") or panel_id

    if not path:
        panel_handle = genes
    else:
        panel_handle = get_file_handle(gene_panel["path"])
    gene_panel["genes"] = parse_genes(gene_lines=panel_handle)

    return gene_panel


def get_omim_panel_genes(genemap2_lines: list, mim2gene_lines: list, alias_genes: dict):
    """Return all genes that should be included in the OMIM-AUTO panel
    Return the hgnc symbols

    Genes that have at least one 'established' or 'provisional' phenotype connection
    are included in the gene panel

    Args:
        genemap2_lines(iterable)
        mim2gene_lines(iterable)
        alias_genes(dict): A dictionary that maps hgnc_symbol to hgnc_id

    Yields:
        hgnc_symbol(str)
    """
    parsed_genes = get_mim_genes(genemap2_lines, mim2gene_lines)

    status_to_add = set(["established", "provisional"])

    for hgnc_symbol in parsed_genes:
        gene = parsed_genes.get(hgnc_symbol)
        if gene is None:
            continue
        keep = False
        for phenotype_info in gene.get("phenotypes", []):
            if not phenotype_info.get("status") in status_to_add:
                continue
            keep = True
            break
        if not keep:
            continue

        hgnc_id_info = alias_genes.get(hgnc_symbol)
        if not hgnc_id_info:
            for symbol in gene.get("hgnc_symbols", []):
                hgnc_id_info = alias_genes.get(symbol)
                if hgnc_id_info is None:
                    continue
                break

        if hgnc_id_info:
            if hgnc_id_info["true"]:
                hgnc_id = hgnc_id_info["true"]
            elif len(hgnc_id_info.get("ids", ())) == 1:
                hgnc_id = list(hgnc_id_info["ids"])[0]
                LOG.warning(
                    "Gene symbol %s does not exist: using an apparently unique alias for hgnc_id %s",
                    hgnc_symbol,
                    hgnc_id,
                )
            else:
                LOG.warning(
                    "Gene symbol %s does not exist, and as an alias it is not unique", hgnc_symbol
                )
            yield {"hgnc_id": hgnc_id, "hgnc_symbol": hgnc_symbol}
        else:
            LOG.warning("Gene symbol %s does not exist", hgnc_symbol)
