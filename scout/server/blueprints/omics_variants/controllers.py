def outliers(store, institute_obj, case_obj, variants_query, variant_count, page=1, per_page=50):
    """Pre-process list of outlier omics variants."""
    skip_count = per_page * max(page - 1, 0)

    more_variants = variant_count > (skip_count + per_page)
    variants = []

    genome_build = str(case_obj.get("genome_build", "38"))
    if genome_build not in ["37", "38"]:
        genome_build = "38"

    for variant_obj in variants_query.skip(skip_count).limit(per_page):
        parsed_variant = decorate_omics_variant(
            store,
            institute_obj,
            case_obj,
            variant_obj,
        )

        variants.append(parsed_variant)

    return {"variants": variants, "more_variants": more_variants}


def decorate_omics_variant(store, institute_obj, case_obj, omics_variant_obj):
    """Decorate each variant with a limited selection of variant obj level information for display on variantS page."""

    omics_variant_obj["comments"] = store.events(
        institute_obj,
        case=case_obj,
        variant_id=omics_variant_obj["variant_id"],
        comments=True,
    )

    return omics_variant_obj
