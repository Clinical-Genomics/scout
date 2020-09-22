# -*- coding: utf-8 -*-
import datetime
import logging

LOG = logging.getLogger(__name__)

from flask_login import current_user
from flask import flash
from scout.constants import CASE_STATUSES
from scout.parse.clinvar import clinvar_submission_header, clinvar_submission_lines
from scout.server.blueprints.genes.controllers import gene
from scout.server.blueprints.variant.utils import predictions
from scout.server.extensions import store
from scout.server.utils import user_institutes
from .forms import CaseFilterForm


TRACKS = {"rare": "Rare Disease", "cancer": "Cancer"}


def institute(store, institute_id):
    """Process institute data.

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
    """Populate institute settings form

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

    # collect all available default HPO terms and populate the pheno_groups form select with these values
    default_phenotypes = [choice[0].split(" ")[0] for choice in form.pheno_groups.choices]
    if institute_obj.get("phenotype_groups"):
        for key, value in institute_obj["phenotype_groups"].items():
            if not key in default_phenotypes:
                custom_group = " ".join(
                    [key, ",", value.get("name"), "( {} )".format(value.get("abbr"))]
                )
                form.pheno_groups.choices.append((custom_group, custom_group))

    # populate gene panels multiselect with panels from institute
    available_panels = list(store.latest_panels(institute_obj["_id"]))
    # And from institute's collaborators
    for collaborator in institute_obj.get("collaborators", []):
        available_panels += list(store.latest_panels(collaborator))
    panel_set = set()
    for panel in available_panels:
        panel_set.add((panel["panel_name"], panel["display_name"]))
    form.gene_panels.choices = list(panel_set)
    return default_phenotypes


def update_institute_settings(store, institute_obj, form):
    """Update institute settings with data collected from institute form

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
    gene_panels = {}
    group_abbreviations = []
    cohorts = []
    loqusdb_id = []

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

    for panel_name in form.getlist("gene_panels"):
        panel_obj = store.gene_panel(panel_name)
        if panel_obj is None:
            continue
        gene_panels[panel_name] = panel_obj["display_name"]

    for cohort in form.getlist("cohorts"):
        cohorts.append(cohort.strip())

    if form.get("loqusdb_id"):
        loqusdb_id.append(form.get("loqusdb_id"))

    updated_institute = store.update_institute(
        internal_id=institute_obj["_id"],
        sanger_recipients=sanger_recipients,
        coverage_cutoff=int(form.get("coverage_cutoff")),
        frequency_cutoff=float(form.get("frequency_cutoff")),
        display_name=form.get("display_name"),
        phenotype_groups=phenotype_groups,
        gene_panels=gene_panels,
        group_abbreviations=group_abbreviations,
        add_groups=False,
        sharing_institutes=sharing_institutes,
        cohorts=cohorts,
        loqusdb_id=form.get("loqusdb_id"),
    )
    return updated_institute


def cases(store, case_query, prioritized_cases_query=None, limit=100):
    """Preprocess case objects.

    Add the necessary information to display the 'cases' view

    Args:
        store(adapter.MongoAdapter)
        case_query(pymongo.Cursor)
        prioritized_cases_query(pymongo.Cursor)
        limit(int): Maximum number of cases to display

    Returns:
        data(dict): includes the cases, how many there are and the limit.
    """
    case_groups = {status: [] for status in CASE_STATUSES}
    nr_cases = 0

    # local function to add info to case obj
    def populate_case_obj(case_obj):
        analysis_types = set(ind["analysis_type"] for ind in case_obj["individuals"])
        LOG.debug("Analysis types found in %s: %s", case_obj["_id"], ",".join(analysis_types))
        if len(analysis_types) > 1:
            LOG.debug("Set analysis types to {'mixed'}")
            analysis_types = set(["mixed"])

        case_obj["analysis_types"] = list(analysis_types)
        case_obj["assignees"] = [
            store.user(user_email) for user_email in case_obj.get("assignees", [])
        ]
        case_obj["is_rerun"] = len(case_obj.get("analyses", [])) > 0
        case_obj["clinvar_variants"] = store.case_to_clinVars(case_obj["_id"])
        case_obj["display_track"] = TRACKS[case_obj.get("track", "rare")]
        return case_obj

    for nr_cases, case_obj in enumerate(case_query.limit(limit), 1):
        case_obj = populate_case_obj(case_obj)
        case_groups[case_obj["status"]].append(case_obj)

    if prioritized_cases_query:
        extra_prioritized = 0
        for case_obj in prioritized_cases_query:
            if any(
                group_obj.get("display_name") == case_obj.get("display_name")
                for group_obj in case_groups[case_obj["status"]]
            ):
                continue
            else:
                extra_prioritized += 1
                case_obj = populate_case_obj(case_obj)
                case_groups[case_obj["status"]].append(case_obj)
        # extra prioritized cases are potentially shown in addition to the case query limit
        nr_cases += extra_prioritized

    data = {
        "cases": [(status, case_groups[status]) for status in CASE_STATUSES],
        "found_cases": nr_cases,
        "limit": limit,
    }
    return data


def populate_case_filter_form(params):
    """Populate filter form with params previosly submitted by user

    Args:
        params(werkzeug.datastructures.ImmutableMultiDict)

    Returns:
        form(scout.server.blueprints.cases.forms.CaseFilterForm)
    """
    form = CaseFilterForm(params)
    form.search_type.default = params.get("search_type")
    search_term = form.search_term.data
    if ":" in search_term:
        form.search_term.data = search_term[search_term.index(":") + 1 :]  # remove prefix
    return form


def get_sanger_unevaluated(store, institute_id, user_id):
    """Get all variants for an institute having Sanger validations ordered but still not evaluated

    Args:
        store(scout.adapter.MongoAdapter)
        institute_id(str)

    Returns:
        unevaluated: a list that looks like this: [ {'case1': [varID_1, varID_2, .., varID_n]}, {'case2' : [varID_1, varID_2, .., varID_n]} ],
                     where the keys are case_ids and the values are lists of variants with Sanger ordered but not yet validated

    """

    # Retrieve a list of ids for variants with Sanger ordered grouped by case from the 'event' collection
    # This way is much faster than querying over all variants in all cases of an institute
    sanger_ordered_by_case = store.sanger_ordered(institute_id, user_id)
    unevaluated = []

    # for each object where key==case and value==[variant_id with Sanger ordered]
    for item in sanger_ordered_by_case:
        case_id = item["_id"]
        # Get the case to collect display name
        case_obj = store.case(case_id=case_id)

        if not case_obj:  # the case might have been removed
            continue

        case_display_name = case_obj.get("display_name")

        # List of variant document ids
        varid_list = item["vars"]

        unevaluated_by_case = {}
        unevaluated_by_case[case_display_name] = []

        for var_id in varid_list:
            # For each variant with sanger validation ordered
            variant_obj = store.variant(document_id=var_id, case_id=case_id)

            # Double check that Sanger was ordered (and not canceled) for the variant
            if (
                variant_obj is None
                or variant_obj.get("sanger_ordered") is None
                or variant_obj.get("sanger_ordered") is False
            ):
                continue

            validation = variant_obj.get("validation", "not_evaluated")

            # Check that the variant is not evaluated
            if validation in ["True positive", "False positive"]:
                continue

            unevaluated_by_case[case_display_name].append(variant_obj["_id"])

        # If for a case there is at least one Sanger validation to evaluate add the object to the unevaluated objects list
        if len(unevaluated_by_case[case_display_name]) > 0:
            unevaluated.append(unevaluated_by_case)

    return unevaluated


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

        genome_build = get_genome_build(variant_case_obj)
        variant_genes = variant_obj.get("genes")
        gene_object = update_HGNC_symbols(store, variant_genes, genome_build)

        # Populate variant HGVS and predictions
        variant_genes = variant_obj.get("genes")
        hgvs_c = []
        hgvs_p = []
        if variant_genes is not None:
            for gene_obj in variant_genes:
                hgnc_id = gene_obj["hgnc_id"]
                gene_symbol = gene(store, hgnc_id)["symbol"]
                gene_symbols = [gene_symbol]

                # gather HGVS info from gene transcripts
                (hgvs_nucleotide, hgvs_protein) = get_hgvs(gene_obj)
                hgvs_c.append(hgvs_nucleotide)
                hgvs_p.append(hgvs_protein)

            if len(gene_symbols) == 1:
                variant_obj["hgvs"] = hgvs_str(gene_symbols, hgvs_p, hgvs_c)

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
            clinvar_id=request.form.get("clinvar_id"),
            submission_id=submission_id,
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
        f"Renamed {n_renamed} case data individuals from '{old_name}' to '{new_name}'",
        "info",
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
    """Call clinvar parser to extract required fields to include in csv header from clinvar submission objects

    Args:
        submission_objs(list)
        csv_type(str)

    Returns:
        clinvar_header_obj(dict) # custom csv header (dict based on constants CLINVAR_HEADER and CASEDATA_HEADER, but with required fields only)
    """

    clinvar_header_obj = clinvar_submission_header(submission_objs, csv_type)
    return clinvar_header_obj


def clinvar_lines(clinvar_objects, clinvar_header_obj):
    """Call clinvar parser to extract required lines to include in csv file from clinvar submission objects and header

    Args:
        clinvar_objects(list)
        clinvar_header_obj(dict)

    Returns:
        clinvar_lines(list) # csv lines (one for each variant/casedata to be submitted)

    """

    clinvar_lines = clinvar_submission_lines(clinvar_objects, clinvar_header_obj)
    return clinvar_lines


def update_HGNC_symbols(store, variant_genes, genome_build):
    """Update the HGNC symbols if they are not set
    Returns:
        gene_object()"""

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


def get_genome_build(variant_case_obj):
    """Find genom build in `variant_case_obj`. If not found use build #37"""
    build = variant_case_obj.get("genome_build")
    if build in ["37", "38"]:
        return build
    return "37"


def get_hgvs(gene_obj):
    """Analyse gene object
    Return:
       (hgvs_nucleotide, hgvs_protein)"""
    hgvs_nucleotide = "-"
    hgvs_protein = ""

    transcripts_list = gene_obj.get("transcripts")
    for transcript_obj in transcripts_list:
        if transcript_obj.get("is_canonical") is True:
            hgvs_nucleotide = str(transcript_obj.get("coding_sequence_name"))
            hgvs_protein = str(transcript_obj.get("protein_sequence_name"))
    return (hgvs_nucleotide, hgvs_protein)


def hgvs_str(gene_symbols, hgvs_p, hgvs_c):
    """"""
    if hgvs_p[0] != "None":
        return hgvs_p[0]
    if hgvs_c[0] != "None":
        return hgvs_c[0]
    return "-"
