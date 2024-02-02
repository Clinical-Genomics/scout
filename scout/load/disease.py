import logging
from datetime import datetime
from typing import Dict, Iterable, List, Optional

from click import progressbar

from scout.adapter import MongoAdapter
from scout.build.disease import build_disease_term
from scout.parse.disease_terms import get_all_disease_terms
from scout.parse.hpo_mappings import parse_hpo_to_genes

LOG = logging.getLogger(__name__)


def load_disease_terms(
    adapter: MongoAdapter,
    genemap_lines: List[str],
    genes: Optional[dict] = None,
    hpo_annotation_lines: Optional[List] = None,
    orpha_to_hpo_lines: Optional[List] = None,
    orpha_to_genes_lines: Optional[List] = None,
    orpha_inheritance_lines: Optional[List] = None,
):
    """Load the diseases into the database."""
    if not genemap_lines:
        LOG.warning("No OMIM (genemap2) information, skipping load disease terms")
        return

    start_time = datetime.now()

    # Get a map with hgnc symbols to hgnc ids from scout
    if not genes:
        genes = adapter.genes_by_alias()

    # Combine disease information
    disease_terms = get_all_disease_terms(
        genemap_lines=genemap_lines,
        hpo_annotation_lines=hpo_annotation_lines,
        orpha_to_hpo_lines=orpha_to_hpo_lines,
        orpha_to_genes_lines=orpha_to_genes_lines,
        orpha_inheritance_lines=orpha_inheritance_lines,
    )

    LOG.info("building disease objects")

    disease_objs: List[dict] = []
    for disease_id, disease_info in disease_terms.items():
        disease_objs.append(
            build_disease_term(
                disease_id=disease_id,
                disease_info=disease_info,
                alias_genes=genes,
            )
        )

    LOG.info("Dropping disease terms")
    adapter.disease_term_collection.delete_many({})
    LOG.debug("Disease terms dropped")

    nr_diseases = len(disease_objs)
    LOG.info("Loading new disease terms")

    with progressbar(disease_objs, length=nr_diseases) as bar:
        for disease_obj in bar:
            adapter.load_disease_term(disease_obj)

    LOG.info(f"Loading done. Nr of diseases loaded {nr_diseases}")
    LOG.info(f"Time to load diseases: {datetime.now() - start_time}")


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
