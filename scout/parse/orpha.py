"""Code for parsing ORPHA formatted files"""
import logging
from typing import Any, Dict, List
from xml.etree.ElementTree import Element

from defusedxml.ElementTree import fromstring

from scout.constants import DISEASE_INHERITANCE_TERMS, INHERITANCE_TERMS_MAPPER

LOG = logging.getLogger(__name__)


def parse_orpha_downloads(lines: List) -> Element:
    """Combine lines of xml file to an element tree"""

    tree: Element = fromstring("\n".join([str(line) for line in lines]))
    return tree


def get_orpha_to_genes_information(lines: List[str]) -> Dict[str, dict]:
    """Get a dictionary with diseases, ORPHA:nr as keys and gene information as values"""
    LOG.info("Parsing Orphadata en_product6")

    orpha_to_genes: Element = parse_orpha_downloads(lines=lines)

    orpha_diseases_found = {}

    # Collect disease and gene information
    for disorder in orpha_to_genes.iter("Disorder"):
        disease = {}

        source = "ORPHA"
        orpha_code = disorder.find("OrphaCode").text
        disease_id = f"{source}:{orpha_code}"
        description = disorder.find("Name").text

        disease["description"] = description
        disease["hgnc_ids"] = set()

        gene_list = disorder.find("DisorderGeneAssociationList")

        #: Include only hgnc_id for Disease-causing gene relations in phenotype
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
                        disease["hgnc_ids"].add(int(reference))
                        break
        orpha_diseases_found[disease_id] = disease

    return orpha_diseases_found


def get_orpha_to_hpo_information(lines: List[str]) -> Dict[str, Any]:
    """Get a dictionary with diseases, ORPHA:nr as keys and related hpo terms as values"""
    LOG.info("Parsing Orphadata en_product4")

    orpha_to_hpo: Element = parse_orpha_downloads(lines=lines)

    orpha_diseases_found = {}

    # Collect disease information
    for disorder in orpha_to_hpo.iter("Disorder"):
        disease = {}

        source = "ORPHA"
        orpha_code = disorder.find("OrphaCode").text
        disease_id = source + ":" + orpha_code
        description = disorder.find("Name").text

        disease["description"] = description
        disease["hgnc_ids"] = set()
        disease["orpha_code"] = int(orpha_code)
        disease["hpo_terms"] = set()
        hpo_list = disorder.find("HPODisorderAssociationList")

        for hpo_association in hpo_list:
            hpo_id = hpo_association.find("HPO").find("HPOId").text
            disease["hpo_terms"].add(hpo_id)

        orpha_diseases_found[disease_id] = disease

    return orpha_diseases_found


def get_orpha_inheritance_information(lines: List[str]) -> Dict[str, dict]:
    """Get a dictionary with diseases, ORPHA:nr as keys and inheritance information as values"""
    LOG.info("Parsing Orphadata en_product9")

    orpha_inheritance: Element = parse_orpha_downloads(lines=lines)
    orpha_diseases_found = {}

    # Collect disease and inheritance information
    for disorder in orpha_inheritance.iter("Disorder"):
        disease = {}

        source = "ORPHA"
        orpha_code = disorder.find("OrphaCode").text
        disease_id = f"{source}:{orpha_code}"
        description = disorder.find("Name").text
        disease["description"] = description
        disease["inheritance"] = set()

        inheritance_list = disorder.find("TypeOfInheritanceList")
        nr = int(inheritance_list.attrib["count"])

        #: Include inheritance
        if nr > 0:
            for inheritance in inheritance_list:
                inheritance_mode = inheritance.find("Name").text
                for term in DISEASE_INHERITANCE_TERMS:
                    if term in inheritance_mode:
                        disease["inheritance"].add(INHERITANCE_TERMS_MAPPER[term])

        orpha_diseases_found[disease_id] = disease
    return orpha_diseases_found
