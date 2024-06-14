import logging
from typing import Dict, Optional

from scout.constants import GENE_CONSTRAINT_LABELS
from scout.models.hgnc_map import HgncGene

LOG = logging.getLogger(__name__)


def build_phenotype(phenotype_info):
    phenotype_obj = {}
    phenotype_obj["mim_number"] = phenotype_info["mim_number"]
    phenotype_obj["description"] = phenotype_info["description"]
    phenotype_obj["inheritance_models"] = list(phenotype_info.get("inheritance", set()))
    phenotype_obj["status"] = phenotype_info["status"]

    return phenotype_obj


def build_hgnc_gene(
    gene_info: dict, cytoband_coords: Dict[str, dict], build: str = "37"
) -> Optional[dict]:
    """Build a hgnc_gene object

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
    if gene_info is None:
        return

    cytoband_chrom = None
    cytoband_start = None
    cytoband_end = None

    if gene_info.get("chromosome") is None:  # Gene not present in Ensembl.
        # Try to use cytoband coordinates instead
        cytoband_coords: Optional[dict] = cytoband_coords.get(gene_info["location"])
        if not cytoband_coords:
            LOG.warning(
                f"Gene {gene_info.get('hgnc_symbol') or gene_info.get('hgnc_id')} doesn't have coordinates and cytoband not present in database, skipping."
            )
            return
        cytoband_chrom: str = cytoband_coords["chromosome"]
        cytoband_start: int = cytoband_coords["start"]
        cytoband_end: int = cytoband_coords["stop"]

    chromosome: Optional[str] = gene_info.get("chromosome") or cytoband_chrom
    start: Optional[int] = int(gene_info.get("start")) if gene_info.get("start") else cytoband_start
    end: Optional[int] = int(gene_info.get("end")) if gene_info.get("end") else cytoband_end

    try:
        gene_obj = HgncGene(
            hgnc_id=gene_info.get("hgnc_id"),
            hgnc_symbol=gene_info.get("hgnc_symbol"),
            ensembl_id=gene_info.get("ensembl_gene_id"),
            chrom=chromosome,
            start=start,
            end=end,
            build=build,
        )
    except Exception as ex:
        LOG.error(
            f"failed to build gene {gene_info.get('hgnc_id') or gene_info.get('hgnc_symbol')}: {ex}"
        )
        return

    for key in ["hgnc_id", "hgnc_symbol", "chromosome", "start", "end"]:
        if gene_obj.get(key) is None:
            LOG.warning(f"Gene {gene_obj} is missing {key}, skipping.")
            return

    if gene_info.get("description"):
        gene_obj["description"] = gene_info["description"]
        # LOG.debug("Adding info %s", gene_info['description'])

    if gene_info.get("previous_symbols"):
        gene_obj["aliases"] = gene_info["previous_symbols"]

    if gene_info.get("entrez_id"):
        gene_obj["entrez_id"] = int(gene_info["entrez_id"])

    if gene_info.get("omim_id"):
        gene_obj["omim_id"] = int(gene_info["omim_id"])

    for constraint in GENE_CONSTRAINT_LABELS.keys():
        if gene_info.get(constraint):
            gene_obj[constraint] = float(gene_info[constraint])

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
