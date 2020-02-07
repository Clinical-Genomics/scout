from scout.parse.clinvar import (
    set_submission_objects,
    get_submission_variants,
    clinvar_submission_header,
)


def get_submission_dict():
    # returns a clinvar submission dictionary with two variants and one case data to include. It's the format you obtain by converting a form request into a dict (form_dict = request.form.to_dict())
    test_form_fields_dict = {
        "main_var": "test_snv_variant",
        "all_vars": "all_vars",
        "case_id@test_snv_variant": "case1",
        "individual_id@test_snv_variant": "subject1",
        "variant-type@test_snv_variant": "snv",
        "local_id@@test_snv_variant": "test_snv_variant",
        "linking_id@test_snv_variant": "test_snv_variant",
        "chromosome@test_snv_variant": "7",
        "start@test_snv_variant": "124491972",  # This field is valid for snvs
        "stop@test_snv_variant": "124491972",  # This field is valid for snvs
        "ref@test_snv_variant": "C",
        "alt@test_snv_variant": "A",
        "condition_id_value@test_snv_variant": ["OMIM_145590", "HPO_HP:0000707"],
        "casedata_test_snv_variant": "on",  # the form checkbox for this sample is checked
        "clin_features@test_snv_variant": ["HPO_HP:0001298"],
        "variant-type@test_sv_variant": "sv",
        "local_id@test_sv_variant": "test_sv_variant",
        "linking_id@test_sv_variant": "test_sv_variant",
        "chromosome@test_sv_variant": "4",
        "ref@test_sv_variant": "CGGCCAGCACCAGGGTCCCCACGGCGCGTCCCTTCAGGGCCTCCTCGGCCCAGGGCCTTGGTGAACACACGT",
        "alt@test_sv_variant": "C",
        "variant-type@test_sv_variant": "deletion",  # this field is valid for SVs only
    }
    return test_form_fields_dict


def test_parse_clinvar_form():
    """Test create list of submission objects (variants and casedata) from clinvar page form"""

    # Given a filled in form
    form_fields_dict = get_submission_dict()

    # Retrieve the IDs of variants in the form
    variant_ids = get_submission_variants(form_fields_dict)
    assert len(variant_ids) == 2

    # obtain variant and casedata objects to include in submission
    subm_objs = set_submission_objects(form_fields_dict)
    assert len(subm_objs[0]) == 2  # one snv and one sv variant
    assert len(subm_objs[1]) == 1  # one case data object
