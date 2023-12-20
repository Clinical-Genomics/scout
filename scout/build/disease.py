import logging

from scout.models.disease_term import DiseaseTerm

LOG = logging.getLogger(__name__)


def build_disease_term(disease_id: str, disease_info: dict, alias_genes: dict) -> dict:
    """Build a disease term object."""

    disease_obj = {}
    disease_nr = disease_id.split(":")[1]
    disease_source = disease_id.split(":")[0]

    disease_obj["disease_nr"] = int(disease_nr)
    disease_obj["disease_id"] = disease_id
    disease_obj["source"] = disease_source

    for key in ["hpo_terms", "inheritance"]:
        if key in disease_info:
            disease_obj[key] = list(disease_info[key])

    if disease_info.get("description"):
        disease_obj["description"] = disease_info["description"]

    translate_hgnc_symbols_to_ids(disease_info=disease_info, alias_genes=alias_genes)

    disease_obj["genes"] = list(disease_info["hgnc_ids"])
    disease_obj["_id"] = disease_obj["disease_id"]

    DiseaseTerm(**disease_obj)

    return disease_obj


def translate_hgnc_symbols_to_ids(disease_info: dict, alias_genes: dict) -> None:
    """Translates hgnc symbols to hgnc id:s and adds them to disease[hgnc_ids]."""
    hgnc_ids = disease_info.get("hgnc_ids", set())
    hgnc_symbols_not_found = set()

    #: If the symbol is present in alias_genes, add the corresponding id
    for hgnc_symbol in disease_info.get("hgnc_symbols", []):
        if hgnc_symbol is None:
            continue
        if hgnc_symbol in alias_genes:
            # If the symbol identifies a unique gene we add that
            if alias_genes[hgnc_symbol]["true"]:
                hgnc_ids.add(alias_genes[hgnc_symbol]["true"])
            else:
                for hgnc_id in alias_genes[hgnc_symbol]["ids"]:
                    hgnc_ids.add(hgnc_id)
        else:
            hgnc_symbols_not_found.add(hgnc_symbol)

    if hgnc_symbols_not_found:
        LOG.debug(
            f"The following gene symbols could not be found in database: {hgnc_symbols_not_found}"
        )
    disease_info["hgnc_ids"].update(hgnc_ids)
