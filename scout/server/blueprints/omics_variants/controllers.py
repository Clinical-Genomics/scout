def outliers(store, institute_obj, case_obj, variants_query, variant_count, page=1, per_page=50):
    """Pre-process list of outlier omics variants."""
    skip_count = per_page * max(page - 1, 0)

    more_variants = variant_count > (skip_count + per_page)
    variants = []
    genome_build = str(case_obj.get("genome_build", "38"))
    if genome_build not in ["37", "38"]:
        genome_build = "38"

    case_dismissed_vars = store.case_dismissed_variants(institute_obj, case_obj)

    for variant_obj in variants_query.skip(skip_count).limit(per_page):
        # show previous classifications for research variants
        clinical_var_obj = variant_obj
        if variant_obj["variant_type"] == "research":
            clinical_var_obj = store.variant(
                case_id=case_obj["_id"],
                simple_id=variant_obj["simple_id"],
                variant_type="clinical",
            )
        if clinical_var_obj is not None:
            variant_obj["clinical_assessments"] = get_manual_assessments(clinical_var_obj)

        parsed_variant = parse_variant(
            store,
            institute_obj,
            case_obj,
            variant_obj,
            genome_build=genome_build,
            case_dismissed_vars=case_dismissed_vars,
        )

        variants.append(parsed_variant)

    return {"variants": variants, "more_variants": more_variants}
