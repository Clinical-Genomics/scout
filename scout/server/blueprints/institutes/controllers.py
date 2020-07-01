# -*- coding: utf-8 -*-
import datetime
import logging

LOG = logging.getLogger(__name__)

from flask import flash
from scout.parse.clinvar import clinvar_submission_header, clinvar_submission_lines
from scout.server.extensions import store


def institute(store, institute_id):
    """ Process institute data.

    Args:
        store(adapter.MongoAdapter)
        institute_id(str)

    Returns
        data(dict): includes institute obj and specific settings
    """

    institute_obj = store.institute(institute_id)
    users = store.users(institute_id)

    data = {"institute": institute_obj, "users": users}
    return data


def populate_institute_form(form, institute_obj):
    """ Populate institute settings form

    Args:
        form(scout.server.blueprints.institutes.models.InstituteForm)
        institute_obj(dict) An institute object
    """
    # get all other institutes to populate the select of the possible collaborators
    institutes_tuples = []
    for inst in store.institutes():
        if not inst["_id"] == institute_obj["_id"]:
            institutes_tuples.append(((inst["_id"], inst["display_name"])))

    form.display_name.default = institute_obj.get("display_name")
    form.institutes.choices = institutes_tuples
    form.coverage_cutoff.default = institute_obj.get("coverage_cutoff")
    form.frequency_cutoff.default = institute_obj.get("frequency_cutoff")

    # collect all available default HPO terms
    default_phenotypes = [choice[0].split(" ")[0] for choice in form.pheno_groups.choices]
    if institute_obj.get("phenotype_groups"):
        for key, value in institute_obj["phenotype_groups"].items():
            if not key in default_phenotypes:
                custom_group = " ".join(
                    [key, ",", value.get("name"), "( {} )".format(value.get("abbr"))]
                )
                form.pheno_groups.choices.append((custom_group, custom_group))

    return default_phenotypes


def update_institute_settings(store, institute_obj, form):
    """ Update institute settings with data collected from institute form

    Args:
        score(adapter.MongoAdapter)
        institute_id(str)
        form(dict)

    Returns:
        updated_institute(dict)

    """
    sanger_recipients = []
    sharing_institutes = []
    phenotype_groups = []
    group_abbreviations = []
    cohorts = []

    for email in form.getlist("sanger_emails"):
        sanger_recipients.append(email.strip())

    for inst in form.getlist("institutes"):
        sharing_institutes.append(inst)

    for pheno_group in form.getlist("pheno_groups"):
        phenotype_groups.append(pheno_group.split(" ,")[0])
        group_abbreviations.append(pheno_group[pheno_group.find("( ") + 2 : pheno_group.find(" )")])

    if form.get("hpo_term") and form.get("pheno_abbrev"):
        phenotype_groups.append(form["hpo_term"].split(" |")[0])
        group_abbreviations.append(form["pheno_abbrev"])

    for cohort in form.getlist("cohorts"):
        cohorts.append(cohort.strip())

    updated_institute = store.update_institute(
        internal_id=institute_obj["_id"],
        sanger_recipients=sanger_recipients,
        coverage_cutoff=int(form.get("coverage_cutoff")),
        frequency_cutoff=float(form.get("frequency_cutoff")),
        display_name=form.get("display_name"),
        phenotype_groups=phenotype_groups,
        group_abbreviations=group_abbreviations,
        add_groups=False,
        sharing_institutes=sharing_institutes,
        cohorts=cohorts,
    )
    return updated_institute


def clinvar_submissions(store, institute_id):
    """Get all Clinvar submissions for a user and an institute"""
    submissions = list(store.clinvar_submissions(institute_id))
    return submissions


def update_clinvar_submission_status(store, request, institute_id, submission_id):
    """Update the status of a clinVar submission

    Args:
        store(adapter.MongoAdapter)
        request(flask.request) POST request sent by form submission
        institute_id(str) institute id
        submission_id(str) the database id of a clinvar submission
    """
    update_status = request.form.get("update_submission")

    if update_status in ["open", "closed"]:  # open or close a submission
        store.update_clinvar_submission_status(institute_id, submission_id, update_status)
    if update_status == "register_id":  # register an official clinvar submission ID
        result = store.update_clinvar_id(
            clinvar_id=request.form.get("clinvar_id"), submission_id=submission_id,
        )
    if update_status == "delete":  # delete a submission
        deleted_objects, deleted_submissions = store.delete_submission(submission_id=submission_id)
        flash(
            f"Removed {deleted_objects} objects and {deleted_submissions} submission from database",
            "info",
        )


def update_clinvar_sample_names(store, submission_id, case_id, old_name, new_name):
    """Update casedata sample names

    Args:
        store(adapter.MongoAdapter)
        submission_id(str) the database id of a clinvar submission
        case_id(str): case id
        old_name(str): old name of an individual in case data
        new_name(str): new name of an individual in case data
    """
    n_renamed = store.rename_casedata_samples(submission_id, case_id, old_name, new_name)
    flash(f"Renamed {n_renamed} case data individuals from '{old_name}' to '{new_name}'", "info")


def clinvar_submission_file(store, submission_id, csv_type, clinvar_subm_id):
    """Prepare content (header and lines) of a csv clinvar submission file

    Args:
        store(adapter.MongoAdapter)
        submission_id(str): the database id of a clinvar submission
        csv_type(str): 'variant_data' or 'case_data'
        clinvar_subm_id(str): The ID assigned to this submission by clinVar

    Returns:
        (filename, csv_header, csv_lines):
            filename(str) name of file to be downloaded
            csv_header(list) string list content of file header
            csv_lines(list) string list content of file lines
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
    csv_header_obj = clinvar_header(submission_objs, csv_type)
    csv_lines = clinvar_lines(submission_objs, csv_header_obj)
    csv_header = list(csv_header_obj.values())
    csv_header = [
        '"' + str(x) + '"' for x in csv_header
    ]  # quote columns in header for csv rendering

    today = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    if csv_type == "variant_data":
        filename = f"{clinvar_subm_id}_{today}.Variant.csv"
    else:
        filename = f"{clinvar_subm_id}_{today}.CaseData.csv"

    return (filename, csv_header, csv_lines)


def clinvar_header(submission_objs, csv_type):
    """ Call clinvar parser to extract required fields to include in csv header from clinvar submission objects

    Args:
        submission_objs(list)
        csv_type(str)

    Returns:
        clinvar_header_obj(dict) # custom csv header (dict based on constants CLINVAR_HEADER and CASEDATA_HEADER, but with required fields only)
    """

    clinvar_header_obj = clinvar_submission_header(submission_objs, csv_type)
    return clinvar_header_obj


def clinvar_lines(clinvar_objects, clinvar_header_obj):
    """ Call clinvar parser to extract required lines to include in csv file from clinvar submission objects and header

    Args:
        clinvar_objects(list)
        clinvar_header_obj(dict)

    Returns:
        clinvar_lines(list) # csv lines (one for each variant/casedata to be submitted)

    """

    clinvar_lines = clinvar_submission_lines(clinvar_objects, clinvar_header_obj)
    return clinvar_lines
