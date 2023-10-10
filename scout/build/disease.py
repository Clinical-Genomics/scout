import logging

from scout.models.phenotype_term import DiseaseTerm

LOG = logging.getLogger(__name__)


def build_disease_term(disease_info: dict, alias_genes:dict={}) -> DiseaseTerm:
    """Build a disease phenotype object

    Args:
        disease_info(dict): Dictionary with phenotype information
        alias_genes(dict): {
                    <alias_symbol>: {
                                        'true': hgnc_id or None,
                                        'ids': [<hgnc_id>, ...]}}

    """
    disease_nr = int(disease_info["mim_number"])

    disease_obj = dict(
        disease_id="{0}:{1}".format("OMIM", disease_nr),
        disease_nr=disease_nr,
        description=disease_info.get("description"),
        source="OMIM",
    )

    # Check for inheritance models info
    inheritance_models = disease_info.get("inheritance")
    if inheritance_models:
        disease_obj["inheritance"] = list(inheritance_models)

    hgnc_symbols_not_found = set()
    hgnc_ids = set()
    for hgnc_symbol in disease_info.get("hgnc_symbols", []):

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
            "The following gene symbols could not be found in database: %s", hgnc_symbols_not_found
        )

    disease_obj["genes"] = list(hgnc_ids)

    if "hpo_terms" in disease_info:
        disease_obj["hpo_terms"] = list(disease_info["hpo_terms"])

    return DiseaseTerm(**disease_obj)
