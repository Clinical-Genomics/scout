from scout.parse.clinvar import get_submission_variants, get_submission_header, get_submission_lines, create_clinvar_submission_dict
def get_submission_dict():
    #returns a clinvar submission dictionary with one variant and one case data to include. It's the format you obtain by converting a form request into a dict (form_dict = request.form.to_dict())
    test_form_fields_dict = {
        'main_var': '3eecfca5efea445eec6c19a53299043b',
        'all_vars': 'all_vars',
        'variant-type_3eecfca5efea445eec6c19a53299043b': 'snv',
        '##Local ID_3eecfca5efea445eec6c19a53299043b': '3eecfca5efea445eec6c19a53299043b',
        'Linking ID_3eecfca5efea445eec6c19a53299043b': '3eecfca5efea445eec6c19a53299043b',
        'Chromosome_3eecfca5efea445eec6c19a53299043b': '7',
        'Start_3eecfca5efea445eec6c19a53299043b': '124491972', # This field is valid for snvs
        'Stop_3eecfca5efea445eec6c19a53299043b': '124491972', # This field is valid for snvs
        'Reference allele_3eecfca5efea445eec6c19a53299043b': 'C',
        'Alternate allele_3eecfca5efea445eec6c19a53299043b': 'A',
        'casedata_3eecfca5efea445eec6c19a53299043b': 'on', # the form checkbox for this sample is checked
        'Individual ID_3eecfca5efea445eec6c19a53299043b': 'NA12882',
        'Affected status_3eecfca5efea445eec6c19a53299043b': 'yes',
        'variant-type_a3ec99657a128d14419563d77e1381bd': 'sv',
        '##Local ID_a3ec99657a128d14419563d77e1381bd': 'a3ec99657a128d14419563d77e1381bd',
        'Linking ID_a3ec99657a128d14419563d77e1381bd': 'a3ec99657a128d14419563d77e1381bd',
        'Chromosome_a3ec99657a128d14419563d77e1381bd': '4',
        'Reference allele_a3ec99657a128d14419563d77e1381bd': 'CGGCCAGCACCAGGGTCCCCACGGCGCGTCCCTTCAGGGCCTCCTCGGCCCAGGGCCTTGGTGAACACACGT',
        'Alternate allele_a3ec99657a128d14419563d77e1381bd': 'C',
        'Variant type_a3ec99657a128d14419563d77e1381bd': 'deletion' # this field is valid for SVs only
    }

    return test_form_fields_dict


def test_clinvar_submission_parser():
    # GIVEN a clinvar form submission
    test_clinvar_form_dict = get_submission_dict()

    # call the parser to get a list of the variants IDs to be used in the submission
    test_clinvars = get_submission_variants(test_clinvar_form_dict)

    # assert that the form contains info for 2 variants
    assert len(test_clinvars) == 2 # variant '3eecfca5efea445eec6c19a53299043b' and 'a3ec99657a128d14419563d77e1381bd'

    # call the parser to get the header (a mini version of it actually, because of the shortened test form) of the .Variants csv file for the submission
    test_variants_header = get_submission_header(test_clinvar_form_dict, test_clinvars, 'variants')

    # assert that the file header contains all the unique variant-related control fields (taken both from snv and sv variants):
    variant_control_fields = ['##Local ID', 'Linking ID', 'Chromosome', 'Start', 'Stop', 'Reference allele', 'Alternate allele', 'Variant type']
    assert test_variants_header == variant_control_fields

    # call the parser to get the lines of the .Variants csv file for the submission
    test_variants_lines = get_submission_lines(test_clinvar_form_dict, test_clinvars, test_variants_header)

    # assert that each variant (== each line of the file) contains the same number of elements specified in the file header
    for variant_line in test_variants_lines:
        assert len(variant_line)==len(test_variants_header)

    # call the parser to get the header of the .Casedata csv file for the submission
    test_casedata_header = get_submission_header(test_clinvar_form_dict, test_clinvars, 'casedata')

    # call the parser to get the lines of the .Casedata csv file for the submission
    test_casedata_lines = get_submission_lines(test_clinvar_form_dict, test_clinvars, test_casedata_header)

    # assert that there is casedata for one sample only
    assert len(test_casedata_lines) == 1

    # assert that the casedata line for that sample has three fields ('Linking ID', 'Individual ID', 'Affected status')
    assert len(test_casedata_lines[0]) == 3

    test_variant_types = {
        '3eecfca5efea445eec6c19a53299043b' : 'snv',
        'a3ec99657a128d14419563d77e1381bd' : 'sv'
    }
    # transform the text files values into a dictionary list. Each dictionary item of this list is a variant submission onject that is saved to scout db.
    test_vars_dict_list = create_clinvar_submission_dict(test_variants_header, test_variants_lines, test_casedata_header, test_casedata_lines, test_variant_types)

    # assert that two variant objects were created
    assert len(test_vars_dict_list) == 2
