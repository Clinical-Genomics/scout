"""Code for parsing disease terms from OMIM and ORPHA data"""
from typing import Dict, List, Any
from scout.parse.orpha import get_orpha_to_genes_information, get_orpha_to_hpo_information
from scout.utils.scout_requests import fetch_hpo_disease_annotation, fetch_orpha_files
from scout.parse.omim import get_mim_phenotypes
from scout.parse.hpo_mappings import parse_hpo_annotations


def get_all_disease_terms(
    orpha_to_hpo_lines, orpha_to_genes_lines, hpo_annotation_lines, genemap_lines
):
    #: Collect ORPHA terms including gene and disease annotations from Orphadata
    orpha_disease_terms: Dict = get_orpha_disease_terms(
        orpha_to_hpo_lines=orpha_to_hpo_lines, orpha_to_genes_lines=orpha_to_genes_lines
    )
    #: Collect OMIM and ORPHA disease terms including gene and hpo annotations
    omim_disease_terms: Dict = get_omim_disease_terms(
        genemap_lines=genemap_lines, hpo_annotation_lines=hpo_annotation_lines
    )

    #: Combine disease information and return disease_terms to load
    all_disease_terms: Dict = parse_disease_terms(
        omim_disease_terms=omim_disease_terms, orpha_disease_terms=orpha_disease_terms
    )

    return all_disease_terms


def parse_disease_terms(omim_disease_terms: Dict, orpha_disease_terms: Dict) -> Dict:
    """Pool disease terms and linked HPO terms and genes from OMIM and ORPHAdata files"""

    combined_disease_terms = omim_disease_terms.copy()

    # Add missing ORPHA disease-terms parsed from orphadata downloads
    for disease_id, orpha_disease_content in orpha_disease_terms.items():
        if disease_id not in combined_disease_terms:
            combined_disease_terms[disease_id] = {
                "inheritance": set(),
                "description": orpha_disease_content["description"],
                "hgnc_ids": orpha_disease_content["hgnc_ids"],
                "hpo_terms": orpha_disease_content.get("hpo_terms", set()),
            }

    return combined_disease_terms


def get_omim_disease_terms(genemap_lines: List = None, hpo_annotation_lines: List = None) -> Dict:
    genemap_disease: Dict = get_mim_phenotypes(genemap_lines=genemap_lines)
    #: Fetch hpo information if missing
    if not hpo_annotation_lines:
        hpo_annotation_lines: List = fetch_hpo_disease_annotation()
    omim_hpo_annotations: Dict = parse_hpo_annotations(hpo_annotation_lines)

    # Combine information
    omim_disease_terms = combine_disease_information(
        hpo_annotations=omim_hpo_annotations, gene_annotations=genemap_disease
    )

    return omim_disease_terms


def combine_disease_information(hpo_annotations, gene_annotations):
    """Annotate disease terms with both gene and hpo information"""
    disease_terms = gene_annotations.copy()
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


# def combine_omim_disease(genemap_disease: Dict, omim_hpo_annotations: Dict) -> Dict:
#     # # Add OMIM disease terms from genemap
#     #
#     omim_disease_terms = genemap_disease.copy()
#
#     # If missing, add properties to be updated from other files
#     for disease_id, combined_disease_content in omim_disease_terms.items():
#         if "hpo_terms" not in combined_disease_content:
#             combined_disease_content["hpo_terms"] = set()
#         if "hgnc_symbols" not in combined_disease_content:
#             combined_disease_content["hgnc_symbols"] = set()
#         if "hpo_terms" not in combined_disease_content:
#             combined_disease_content["hpo_terms"] = set()
#
#     for disease_id, omim_hpo_content in omim_hpo_annotations.items():
#         if disease_id not in omim_disease_terms:
#             omim_disease_terms[disease_id] = {
#                 "inheritance": set(),
#                 "description": omim_hpo_content["description"],
#                 "hgnc_symbols": omim_hpo_content["hgnc_symbols"],
#                 "hpo_terms": omim_hpo_content["hpo_terms"],
#             }
#         else:
#             omim_disease_terms[disease_id]["hgnc_symbols"].update(omim_hpo_content["hgnc_symbols"])
#             omim_disease_terms[disease_id]["hpo_terms"].update(omim_hpo_content["hpo_terms"])
#     return omim_disease_terms


def get_orpha_disease_terms(orpha_to_genes_lines: List = None, orpha_to_hpo_lines: List = None):
    """Extract disease-gene and disease-hpo information from ORPHA downloads and combine in disease_terms"""
    #: Fetch information from Orphadata if missing
    if not orpha_to_genes_lines or not orpha_to_genes_lines:
        orpha_files: Dict = fetch_orpha_files()
        if not orpha_to_hpo_lines:
            orpha_to_hpo_lines: List = orpha_files["orphadata_en_product4"]
        if not orpha_to_genes_lines:
            orpha_to_genes_lines: List = orpha_files["orphadata_en_product6"]

    #: Extract information of genes and hpo relations of orphacodes
    orpha_disease_terms = get_orpha_to_genes_information(lines=orpha_to_genes_lines)
    orpha_hpo_annotations = get_orpha_to_hpo_information(lines=orpha_to_hpo_lines)

    #: Combine information
    orpha_disease_terms = combine_disease_information(
        gene_annotations=orpha_disease_terms, hpo_annotations=orpha_hpo_annotations
    )
    return orpha_disease_terms


# def combine_orpha_disease(orpha_to_genes: Dict = None, orpha_to_hpo: Dict = None) -> Dict:
#     """Annotate disease terms with both gene and hpo information"""
#     orpha_disease_terms = orpha_to_genes.copy()
#
#     for disease_id in orpha_to_hpo:
#         if disease_id in orpha_disease_terms:
#             orpha_disease_terms[disease_id]["hpo_terms"] = set()
#             orpha_disease_terms[disease_id]["hpo_terms"].update(
#                 orpha_to_hpo[disease_id]["hpo_terms"]
#             )
#         else:
#             orpha_disease_terms[disease_id] = orpha_to_hpo[disease_id].copy()
#             orpha_disease_terms[disease_id]["hgnc_ids"] = set()
#             orpha_disease_terms[disease_id]["hpo_terms"] = set()
#
#     return orpha_disease_terms
