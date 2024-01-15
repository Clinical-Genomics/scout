import logging
from typing import Any, Dict, Iterable, Optional

LOG = logging.getLogger(__name__)


def parse_hpo_to_genes(lines):
    """Parse the map from hpo term to hgnc symbol

    Args:
        lines(iterable(str)): example:
        #Format: HPO-id<tab>HPO label<tab>entrez-gene-id<tab>entrez-gene-symbol\
        <tab>Additional Info from G-D source<tab>G-D source<tab>disease-ID for link
        HP:0000002	Abnormality of body height	3954	LETM1	-	mim2gene	OMIM:194190
        HP:0000002	Abnormality of body height	197131	UBR1	-	mim2gene	OMIM:243800
        HP:0000002	Abnormality of body height	79633	FAT4		orphadata	ORPHA:314679

    Yields:
        hpo_to_gene(dict): A dictionary with information on how a term map to a hgnc symbol
    """
    for line in lines:
        if line.startswith("#") or len(line) < 5:
            continue
        line = line.rstrip().split("\t")
        hpo_id = line[0]
        hgnc_symbol = line[3]

        yield {"hpo_id": hpo_id, "hgnc_symbol": hgnc_symbol}


def parse_hpo_annotations(hpo_annotation_lines: Iterable[str]) -> Dict[str, Any]:
    """Parse HPO annotation files.
    Returns HPO info, description and disease coding system
    """
    diseases = {}
    for index, line in enumerate(hpo_annotation_lines):
        # First line is a header
        if index == 0:
            continue
        disease = parse_hpo_annotation_line(line)
        if not disease:
            continue

        disease_id = disease["disease_id"]
        if disease_id not in diseases:
            diseases[disease_id] = {
                "source": disease["source"],
                "description": disease["description"],
                "hpo_terms": set(),
            }

        if "hpo_terms" in disease and disease["hpo_terms"]:
            diseases[disease_id]["hpo_terms"].add(disease["hpo_terms"])

    return diseases


def parse_hpo_annotation_line(hpo_annotation_line: str) -> Optional[Dict[str, Any]]:
    """Parse HPO annotation file line"""

    hpo_annotation_line = hpo_annotation_line.rstrip().split("\t")
    hpo_info = {}

    # phenotype.hpoa::database_id
    hpo_info["disease_id"] = hpo_annotation_line[0]
    disease = hpo_info["disease_id"].split(":")
    hpo_info["source"] = disease[0]
    # we only support OMIM and ORPHA diseases for now - HPOA also has DECIPHER
    if hpo_info["source"] not in ["OMIM", "ORPHA"]:
        return

    hpo_info["description"] = hpo_annotation_line[1]

    qualifier = hpo_annotation_line[2]
    if qualifier == "NOT":
        return

    hpo_info["hpo_terms"] = hpo_annotation_line[3]

    hpo_info["hgnc_symbol"] = None

    return hpo_info
