"""Code for parsing ORPHA formatted files"""
import logging
from typing import Any, Dict

LOG = logging.getLogger(__name__)


def get_orpha_diseases_product6(tree: Any) -> Dict[str, Any]:
    """Get a dictionary with phenotypes

    Uses the orpha numbers as keys and phenotype information as
    values.

    Args:
        Root element of orphadata_en_product6.xml

    Returns:
        orpha_phenotypes_found(dict): A dictionary with ORPHA:orphacode as key and
        dictionaries with phenotype information as values.

        {
             'description': str, # Description of the phenotype
             'hgnc_ids': set(), # Associated hgnc symbols
             'inheritance': set(),  # Associated phenotypes
             'orpha_code': int, # orpha code of phenotype
        }
    """
    LOG.info(f"Parsing Orphadata en_product6")

    orpha_phenotypes_found = {}

    for disorder in tree.iter("Disorder"):
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
