"""Code for parsing ORPHA formatted files"""
import logging
from typing import Any, Dict

LOG = logging.getLogger(__name__)


def get_orpha_phenotypes_product6(tree: Any) -> Dict[str, Any]:
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
             'hgnc_symbols': set(), # Associated hgnc symbols
             'inheritance': set(),  # Associated phenotypes
             'orpha_code': int, # orpha code of phenotype
        }
    """
    orpha_phenotypes_found = {}

    for disorder in tree.iter("Disorder"):
        phenotype = {}

        source = "ORPHA"
        orpha_code = disorder.find("OrphaCode").text
        phenotype_id = source + ":" + orpha_code
        description = disorder.find("Name").text

        phenotype["description"] = description
        phenotype["hgnc"] = set()
        phenotype["orpha_code"] = int(orpha_code)

        LOG.info(f"Now listing {source}:{orpha_code}, aka {phenotype['description']}")
        #: For each disorder, find and extract gene information from hgnc to be added to phenotype
        for external_reference in disorder.iter("ExternalReference"):
            gene_source = external_reference.find("Source").text
            if gene_source == "HGNC":
                reference = external_reference.find("Reference").text
                phenotype["hgnc"].add(reference)
        orpha_phenotypes_found[phenotype_id] = phenotype

        #: Verify that the number of expected and saved hgnc-genes match
        nr_of_genes = int(disorder.find("DisorderGeneAssociationList").attrib["count"])
        nr_of_genes_saved = len(phenotype["hgnc"])
        if nr_of_genes != nr_of_genes_saved:
            LOG.debug(
                f"{phenotype_id} had a missmatch between the expected number of genes ({nr_of_genes})"
                f" and the nr f HGNC id:s saved ({nr_of_genes_saved})"
            )

    return orpha_phenotypes_found
