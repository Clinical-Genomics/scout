import logging
from datetime import datetime
from typing import Any, Dict, Iterable

from click import progressbar

from scout.build.disease import build_disease_term
from scout.build.hpo import build_hpo_term
from scout.parse.hpo_mappings import parse_hpo_annotations, parse_hpo_to_genes
from scout.parse.hpo_terms import build_hpo_tree
from scout.parse.omim import get_mim_phenotypes
from scout.utils.scout_requests import (
    fetch_hpo_disease_annotation,
    fetch_hpo_terms,
    fetch_hpo_to_genes_to_disease,
)

LOG = logging.getLogger(__name__)


def load_hpo(
    adapter,
    disease_lines=None,
    hpo_lines=None,
    hpo_gene_lines=None,
    hpo_annotation_lines=None,
):
    """Load the hpo terms and hpo diseases into database

    Args:
        adapter(MongoAdapter)
        disease_lines(iterable(str)): These are the omim genemap2 information
        hpo_lines(iterable(str)): lines from file http://purl.obolibrary.org/obo/hp.obo
        hpo_gene_lines(iterable(str)): lines from file
            https://ci.monarchinitiative.org/view/hpo/job/hpo.annotations/lastSuccessfulBuild/artifact/rare-diseases/util/annotation/phenotype_to_genes.txt

    """
    # Create a map from gene aliases to gene objects
    alias_genes = adapter.genes_by_alias()

    # Fetch the hpo terms if no file
    if not hpo_lines:
        hpo_lines = fetch_hpo_terms()

    # Fetch the hpo gene information if no file
    if not hpo_gene_lines:
        hpo_gene_lines = fetch_hpo_to_genes_to_disease()

    if not hpo_annotation_lines:
        hpo_annotation_lines = fetch_hpo_disease_annotation()

    load_hpo_terms(adapter, hpo_lines, hpo_gene_lines, alias_genes)

    if not disease_lines:
        LOG.warning("No OMIM (genemap2) information, skipping load disease terms")
        return

    load_disease_terms(
        adapter=adapter,
        genemap_lines=disease_lines,
        genes=alias_genes,
        hpo_disease_lines=hpo_gene_lines,
        hpo_annotation_lines=hpo_annotation_lines,
    )


def load_hpo_terms(
    adapter,
    hpo_lines=None,
    hpo_gene_lines=None,
    alias_genes=None,
):
    """Load the hpo terms into the database

    Parse the hpo lines, build the objects and add them to the database

    Args:
        adapter(MongoAdapter)
        hpo_lines(iterable(str)): lines from file http://purl.obolibrary.org/obo/hp.obo
        hpo_gene_lines(iterable(str)): lines from file
            https://ci.monarchinitiative.org/view/hpo/job/hpo.annotations/lastSuccessfulBuild/artifact/rare-diseases/util/annotation/phenotype_to_genes.txt
        alias_genes
    """
    # Fetch the hpo terms if no file
    if not hpo_lines:
        hpo_lines = fetch_hpo_terms()

    # Parse the terms
    LOG.info("Parsing hpo terms")
    hpo_terms = build_hpo_tree(hpo_lines)

    # Fetch the hpo gene information if no file
    if not hpo_gene_lines:
        hpo_gene_lines = fetch_hpo_to_genes_to_disease()

    # Get a map with hgnc symbols to hgnc ids from scout
    if not alias_genes:
        alias_genes = adapter.genes_by_alias()

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


def _get_hpo_term_to_symbol(hpo_disease_lines: Iterable[str]) -> Dict:
    """
    Parse out a mapping between HPO term id and hgnc symbol from
    the HPO phenotype to genes file.
    """
    hpo_term_to_symbol = {}
    for hpo_to_symbol in parse_hpo_to_genes(hpo_disease_lines):
        hpo_id = hpo_to_symbol["hpo_id"]

        if hpo_id not in hpo_term_to_symbol:
            hpo_term_to_symbol[hpo_id] = set([hpo_to_symbol["hgnc_symbol"]])
        else:
            hpo_term_to_symbol[hpo_id].update(hpo_to_symbol["hgnc_symbol"])
    return hpo_term_to_symbol


def load_disease_terms(
    adapter, genemap_lines, genes=None, hpo_disease_lines=None, hpo_annotation_lines=None
):
    """Load the omim phenotypes into the database

    Parse the phenotypes from genemap2.txt and find the associated hpo terms
    from https://ci.monarchinitiative.org/view/hpo/job/hpo.annotations/lastSuccessfulBuild/artifact/rare-diseases/util/annotation/phenotype_to_genes.txt

    Args:
        adapter(MongoAdapter)
        genemap_lines(iterable(str))
        genes(dict): Dictionary with all genes found in database
        hpo_disease_lines(iterable(str))
        hpo_annotation_lines(iterable(str))
    """
    start_time = datetime.now()

    # Get a map with hgnc symbols to hgnc ids from scout
    if not genes:
        genes = adapter.genes_by_alias()

    # Fetch the disease terms from omim
    disease_terms = get_mim_phenotypes(genemap_lines=genemap_lines)

    if not hpo_disease_lines:
        hpo_disease_lines = fetch_hpo_to_genes_to_disease()
    hpo_term_to_symbol = _get_hpo_term_to_symbol(hpo_disease_lines)

    if not hpo_annotation_lines:
        hpo_annotation_lines = fetch_hpo_disease_annotation()
    disease_annotations = parse_hpo_annotations(hpo_annotation_lines)

    nr_diseases = len(disease_terms)
    with progressbar(
        disease_terms.keys(), label="Loading disease terms", length=nr_diseases
    ) as bar:
        for disease_number in bar:
            disease_info = disease_terms[disease_number]

            _parse_disease_term_info(
                disease_info,
                disease_annotations,
                disease_id="OMIM:{0}".format(disease_number),
                hpo_term_to_symbol=hpo_term_to_symbol,
            )

            disease_obj = build_disease_term(disease_info, genes)

            adapter.load_disease_term(disease_obj)

    LOG.info("Loading done. Nr of diseases loaded {0}".format(nr_diseases))
    LOG.info("Time to load diseases: {0}".format(datetime.now() - start_time))


def _parse_disease_term_info(
    disease_info: Dict,
    disease_annotations: Dict[str, Any],
    disease_id: str,
    hpo_term_to_symbol: Dict[Any, set],
) -> Dict:
    """
    Starting from the OMIM disease terms (genemap2), update with HPO terms from
    HPO annotations, aadd in any missing diseases from hpo_anontations,
    and
    Args:
        disease_annotations(dict(dict)): indexed by disease_id, from phenotype.hpoa
        disease_terms(dict(dict)): indexed by HPO term number, from genemap2.txt
        disease_number: current disease number
        hpo_term_to_symbol(dict(set)):  dict, keyed on HPO term, with sets of gene symbols, from phenotype_to_genes.txt

    Modifies:
        disease_info(dict)
    """

    if disease_id in disease_annotations:
        if "hpo_terms" in disease_info:
            disease_info["hpo_terms"].update(disease_annotations[disease_id]["hpo_terms"])
        else:
            disease_info["hpo_terms"] = set(disease_annotations[disease_id]["hpo_terms"])

        for hpo_term in disease_info["hpo_terms"]:
            if hpo_term not in hpo_term_to_symbol:
                continue

            if disease_info["hgnc_symbols"]:
                disease_info["hgnc_symbols"].update(hpo_term_to_symbol[hpo_term])
            else:
                disease_info["hgnc_symbols"] = hpo_term_to_symbol[hpo_term]
