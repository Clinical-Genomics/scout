"""Code for parsing disease terms from OMIM and ORPHA data"""
import logging
from typing import Dict, List

from scout.parse.hpo_mappings import parse_hpo_annotations
from scout.parse.omim import get_mim_disease
from scout.parse.orpha import (
    get_orpha_inheritance_information,
    get_orpha_to_genes_information,
    get_orpha_to_hpo_information,
)
from scout.utils.scout_requests import fetch_hpo_disease_annotation, fetch_orpha_files

LOG = logging.getLogger(__name__)


def get_all_disease_terms(
    orpha_to_hpo_lines: List,
    orpha_to_genes_lines: List,
    orpha_inheritance_lines: List,
    hpo_annotation_lines: List,
    genemap_lines: List,
) -> Dict:
    #: Collect ORPHA terms including gene and disease annotations from Orphadata
    orpha_disease_terms: Dict[str, dict] = get_orpha_disease_terms(
        orpha_to_hpo_lines=orpha_to_hpo_lines,
        orpha_to_genes_lines=orpha_to_genes_lines,
        orpha_inheritance_lines=orpha_inheritance_lines,
    )

    #: Collect OMIM and ORPHA disease terms including gene and hpo annotations
    omim_disease_terms: Dict[str, dict] = get_omim_disease_terms(
        genemap_lines=genemap_lines, hpo_annotation_lines=hpo_annotation_lines
    )

    #: Combine disease information and return disease_terms to load
    all_disease_terms: Dict = parse_disease_terms(
        omim_disease_terms=omim_disease_terms, orpha_disease_terms=orpha_disease_terms
    )

    return all_disease_terms


def parse_disease_terms(
    omim_disease_terms: Dict[str, dict], orpha_disease_terms: Dict[str, dict]
) -> Dict[str, dict]:
    """Pool disease terms and linked HPO terms and genes from OMIM and ORPHAdata files"""
    LOG.info("Consolidating OMIM and ORPHA disease terms")

    combined_disease_terms = omim_disease_terms.copy()

    # Add missing ORPHA disease-terms parsed from orphadata downloads
    for disease_id, orpha_disease_content in orpha_disease_terms.items():
        if disease_id not in combined_disease_terms:
            combined_disease_terms[disease_id] = {
                "inheritance": orpha_disease_content.get("inheritance", set()),
                "description": orpha_disease_content["description"],
                "hgnc_ids": orpha_disease_content.get("hgnc_ids", set()),
                "hpo_terms": orpha_disease_content.get("hpo_terms", set()),
            }
        else:
            combined_disease_terms[disease_id]["hpo_terms"].update(
                orpha_disease_content.get("hpo_terms", set())
            )
            combined_disease_terms[disease_id]["hgnc_ids"].update(
                orpha_disease_content.get("hgnc_ids", set())
            )
            combined_disease_terms[disease_id]["inheritance"].update(
                orpha_disease_content.get("inheritance", set())
            )
    return combined_disease_terms


def consolidate_gene_and_hpo_annotation(
    hpo_annotations: Dict[str, dict], gene_annotations: Dict[str, dict]
) -> Dict[str, dict]:
    """Annotate disease terms with both gene and hpo information"""

    LOG.info("Consolidating gene and HPO information for disease terms")
    disease_terms: Dict = gene_annotations.copy()
    # If missing, add disease properties to be updated from other files
    for disease_id, disease_content in disease_terms.items():
        if "hpo_terms" not in disease_content:
            disease_content["hpo_terms"] = set()
        if "hgnc_symbols" not in disease_content:
            disease_content["hgnc_symbols"] = set()
        if "hgnc_ids" not in disease_content:
            disease_content["hgnc_ids"] = set()
        if "hpo_terms" not in disease_content:
            disease_content["hpo_terms"] = set()

    #: Add or update diseases to include information from both sources
    for disease_id, hpo_annotation in hpo_annotations.items():
        if disease_id not in disease_terms:
            disease_terms[disease_id] = {
                "inheritance": set(),
                "description": hpo_annotation.get("description", set()),
                "hgnc_symbols": hpo_annotation.get("hgnc_symbols", set()),
                "hpo_terms": hpo_annotation.get("hpo_terms", set()),
                "hgnc_ids": hpo_annotation.get("hgnc_ids", set()),
            }
        else:
            disease_terms[disease_id]["hgnc_symbols"].update(
                hpo_annotation.get("hgnc_symbols", set())
            )
            disease_terms[disease_id]["hpo_terms"].update(hpo_annotation.get("hpo_terms", set()))
            disease_terms[disease_id]["hgnc_ids"].update(hpo_annotation.get("hgnc_ids", set()))

    return disease_terms


def get_omim_disease_terms(genemap_lines: List = None, hpo_annotation_lines: List = None) -> Dict:
    genemap_disease: Dict = get_mim_disease(genemap_lines=genemap_lines)
    #: Fetch hpo information if missing
    if not hpo_annotation_lines:
        hpo_annotation_lines: List = fetch_hpo_disease_annotation()
    omim_hpo_annotations: Dict = parse_hpo_annotations(hpo_annotation_lines)

    # Combine information
    omim_disease_terms: Dict = consolidate_gene_and_hpo_annotation(
        hpo_annotations=omim_hpo_annotations, gene_annotations=genemap_disease
    )

    return omim_disease_terms


def get_orpha_disease_terms(
    orpha_to_genes_lines: List = None,
    orpha_to_hpo_lines: List = None,
    orpha_inheritance_lines: List = None,
) -> Dict:
    """Extract disease-gene and disease-hpo information from ORPHA downloads and combine in disease_terms"""

    #: Fetch information from Orphadata if missing
    if not orpha_to_genes_lines or not orpha_to_hpo_lines or not orpha_inheritance_lines:
        orpha_files: Dict = fetch_orpha_files()
        if not orpha_to_hpo_lines:
            orpha_to_hpo_lines: List = orpha_files["orphadata_en_product4"]
        if not orpha_to_genes_lines:
            orpha_to_genes_lines: List = orpha_files["orphadata_en_product6"]
        if not orpha_inheritance_lines:
            orpha_inheritance_lines: List = orpha_files["en_product9_ages"]

    #: Extract information of genes and hpo relations of orphacodes
    orpha_disease: Dict = get_orpha_to_genes_information(lines=orpha_to_genes_lines)
    orpha_inheritance: Dict = get_orpha_inheritance_information(lines=orpha_inheritance_lines)
    orpha_hpo_annotations: Dict = get_orpha_to_hpo_information(lines=orpha_to_hpo_lines)

    #: Add inheritance to disease
    orpha_disease: Dict = add_inheritance_information(
        orpha_disease=orpha_disease, orpha_inheritance=orpha_inheritance
    )

    #: Combine information
    orpha_disease_terms: Dict = consolidate_gene_and_hpo_annotation(
        gene_annotations=orpha_disease, hpo_annotations=orpha_hpo_annotations
    )

    return orpha_disease_terms


def add_inheritance_information(orpha_disease: Dict, orpha_inheritance: Dict) -> Dict:
    """Adds inheritance information to orpha_disease"""

    LOG.info("Adding inheritance to ORPHA disease terms")

    #: Update diseases already present with inheritance
    for disease_id, disease_information in orpha_disease.items():
        disease_information.update(orpha_inheritance.get(disease_id, set()))
    #: Add disease information for missing diseases
    for disease_id, disease_information in orpha_inheritance.items():
        if disease_id not in orpha_disease:
            orpha_disease[disease_id] = {}
            orpha_disease[disease_id].update(disease_information)

    return orpha_disease
