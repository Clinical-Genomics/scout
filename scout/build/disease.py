import logging

from scout.models.disease_term import DiseaseTerm

LOG = logging.getLogger(__name__)


def build_disease_term(disease_info: dict, alias_genes: dict = {}) -> dict:
    """Build a disease term object."""

    disease_obj = {}
    disease_nr = disease_info.get("mim_number")
    if disease_nr:
        disease_obj["disease_nr"] = disease_nr
        disease_obj["disease_id"] = f"OMIM:{disease_nr}"
        disease_obj["source"] = "OMIM"
    for key in ["hpo_terms", "inheritance"]:
        if key in disease_info:
            disease_obj[key] = list(disease_info[key])

    if disease_info.get("description"):
        disease_obj["description"] = disease_info["description"]

    hgnc_symbols_not_found = set()
    hgnc_ids = set()
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
            "The following gene symbols could not be found in database: %s",
            hgnc_symbols_not_found,
        )

    disease_obj["genes"] = list(hgnc_ids)

    DiseaseTerm(**disease_obj)

    disease_obj["_id"] = disease_obj["disease_id"]
    return disease_obj
