from scout.utils.sort import get_load_priority


def test_category_load_priority():
    """
    Test load priority helper, file type category.
    """

    # GIVEN an SNV and SV file category
    category_cancer_snv = "cancer"
    category_cancer_sv = "cancer_sv"
    variant_type = "clinical"

    # WHEN asking for the priority, as eg in a sort lambda function
    snv_prio = get_load_priority(category=category_cancer_snv, variant_type=variant_type)
    sv_prio = get_load_priority(category=category_cancer_sv, variant_type=variant_type)

    # THEN SNVs are given precedence, which has importance for variant id assignment collisions
    assert snv_prio < sv_prio


def test_file_load_priority():
    """
    Test load priority helper, explicit file type e.g. within category.
    """

    # GIVEN two different SV file category files
    general_sv = "vcf_sv"
    mt_sv = "vcf_sv_mt"

    # WHEN asking for the priority, as eg in a sort lambda function
    general_sv_prio = get_load_priority(file_type=general_sv)
    mt_sv_prio = get_load_priority(file_type=mt_sv)

    # THEN the more specific MT vars are given precedence, which has importance for variant id assignment collisions
    assert mt_sv_prio < general_sv_prio
