import logging
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from click import progressbar

from scout.adapter import MongoAdapter
from scout.build.disease import build_disease_term
from scout.parse.hpo_mappings import parse_hpo_annotations, parse_hpo_to_genes
from scout.parse.omim import get_mim_phenotypes
from scout.utils.scout_requests import fetch_hpo_disease_annotation, fetch_hpo_to_genes_to_disease

LOG = logging.getLogger(__name__)


def load_disease_terms(
    adapter: MongoAdapter,
    genemap_lines: Iterable,
    genes: Optional[dict] = None,
    hpo_disease_lines: Optional[Iterable] = None,
    hpo_annotation_lines: Optional[Iterable] = None,
):
    """Load the diseases into the database."""

    if not genemap_lines:
        LOG.warning("No OMIM (genemap2) information, skipping load disease terms")
        return

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

    LOG.info("building disease objects")

    disease_objs: List[dict] = []
    for disease_nr, disease_info in disease_terms.items():
        disease_id = f"OMIM:{disease_nr}"
        if disease_id not in disease_annotations:
            continue
        _parse_disease_term_info(
            disease_info=disease_info,
            disease_annotations=disease_annotations,
            disease_id=disease_id,
            hpo_term_to_symbol=hpo_term_to_symbol,
        )
        disease_objs.append(build_disease_term(disease_info=disease_info, alias_genes=genes))

    LOG.info("Dropping disease terms")
    adapter.disease_term_collection.delete_many({})
    LOG.debug("Disease terms dropped")

    nr_diseases = len(disease_objs)
    LOG.info("Loading new disease terms")

    with progressbar(disease_objs, length=nr_diseases) as bar:
        for disease_obj in bar:
            adapter.load_disease_term(disease_obj)

    LOG.info(f"Loading done. Nr of diseases loaded {nr_diseases}")
    LOG.info("Time to load diseases: {0}".format(datetime.now() - start_time))


def _get_hpo_term_to_symbol(hpo_disease_lines: Iterable[str]) -> Dict:
    """
    Parse out a mapping between HPO term id and hgnc symbol from
    the HPO phenotype to genes file.
    """
    hpo_term_to_symbol = {}
    for hpo_to_symbol in parse_hpo_to_genes(hpo_disease_lines):
        hpo_id = hpo_to_symbol["hpo_id"]
        hgnc_symbol = hpo_to_symbol["hgnc_symbol"]

        if hpo_id not in hpo_term_to_symbol:
            hpo_term_to_symbol[hpo_id] = set([hgnc_symbol])
        else:
            hpo_term_to_symbol[hpo_id].add(hgnc_symbol)
    return hpo_term_to_symbol


def _parse_disease_term_info(
    disease_info: Dict,
    disease_annotations: Dict[str, Any],
    disease_id: str,
    hpo_term_to_symbol: Dict[Any, set],
):
    """
    Starting from the OMIM disease terms (genemap2), update with HPO terms from
    HPO annotations, add any missing diseases from HPO annotations.
    """

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
