# -*- coding: utf-8 -*-
import datetime
import logging

LOG = logging.getLogger(__name__)

from flask import flash
from scout.parse.clinvar import clinvar_submission_header, clinvar_submission_lines

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

    if update_status == "close":  # close a submission
        store.update_clinvar_submission_status(institute_id, submission_id, "closed")
    elif update_status == "open":
        store.update_clinvar_submission_status(
            institute_id, submission_id, "open"
        )  # open a submission
    elif update_status == "register_id" and request.form.get(
        "clinvar_id"
    ):  # provide an official clinvar submission ID
        result = store.update_clinvar_id(
            clinvar_id=request.form.get("clinvar_id"), submission_id=submission_id,
        )
    elif request.form.get("update_submission") == "delete":  # delete a submission
        deleted_objects, deleted_submissions = store.delete_submission(submission_id=submission_id)
        flash(
            f"Removed {deleted_objects} objects and {deleted_submissions} submission from database",
            "info"
        )

def clinvar_submission_file(store, request, submission_id):
    """Prepare content (header and lines) of a csv clinvar submission file

    Args:
        store(adapter.MongoAdapter)
        request(flask.request) POST request sent by form submission
        submission_id(str) the database id of a clinvar submission

    Returns:
        (filename, csv_header, csv_lines):
            filename(str) name of file to be downloaded
            csv_header(list) string list content of file header
            csv_lines(list) string list content of file lines
    """
    clinvar_subm_id = request.form.get("clinvar_id")
    if clinvar_subm_id == "":
        flash(
            "In order to download a submission CSV file you should register a Clinvar submission Name first!",
            "warning",
        )
        return

    csv_type = request.form.get("csv_type", "")

    submission_objs = store.clinvar_objs(
        submission_id=submission_id, key_id=csv_type
    )  # a list of clinvar submission objects (variants or casedata)

    if submission_objs is None or len(submission_objs) == 0:
        flash(
            f"There are no submission objects of type '{csv_type}' to include in the csv file!",
            "warning")
        return

    # Download file
    csv_header_obj = clinvar_header(
        submission_objs, csv_type
    )  # custom csv header (dict as in constants CLINVAR_HEADER and CASEDATA_HEADER, but with required fields only)
    csv_lines = clinvar_lines(
        submission_objs, csv_header_obj
    )  # csv lines (one for each variant/casedata to be submitted)
    csv_header = list(csv_header_obj.values())
    csv_header = [
        '"' + str(x) + '"' for x in csv_header
    ]  # quote columns in header for csv rendering

    today = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    filename = f"{clinvar_subm_id}_{csv_type}_{today}.csv"

    return (filename, csv_header, csv_lines)


def clinvar_header(submission_objs, csv_type):
    """ Call clinvar parser to extract required fields to include in csv header from clinvar submission objects"""

    clinvar_header_obj = clinvar_submission_header(submission_objs, csv_type)
    return clinvar_header_obj


def clinvar_lines(clinvar_objects, clinvar_header):
    """ Call clinvar parser to extract required lines to include in csv file from clinvar submission objects and header"""

    clinvar_lines = clinvar_submission_lines(clinvar_objects, clinvar_header)
    return clinvar_lines
