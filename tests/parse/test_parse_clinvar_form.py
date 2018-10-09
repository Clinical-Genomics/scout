from scout.parse.clinvar import set_submission_objects, get_submission_variants, clinvar_submission_header

def get_submission_dict():
    #returns a clinvar submission dictionary with two variants and one case data to include. It's the format you obtain by converting a form request into a dict (form_dict = request.form.to_dict())
    test_form_fields_dict = {
        'main_var': '3eecfca5efea445eec6c19a53299043b',
        'all_vars': 'all_vars',
        'case_id@3eecfca5efea445eec6c19a53299043b' : 'case1',
        'individual_id@3eecfca5efea445eec6c19a53299043b' : 'subject1',
        'variant-type@3eecfca5efea445eec6c19a53299043b': 'snv',
        'local_id@@3eecfca5efea445eec6c19a53299043b': '3eecfca5efea445eec6c19a53299043b',
        'linking_id@3eecfca5efea445eec6c19a53299043b': '3eecfca5efea445eec6c19a53299043b',
        'chromosome@3eecfca5efea445eec6c19a53299043b': '7',
        'start@3eecfca5efea445eec6c19a53299043b': '124491972', # This field is valid for snvs
        'stop@3eecfca5efea445eec6c19a53299043b': '124491972', # This field is valid for snvs
        'ref@3eecfca5efea445eec6c19a53299043b': 'C',
        'alt@3eecfca5efea445eec6c19a53299043b': 'A',
        'casedata_3eecfca5efea445eec6c19a53299043b': 'on', # the form checkbox for this sample is checked
        'variant-type@a3ec99657a128d14419563d77e1381bd': 'sv',
        'local_id@a3ec99657a128d14419563d77e1381bd': 'a3ec99657a128d14419563d77e1381bd',
        'linking_id@a3ec99657a128d14419563d77e1381bd': 'a3ec99657a128d14419563d77e1381bd',
        'chromosome@a3ec99657a128d14419563d77e1381bd': '4',
        'ref@a3ec99657a128d14419563d77e1381bd': 'CGGCCAGCACCAGGGTCCCCACGGCGCGTCCCTTCAGGGCCTCCTCGGCCCAGGGCCTTGGTGAACACACGT',
        'alt@a3ec99657a128d14419563d77e1381bd': 'C',
        'variant-type@a3ec99657a128d14419563d77e1381bd': 'deletion' # this field is valid for SVs only
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
    assert len(subm_objs[0]) == 2 # one snv and one sv variant
    assert len(subm_objs[1]) ==1 # one case data object
