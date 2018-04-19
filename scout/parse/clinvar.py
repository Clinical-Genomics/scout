import urllib.request
import sys
from scout.constants import CLINVAR_HEADER, CLINVAR_OPTIONAL, CASEDATA_HEADER, CASEDATA_OPTIONAL

def get_variant_lines(form_fields):
    """Parses the form from blueprints/variants/clinvar.html (creation of a new clinvar submission).
       According to what the uses has inserted in the form, the function evaluates which fields are to
       be included in the .Variant.csv clinvar submission file (both header and lines).
       Mandatory fields are defined in CLINVAR_HEADER, optional fields in CLINVAR_OPTIONAL.

       Args:
            form_fields(dict) # it's the submission form dictionary. Keys have the same names as CLINVAR_HEADER and CLINVAR_OPTIONAL

       Returns:
            clinvar_header(list) # the header of the .Variant.csv CSV file
            clinvar_lines(list of lists) each inner list is a variant line
    """

    clinvar_header  = list(CLINVAR_HEADER)
    optional_fields = dict(CLINVAR_OPTIONAL)
    clinvars_dict = {}

    if 'all_vars' in form_fields:
        clinvars = form_fields['local'] #this is a list
    else:
        clinvars = [form_fields['main_var'][0]] #also a list, but has one element

    for clinvar in clinvars:
        clinvar_dict = {}
        for field in clinvar_header:
            clinvar_dict[field] = ''
            if field == 'Gene symbol': # field could contain multiple values
                clinvar_dict[field] = ';'.join(form_fields[field+'_'+clinvar])
            elif field == 'Reference sequence' or field == 'HGVS':
                if 'Reference sequence_'+clinvar in form_fields: #value is provided on the form
                    ref_HGVS = form_fields['Reference sequence_'+clinvar] # this is a list
                    if field == 'Reference sequence':
                        refseq = ref_HGVS[0].split('|')
                        clinvar_dict[field] = refseq[0]
                    else:
                        hgvs = ref_HGVS[0].split('|')
                        clinvar_dict[field] = hgvs[1]
                    optional_fields[field] = True
                else:
                    if optional_fields[field] == True:
                        clinvar_dict[field] = ''
            else: #optional fields
                if field+"_"+clinvar in form_fields: # optional field is provided
                    field_value = form_fields[field+'_'+clinvar][0]
                    if len(field_value) > 0 and field_value != '-': #it's filled in field
                        clinvar_dict[field] = field_value
                        if field in optional_fields: # if it's an optional field but it is provided:
                            optional_fields[field] = True
                    else: #not filled in, but was filled in for any other variant in this submission
                        if field in optional_fields and optional_fields[field] == True:
                            clinvar_dict[field] = ''
                else: #not provided, but was provided for another variant in this submission form
                    if field in optional_fields and optional_fields[field] == True:
                        clinvar_dict[field] = ''
        # Add variant line to the dictionary of variants to submit
        clinvars_dict[clinvar] = clinvar_dict

    # remove empty fields from header:
    for field, used in optional_fields.items():
        if used == False: #field is not used, remove it from header:
            clinvar_header.remove(field)

    variants = [] #one line for each variant
    for clinvar in clinvars:
        variant_line = []
        clinvar_dict = clinvars_dict[clinvar]
        for field in clinvar_header:
            variant_line.append('"'+clinvar_dict[field]+'"')
        variants.append(variant_line)

    #returning a list and a list of lists
    return clinvar_header, variants


def get_casedata_lines(form_fields):
    """Parses the form from blueprints/variants/clinvar.html (creation of a new clinvar submission).
       According to what the used has inserted in the form, the function evaluates which fields are to
       be included in the .CaseData.csv clinvar submission file (both header and lines).
       Mandatory fields are defined in CASEDATA_HEADER, optional (or pre-filled) fields in CASEDATA_OPTIONAL.

       Args:
            form_fields(dict) # it's the submission form dictionary. Keys have the same names as CASEDATA_HEADER and CASEDATA_OPTIONAL

       Returns:
            casedata_header(list) # the header of the .CaseData.csv CSV file
            casedata_lines(list of lists) each inner list is a case data line
    """

    casedata_header = list(CASEDATA_HEADER)
    casedata_optional = dict(CASEDATA_OPTIONAL)
    subjs_dict={}

    if 'all_vars' in form_fields:
        clinvars = form_fields['local'] #this is a list
    else:
        clinvars = [form_fields['main_var'][0]] #also a list, but has one element

    for clinvar in clinvars:
        if 'casedata_'+clinvar in form_fields: #if the user has chosen to add this case using the relative checkbox
            subj_dict = {}
            for field in casedata_header: # If the field is in the dynamic form
                if field+'_'+clinvar in form_fields: #filled in field
                    field_value = form_fields[field+'_'+clinvar][0]
                    if len(field_value) > 0:
                        subj_dict[field] = form_fields[field+'_'+clinvar][0]
                        if field in casedata_optional:
                            casedata_optional[field] = True
                # else it might be either an empty option or a constant:
                elif field in casedata_optional: # it's a constant
                    subj_dict[field] = casedata_optional[field]
            subjs_dict[clinvar] = subj_dict

    # remove empty fields from header:
    for field, used in casedata_optional.items():
        if used is False: # Remove it from the header and from the fields to be printed in the file:
            casedata_header.remove(field)

    casedata_lines = []
    #key is variant, value the subject data
    for clinvar in clinvars: # for each variant to submit (1 line in the document)
        if clinvar in subjs_dict:
            subj_dict = subjs_dict[clinvar]
            casedata_line = []
            for field in casedata_header:
                if field in subj_dict:
                    casedata_line.append('"'+subj_dict[field]+'"')
                else:
                    casedata_line.append('""')
            casedata_lines.append(casedata_line)

    return casedata_header,casedata_lines

def extract_submission_csv_lines(clinvars_dictlist):
    """Parses a list of clinvar submission object (variants) and creates the lines for printing
    .Variant.csv and .CaseData.csv clinvar submission files.
    """
    variants_header = []
    clinvar_lines = []
    cdata_header = []
    casedata_lines = []

    variants_header = clinvars_dictlist[0]['variant_header']
    casedata_header = clinvars_dictlist[0]['casedata_header']

    for clinvar in clinvars_dictlist:
        temp_var_fields = []
        for v_field in variants_header:
            temp_var_fields.append('"'+clinvar[v_field.replace(' ','_')]+'"')
        clinvar_lines.append(','.join(temp_var_fields))

        #collect casedata info:
        if 'casedata' in clinvar:
            cdata_objs = clinvar['casedata']
            for case in cdata_objs:
                temp_cd_fields = []
                for cd_field in casedata_header:
                    temp_cd_fields.append('"'+case[cd_field.replace(' ','_')]+'"')
                casedata_lines.append(','.join(temp_cd_fields))

    return '"'+'","'.join(variants_header)+'"', '"'+'","'.join(casedata_header)+'"', clinvar_lines, casedata_lines


def create_clinvar_submission_dict(variant_header, variant_lines, casedata_header, casedata_lines):
    """
    Creates a list of variants used for a clinvar submission. The returned list has the following format:
    [
        {
            _id : "variant_1",
            variant_id : "variant_1",
            case_id : "case_id",
            ..
            form fields for variant 1
            casedata: [
                {
                    form fields for casedata 1
                },
                {
                    form fields for casedata 2
                }
                ..
            ]
        },
        {
            _id : "variant_2",
            variant_id : "variant_2",
            case_id : "case_id",
            ..
            form fields for variant 2
            casedata: [
                {
                    form fields for casedata 1
                },
                {
                    form fields for casedata 2
                }
                ..
            ]
        },
    ]
    """
    submitted_vars= []
    # variant header items become dictionary keys and variant lines dictionary values
    for item in variant_lines: #each line is a variant

        var_dictionary = {}
        var_dictionary['_id']= item[0].strip('"') #variant_id
        field_counter = 0
        for column in variant_header:
            var_dictionary[column.replace(' ','_')] = item[field_counter].strip('"')
            field_counter += 1

        # add casedata info to the submission object:
        casedata = []
        for line in casedata_lines: #for each subject in casedata:
            if line[0] == item[0]:
                casedata_obj = {}
                field_counter=0
                for column in casedata_header:
                    casedata_obj[column.replace(' ','_')] = line[field_counter].strip('"')
                    field_counter += 1
                casedata.append(casedata_obj)
        if len(casedata) > 0:
            var_dictionary['casedata'] = casedata
        var_dictionary['variant_header'] = variant_header
        var_dictionary['casedata_header'] = casedata_header

        submitted_vars.append(var_dictionary)

    return submitted_vars
