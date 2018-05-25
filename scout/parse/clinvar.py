from scout.constants import CLINVAR_HEADER, CLINVAR_OPTIONAL, CASEDATA_HEADER, CASEDATA_OPTIONAL

def get_submission_variants(form_fields):
    """Extracts a list of variant ids from the clinvar submission form in blueprints/variants/clinvar.html (creation of a new clinvar submission).

        Args:
             form_fields(dict): it's the submission form dictionary. Keys have the same names as CLINVAR_HEADER and CASEDATA_HEADER

        Returns:
             clinvars: A list of variant IDs
    """

    clinvars = []

    # if the html checkbox named 'all_vars' is checked in the html form, then all pinned variants from a case should be included in the clinvar submission file,
    # otherwise just the selected one.
    if 'all_vars' in form_fields:
        for field, value in form_fields.items():
            if field.startswith('##Local ID_'):
                clinvars.append(form_fields[field].replace('##Local ID_',''))
    else:
        clinvars = [form_fields['main_var']] #also a list, but has one element

    return clinvars


def get_submission_header(form_fields, clinvars, csv_type):
    """Extracts a valid header for a csv clinvar submission file (blueprints/variants/clinvar.html). This file can be either the .Variant.csv file or the .Casedata.csv file according to the csv_type parameter passed.

        Args:
             form_fields(dict): it's the submission form dictionary. Keys have the same names as CLINVAR_HEADER and CASEDATA_HEADER
             clinvars: it's a list of variant ids to be used in the clinvar siubmission
             csv_type: either 'variants' or 'casedata'

        Returns:
             submission_header # a list of header fields for either the .Variant.csv or .Casedata.csv file
    """
    complete_header = []
    optional_fields = {}

    if csv_type == 'variants':
        complete_header  = list(CLINVAR_HEADER)
        optional_fields = dict(CLINVAR_OPTIONAL)
    else: # csv_type == casedata
        complete_header  = list(CASEDATA_HEADER)
        optional_fields = dict(CASEDATA_OPTIONAL)

    clinvars = get_submission_variants(form_fields)
    submission_header = []

    # loop over the header items and see if the field was filled in in each variant/casedata item in the form
    for field in complete_header: #for each field
        for clinvar in clinvars: #for each variant
            if field+"_"+clinvar in form_fields: # might be a mandatory or an optional field
                field_value = form_fields[field+'_'+clinvar] #get the value of that field in the form
                if len(field_value) > 0 and field_value != '-': # if the field is filled in with some value
                    if field not in submission_header: # collect the value in the file header
                        submission_header.append(field)
            elif field in optional_fields and optional_fields[field]:
                if field not in submission_header: # collect the value in the file header
                    submission_header.append(field)

    return submission_header


def get_submission_lines(form_fields, clinvars, file_header):
    """Extracts the lines for a csv clinvar submission file (blueprints/variants/clinvar.html). This file can be either the .Variant.csv file or the .Casedata.csv file according to the header passed (form_fields)

        Args:
             form_fields(dict): it's the submission form dictionary. Keys have the same names as CLINVAR_HEADER and CASEDATA_HEADER
             clinvars: it's a list of variant ids to be used in the clinvar siubmission
             file_header: it's the file header

        Returns:
             csv_lines # a list of lists. Each inner list is a line for the .Variant.csv or .Casedata.csv file.
    """

    clinvars = get_submission_variants(form_fields)
    csv_lines = [] #the list containing all the lines (one line for each variant/casedata)
    csv_line = []

    for clinvar in clinvars:
        if '##Local ID' in file_header or 'Individual ID' in file_header and 'casedata_'+clinvar in form_fields: # either the lines for a variant or the casedata lines for a variant with casedata filled in in the form
            csv_line = [] # a line object for a single variant/casedata
            for field in file_header:
                if field+"_"+clinvar in form_fields: # field is provided for this variant
                    if field == 'Reference sequence' or field == 'HGVS':
                        ref_HGVS = form_fields['Reference sequence_'+clinvar] # capture both refseq and hgvs
                        if field == 'Reference sequence':
                            refseq = ref_HGVS.split('|')
                            csv_line.append('"'+refseq[0]+'"')
                        else:
                            hgvs = ref_HGVS.split('|')
                            csv_line.append('"'+hgvs[1]+'"')
                    else:
                        csv_line.append('"'+form_fields[field+"_"+clinvar]+'"') # capture the provided value
                else: #field is not provided but it is provided for some other variant. Adding a blank cell for this one
                    csv_line.append('""') # empty cell

        if csv_line not in csv_lines and len(csv_line)>0:
            csv_lines.append(csv_line)

    return csv_lines


def extract_submission_csv_lines(clinvars_dictlist):
    """Parses a list of clinvar submission objects (variants) already in the database and creates the lines for printing .Variant.csv and .CaseData.csv clinvar submission files.

        Args:
            clinvars_dictlist(list of objects): list of clinvar submission objects from the clinvar database collection

        Returns:
            The strings used to produce the comma separated files .Variant.csv or .Casedata.csv to be downloaded for a clinvar submission

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


def create_clinvar_submission_dict(variant_header, variant_lines, casedata_header, casedata_lines, variant_types):
    """Creates a list of variants used for a clinvar submission.

        Args:
            variant_header(list): A list of strings representing the fields for the header of the .Variant.csv file
            variant_lines: A list of strings representing the lines of the .Variant.csv file
            casedata_header: A list of strings representing the fields for the header of the .Casedata.csv file
            casedata_lines: A list of strings representing the lines of the .Casedata.csv file
            variant_types(dict) : a dictionary where the key is the variant ID and the value is the type of variant (snv or sv)

        Returns:
         A list of clinvar variant submission objects. This list has the following format:
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
        var_dictionary['variant_type'] = variant_types[var_dictionary['_id']]
        field_counter = 0
        for column in variant_header:
            var_dictionary[column.replace(' ','_')] = item[field_counter].strip('"')
            field_counter += 1

        # add casedata info to the submission object:
        casedata = []
        for line in casedata_lines: #for each subject in casedata:
            if line and line[0] == item[0]:
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
