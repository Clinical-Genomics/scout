import logging
from typing import Iterable, List, Optional

from scout.adapter import MongoAdapter
from scout.load.disease import load_disease_terms
from scout.load.hpo import load_hpo_terms

LOG = logging.getLogger(__name__)


def load_phenotypes(
    adapter: MongoAdapter,
    disease_lines: Optional[Iterable] = None,
    hpo_lines: Optional[Iterable] = None,
    hpo_gene_lines: Optional[Iterable] = None,
    hpo_annotation_lines: Optional[Iterable] = None,
):
    """Load HPO terms and OMIM diseases into database."""

    # Create a map from gene aliases to gene objects
    alias_genes = adapter.genes_by_alias()

    # Load HPO terms
    load_hpo_terms(adapter, hpo_lines, hpo_gene_lines, alias_genes)

    load_disease_terms(
        adapter=adapter,
        genemap_lines=disease_lines,
        genes=alias_genes,
        hpo_disease_lines=hpo_gene_lines,
        hpo_annotation_lines=hpo_annotation_lines,
    )
