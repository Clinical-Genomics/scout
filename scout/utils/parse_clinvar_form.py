import urllib.request
import sys
from scout.constants import CLIVAR_HEADER, CLINVAR_OPTIONAL, CASEDATA_HEADER, CASEDATA_OPTIONAL

def get_variant_lines(form_fields):

    clinvar_header  = list(CLIVAR_HEADER)
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
            if field == 'Gene symbol' or field == 'Condition ID value': #these fields could contain multiple values
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
            variant_line.append(clinvar_dict[field])
        variants.append(variant_line)

    #returning a list and a list of lists
    return clinvar_header, variants


def get_casedata_lines(form_fields):

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
                        if field == 'Clinical features': #these fields could contain multiple values
                            subj_dict[field] = form_fields[field+'_'+clinvar][0][:-1]
                        else:
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
                    casedata_line.append(subj_dict[field])
                else:
                    casedata_line.append('')
            casedata_lines.append(casedata_line)

    return casedata_header,casedata_lines
