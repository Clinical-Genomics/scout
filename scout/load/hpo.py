import logging

from datetime import datetime

from click import progressbar

from scout.parse.hpo import (
    parse_hpo_phenotypes,
    parse_hpo_diseases,
    parse_hpo_obo,
    parse_hpo_to_genes,
    build_hpo_tree,
)
from scout.utils.scout_requests import (
    fetch_hpo_terms,
    fetch_hpo_to_genes,
    fetch_hpo_phenotype_to_terms,
)

from scout.parse.omim import get_mim_phenotypes
from scout.build.hpo import build_hpo_term
from scout.build.disease import build_disease_term

from pprint import pprint as pp

LOG = logging.getLogger(__name__)


def load_hpo(
    adapter, disease_lines, hpo_disease_lines=None, hpo_lines=None, hpo_gene_lines=None
):
    """Load the hpo terms and hpo diseases into database

    Args:
        adapter(MongoAdapter)
        disease_lines(iterable(str)): These are the omim genemap2 information
        hpo_lines(iterable(str))
        disease_lines(iterable(str))
        hpo_gene_lines(iterable(str))
    """
    # Create a map from gene aliases to gene objects
    alias_genes = adapter.genes_by_alias()

    # Fetch the hpo terms if no file
    if not hpo_lines:
        hpo_lines = fetch_hpo_terms()

    # Fetch the hpo gene information if no file
    if not hpo_gene_lines:
        hpo_gene_lines = fetch_hpo_to_genes()

    # Fetch the hpo phenotype information if no file
    if not hpo_disease_lines:
        hpo_disease_lines = fetch_hpo_phenotype_to_terms()

    load_hpo_terms(adapter, hpo_lines, hpo_gene_lines, alias_genes)

    if not disease_lines:
        LOG.warning("No omim information, skipping to load disease terms")
        return

    load_disease_terms(adapter, disease_lines, alias_genes, hpo_disease_lines)


def load_hpo_terms(adapter, hpo_lines=None, hpo_gene_lines=None, alias_genes=None):
    """Load the hpo terms into the database

    Parse the hpo lines, build the objects and add them to the database

    Args:
        adapter(MongoAdapter)
        hpo_lines(iterable(str))
        hpo_gene_lines(iterable(str))
    """

    # Fetch the hpo terms if no file
    if not hpo_lines:
        hpo_lines = fetch_hpo_terms()

    # Fetch the hpo gene information if no file
    if not hpo_gene_lines:
        hpo_gene_lines = fetch_hpo_to_genes()

    # Parse the terms
    LOG.info("Parsing hpo terms")
    hpo_terms = build_hpo_tree(hpo_lines)

    # Get a map with hgnc symbols to hgnc ids from scout
    if not alias_genes:
        alias_genes = adapter.genes_by_alias()

    LOG.info("Adding gene information to hpo terms ...")
    for hpo_to_symbol in parse_hpo_to_genes(hpo_gene_lines):
        hgnc_symbol = hpo_to_symbol["hgnc_symbol"]
        hpo_id = hpo_to_symbol["hpo_id"]

        # Fetch gene info to get correct hgnc id
        gene_info = alias_genes.get(hgnc_symbol)
        if not gene_info:
            continue

        hgnc_id = gene_info["true"]

        if hpo_id not in hpo_terms:
            continue

        hpo_term = hpo_terms[hpo_id]

        if not "genes" in hpo_term:
            hpo_term["genes"] = set()

        hpo_term["genes"].add(hgnc_id)

    start_time = datetime.now()

    LOG.info("Loading the hpo terms...")
    nr_terms = len(hpo_terms)
    hpo_bulk = []
    with progressbar(
        hpo_terms.values(), label="Loading hpo terms", length=nr_terms
    ) as bar:

        for hpo_info in bar:
            hpo_bulk.append(build_hpo_term(hpo_info))

        if len(hpo_bulk) > 10000:
            adapter.load_hpo_bulk(hpo_bulk)
            hpo_bulk = []

    if hpo_bulk:
        adapter.load_hpo_bulk(hpo_bulk)

    LOG.info("Loading done. Nr of terms loaded {0}".format(nr_terms))
    LOG.info("Time to load terms: {0}".format(datetime.now() - start_time))


def load_disease_terms(adapter, genemap_lines, genes=None, hpo_disease_lines=None):
    """Load the omim phenotypes into the database

    Parse the phenotypes from genemap2.txt and find the associated hpo terms
    from ALL_SOURCES_ALL_FREQUENCIES_diseases_to_genes_to_phenotypes.txt.

    Args:
        adapter(MongoAdapter)
        genemap_lines(iterable(str))
        genes(dict): Dictionary with all genes found in database
        hpo_disease_lines(iterable(str))

    """
    # Get a map with hgnc symbols to hgnc ids from scout
    if not genes:
        genes = adapter.genes_by_alias()

    # Fetch the disease terms from omim
    disease_terms = get_mim_phenotypes(genemap_lines=genemap_lines)

    if not hpo_disease_lines:
        hpo_disease_lines = fetch_hpo_phenotype_to_terms()
    hpo_diseases = parse_hpo_diseases(hpo_disease_lines)

    start_time = datetime.now()
    nr_diseases = None

    LOG.info("Loading the hpo disease...")
    for nr_diseases, disease_number in enumerate(disease_terms):
        disease_info = disease_terms[disease_number]
        disease_id = "OMIM:{0}".format(disease_number)

        if disease_id in hpo_diseases:
            hpo_terms = hpo_diseases[disease_id]["hpo_terms"]
            if hpo_terms:
                disease_info["hpo_terms"] = hpo_terms
        disease_obj = build_disease_term(disease_info, genes)

        adapter.load_disease_term(disease_obj)

    LOG.info("Loading done. Nr of diseases loaded {0}".format(nr_diseases))
    LOG.info("Time to load diseases: {0}".format(datetime.now() - start_time))
