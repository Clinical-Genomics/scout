import logging

from scout.models.hgnc_map import HgncGene

LOG = logging.getLogger(__name__)


def build_phenotype(phenotype_info):
    phenotype_obj = {}
    phenotype_obj["mim_number"] = phenotype_info["mim_number"]
    phenotype_obj["description"] = phenotype_info["description"]
    phenotype_obj["inheritance_models"] = list(phenotype_info.get("inheritance", set()))
    phenotype_obj["status"] = phenotype_info["status"]

    return phenotype_obj


def build_hgnc_gene(gene_info, build="37"):
    """Build a hgnc_gene object

    Args:
        gene_info(dict): Gene information

    Returns:
        gene_obj(dict)

        {
            '_id': ObjectId(),
            # This is the hgnc id, required:
            'hgnc_id': int,
            # The primary symbol, required
            'hgnc_symbol': str,
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
            'transcripts': list(), # List of hgnc_transcript

            # Inheritance information
            'inheritance_models': list(), # List of model names
            'incomplete_penetrance': bool, # Acquired from HPO

            # Phenotype information
            'phenotypes': list(), # List of dictionaries with phenotype information
        }
    """
    try:
        hgnc_id = int(gene_info["hgnc_id"])
    except KeyError as err:
        raise KeyError("Gene has to have a hgnc_id")
    except ValueError as err:
        raise ValueError("hgnc_id has to be integer")

    try:
        hgnc_symbol = gene_info["hgnc_symbol"]
    except KeyError as err:
        raise KeyError("Gene has to have a hgnc_symbol")

    try:
        ensembl_id = gene_info["ensembl_gene_id"]
    except KeyError as err:
        raise KeyError("Gene has to have a ensembl_id")

    try:
        chromosome = gene_info["chromosome"]
    except KeyError as err:
        raise KeyError("Gene has to have a chromosome")

    try:
        start = int(gene_info["start"])
    except KeyError as err:
        raise KeyError("Gene has to have a start position")
    except TypeError as err:
        raise TypeError("Gene start has to be a integer")

    try:
        end = int(gene_info["end"])
    except KeyError as err:
        raise KeyError("Gene has to have a end position")
    except TypeError as err:
        raise TypeError("Gene end has to be a integer")

    gene_obj = HgncGene(
        hgnc_id=hgnc_id,
        hgnc_symbol=hgnc_symbol,
        ensembl_id=ensembl_id,
        chrom=chromosome,
        start=start,
        end=end,
        build=build,
    )

    if gene_info.get("description"):
        gene_obj["description"] = gene_info["description"]
        # LOG.debug("Adding info %s", gene_info['description'])

    if gene_info.get("previous_symbols"):
        gene_obj["aliases"] = gene_info["previous_symbols"]

    if gene_info.get("entrez_id"):
        gene_obj["entrez_id"] = int(gene_info["entrez_id"])

    if gene_info.get("omim_id"):
        gene_obj["omim_id"] = int(gene_info["omim_id"])

    if gene_info.get("pli_score"):
        gene_obj["pli_score"] = float(gene_info["pli_score"])

    if gene_info.get("ref_seq"):
        gene_obj["primary_transcripts"] = gene_info["ref_seq"]

    if gene_info.get("ucsc_id"):
        gene_obj["ucsc_id"] = gene_info["ucsc_id"]

    if gene_info.get("uniprot_ids"):
        gene_obj["uniprot_ids"] = gene_info["uniprot_ids"]

    if gene_info.get("vega_id"):
        gene_obj["vega_id"] = gene_info["vega_id"]

    if gene_info.get("incomplete_penetrance"):
        gene_obj["incomplete_penetrance"] = True

    if gene_info.get("inheritance_models"):
        gene_obj["inheritance_models"] = gene_info["inheritance_models"]

    phenotype_objs = []
    for phenotype_info in gene_info.get("phenotypes", []):
        phenotype_objs.append(build_phenotype(phenotype_info))

    if phenotype_objs:
        gene_obj["phenotypes"] = phenotype_objs

    for key in list(gene_obj):
        if gene_obj[key] is None:
            gene_obj.pop(key)

    return gene_obj
