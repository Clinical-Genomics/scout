import logging
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from click import progressbar

from scout.adapter import MongoAdapter
from scout.build.disease import build_disease_term
from scout.parse.hpo_mappings import parse_hpo_annotations, parse_hpo_to_genes
from scout.parse.omim import get_mim_phenotypes
from scout.parse.orpha import get_orpha_diseases_product6
from scout.utils.scout_requests import fetch_hpo_disease_annotation, fetch_orpha_files

LOG = logging.getLogger(__name__)


def load_disease_terms(
    adapter: MongoAdapter,
    genemap_lines: Iterable,
    genes: Optional[dict] = None,
    hpo_annotation_lines: Optional[Iterable] = None,
    orphadata_en_product6_lines: Optional[List] = None,
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
    genemap_disease_terms = get_mim_phenotypes(genemap_lines=genemap_lines)

    if not hpo_annotation_lines:
        hpo_annotation_lines = fetch_hpo_disease_annotation()
    disease_annotations = parse_hpo_annotations(hpo_annotation_lines)

    if not orphadata_en_product6_lines:
        orphadata_en_product6_lines = fetch_orpha_files()["orphadata_en_product6"]
    orpha_annotations = get_orpha_diseases_product6(orphadata_en_product6_lines)

    disease_terms = combine_disease_sources(
        genemap_disease_terms=genemap_disease_terms,
        disease_annotations=disease_annotations,
        orpha_annotations=orpha_annotations,
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


def combine_disease_sources(
    genemap_disease_terms: Dict, disease_annotations: Dict, orpha_annotations: Dict
) -> Dict:
    """Pool disease terms and linked HPO terms and genes from OMIM and ORPHAdata files"""
    # Add OMIM disease terms from genemap
    combined_disease_terms = genemap_disease_terms

    # If missing, add properties to be updated from other files
    for disease_id, content in combined_disease_terms.items():
        if "hpo_terms" not in content:
            content["hpo_terms"] = set()
        if "hgnc_symbols" not in content:
            content["hgnc_symbols"] = set()

    # Add missing OMIM and ORPHA disease-terms parsed from phenotypes.hpoa
    for disease_id, content in disease_annotations.items():
        if disease_id not in combined_disease_terms:
            combined_disease_terms[disease_id] = {
                "inheritance": set(),
                "description": content["description"],
                "hgnc_symbols": content["hgnc_symbols"],
                "hpo_terms": content["hpo_terms"],
            }
        else:
            combined_disease_terms[disease_id]["hgnc_symbols"].update(content["hgnc_symbols"])
            combined_disease_terms[disease_id]["hpo_terms"].update(content["hpo_terms"])

    # Add missing ORPHA disease-terms parsed from Orphadata_product6.xml to disease_terms
    for disease_id, content in orpha_annotations.items():
        if disease_id not in combined_disease_terms:
            combined_disease_terms[disease_id] = {
                "inheritance": set(),
                "description": content["description"],
                "hgnc_ids": content["hgnc_ids"],
            }

    return combined_disease_terms
