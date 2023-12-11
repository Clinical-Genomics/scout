"""Code for parsing ORPHA formatted files"""
import logging
from typing import Any, Dict, List
from xml.etree.ElementTree import Element

from defusedxml.ElementTree import fromstring

LOG = logging.getLogger(__name__)


def parse_orpha_downloads(lines: List) -> Element:
    """Combine lines of xml file to an element tree"""

    tree = fromstring("\n".join([str(line) for line in lines]))
    LOG.info(f"My tree is a {type(tree)}")
    return tree


def get_orpha_to_genes_information(lines: List) -> Dict[str, Any]:
    """Get a dictionary with diseases, ORPHA:nr as keys and gene information as values"""
    LOG.info("Parsing Orphadata en_product6")

    orpha_to_genes: Element = parse_orpha_downloads(lines=lines)

    orpha_phenotypes_found = {}

    for disorder in orpha_to_genes.iter("Disorder"):
        phenotype = {}

        source = "ORPHA"
        orpha_code = disorder.find("OrphaCode").text
        phenotype_id = source + ":" + orpha_code
        description = disorder.find("Name").text

        phenotype["description"] = description
        phenotype["hgnc_ids"] = set()
        phenotype["orpha_code"] = int(orpha_code)

        gene_list = disorder.find("DisorderGeneAssociationList")

        #: Include hgnc_id for Disease-causing gene relations in phenotype
        for gene_association in gene_list:
            gene_association_type = (
                gene_association.find("DisorderGeneAssociationType").find("Name").text
            )
            inclusion_term = "Disease-causing"

            if inclusion_term in gene_association_type:
                for external_reference in gene_association.iter("ExternalReference"):
                    gene_source = external_reference.find("Source").text

                    if gene_source == "HGNC":
                        reference = external_reference.find("Reference").text
                        phenotype["hgnc_ids"].add(reference)
                        break
        orpha_phenotypes_found[phenotype_id] = phenotype
    return orpha_phenotypes_found


def get_orpha_to_hpo_information(lines: List) -> Dict[str, Any]:
    """Get a dictionary with diseases, ORPHA:nr as keys and related hpo terms as values"""
    LOG.info("Parsing Orphadata en_product4")

    orpha_to_hpo: Element = parse_orpha_downloads(lines=lines)
    LOG.info(orpha_to_hpo)
    orpha_diseases_found = {}

    for disorder in orpha_to_hpo.iter("Disorder"):
        LOG.info(disorder)
        disease = {}

        source = "ORPHA"
        orpha_code = disorder.find("OrphaCode").text
        phenotype_id = source + ":" + orpha_code
        description = disorder.find("Name").text

        disease["description"] = description
        disease["hgnc_ids"] = set()
        disease["orpha_code"] = int(orpha_code)
        disease["hpo_terms"] = set()
        hpo_list = disorder.find("HPODisorderAssociationList")

        #: Include hpoid for all phenotypes occurring in the disease
        for hpo_association in hpo_list:
            hpo_id = hpo_association.find("HPO").find("HPOId").text
            disease["hpo_terms"].add(hpo_id)

        orpha_diseases_found[phenotype_id] = disease
    return orpha_diseases_found


def get_orpha_disease_terms(orpha_to_genes_lines: List = None, orpha_to_hpo_lines: List = None):
    orpha_disease_terms = get_orpha_to_genes_information(lines=orpha_to_genes_lines)
    orpha_hpo_annotations = get_orpha_to_hpo_information(lines=orpha_to_hpo_lines)
    LOG.info(f"ORpha disease: {orpha_disease_terms}")
    orpha_disease_terms = combine_orpha_disease(
        orpha_to_genes=orpha_disease_terms, orpha_to_hpo=orpha_hpo_annotations
    )
    return orpha_disease_terms


def combine_orpha_disease(orpha_to_genes: Dict = None, orpha_to_hpo: Dict = None) -> Dict:
    orpha_disease_terms = orpha_to_genes.copy()

    for disease_id in orpha_to_hpo:
        if disease_id in orpha_disease_terms:
            orpha_disease_terms[disease_id]["hpo_terms"] = set()
            orpha_disease_terms[disease_id]["hpo_terms"].update(
                orpha_to_hpo[disease_id]["hpo_terms"]
            )
        else:
            orpha_disease_terms[disease_id] = orpha_to_hpo[disease_id].copy()
            orpha_disease_terms[disease_id]["hgnc_ids"] = set()
            orpha_disease_terms[disease_id]["hpo_terms"] = set()
        LOG.info(f"orpha to hpo HAS hgmnc-id")
    return orpha_disease_terms
