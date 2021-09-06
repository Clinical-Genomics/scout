"""Code to parse panel information"""
import logging
from datetime import datetime

from scout.utils.date import get_date
from scout.utils.handle import get_file_handle
from scout.utils.link import get_correct_ids

from .omim import get_mim_genes

LOG = logging.getLogger(__name__)

VALID_MODELS = ("AR", "AD", "MT", "XD", "XR", "X", "Y")

MODELS_MAP = {
    "monoallelic_not_imprinted": ["AD"],
    "monoallelic_maternally_imprinted": ["AD"],
    "monoallelic_paternally_imprinted": ["AD"],
    "monoallelic": ["AD"],
    "biallelic": ["AR"],
    "monoallelic_and_biallelic": ["AD", "AR"],
    "monoallelic_and_more_severe_biallelic": ["AD", "AR"],
    "xlinked_biallelic": ["XR"],
    "xlinked_monoallelic": ["XD"],
    "mitochondrial": ["MT"],
    "unknown": [],
}

INCOMPLETE_PENETRANCE_MAP = {"unknown": None, "Complete": None, "Incomplete": True}


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


def parse_gene(gene_info):
    """Parse a gene line with information from a panel file

    Args:
        gene_info(dict): dictionary with gene info

    Returns:
        gene(dict): A dictionary with the gene information
            {
            'hgnc_id': int,
            'hgnc_symbol': str,
            'disease_associated_transcripts': list(str),
            'inheritance_models': list(str),
            'mosaicism': bool,
            'reduced_penetrance': bool,
            'database_entry_version': str,
            }

    """
    gene = {}

    hgnc_id = get_hgnc_identifier(gene_info, id_type="hgnc_id")
    if hgnc_id is not None:
        try:
            hgnc_id = int(hgnc_id)
        except ValueError:
            raise SyntaxError("Invalid hgnc id: {0}".format(hgnc_id))

    gene["hgnc_id"] = hgnc_id

    gene["hgnc_symbol"] = get_hgnc_identifier(gene_info, id_type="hgnc_symbol")
    gene["identifier"] = hgnc_id or gene["hgnc_symbol"]

    # Disease associated transcripts is a ','-separated list of
    # manually curated transcripts
    transcripts = ""
    if "disease_associated_transcripts" in gene_info:
        transcripts = gene_info["disease_associated_transcripts"]
    elif "disease_associated_transcript" in gene_info:
        transcripts = gene_info["disease_associated_transcript"]
    elif "transcripts" in gene_info:
        transcripts = gene_info["transcripts"]

    gene["transcripts"] = [
        transcript.strip() for transcript in transcripts.split(",") if transcript
    ]

    # Genetic disease models is a ','-separated list of manually curated
    # inheritance patterns that are followed for a gene
    models = ""
    if "genetic_disease_models" in gene_info:
        models = gene_info["genetic_disease_models"]
    elif "genetic_disease_model" in gene_info:
        models = gene_info["genetic_disease_model"]
    elif "inheritance_models" in gene_info:
        models = gene_info["inheritance_models"]
    elif "genetic_inheritance_models" in gene_info:
        models = gene_info["genetic_inheritance_models"]

    gene["inheritance_models"] = [
        model.strip() for model in models.split(",") if model.strip() in VALID_MODELS
    ]

    # If a gene is known to be associated with mosaicism this is annotated
    gene["mosaicism"] = bool(gene_info.get("mosaicism"))

    # If a gene is known to have reduced penetrance this is annotated
    gene["reduced_penetrance"] = bool(gene_info.get("reduced_penetrance"))

    # The database entry version is a way to track when a a gene was added or
    # modified, optional
    gene["database_entry_version"] = gene_info.get("database_entry_version")

    return gene


def get_delimiter(line):
    """Try to find out what delimiter to use"""
    delimiters = ["\t", " ", ";"]
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
            raise SyntaxError("Line {0} is malformed".format(i + 1))

        identifier = gene.pop("identifier")

        if identifier not in hgnc_identifiers:
            hgnc_identifiers.add(identifier)
            genes.append(gene)

    return genes


def parse_gene_panel(
    path, institute="cust000", panel_id="test", panel_type="clinical", genes=None, **kwargs
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


def parse_panel_app_gene(app_gene, hgnc_map):
    """Parse a panel app formated gene

    Args:
        app_gene(dict): Dict with panel app info
        hgnc_map(dict): Map from hgnc_symbol to hgnc_id

    Returns:
        gene_info(dict): Scout infromation
    """
    gene_info = {}
    confidence_level = app_gene["LevelOfConfidence"]
    # Return empty gene if not confident gene
    if not confidence_level == "HighEvidence":
        return gene_info

    hgnc_symbol = app_gene["GeneSymbol"]
    # Returns a set of hgnc ids
    hgnc_ids = get_correct_ids(hgnc_symbol, hgnc_map)
    if not hgnc_ids:
        LOG.warning("Gene %s does not exist in database. Skipping gene...", hgnc_symbol)
        return gene_info

    if len(hgnc_ids) > 1:
        LOG.warning("Gene %s has unclear identifier. Choose random id", hgnc_symbol)

    gene_info["hgnc_symbol"] = hgnc_symbol
    for hgnc_id in hgnc_ids:
        gene_info["hgnc_id"] = hgnc_id

    gene_info["reduced_penetrance"] = INCOMPLETE_PENETRANCE_MAP.get(app_gene["Penetrance"])

    inheritance_models = []
    for model in MODELS_MAP.get(app_gene["ModeOfInheritance"], []):
        inheritance_models.append(model)

    gene_info["inheritance_models"] = inheritance_models

    return gene_info


def parse_panel_app_panel(panel_info, hgnc_map, institute="cust000", panel_type="clinical"):
    """Parse a PanelApp panel

    Args:
        panel_info(dict)
        hgnc_map(dict): Map from symbol to hgnc ids
        institute(str)
        panel_type(str)

    Returns:
        gene_panel(dict)
    """
    date_format = "%Y-%m-%dT%H:%M:%S.%f"

    gene_panel = {}
    gene_panel["version"] = float(panel_info["version"])
    gene_panel["date"] = get_date(panel_info["Created"][:-1], date_format=date_format)
    gene_panel["display_name"] = panel_info["SpecificDiseaseName"]
    gene_panel["institute"] = institute
    gene_panel["panel_type"] = panel_type

    LOG.info("Parsing panel %s", gene_panel["display_name"])

    gene_panel["genes"] = []

    nr_low_confidence = 1
    nr_genes = 0
    for nr_genes, gene in enumerate(panel_info["Genes"], 1):
        gene_info = parse_panel_app_gene(gene, hgnc_map)
        if not gene_info:
            nr_low_confidence += 1
            continue
        gene_panel["genes"].append(gene_info)

    LOG.info("Number of genes in panel %s", nr_genes)
    LOG.info("Number of low confidence genes in panel %s", nr_low_confidence)

    return gene_panel


def get_omim_panel_genes(genemap2_lines, mim2gene_lines, alias_genes):
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
            yield {"hgnc_id": hgnc_id_info["true"], "hgnc_symbol": hgnc_symbol}
        else:
            LOG.warning("Gene symbol %s does not exist", hgnc_symbol)
