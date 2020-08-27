def build_phenotype(phenotype_info):
    """Build a phenotype term object

    Args:
        phenotype(dict)

    Returns:
        phenotype_obj(dict)
    """
    phenotype_obj = dict(
        phenotype_id=phenotype_info["phenotype_id"],
        disease_models=phenotype_info["disease_models"],
    )

    return phenotype_obj
