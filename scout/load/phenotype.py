import logging
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from click import progressbar

from scout.adapter import MongoAdapter
from scout.build.disease import build_disease_term
from scout.build.hpo import build_hpo_term
from scout.load.hpo import load_hpo_terms
from scout.models.phenotype_term import HpoTerm
from scout.parse.hpo_mappings import parse_hpo_annotations, parse_hpo_to_genes
from scout.parse.hpo_terms import build_hpo_tree
from scout.parse.omim import get_mim_phenotypes
from scout.utils.scout_requests import (
    fetch_hpo_disease_annotation,
    fetch_hpo_terms,
    fetch_hpo_to_genes_to_disease,
)

LOG = logging.getLogger(__name__)


def load_phenotypes(
    adapter: MongoAdapter,
    disease_lines: Optional[List[str]] = None,
    hpo_lines: Optional[List[str]] = None,
    hpo_gene_lines: Optional[List[str]] = None,
    hpo_annotation_lines: Optional[List[str]] = None,
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
