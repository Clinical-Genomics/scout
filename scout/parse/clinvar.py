from scout.constants import CASEDATA_HEADER, CLINVAR_HEADER


def set_submission_objects(form_fields):
    """Creates a list of submission objects (variant and case-data) from the clinvar submission form in blueprints/variants/clinvar.html.

    Args:
         form_fields(dict): it's the submission form dictionary. Keys have the same names as CLINVAR_HEADER and CASEDATA_HEADER

    Returns:
         submission_objects(list): a list of variant and case-data submission objects, ready to be included in the clinvar database collection
    """
    variant_ids = get_submission_variants(
        form_fields
    )  # A list of variant IDs present in the submitted form

    # Extract list of variant objects to be submitted
    variant_objs = get_objects_from_form(variant_ids, form_fields, "variant")

    # Extract list of casedata objects to be submitted
    casedata_objs = get_objects_from_form(variant_ids, form_fields, "casedata")

    return (variant_objs, casedata_objs)


def get_objects_from_form(variant_ids, form_fields, object_type):
    """Extract the objects to be saved in the clinvar database collection.
    object_type param specifies if these objects are variant or casedata objects

    Args:
     variant_ids(list): list of database variant ids
     form_fields(dict): it's the submission form dictionary. Keys have the same names as CLINVAR_HEADER and CASEDATA_HEADER
     object_type(str): either 'variant' or 'case_data'

    Returns:
     submission_objects(list): list of submission objects of either type 'variant' or 'casedata'
    """
    submission_fields = []
    if object_type == "variant":
        submission_fields = CLINVAR_HEADER
    else:  # collect casedata objects
        submission_fields = CASEDATA_HEADER

    # A list of objects (variants of casedata info) to be saved into clinvar database collection
    submission_objects = []

    # Loop over the form fields and collect the data:
    for variant_id in variant_ids:  # loop over the variants

        subm_obj = {}  # A new submission object for each

        # Don't included casedata for a variant unless specified by user
        if object_type == "casedata" and "casedata_" + variant_id not in form_fields:
            continue

        subm_obj["csv_type"] = object_type
        subm_obj["case_id"] = form_fields.get("case_id")
        subm_obj["category"] = form_fields.get("category@" + variant_id)

        for key, values in submission_fields.items():  # loop over the form info fields
            field_value = form_fields.get(key + "@" + variant_id)
            if field_value and not field_value == "-":
                if key == "ref_seq":  # split this field into
                    refseq_raw = field_value.split("|")
                    subm_obj["ref_seq"] = refseq_raw[0]
                    subm_obj["hgvs"] = refseq_raw[1]
                else:
                    subm_obj[key] = field_value

        # Create a unique ID for the database
        # For casedata : = caseID_sampleID_variantID
        # For variants : ID = caseID_variantID
        if object_type == "casedata":
            subm_obj["_id"] = (
                str(subm_obj["case_id"]) + "_" + variant_id + "_" + str(subm_obj["individual_id"])
            )
        else:
            subm_obj["_id"] = str(subm_obj["case_id"]) + "_" + variant_id

        submission_objects.append(subm_obj)

    return submission_objects


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
    if "all_vars" in form_fields:
        for field, value in form_fields.items():
            if field.startswith("local_id"):
                clinvars.append(form_fields[field].replace("local_id@", ""))
    else:
        clinvars = [form_fields["main_var"]]  # also a list, but has one element

    return clinvars


def clinvar_submission_header(submission_objs, csv_type):
    """Determine which fields to include in csv header by checking a list of submission objects

    Args:
        submission_objs(list): a list of objects (variants or casedata) to include in a csv file
        csv_type(str) : 'variant_data' or 'case_data'

    Returns:
        custom_header(dict): A dictionary with the fields required in the csv header. Keys and values are specified in CLINVAR_HEADER and CASEDATA_HEADER

    """

    complete_header = {}  # header containing all available fields
    custom_header = {}  # header reflecting the real data included in the submission objects
    if csv_type == "variant_data":
        complete_header = CLINVAR_HEADER
    else:
        complete_header = CASEDATA_HEADER

    for (
        header_key,
        header_value,
    ) in complete_header.items():  # loop over the info fields provided in each submission object
        for clinvar_obj in submission_objs:  # loop over the submission objects
            for (
                key,
                value,
            ) in clinvar_obj.items():  # loop over the keys and values of the clinvar objects

                if (
                    not header_key in custom_header and header_key == key
                ):  # add to custom header if missing and specified in submission object
                    custom_header[header_key] = header_value

    return custom_header


def clinvar_submission_lines(submission_objs, submission_header):
    """Create the lines to include in a Clinvar submission csv file from a list of submission objects and a custom document header

    Args:
        submission_objs(list): a list of objects (variants or casedata) to include in a csv file
        submission_header(dict) : as in constants CLINVAR_HEADER and CASEDATA_HEADER, but with required fields only

    Returns:
        submission_lines(list) a list of strings, each string represents a line of the clinvar csv file to be doenloaded
    """
    submission_lines = []
    for (
        submission_obj
    ) in submission_objs:  # Loop over the submission objects. Each of these is a line
        csv_line = []
        for (
            header_key,
            header_value,
        ) in submission_header.items():  # header_keys are the same keys as in submission_objs
            if (
                header_key in submission_obj
            ):  # The field is filled in for this variant/casedata object
                csv_line.append('"' + submission_obj.get(header_key) + '"')
            else:  # Empty field for this this variant/casedata object
                csv_line.append('""')

        submission_lines.append(",".join(csv_line))

    return submission_lines
