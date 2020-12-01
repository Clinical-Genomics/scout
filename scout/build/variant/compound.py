def build_compound(compound):
    """Build a compound

    Args:
        compound(dict)

    Returns:
        compound_obj(dict)

    dict(
        # This must be the document_id for this variant
        variant = str, # required=True
        # This is the variant id
        display_name = str, # required
        combined_score = float, # required
        rank_score = float,
        not_loaded = bool
        genes = [
            {
                hgnc_id: int,
                hgnc_symbol: str,
                region_annotation: str,
                functional_annotation:str
            }, ...
        ]
    )

    """

    compound_obj = dict(
        variant=compound["variant"],
        display_name=compound["display_name"],
        combined_score=float(compound["score"]),
    )

    return compound_obj
