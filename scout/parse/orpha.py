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
        phenotype["hgnc_id"] = set()
        phenotype["orpha_code"] = int(orpha_code)

        gene_list= disorder.find("DisorderGeneAssociationList")
        LOG.info(f"Genelist: {gene_list}")
        for gene_association in gene_list:
            #LOG.info(f"Geneassociation: {gene_association}")
            gene_association_type=gene_association.find("DisorderGeneAssociationType").find("Name").text
            #LOG.info(f"Geneassociation text: {gene_association_type}")
            # TODO: create list of associations to include and replace string below
            if gene_association_type=="Disease-causing germline mutation(s) in":
               # LOG.info(f"Geneassociation text == chosen, loop genes inside")
                # : For each gene association og selected type, find and extract gene information from hgnc to be
                # added to phenotype
                for external_reference in gene_association.iter("ExternalReference"):
                   # LOG.info(f"Looping")
                    gene_source = external_reference.find("Source").text

                    if gene_source == "HGNC":
                        LOG.info(f"Found HGNC")
                        reference = external_reference.find("Reference").text
                        LOG.info(f"Heres the HGNC-id: {reference}")
                        phenotype["hgnc_id"].add(reference)
                        break

        orpha_phenotypes_found[phenotype_id] = phenotype
    #LOG.info(orpha_phenotypes_found)
    return orpha_phenotypes_found
