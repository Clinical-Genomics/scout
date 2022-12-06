import logging
from datetime import datetime

from flask import flash

from scout.constants.acmg import ACMG_MAP
from scout.constants.clinvar import CASEDATA_HEADER, CLINVAR_HEADER
from scout.constants.variant_tags import MANUAL_RANK_OPTIONS
from scout.models.clinvar import clinvar_variant
from scout.server.extensions import store
from scout.utils.scout_requests import fetch_refseq_version

from .form import CaseDataForm, SNVariantForm, SVariantForm

LOG = logging.getLogger(__name__)


def _get_var_tx_hgvs(variant_obj):
    """Retrieve all transcripts / hgvs for a given variant
    Args:
        variant_obj(scout.models.Variant)
    Returns:
        list. example: ["NM_000277 | c.1241A>G", ...]
    """
    tx_hgvs_list = [("Do not specify")]
    for gene in variant_obj.get("genes", []):
        for tx in gene.get("transcripts", []):
            if tx.get("refseq_id") and tx.get("coding_sequence_name"):
                for refseq in tx.get("refseq_identifiers"):
                    tx_hgvs_list.append(
                        " | ".join([fetch_refseq_version(refseq), tx["coding_sequence_name"]])
                    )

    return [(item, item) for item in tx_hgvs_list]


def _set_var_form_common_fields(var_form, variant_obj, case_obj):
    """Sets up fields for a variant form that are shared by SNVs and SVs

    Args:
        var_form(SNVariantForm or SVariantForm)
        variant_obj(dict) scout.models.Variant
        case_obj(dict) scout.models.Case
    """
    var_form.case_id.data = case_obj["_id"]
    var_form.local_id.data = variant_obj["_id"]
    var_form.linking_id.data = variant_obj["_id"]
    var_form.chromosome.data = variant_obj.get("chromosome")
    var_form.ref.data = variant_obj.get("reference")
    var_form.alt.data = variant_obj.get("alternative")
    if variant_obj.get("category") in ["snv", "cancer"]:
        var_form.gene_symbol.data = ",".join(variant_obj.get("hgnc_symbols", []))
    var_form.last_evaluated.data = datetime.now()
    var_form.hpo_terms.choices = [
        (hpo.get("phenotype_id"), " - ".join([hpo.get("phenotype_id"), hpo.get("feature")]))
        for hpo in case_obj.get("phenotype_terms", [])
    ]
    var_form.omim_terms.choices = [
        (omim.get("disease_nr"), " - ".join([str(omim.get("disease_nr")), omim.get("description")]))
        for omim in case_obj.get("diagnosis_phenotypes", [])
    ]


def _get_snv_var_form(variant_obj, case_obj):
    """Sets up values for a SNV variant form
    Args:
        variant_obj(dict) scout.models.Variant
        case_obj(dict) scout.models.Case

    Returns:
        var_form(scout.server.blueprints.clinvar.form.SNVariantForm)
    """
    var_form = SNVariantForm()
    _set_var_form_common_fields(var_form, variant_obj, case_obj)
    var_form.tx_hgvs.choices = _get_var_tx_hgvs(variant_obj)
    var_ids = variant_obj.get("dbsnp_id") or ""
    var_form.variations_ids.data = var_ids.split(";")[0]
    var_form.chromosome.data = variant_obj.get("chromosome")
    var_form.start.data = variant_obj.get("position")
    var_form.stop.data = variant_obj.get("position")
    return var_form


def _get_sv_var_form(variant_obj, case_obj):
    """Sets up values for a SV variant form

    Args:
        variant_obj(dict) scout.models.Variant
        case_obj(dict) scout.models.Case

    Returns:
        var_form(scout.server.blueprints.clinvar.form.SVariantForm)
    """
    var_form = SVariantForm()
    _set_var_form_common_fields(var_form, variant_obj, case_obj)
    var_form.chromosome.data = variant_obj.get("chromosome")
    var_form.end_chromosome.data = variant_obj.get("end_chrom")
    var_form.breakpoint1.data = variant_obj.get("position")
    var_form.breakpoint2.data = variant_obj.get("end")

    return var_form


def _populate_variant_form(variant_obj, case_obj):
    """Populate the Flaskform associated to a variant

    Args:
        variant_obj(dict) scout.models.Variant
        case_obj(dict) scout.models.Case

    Return:
        var_form(scout.server.blueprints.clinvar.form.SVariantForm or
                 scout.server.blueprints.clinvar.form.SNVariantForm )

    """
    if variant_obj["category"] in ["snv", "cancer"]:
        var_form = _get_snv_var_form(variant_obj, case_obj)
        var_form.category.data = "snv"

    elif variant_obj["category"] in ["sv", "cancer_sv"]:
        var_form = _get_sv_var_form(variant_obj, case_obj)
        var_form.category.data = "sv"

    return var_form


def _populate_case_data_form(variant_obj, case_obj):
    """Loop over the individuals of the case and populate a CaseDataForm for each one of them

    Args:
        variant_obj(dict) scout.models.Variant
        case_obj(dict) scout.models.Case

    Returns:
        cdata_form_list(list) list of scout.server.blueprints.clinvar.form.CaseDataForm

    """
    cdata_form_list = []  # A list of CaseData forms, one for each case individual/sample
    for ind in case_obj.get("individuals", []):
        affected = ind.get("phenotype") == 2
        ind_form = CaseDataForm()
        ind_form.affected_status.data = "yes" if affected else "no"
        ind_form.include_ind.render_kw = {"value": ind.get("display_name")}
        ind_form.include_ind.data = affected
        ind_form.individual_id.data = ind.get("display_name")
        ind_form.linking_id.data = variant_obj["_id"]
        cdata_form_list.append(ind_form)
    return cdata_form_list


def _variant_classification(var_obj):
    """Set a 'classified_as' key/header_value in the variant object, to be displayed on
    form page with the aim of aiding setting the mandatory 'clinsig' form field

    Args:
        var_obj(scout.model.Variant) Could be a SNV, Cancer SNV, SV or cancer SV

    Returns:
        classification(str): Human readable classification or None
    """
    if "acmg_classification" in var_obj:
        return ACMG_MAP[var_obj["acmg_classification"]]
    elif "manual_rank" in var_obj:
        return MANUAL_RANK_OPTIONS[var_obj["manual_rank"]]["name"]


def set_clinvar_form(var_id, data):
    """Adds form key/values to the form used in ClinVar create submission page

    Args:
        var_id(str): variant _id
        data(dict): data to show in clinvar_create.html template
    """
    var_obj = store.variant(var_id)
    if not var_obj:
        return

    var_obj["classification"] = _variant_classification(var_obj)

    var_form = _populate_variant_form(var_obj, data["case"])  # variant-associated form
    cdata_forms = _populate_case_data_form(var_obj, data["case"])  # CaseData form
    variant_data = {
        "var_id": var_id,
        "var_obj": var_obj,
        "var_form": var_form,
        "cdata_forms": cdata_forms,
    }
    data["variant_data"] = variant_data


def _parse_tx_hgvs(clinvar_var, form):
    """Set ref_seq and hgvs symbols for a clinvar variant

    Args:
        clinvar_var(dict): scout.models.clinvar.clinvar_variant
        form(werkzeug.datastructures.ImmutableMultiDic)
    """
    tx_hgvs = form.get("tx_hgvs")
    if not tx_hgvs or tx_hgvs == "Do not specify":
        return
    clinvar_var["ref_seq"] = tx_hgvs.split(" | ")[0]
    clinvar_var["hgvs"] = tx_hgvs.split(" | ")[1]


def _set_conditions(clinvar_var, form):
    """Set condition_id_type and condition_id_value for a clinvar variant

    Args:
        clinvar_var(dict): scout.models.clinvar.clinvar_variant
        form(werkzeug.datastructures.ImmutableMultiDic)
    """
    clinvar_var["condition_id_type"] = form.get("condition_type")
    clinvar_var["condition_id_value"] = ";".join(form.getlist("conditions"))


def parse_variant_form_fields(form):
    """Parses input values provided by the user in the ClinVar add_one form
       and creates a Variant ClinVar dictionary to be saved in database (clinvar collection)

    Args:
        form(werkzeug.datastructures.ImmutableMultiDic): form submitted by a user

    Returns:
        clinvar_var(dict): scout.models.clinvar.clinvar_variant
    """
    clinvar_var = {"csv_type": "variant"}

    # Set key/values in clinvar_var dictionary
    for key in clinvar_variant:
        if key in form and form[key] != "":
            clinvar_var[key] = form[key]

    clinvar_var["_id"] = "_".join([form["case_id"], form["local_id"]])
    _parse_tx_hgvs(clinvar_var, form)
    _set_conditions(clinvar_var, form)
    if form.get("dbsnp_id"):
        clinvar_var["variations_ids"] = form["dbsnp_id"]

    if clinvar_var.get("ref_seq") and clinvar_var.get("hgvs"):
        # Variant is described by RefSeq and HGVS already, remove redundanti fields from submission
        for item in ["chromosome", "start", "stop", "ref", "alt"]:
            clinvar_var.pop(item)

    return clinvar_var


def parse_casedata_form_fields(form):
    """Parses input values provided by the user in the ClinVar add_one form
      and creates a Variant ClinVar dictionary to be saved in database (clinvar collection)

    Args:
        form(werkzeug.datastructures.ImmutableMultiDic): form submitted by a user

    Returns:
        casedata_list(list of dicts): [scout.models.clinvar.clinvar_casedata, ..]
    """
    casedata_list = []

    # Get the list of individuals to be included in CaseData
    # Each individual will become a document in clinvar collection and a line in the CaseData CVS file
    inds_included = form.getlist("include_ind")

    if not inds_included:
        return casedata_list

    ind_ids = form.getlist("individual_id")
    ind_affected = form.getlist("affected_status")
    ind_allele_origin = form.getlist("allele_of_origin")
    coll_methods = form.getlist("collection_method")

    for ind in inds_included:
        casedata_dict = {"csv_type": "casedata"}
        casedata_dict["case_id"] = form["case_id"]
        casedata_dict["_id"] = "_".join([form["case_id"], form["local_id"], ind])
        casedata_dict["linking_id"] = form["local_id"]  # associate individual obs to a variant
        casedata_dict["individual_id"] = ind

        indx = ind_ids.index(ind)  # collect items at this index from the form lists
        casedata_dict["collection_method"] = coll_methods[indx]
        casedata_dict["allele_origin"] = ind_allele_origin[indx]
        casedata_dict["is_affected"] = ind_affected[indx]

        casedata_list.append(casedata_dict)

    return casedata_list


def update_clinvar_sample_names(submission_id, case_id, old_name, new_name):
    """Update casedata sample names
    Args:
        submission_id(str) the database id of a clinvar submission
        case_id(str): case id
        old_name(str): old name of an individual in case data
        new_name(str): new name of an individual in case data
    """
    n_renamed = store.rename_casedata_samples(submission_id, case_id, old_name, new_name)
    flash(
        f"Renamed {n_renamed} case data individuals from '{old_name}' to '{new_name}'",
        "info",
    )


def update_clinvar_submission_status(request_obj, institute_id, submission_id):
    """Update the status of a clinVar submission
    Args:
        store(adapter.MongoAdapter)
        request_obj(flask.request) POST request sent by form submission
        institute_id(str) institute id
        submission_id(str) the database id of a clinvar submission
    """
    update_status = request_obj.form.get("update_submission")

    if update_status in ["open", "closed"]:  # open or close a submission
        store.update_clinvar_submission_status(institute_id, submission_id, update_status)
    if update_status == "register_id":  # register an official clinvar submission ID
        store.update_clinvar_id(
            clinvar_id=request_obj.form.get("clinvar_id"),
            submission_id=submission_id,
        )
    if update_status == "delete":  # delete a submission
        deleted_objects, deleted_submissions = store.delete_submission(submission_id=submission_id)
        flash(
            f"Removed {deleted_objects} objects and {deleted_submissions} submission from database",
            "info",
        )


def clinvar_submission_file(submission_id, csv_type, clinvar_subm_id):
    """Prepare content (header and lines) of a csv clinvar submission file
    Args:
        submission_id(str): the database id of a clinvar submission
        csv_type(str): 'variant_data' or 'case_data'
        clinvar_subm_id(str): The ID assigned to this submission by clinVar
    Returns:
        (filename, csv_header, csv_lines):
            filename(str) name of file to be downloaded
            csv_header(list) content of header cells
            csv_lines(list of lists) content of file lines, one for each variant/case data
    """
    if clinvar_subm_id == "None":
        flash(
            "In order to download a submission CSV file you should register a Clinvar submission Name first!",
            "warning",
        )
        return

    submission_objs = store.clinvar_objs(submission_id=submission_id, key_id=csv_type)

    if submission_objs is None or len(submission_objs) == 0:
        flash(
            f"There are no submission objects of type '{csv_type}' to include in the csv file!",
            "warning",
        )
        return

    # Download file
    csv_header_obj = _clinvar_submission_header(submission_objs, csv_type)
    csv_lines = _clinvar_submission_lines(submission_objs, csv_header_obj)
    csv_header = list(csv_header_obj.values())

    today = str(datetime.now().strftime("%Y-%m-%d"))
    if csv_type == "variant_data":
        filename = f"{clinvar_subm_id}_{today}.Variant.csv"
    else:
        filename = f"{clinvar_subm_id}_{today}.CaseData.csv"

    return (filename, csv_header, csv_lines)


def _clinvar_submission_lines(submission_objs, submission_header):
    """Create the lines to include in a Clinvar submission csv file from a list of submission objects and a custom document header
    Args:
        submission_objs(list): a list of objects (variants or casedata) to include in a csv file
        submission_header(dict) : as in constants CLINVAR_HEADER and CASEDATA_HEADER, but with required fields only
    Returns:
        submission_lines(list) a list of strings, each string represents a line of the clinvar csv file to be doenloaded
    """
    submission_lines = []

    for subm_obj in submission_objs:  # Loop over the submission objects. Each of these is a line
        csv_line = []
        for (
            header_key,
            header_value,
        ) in submission_header.items():  # header_keys are the same keys as in submission_objs
            if header_key not in subm_obj:
                csv_line.append("")
            else:
                csv_line.append(subm_obj.get(header_key))
        submission_lines.append(csv_line)

    return submission_lines


def _clinvar_submission_header(submission_objs, csv_type):
    """Determine which fields to include in csv header by checking a list of submission objects
    Args:
        submission_objs(list): a list of objects (variants or casedata) to include in a csv file
        csv_type(str) : 'variant_data' or 'case_data'
    Returns:
        custom_header(dict): A dictionary with the fields required in the csv header. Keys and values are specified in CLINVAR_HEADER and CASEDATA_HEADER
    """

    complete_header = {}  # header containing all available fields
    custom_header = {}  # header keys reflecting the real data included in the submission objects
    if csv_type == "variant_data":
        complete_header = CLINVAR_HEADER
    else:
        complete_header = CASEDATA_HEADER

    for key, value in complete_header.items():
        for clinvar_obj in submission_objs:
            if key not in clinvar_obj or key in custom_header:
                continue
            custom_header[key] = value
    return custom_header
