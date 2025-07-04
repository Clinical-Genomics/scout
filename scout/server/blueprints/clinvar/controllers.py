import csv
import logging
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import List, Optional, Tuple, Union

from flask import flash, request
from flask_login import current_user
from pydantic_core._pydantic_core import ValidationError
from werkzeug.datastructures import ImmutableMultiDict

from scout.constants.acmg import ACMG_MAP
from scout.constants.ccv import CCV_MAP
from scout.constants.clinvar import (
    CASEDATA_HEADER,
    CLINVAR_HEADER,
    CONDITION_PREFIX,
    SCOUT_CLINVAR_SV_TYPES_MAP,
)
from scout.constants.variant_tags import MANUAL_RANK_OPTIONS
from scout.models.clinvar import OncogenicitySubmissionItem, clinvar_variant
from scout.server.blueprints.variant.utils import add_gene_info
from scout.server.extensions import clinvar_api, store
from scout.server.utils import get_case_genome_build, safe_redirect_back
from scout.utils.hgvs import validate_hgvs
from scout.utils.scout_requests import fetch_refseq_version

from .form import (
    CancerSNVariantForm,
    CaseDataForm,
    SNVariantForm,
    SVariantForm,
)

LOG = logging.getLogger(__name__)


def _get_var_tx_hgvs(case_obj: dict, variant_obj: dict) -> List[Tuple[str, str]]:
    """Retrieve all transcripts / HGVS for a given variant."""

    build = get_case_genome_build(case_obj)
    tx_hgvs_list = [("", "Do not specify")]
    case_has_build_37 = "37" in case_obj.get("genome_build", "37")

    add_gene_info(store, variant_obj, genome_build=build)

    for gene in variant_obj.get("genes", []):
        transcripts = gene.get("transcripts", [])

        for tx in transcripts:
            refseq_id = tx.get("refseq_id")
            coding_seq_name = tx.get("coding_sequence_name")
            if not (refseq_id and coding_seq_name):
                continue  # Skip transcripts missing required fields

            if case_has_build_37:
                for refseq in tx.get("refseq_identifiers", []):
                    refseq_version = fetch_refseq_version(refseq)
                    hgvs_simple = f"{refseq_version}:{coding_seq_name}"
                    validated = validate_hgvs(build, hgvs_simple)
                    label = f"{hgvs_simple}{'_validated_' if validated else ''}"
                    tx_hgvs_list.append((hgvs_simple, label))

            else:  # build 38, collect only MANE Select or MANE Plus Clinical
                mane_select = tx.get("mane_select_transcript")
                mane_plus_clinical = tx.get("mane_plus_clinical_transcript")
                if mane_select is None and mane_plus_clinical is None:
                    continue
                hgvs_simple = f"{mane_select or mane_plus_clinical}:{coding_seq_name}"
                label = f"{hgvs_simple}{'_mane-select_' if mane_select else ''}{'_mane-plus-clinical_' if mane_plus_clinical else ''}"
                tx_hgvs_list.append((hgvs_simple, label))
    return tx_hgvs_list


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
    var_form.assembly.data = "GRCh38" if get_case_genome_build(case_obj) == "38" else "GRCh37"
    var_form.chromosome.data = variant_obj.get("chromosome")
    var_form.ref.data = variant_obj.get("reference")
    var_form.alt.data = variant_obj.get("alternative")
    if variant_obj.get("category") in ["snv", "cancer"]:
        var_form.gene_symbol.data = ",".join(variant_obj.get("hgnc_symbols", []))
    var_form.last_evaluated.data = datetime.now()
    var_form.hpo_terms.choices = [
        (
            hpo.get("phenotype_id").replace("HP:", ""),
            " - ".join([hpo.get("phenotype_id"), hpo.get("feature")]),
        )
        for hpo in case_obj.get("phenotype_terms", [])
    ]
    var_form.omim_terms.choices = [
        (term.get("disease_nr"), " - ".join([str(term.get("disease_nr")), term.get("description")]))
        for term in case_obj.get("diagnosis_phenotypes", [])
        if term["disease_id"].startswith("OMIM")
    ]
    var_form.orpha_terms.choices = [
        (term.get("disease_nr"), " - ".join([str(term.get("disease_nr")), term.get("description")]))
        for term in case_obj.get("diagnosis_phenotypes", [])
        if term["disease_id"].startswith("ORPHA")
    ]


def _get_snv_var_form(variant_obj: dict, case_obj: dict):
    """Sets up values for a SNV variant form
    Args:
        variant_obj(dict) scout.models.Variant
        case_obj(dict) scout.models.Case

    Returns:
        var_form(scout.server.blueprints.clinvar.form.SNVariantForm)
    """
    if case_obj.get("track") == "cancer":
        var_form = CancerSNVariantForm()
    else:
        var_form = SNVariantForm()
    _set_var_form_common_fields(var_form, variant_obj, case_obj)
    var_form.tx_hgvs.choices = _get_var_tx_hgvs(case_obj, variant_obj)
    var_ids = variant_obj.get("dbsnp_id") or ""
    var_form.variations_ids.data = var_ids.split(";")[0]
    var_form.chromosome.data = variant_obj.get("chromosome")
    var_form.start.data = variant_obj.get("position")
    var_form.stop.data = variant_obj.get("end")
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

    # try to preselect variant type from variant subcategory
    if variant_obj["sub_category"] in SCOUT_CLINVAR_SV_TYPES_MAP:
        var_form.var_type.data = SCOUT_CLINVAR_SV_TYPES_MAP[variant_obj["sub_category"]]

    return var_form


def _populate_variant_form(
    variant_obj: dict, case_obj: dict
) -> Union[SNVariantForm, SVariantForm, CancerSNVariantForm]:
    """Populate the Flaskform associated to a variant. This form will be used in the multistep ClinVar submission form."""

    form_getters = {
        "snv": _get_snv_var_form,
        "sv": _get_sv_var_form,
        "cancer": _get_snv_var_form,
    }
    category = variant_obj["category"]
    var_form = form_getters[category](variant_obj, case_obj)

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
        ind_form.allele_of_origin.data = (
            "somatic" if case_obj.get("track") == "cancer" else "germline"
        )
        cdata_form_list.append(ind_form)
    return cdata_form_list


def _variant_classification(var_obj: dict):
    """Set a 'classified_as' key/header_value in the variant object, to be displayed on
    form page with the aim of aiding setting the mandatory 'clinsig' form field

    Args:
        var_obj(scout.model.Variant) Could be a SNV, Cancer SNV, SV or cancer SV

    Returns:
        classification(str): Human readable classification or None
    """
    if "acmg_classification" in var_obj:
        return ACMG_MAP[var_obj["acmg_classification"]]
    elif "ccv_classification" in var_obj:
        return CCV_MAP[var_obj["ccv_classification"]]
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
    if not tx_hgvs:
        return
    clinvar_var["ref_seq"] = tx_hgvs.split(":")[0]
    clinvar_var["hgvs"] = tx_hgvs.split(":")[1]


def _set_conditions(clinvar_var: dict, form: ImmutableMultiDict):
    """Set condition_id_type and condition_id_values for a ClinVar variant."""

    condition_db: str = form.get("condition_type")
    clinvar_var["condition_id_type"] = condition_db
    condition_prefix: str = CONDITION_PREFIX[condition_db]
    clinvar_var["condition_id_value"] = ";".join(
        [f"{condition_prefix}{condition_id}" for condition_id in form.getlist("conditions")]
    )
    if bool(form.get("multiple_condition_explanation")):
        clinvar_var["explanation_for_multiple_conditions"] = form.get(
            "multiple_condition_explanation"
        )


def parse_variant_form_fields(form):
    """Parses input values provided by the user in the ClinVar add_one form
       and creates a Variant ClinVar dictionary to be saved in database (ClinVar collection)

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
    clinvar_var["assertion_method_cit"] = ":".join(
        [form["assertion_method_cit_db"], form["assertion_method_cit_id"]]
    )
    _parse_tx_hgvs(clinvar_var, form)
    _set_conditions(clinvar_var, form)
    if form.get("dbsnp_id"):
        clinvar_var["variations_ids"] = form["dbsnp_id"]

    if clinvar_var.get("ref_seq") and clinvar_var.get("hgvs"):
        # Variant is described by RefSeq and HGVS already, remove redundant fields from submission
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

    if update_status in ["open", "closed", "submitted"]:  # open or close a submission
        store.update_clinvar_submission_status(institute_id, submission_id, update_status)
    if update_status == "register_id":  # register an official ClinVar submission ID
        clinvar_id: str = request_obj.form.get("clinvar_id").replace(" ", "") or None
        store.update_clinvar_id(
            clinvar_id=clinvar_id if clinvar_id else None,
            submission_id=submission_id,
        )
    if update_status == "delete":  # delete a submission
        deleted_objects, deleted_submissions = store.delete_submission(submission_id=submission_id)
        flash(
            f"Removed {deleted_objects} objects and {deleted_submissions} submission from database",
            "info",
        )

    if update_status == "submit":
        submitter_key = request_obj.form.get("apiKey")
        send_api_submission(institute_id, submission_id, submitter_key)


def json_api_submission(submission_id: str) -> Tuple[int, dict]:
    """Returns an integer and a json submission object as a dict. If the submission is of type "oncogenocity" there is no need for conversion and can be used as is.
    Germline submission objects (Variant and Casedata database documents) are converted to a json submission using
    the PreClinVar service.
    """

    json_submission: dict = store.get_onc_submission_json(
        submission=submission_id
    )  # Oncogenocity submissions are already saved in the desired format
    if json_submission:
        return 200, json_submission

    variant_data: list = store.clinvar_objs(submission_id, "variant_data")
    obs_data: list = store.clinvar_objs(submission_id, "case_data")

    if not variant_data or not obs_data:
        return (400, "Submission must contain both Variant and CaseData info")

    # Retrieve eventual assertion criteria for the submission
    extra_params = store.clinvar_assertion_criteria(variant_data[0]) or {}

    # Retrieve genome build for the case submitted
    case_obj = store.case(case_id=variant_data[0].get("case_id")) or {"genome_build": 37}
    extra_params["assembly"] = "GRCh37" if "37" in get_case_genome_build(case_obj) else "GRCh38"

    def _write_file(afile, header, lines):  # Write temp CSV file
        writes = csv.writer(afile, delimiter=",", quoting=csv.QUOTE_ALL)
        writes.writerow(header)
        for line in lines:
            writes.writerow(line)
        afile.flush()
        afile.seek(0)

    with (
        NamedTemporaryFile(mode="a+", prefix="Variant", suffix=".csv") as variant_file,
        NamedTemporaryFile(mode="a+", prefix="CaseData", suffix=".csv") as casedata_file,
    ):
        # Write temp Variant CSV file
        _, variants_header, variants_lines = clinvar_submission_file(
            submission_id, "variant_data", "SUB000"
        )
        _write_file(variant_file, variants_header, variants_lines)

        # Write temp CaseData CSV file
        _, casedata_header, casedata_lines = clinvar_submission_file(
            submission_id, "case_data", "SUB000"
        )
        _write_file(casedata_file, casedata_header, casedata_lines)

        return clinvar_api.convert_to_json(variant_file.name, casedata_file.name, extra_params)


def send_api_submission(institute_id, submission_id, key):
    """Convert and validate ClinVar submission data to json.
       If json submission is validated, submit it using the ClinVar API

    Args:
        institute_id(str): _id of an institute
        submission_id(str): the database id of a clinvar submission
        key(str): a 64 alphanumeric characters' key
    """
    # Convert submission objects to json:
    code, conversion_res = json_api_submission(submission_id)

    if code != 200:  # Connection or conversion object errors
        flash(str(conversion_res), "warning")
        return

    clinvar_id = store.get_clinvar_id(
        submission_id
    )  # This is the official ID associated with this submission in Clinvar (ex: SUB999999)

    if clinvar_id:  # Check if submission object has already an associated ClinVar ID
        conversion_res["submissionName"] = clinvar_id

    service_url, code, submit_res = clinvar_api.submit_json(conversion_res, key)

    if code in [200, 201]:
        clinvar_id = submit_res.json().get("id")
        flash(
            f"Submission sent to API URL '{service_url}'. Saved successfully with ID: {clinvar_id}",
            "success",
        )

        # Update ClinVar submission ID with the ID returned from ClinVar
        store.update_clinvar_id(
            clinvar_id=clinvar_id,
            submission_id=submission_id,
        )
        # Update submission status as submitted
        store.update_clinvar_submission_status(
            institute_id=institute_id, submission_id=submission_id, status="submitted"
        )

    else:
        flash(
            f"Submission sent to API URL '{service_url}'. Returned the following error: {str(submit_res.json())}",
            "warning",
        )


def clinvar_submission_file(submission_id, csv_type, clinvar_subm_id):
    """Prepare content (header and lines) of a csv clinvar submission file
    Args:
        submission_id(str): the database id of a clinvar submission
        csv_type(str): 'variant_data' or 'case_data'
        clinvar_subm_id(str): The ID assigned to this submission by ClinVar
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


def add_clinvar_events(institute_obj: dict, case_obj: dict, variant_id: str):
    """Create case and variant-related events when a variants gets added to a ClinVar submission object."""

    variant_obj: dict = store.variant(document_id=variant_id)
    user_obj: dict = store.user(user_id=current_user._id)
    for category in ["case", "variant"]:
        store.create_event(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link=f"/{institute_obj['_id']}/{case_obj['display_name']}/{variant_obj['_id']}",
            category=category,
            verb="clinvar_add",
            variant=variant_obj,
            subject=variant_obj["display_name"],
        )


def add_variant_to_submission(institute_obj: dict, case_obj: dict, form: ImmutableMultiDict):
    """It is invoked by the 'clinvar_save' endpoint. Adds one variant with eventual CaseData observations to an open (or new) ClinVar submission."""

    variant_data: dict = parse_variant_form_fields(form)
    casedata_list: List[dict] = parse_casedata_form_fields(form)
    institute_id = institute_obj["_id"]

    # retrieve or create an open germline ClinVar submission:
    subm: dict = store.get_open_germline_clinvar_submission(institute_id, current_user._id)
    # save submission objects in submission:
    result: Optional[dict] = store.add_to_submission(subm["_id"], (variant_data, casedata_list))
    if result:
        flash(
            "An open ClinVar submission was updated correctly with submitted data",
            "success",
        )

        # Create user-related events
        add_clinvar_events(
            institute_obj=institute_obj, case_obj=case_obj, variant_id=form.get("linking_id")
        )


def remove_item_from_submission(submission: str, object_type: str, subm_variant_id: str):
    """It is invoked by the clinvar_delete_object endpoint. Removes a variant (+ casedata) or casedata info only from one ClinVar submission object."""

    store.delete_clinvar_object(
        object_id=subm_variant_id,
        object_type=object_type,
        submission_id=submission,
    )

    # If variant itself is removed, register event
    if object_type == "variant_data":
        variant_id: str = subm_variant_id.split("_")[-1]
        variant_obj: dict = store.variant(document_id=variant_id)
        if not variant_obj:
            return
        case_obj = store.case(case_id=variant_obj["case_id"])
        if not case_obj:
            return
        institute_obj: dict = store.institute(institute_id=variant_obj["institute"])
        user_obj: dict = store.user(user_id=current_user._id)
        for category in ["case", "variant"]:
            store.create_event(
                institute=institute_obj,
                case=case_obj,
                user=user_obj,
                link=f"/{variant_obj['_id']}/{case_obj['display_name']}/{variant_id}",
                category=category,
                verb="clinvar_remove",
                variant=variant_obj,
                subject=variant_obj["display_name"],
            )


### ClinVar oncogenicity variants submissions controllers


def set_onc_clinvar_form(var_id: str, data: dict):
    """Adds form key/values to the form used in ClinVar to create a multistep submission page for an oncogenic variant."""

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


def _parse_onc_classification(onc_item: dict, form: ImmutableMultiDict):
    """Assigns an oncogenicity classification to a submission item based on the user form."""
    onc_item["oncogenicityClassification"] = {
        "oncogenicityClassificationDescription": form.get("onc_classification"),
        "dateLastEvaluated": form.get("last_evaluated"),
    }
    if form.get("clinsig_comment"):
        onc_item["oncogenicityClassification"]["comment"] = form.get("clinsig_comment")


def _parse_onc_assertion(onc_item: dict, form: ImmutableMultiDict):
    """Adds to an oncogenicity classification item the specifics of the user classification."""

    if form.get("assertion_method_cit_id"):
        onc_item["oncogenicityClassification"]["citation"] = [
            {
                "db": form.get("assertion_method_cit_db"),
                "id": form.get("assertion_method_cit_id"),
            }
        ]


def _parse_variant_set(onc_item: dict, form: ImmutableMultiDict):
    """Parse variant specifics from the ClinVar user form. It's an array but we support oonly one variant per oncogenic item."""

    variant = {}
    if form.get("tx_hgvs") not in [None, "Do not specify"]:
        variant["hgvs"] = form["tx_hgvs"]
    else:  # Use coordinates
        variant["chromosomeCoordinates"] = {
            "assembly": form.get("assembly"),
            "chromosome": "MT" if form.get("chromosome") == "M" else form.get("chromosome"),
            "start": int(form.get("start")),
            "stop": int(form.get("stop")),
            "alternateAllele": form.get("alt"),
        }

    if form.get("gene_symbol"):
        variant["gene"] = [{"symbol": form["gene_symbol"]}]

    onc_item["variantSet"] = {"variant": [variant]}


def _parse_condition_set(onc_item: dict, form: ImmutableMultiDict):
    """Associate one or more phenotype conditions to a variant of a ClinVar submission."""
    onc_item["conditionSet"] = {"condition": []}
    selected_db = form.get("condition_type")
    selected_conditions: List[str] = form.getlist("conditions")
    for cond in selected_conditions:
        onc_item["conditionSet"]["condition"].append({"db": selected_db, "id": cond})
    if form.get("multiple_condition_explanation"):
        onc_item["conditionSet"]["multipleConditionExplanation"] = form.get(
            "multiple_condition_explanation"
        )


def _parse_observations(onc_item: dict, form: ImmutableMultiDict):
    """Associates observations to a variant of a ClinVar submission."""
    onc_item["observedIn"] = []
    include_inds = form.getlist("include_ind")
    ind_list = form.getlist("individual_id")
    affected_status_list = form.getlist("affected_status")
    allele_origin_list = form.getlist("allele_of_origin")
    collection_method_list = form.getlist("collection_method")
    somatic_fraction = form.getlist("somatic_allele_fraction")
    somatic_in_normal = form.getlist("somatic_allele_in_normal")

    for idx, ind_id in enumerate(ind_list):
        if ind_id not in include_inds:
            continue

        obs = {
            "alleleOrigin": allele_origin_list[idx],
            "affectedStatus": affected_status_list[idx],
            "collectionMethod": collection_method_list[idx],
            "numberOfIndividuals": 1,
            "presenceOfSomaticVariantInNormalTissue": somatic_in_normal[idx],
        }
        if somatic_fraction[idx]:
            obs["somaticVariantAlleleFraction"] = int(somatic_fraction[idx])

        onc_item["observedIn"].append(obs)


def parse_clinvar_onc_item(form: ImmutableMultiDict) -> dict:
    """Parse form fields for an oncogenic classication of a variant and converts it into the format extected by ClinVar (json dict)."""
    onc_item = {"recordStatus": "novel"}
    _parse_onc_classification(onc_item, form)
    _parse_onc_assertion(onc_item, form)
    _parse_variant_set(onc_item, form)
    _parse_condition_set(onc_item, form)
    _parse_observations(onc_item, form)

    return onc_item


def add_onc_variant_to_submission(institute_obj: dict, case_obj: dict, form: ImmutableMultiDict):
    """Adds a somatic variant to a pre-existing open oncogeginicty seubmission. If the latter doesn't exists it creates it."""

    onc_item: dict = parse_clinvar_onc_item(form)  # The variant item to add to an open submission

    # Add case specifics to the submission item
    onc_item["institute_id"] = institute_obj["_id"]
    onc_item["case_id"] = case_obj["_id"]
    onc_item["case_name"] = case_obj.get("display_name", "_id")
    onc_item["variant_id"] = form.get("linking_id")

    # Validate oncogenicity item model
    try:
        OncogenicitySubmissionItem(**onc_item)
    except ValidationError as ve:
        LOG.error(ve)
        flash(str(ve), "warning")
        return

    # retrieve or create an open ClinVar submission:
    onc_subm: dict = store.get_open_onc_clinvar_submission(
        institute_id=institute_obj["_id"], user_id=current_user._id
    )
    # Add variant to submission object
    onc_subm.setdefault("oncogenicitySubmission", []).append(onc_item)
    onc_subm["updated_at"] = datetime.now()
    store.clinvar_submission_collection.find_one_and_replace({"_id": onc_subm["_id"]}, onc_subm)

    # update case with submission info
    add_clinvar_events(
        institute_obj=institute_obj, case_obj=case_obj, variant_id=form.get("linking_id")
    )

    flash(
        "An open ClinVar submission was updated correctly with the variant details.",
        "success",
    )
