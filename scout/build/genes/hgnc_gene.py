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


def build_hgnc_gene(gene_info: dict, build: bool = "37") -> dict:
    """Build a HGNC gene object"""

    gene_info["build"] = build
    hgnc_gene = HgncGene(**gene_info)
    return hgnc_gene.model_dump(exclude_none=True)
