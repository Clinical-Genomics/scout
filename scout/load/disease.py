import logging
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from click import progressbar

from scout.adapter import MongoAdapter
from scout.build.disease import build_disease_term
from scout.parse.hpo_mappings import parse_hpo_annotations, parse_hpo_to_genes
from scout.parse.omim import get_mim_phenotypes
from scout.parse.orpha import get_orpha_phenotypes_product6
from scout.utils.scout_requests import fetch_hpo_disease_annotation, fetch_orpha_files

LOG = logging.getLogger(__name__)


def load_disease_terms(
    adapter: MongoAdapter,
    genemap_lines: Iterable,
    genes: Optional[dict] = None,
    hpo_annotation_lines: Optional[Iterable] = None,
    orphadata_en_product6_tree: Optional[Iterable] = None,
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

    if not hpo_annotation_lines:
        hpo_annotation_lines = fetch_hpo_disease_annotation()
    disease_annotations = parse_hpo_annotations(hpo_annotation_lines)

    if not orphadata_en_product6_tree:
        # TODO: Verify the return of fetch_orpha_files to be a tree
        #  Verify how fetch_function is set ut for other sources to return _lines
        orphadata_en_product6_tree = fetch_orpha_files(product6=True)
    orpha_annotations = get_orpha_phenotypes_product6(orphadata_en_product6_tree)

    # Update disease_terms with all OMIM and ORPHA disease-terms parsed from phenotypes.hpoa file
    for disease_id, content in disease_annotations.items():
        if disease_id not in disease_terms:
            disease_terms[disease_id] = {
                "inheritance": set(),
                "description": content["description"],
                "hgnc_symbols": content["hgnc_symbols"],
            }
    # Update disease_terms with all ORPHA disease-terms parsed from Orphadata_product6.xml
    for disease_id, content in orpha_annotations.items():
        if disease_id not in disease_terms:
            disease_terms[disease_id] = {
                "inheritance": set(),
                "description": content["description"],
                "hgnc_id": content["hgnc_id"],
            }
            #LOG.info(f"Disease after added to terms from orpha {disease_terms[disease_id]}")

    LOG.info("building disease objects")

    disease_objs: List[dict] = []
    for disease_id, disease_info in disease_terms.items():
        #LOG.info(f"Disease term beforew parse and build: {disease_id} and {disease_info}")
        _parse_disease_term_info(
            disease_info=disease_info,
            disease_annotations=disease_annotations,
            disease_id=disease_id,
        )
        #LOG.info(f"Disease term AFTER parse and before build: {disease_id} and {disease_info}")
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


def _parse_disease_term_info(
    disease_info: dict,
    disease_annotations: Dict[str, Any],
    disease_id: str,
):
    """
    Starting from the OMIM disease terms (genemap2), update with HPO terms from
    HPO annotations, add any missing diseases from HPO annotations.
    """
    if "hpo_terms" not in disease_info:
        disease_info["hpo_terms"] = set()
    if disease_id in disease_annotations:
        disease_info["hpo_terms"].update(disease_annotations[disease_id]["hpo_terms"])
