from scout.parse.clinvar import get_variant_lines, get_casedata_lines, create_clinvar_submission_dict

def get_submission_dict():
    #returns a clinvar submission dictionary with one variant and one case data to include. It's the format you obtain by converting a form request into a dict (form_dict = request.form.to_dict())
    test_form_fields_dict = {
        'main_var': '3eecfca5efea445eec6c19a53299043b',
        '##Local ID_3eecfca5efea445eec6c19a53299043b': '3eecfca5efea445eec6c19a53299043b',
        'Linking ID_3eecfca5efea445eec6c19a53299043b': '3eecfca5efea445eec6c19a53299043b',
        'Chromosome_3eecfca5efea445eec6c19a53299043b': '7',
        'Start_3eecfca5efea445eec6c19a53299043b': '124491972',
        'Stop_3eecfca5efea445eec6c19a53299043b': '124491972',
        'Reference allele_3eecfca5efea445eec6c19a53299043b': 'C',
        'Alternate allele_3eecfca5efea445eec6c19a53299043b': 'A',
        'Condition ID type_3eecfca5efea445eec6c19a53299043b': 'HPO',
        'Gene symbol_3eecfca5efea445eec6c19a53299043b': 'POT1',
        'Mode of inheritance_3eecfca5efea445eec6c19a53299043b': 'Autosomal recessive inheritance',
        'Variation identifiers_3eecfca5efea445eec6c19a53299043b': 'rs116916706',
        'Clinical significance_3eecfca5efea445eec6c19a53299043b': 'Likely Pathogenic',
        'Date last evaluated_3eecfca5efea445eec6c19a53299043b': '2018-04-25',
        'Functional consequence_3eecfca5efea445eec6c19a53299043b': '-',
        'Condition ID value_3eecfca5efea445eec6c19a53299043b': 'HP:0001298;HP:0002121',
        'Condition comment_3eecfca5efea445eec6c19a53299043b': '',
        'Assertion method_3eecfca5efea445eec6c19a53299043b': 'ACMG Guidelines, 2015',
        'Assertion method citation_3eecfca5efea445eec6c19a53299043b': 'doi: 10.1038/gim.2015.30',
        'Clinical significance citations_3eecfca5efea445eec6c19a53299043b': '',
        'Method_3eecfca5efea445eec6c19a53299043b': '',
        'Comment on clinical significance_3eecfca5efea445eec6c19a53299043b': '',
        'Drug response condition_3eecfca5efea445eec6c19a53299043b': '',
        'casedata_3eecfca5efea445eec6c19a53299043b': 'on',
        'Individual ID_3eecfca5efea445eec6c19a53299043b': 'NA12882',
        'Affected status_3eecfca5efea445eec6c19a53299043b': 'yes',
        'Population Group/Ethnicity_3eecfca5efea445eec6c19a53299043b': '',
        'Sex_3eecfca5efea445eec6c19a53299043b': 'male',
        'Age_3eecfca5efea445eec6c19a53299043b': '',
        'Allele origin_3eecfca5efea445eec6c19a53299043b': 'germline',
        'Zygosity_3eecfca5efea445eec6c19a53299043b': 'single heterozygote',
        'Proband_3eecfca5efea445eec6c19a53299043b': 'yes',
        'Family history_3eecfca5efea445eec6c19a53299043b': 'no',
        'Secondary finding_3eecfca5efea445eec6c19a53299043b': 'no',
        'Mosaicism_3eecfca5efea445eec6c19a53299043b': 'no',
        'Co-occurrences, same gene_3eecfca5efea445eec6c19a53299043b': '',
        'Co-occurrences, other genes_3eecfca5efea445eec6c19a53299043b': '',
        'Date variant was reported to submitter_3eecfca5efea445eec6c19a53299043b': '2016-10-12',
        'Tissue_3eecfca5efea445eec6c19a53299043b': '',
        'Clinical features_3eecfca5efea445eec6c19a53299043b': 'HP:0001298;HP:0002121',
        'Comment on clinical features_3eecfca5efea445eec6c19a53299043b': '',
        'Evidence citations_3eecfca5efea445eec6c19a53299043b': '',
        'Testing laboratory_3eecfca5efea445eec6c19a53299043b': 'Clinical Genomics - SciLifeLab Solna, Sweden.',
        'Platform type_3eecfca5efea445eec6c19a53299043b': 'next-gen sequencing',
        'Platform name_3eecfca5efea445eec6c19a53299043b': 'Whole exome sequencing, Illumina',
        'Method purpose_3eecfca5efea445eec6c19a53299043b': 'discovery',
        'Method citations_3eecfca5efea445eec6c19a53299043b': ''
    }

    return test_form_fields_dict


def test_parse_variant_lines():
    #given a clinvar form submission
    test_clinvar_form_dict = get_submission_dict()

    #call the parser to get the header and the lines of the .Variants csv file for the submission
    test_variants_header, test_variant_lines = get_variant_lines(test_clinvar_form_dict)

    #assert that the header of the variants file has the same number of fields as the file columns:
    assert len(test_variants_header) == len(test_variant_lines[0])


def test_parse_casedata_lines():
    #given a clinvar form submission
    test_clinvar_form_dict = get_submission_dict()

    #call the parser to get the header and the lines of the .Casedata csv file for the submission
    test_casedata_header, test_casedata_lines = get_casedata_lines(test_clinvar_form_dict)

    #assert that the header of the casedata file has the same number of fields as the file columns:
    assert len(test_casedata_header) == len(test_casedata_lines[0])


def test_create_clinvar_submission_dict():
    #given a clinvar form submission
    test_clinvar_form_dict = get_submission_dict()

    #having identified the fields and columns to include for a variant
    test_variants_header, test_variant_lines = get_variant_lines(test_clinvar_form_dict)

    #having identified the fields and columns to include for the casedata of a variant
    test_casedata_header, test_casedata_lines = get_casedata_lines(test_clinvar_form_dict)

    #transform the text files values into a dictionary list. Each dictionary item of this list is a variant submission onject that is saved to scout db.
    test_vars_dict_list = create_clinvar_submission_dict(test_variants_header, test_variant_lines, test_casedata_header, test_casedata_lines)

    #assert that test_vars_dict_list has the fields provided for the test variant.
    assert len(test_vars_dict_list[0]) == 20
