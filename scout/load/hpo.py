import logging
from datetime import datetime
from typing import Dict, Iterable, Optional

from click import progressbar

from scout.adapter import MongoAdapter
from scout.build.hpo import build_hpo_term
from scout.models.phenotype_term import HpoTerm
from scout.parse.hpo_mappings import parse_hpo_to_genes
from scout.parse.hpo_terms import build_hpo_tree
from scout.utils.scout_requests import fetch_hpo_terms, fetch_hpo_to_genes_to_disease

LOG = logging.getLogger(__name__)


def load_hpo_terms(
    adapter: MongoAdapter,
    hpo_lines: Optional[Iterable] = None,
    hpo_gene_lines: Optional[Iterable] = None,
    alias_genes: dict = None,
):
    """Load the hpo terms into the database."""

    if not hpo_lines:
        hpo_lines = fetch_hpo_terms()

    if not hpo_gene_lines:
        hpo_gene_lines = fetch_hpo_to_genes_to_disease()

    hpo_terms = build_hpo_tree(hpo_lines)
    for hpo_id, hpo_term in hpo_terms.items():
        HpoTerm(**hpo_term)  # Validate basic term using pydantic

    # Get a map with HGNC symbols to HGNC ids from scout
    if not alias_genes:
        alias_genes = adapter.genes_by_alias()

    for hpo_to_symbol in parse_hpo_to_genes(hpo_gene_lines):
        hgnc_symbol = hpo_to_symbol["hgnc_symbol"]
        hpo_id = hpo_to_symbol["hpo_id"]

        # Fetch gene info to get correct HGNC id
        gene_info = alias_genes.get(hgnc_symbol)
        if not gene_info:
            continue

        hgnc_id = gene_info["true"]

        if hpo_id not in hpo_terms:
            continue

        hpo_term = hpo_terms[hpo_id]

        if "genes" not in hpo_term:
            hpo_term["genes"] = set()

        hpo_term["genes"].add(hgnc_id)

    if not hpo_terms:
        LOG.error("No HPO terms found. Aborting update without dropping HPO term collection.")
        return

    LOG.info("Dropping old HPO term collection")
    adapter.hpo_term_collection.delete_many({})

    start_time = datetime.now()

    nr_terms = len(hpo_terms)
    hpo_bulk = []
    with progressbar(hpo_terms.values(), label="Loading hpo terms", length=nr_terms) as bar:
        for hpo_info in bar:
            hpo_bulk.append(build_hpo_term(hpo_info))

        if len(hpo_bulk) > 10000:
            adapter.load_hpo_bulk(hpo_bulk)
            hpo_bulk = []

    if hpo_bulk:
        adapter.load_hpo_bulk(hpo_bulk)

    LOG.info("Loading done. Nr of terms loaded {0}".format(nr_terms))
    LOG.info("Time to load terms: {0}".format(datetime.now() - start_time))
