import logging

from scout.models.hgnc_map import HgncGene

LOG = logging.getLogger(__name__)


def build_hgnc_gene(gene_info: dict, build: bool = "37") -> dict:
    """Build a HGNC gene object"""

    gene_info["build"] = build
    hgnc_gene = HgncGene(**gene_info)
    return hgnc_gene.model_dump(exclude_none=True)
