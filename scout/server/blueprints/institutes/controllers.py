# -*- coding: utf-8 -*-
import datetime
import logging

LOG = logging.getLogger(__name__)

from flask_login import current_user
from flask import flash
from scout.parse.clinvar import clinvar_submission_header, clinvar_submission_lines
from scout.server.extensions import store
from scout.server.utils import user_institutes


def institute(store, institute_id):
    """ Process institute data.

    Args:
        store(adapter.MongoAdapter)
        institute_id(str)

    Returns
        data(dict): includes institute obj and specific settings
    """

    institute_obj = store.institute(institute_id)
    users = list(store.users(institute_id))

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


def gene_variants(store, variants_query, institute_id, page=1, per_page=50):
    """Pre-process list of variants."""
    # We need to call variants_collection.count_documents here
    variant_count = variants_query.count()
    skip_count = per_page * max(page - 1, 0)
    more_variants = True if variant_count > (skip_count + per_page) else False
    variant_res = variants_query.skip(skip_count).limit(per_page)

    my_institutes = set(inst["_id"] for inst in user_institutes(store, current_user))

    variants = []
    for variant_obj in variant_res:
        # Populate variant case_display_name
        variant_case_obj = store.case(case_id=variant_obj["case_id"])
        if not variant_case_obj:
            # A variant with missing case was encountered
            continue
        case_display_name = variant_case_obj.get("display_name")
        variant_obj["case_display_name"] = case_display_name

        # hide other institutes for now
        other_institutes = set([variant_case_obj.get("owner")])
        other_institutes.update(set(variant_case_obj.get("collaborators", [])))
        if my_institutes.isdisjoint(other_institutes):
            # If the user does not have access to the information we skip it
            continue

        genome_build = variant_case_obj.get("genome_build", "37")
        if genome_build not in ["37", "38"]:
            genome_build = "37"

        # Update the HGNC symbols if they are not set
        variant_genes = variant_obj.get("genes")
        if variant_genes is not None:
            for gene_obj in variant_genes:
                # If there is no hgnc id there is nothin we can do
                if not gene_obj["hgnc_id"]:
                    continue
                # Else we collect the gene object and check the id
                if gene_obj.get("hgnc_symbol") is None or gene_obj.get("description") is None:
                    hgnc_gene = store.hgnc_gene(gene_obj["hgnc_id"], build=genome_build)
                    if not hgnc_gene:
                        continue
                    gene_obj["hgnc_symbol"] = hgnc_gene["hgnc_symbol"]
                    gene_obj["description"] = hgnc_gene["description"]

        # Populate variant HGVS and predictions
        gene_ids = []
        gene_symbols = []
        hgvs_c = []
        hgvs_p = []
        variant_genes = variant_obj.get("genes")

        if variant_genes is not None:
            functional_annotation = ""

            for gene_obj in variant_genes:
                hgnc_id = gene_obj["hgnc_id"]
                gene_symbol = gene(store, hgnc_id)["symbol"]
                gene_ids.append(hgnc_id)
                gene_symbols.append(gene_symbol)

                hgvs_nucleotide = "-"
                hgvs_protein = ""
                # gather HGVS info from gene transcripts
                transcripts_list = gene_obj.get("transcripts")
                for transcript_obj in transcripts_list:
                    if (
                        transcript_obj.get("is_canonical")
                        and transcript_obj.get("is_canonical") is True
                    ):
                        hgvs_nucleotide = str(transcript_obj.get("coding_sequence_name"))
                        hgvs_protein = str(transcript_obj.get("protein_sequence_name"))
                hgvs_c.append(hgvs_nucleotide)
                hgvs_p.append(hgvs_protein)

            if len(gene_symbols) == 1:
                if hgvs_p[0] != "None":
                    hgvs = hgvs_p[0]
                elif hgvs_c[0] != "None":
                    hgvs = hgvs_c[0]
                else:
                    hgvs = "-"
                variant_obj["hgvs"] = hgvs

            # populate variant predictions for display
            variant_obj.update(predictions(variant_genes))

        variants.append(variant_obj)

    return {"variants": variants, "more_variants": more_variants}


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
    flash(
        f"Renamed {n_renamed} case data individuals from '{old_name}' to '{new_name}'", "info",
    )


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
