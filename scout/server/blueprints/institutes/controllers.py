# -*- coding: utf-8 -*-
import datetime
import logging
import re

from anytree import Node, RenderTree
from anytree.exporter import DictExporter
from flask import current_app, flash, url_for
from flask_login import current_user
from pymongo import ASCENDING, DESCENDING

from scout.constants import CASE_SEARCH_TERMS, CASE_STATUSES, PHENOTYPE_GROUPS
from scout.server.blueprints.variant.utils import predictions, update_representative_gene
from scout.server.extensions import beacon, store
from scout.server.utils import institute_and_case, user_institutes
from scout.utils.md5 import generate_md5_key

from .forms import BeaconDatasetForm, CaseFilterForm

LOG = logging.getLogger(__name__)


# Do not assume all cases have a valid track set
TRACKS = {None: "Rare Disease", "rare": "Rare Disease", "cancer": "Cancer"}

# These events are registered both for a case and a variant of the same case
VAR_SPECIFIC_EVENTS = [
    "mark_causative",
    "unmark_causative",
    "mark_partial_causative",
    "unmark_partial_causative",
    "pin",
    "unpin",
    "sanger",
    "cancel_sanger",
]


def get_timeline_data(limit):
    """Retrieve chronologially ordered events from the database to display them in the timeline page

    Args:
        limit(str): for instance "50" to display last 50 events. "-1" to display all events

    Returns:
        timeline_results(dict): dictionary containing timeline data
    """
    timeline_results = []
    results = store.user_timeline(current_user.email, int(limit))
    for eventg in results:  # Add links to cases pages
        case_obj = store.case(case_id=eventg["_id"]["case_id"])
        if case_obj is None:
            continue
        # Some events are captured both for case and variant. Display them only once (for the variant)
        if (
            eventg["_id"].get("category") == "case"
            and eventg["_id"].get("verb") in VAR_SPECIFIC_EVENTS
        ):
            continue
        # Build link to case page
        eventg["_id"]["case_name"] = case_obj.get("display_name")
        eventg["_id"]["link"] = url_for(
            "cases.case",
            institute_id=eventg["_id"]["institute"],
            case_name=case_obj["display_name"],
        )
        timeline_results.append(eventg)
    return timeline_results


def verified_vars(institute_id):
    """Create content to be displayed on institute verified page

    Args:
        institute_id(str): institute["_id"] value

    Returns:
        verified(list): list of variant objects (True positive or False Positive)
    """
    verified = []
    for variant_obj in store.verified(institute_id=institute_id):
        variant_genes = variant_obj.get("genes", [])
        if variant_obj["category"] in ["snv", "cancer"]:
            update_representative_gene(
                variant_obj, variant_genes
            )  # required to display cDNA and protein change
        variant_obj.update(predictions(variant_genes))
        verified.append(variant_obj)

    return verified


def verified_stats(institute_id, verified_vars):
    """Create content to be displayed on institute verified page, stats chart

    Args:
        institute_id(str): institute["_id"] value
        verified_vars(list): a list of verified varianst (True positive or False Positive)

    Returns:
        stats(tuple) -> True positives, False positives, validation unknown

    """
    true_pos = 0
    false_pos = 0
    for var in verified_vars:
        if var.get("validation") == "True positive":
            true_pos += 1
        else:
            false_pos += 1

    n_validations_ordered = len(list(store.validations_ordered(institute_id)))
    return true_pos, false_pos, n_validations_ordered - (true_pos + false_pos)


def causatives(institute_obj, request):
    """Create content to be displayed on institute causatives page

    Args:
        institute_obj(dict) An institute object
        request(flask.request) request sent by user's browser

    Returns:
        causatives(list of dictionaries)
    """
    # Retrieve variants grouped by case
    query = request.args.get("query", "")
    hgnc_id = None
    if "|" in query:
        # filter accepts an array of IDs. Provide an array with one ID element
        try:
            hgnc_id = [int(query.split(" | ", 1)[0])]
        except ValueError:
            flash("Provided gene info could not be parsed!", "warning")

    causatives = []

    for variant_obj in store.check_causatives(institute_obj=institute_obj, limit_genes=hgnc_id):
        variant_genes = variant_obj.get("genes", [])
        if variant_obj["category"] in ["snv", "cancer"]:
            update_representative_gene(
                variant_obj, variant_genes
            )  # required to display cDNA and protein change
        variant_obj.update(predictions(variant_genes))
        case_obj = store.case(variant_obj["case_id"])
        if not case_obj:
            continue
        variant_obj["case_obj"] = {
            "display_name": case_obj["display_name"],
            "individuals": case_obj["individuals"],
            "status": case_obj.get("status"),
            "partial_causatives": case_obj.get("partial_causatives", []),
        }

        causatives.append(variant_obj)

    return causatives


def institutes():
    """Returns institutes info available for a user
    Returns:
        data(list): a list of institute dictionaries
    """

    institute_objs = user_institutes(store, current_user)
    institutes = []
    for ins_obj in institute_objs:
        sanger_recipients = []
        for user_mail in ins_obj.get("sanger_recipients", []):
            user_obj = store.user(user_mail)
            if not user_obj:
                continue
            sanger_recipients.append(user_obj["name"])
        institutes.append(
            {
                "display_name": ins_obj["display_name"],
                "internal_id": ins_obj["_id"],
                "coverage_cutoff": ins_obj.get("coverage_cutoff", "None"),
                "sanger_recipients": sanger_recipients,
                "frequency_cutoff": ins_obj.get("frequency_cutoff", "None"),
                "phenotype_groups": ins_obj.get("phenotype_groups", PHENOTYPE_GROUPS),
                "case_count": sum(1 for i in store.cases(collaborator=ins_obj["_id"])),
            }
        )
    return institutes


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


def populate_beacon_form(institute_obj):
    """Populate the form select of scout.server.blueprints.institutes.forms.BeaconDatasetForm with data.
    Available data is a controlled dictionary of dataset names depending of the datasets already existing in the Beacon server

    Args:
        institute_obj(dict) An institute object
    """
    beacon_form = BeaconDatasetForm()

    if current_user.is_admin is False:
        return beacon_form

    if current_app.config.get("BEACON_URL") and current_app.config.get("BEACON_TOKEN"):
        # Collect all dataset IDs names present on the Beacon
        beacon_dsets = beacon.get_datasets()

        dset_options = []  # List of tuples containing dataset select options
        for build in beacon.dataset_builds:
            institute_build = "_".join([institute_obj["_id"], build])
            if (
                institute_build in beacon_dsets
            ):  # If dataset doesn't already exist, add the option to create it
                continue
            dset_options.append(
                (institute_build, f"{institute_obj['_id']} public dataset - Genome build {build}")
            )

        beacon_form.beacon_dataset.choices = dset_options

    return beacon_form


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
    form.gene_panels.choices = sorted(panel_set, key=lambda tup: tup[1])
    form.gene_panels_matching.choices = sorted(panel_set, key=lambda tup: tup[1])

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
    gene_panels_matching = {}
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

    for panel_name in form.getlist("gene_panels"):
        panel_obj = store.gene_panel(panel_name)
        if panel_obj is None:
            continue
        gene_panels[panel_name] = panel_obj["display_name"]

    for panel_name in form.getlist("gene_panels_matching"):
        panel_obj = store.gene_panel(panel_name)
        if panel_obj is None:
            continue
        gene_panels_matching[panel_name] = panel_obj["display_name"]

    for cohort in form.getlist("cohorts"):
        cohorts.append(cohort.strip())

    loqusdb_ids = form.getlist("loqusdb_id")
    if current_user.is_admin is False:
        loqusdb_ids = None

    updated_institute = store.update_institute(
        internal_id=institute_obj["_id"],
        sanger_recipients=sanger_recipients,
        coverage_cutoff=int(form.get("coverage_cutoff")),
        frequency_cutoff=float(form.get("frequency_cutoff")),
        display_name=form.get("display_name"),
        phenotype_groups=phenotype_groups,
        gene_panels=gene_panels,
        gene_panels_matching=gene_panels_matching,
        group_abbreviations=group_abbreviations,
        add_groups=False,
        sharing_institutes=sharing_institutes,
        cohorts=cohorts,
        loqusdb_ids=loqusdb_ids,
        alamut_key=form.get("alamut_key"),
        check_show_all_vars=form.get("check_show_all_vars"),
    )
    return updated_institute


def _sort_cases(data, request, all_cases):
    """Set cases data sorting values in cases data

    Args:
        data(dict): dictionary containing cases data
        request(flask.request) request sent by browser to the api_institutes endpoint
        all_cases(pymongo Cursor)

    Returns:
        all_cases(pymongo Cursor): Cursor of eventually sorted cases
    """

    sort_by = request.args.get("sort")
    sort_order = request.args.get("order") or "asc"
    if sort_by:
        pymongo_sort = ASCENDING
        if sort_order == "desc":
            pymongo_sort = DESCENDING
        if sort_by == "analysis_date":
            all_cases.sort("analysis_date", pymongo_sort)
        elif sort_by == "track":
            all_cases.sort("track", pymongo_sort)
        elif sort_by == "status":
            all_cases.sort("status", pymongo_sort)

    data["sort_order"] = sort_order
    data["sort_by"] = sort_by

    return all_cases


def cases(store, request, institute_id):
    """Preprocess case objects.

    Add all the necessary information to display the 'cases' view

    Args:
        store(adapter.MongoAdapter)
        request(flask.request) request sent by browser to the api_institutes endpoint
        institute_id(str): An _id of an institute

    Returns:
        data(dict): includes the cases, how many there are and the limit.
    """
    data = {"search_terms": CASE_SEARCH_TERMS}
    institute_obj = institute_and_case(store, institute_id)
    data["institute"] = institute_obj
    name_query = None
    if request.args.get("search_term"):
        name_query = "".join(
            [request.args.get("search_type"), re.escape(request.args["search_term"].strip())]
        )
    data["name_query"] = name_query
    limit = int(request.args.get("search_limit")) if request.args.get("search_limit") else 100
    data["form"] = populate_case_filter_form(request.args)

    prioritized_cases = store.prioritized_cases(institute_id=institute_id)
    all_cases = store.cases(
        collaborator=institute_id,
        name_query=name_query,
        skip_assigned=request.args.get("skip_assigned"),
        is_research=request.args.get("is_research"),
        has_rna_data=request.args.get("has_rna"),
        verification_pending=request.args.get("validation_ordered"),
        has_clinvar_submission=request.args.get("clinvar_submitted"),
    )
    all_cases = _sort_cases(data, request, all_cases)

    data["nr_cases"] = store.nr_cases(institute_id=institute_id)
    data["status_ncases"] = store.nr_cases_by_status(institute_id=institute_id)
    data["sanger_unevaluated"] = get_sanger_unevaluated(store, institute_id, current_user.email)

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
        # Check if case was re-runned
        last_analysis_date = case_obj.get("analysis_date", datetime.datetime.now())
        all_analyses_dates = set()
        for analysis in case_obj.get("analyses", [{"date": last_analysis_date}]):
            all_analyses_dates.add(analysis.get("date", last_analysis_date))

        case_obj["is_rerun"] = len(all_analyses_dates) > 1 or last_analysis_date > max(
            all_analyses_dates
        )

        case_obj["clinvar_variants"] = store.case_to_clinVars(case_obj["_id"])
        case_obj["display_track"] = TRACKS[case_obj.get("track", "rare")]
        return case_obj

    for nr_cases, case_obj in enumerate(all_cases.limit(limit), 1):
        case_obj = populate_case_obj(case_obj)
        case_groups[case_obj["status"]].append(case_obj)

    if prioritized_cases:
        extra_prioritized = 0
        for case_obj in prioritized_cases:
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

    data["cases"] = [(status, case_groups[status]) for status in CASE_STATUSES]
    data["found_cases"] = nr_cases
    data["limit"] = limit
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


def gene_variants(store, pymongo_cursor, variant_count, page=1, per_page=50):
    """Pre-process list of variants."""

    skip_count = per_page * max(page - 1, 0)
    more_variants = True if variant_count > (skip_count + per_page) else False
    variant_res = pymongo_cursor.skip(skip_count).limit(per_page)
    variants = []

    for variant_obj in variant_res:
        # Populate variant case_display_name
        variant_case_obj = store.case(case_id=variant_obj["case_id"])
        case_display_name = variant_case_obj.get("display_name")
        variant_obj["case_display_name"] = case_display_name

        genome_build = get_genome_build(variant_case_obj)
        update_variant_genes(store, variant_obj, genome_build)
        variants.append(variant_obj)

    return {"variants": variants, "more_variants": more_variants}


def filters(store, institute_id):
    """Retrieve all filters for an institute"""
    filters = []
    categories = ["cancer", "snv", "str", "sv"]
    for category in categories:
        category_filters = store.filters(institute_id, category)
        filters.extend(category_filters)

    return filters


def update_variant_genes(store, variant_obj, genome_build):
    """Update the HGNC symbols and HGVS predictions if they are not set

    Accepts:
        store(adapter.MongoAdapter)
        variant_obj(scout.models.variant.Variant): a dictionary
        genome_build(str): "37" or "38"
    """

    hgvs_c = []
    hgvs_p = []
    gene_symbols = set()

    for gene_obj in variant_obj.get("genes", []):
        hgnc_id = gene_obj.get("hgnc_id")
        if hgnc_id is None:
            continue
        gene_caption = store.hgnc_gene_caption(hgnc_id, genome_build)
        if gene_caption is None:
            continue
        # Make sure that gene symbol and description have a value
        gene_obj["hgnc_symbol"] = gene_caption["hgnc_symbol"]
        gene_obj["description"] = gene_caption["description"]

        gene_symbols.add(gene_obj["hgnc_symbol"])

        # gather HGVS info from gene transcripts
        (hgvs_nucleotide, hgvs_protein) = get_hgvs(gene_obj)
        hgvs_c.append(hgvs_nucleotide)
        hgvs_p.append(hgvs_protein)

    if len(gene_symbols) == 1:
        variant_obj["hgvs"] = hgvs_str(list(gene_symbols), hgvs_p, hgvs_c)


def get_genome_build(variant_case_obj):
    """Find genom build in `variant_case_obj`. If not found use build #37"""
    build = str(variant_case_obj.get("genome_build"))
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
    """ """
    if hgvs_p[0] != "None":
        return hgvs_p[0]
    if hgvs_c[0] != "None":
        return hgvs_c[0]
    return "-"


def _subpanel_omim_checkbox_add(model_dict, user_form):
    """Add an OMIM checkbox to a phenotype subpanel
    Args:
        model_dict(dict): a dictionary coresponding to a phenotype model
        user_form(request.form): a POST request form object

    Returns:
        model_dict(dict): an updated phenotype model dictionary to be saved to database
    """
    subpanel_id = user_form.get("omim_subpanel_id")
    omim_id = user_form.get("omim_term").split(" | ")[0]
    omim_obj = store.disease_term(omim_id)
    if omim_obj is None:
        flash("Please specify a valid OMIM term", "warning")
        return
    checkboxes = model_dict["subpanels"][subpanel_id].get("checkboxes", {})
    if omim_id in checkboxes:
        flash(f"Omim term '{omim_id}' already exists in this panel", "warning")
        return

    checkbox_obj = dict(name=omim_id, description=omim_obj.get("description"), checkbox_type="omim")
    if user_form.get("omimTermTitle"):
        checkbox_obj["term_title"] = user_form.get("omimTermTitle")
    if user_form.get("omim_custom_name"):
        checkbox_obj["custom_name"] = user_form.get("omim_custom_name")
    checkboxes[omim_id] = checkbox_obj
    model_dict["subpanels"][subpanel_id]["checkboxes"] = checkboxes
    model_dict["subpanels"][subpanel_id]["updated"] = datetime.datetime.now()
    return model_dict


def _subpanel_hpo_checkgroup_add(model_dict, user_form):
    """Add an HPO term (and eventually his children) to a phenotype subpanel

    Args:
        model_dict(dict): a dictionary coresponding to a phenotype model
        user_form(request.form): a POST request form object

    Returns:
        model_dict(dict): an updated phenotype model dictionary to be saved to database
    """
    hpo_id = user_form.get("hpo_term").split(" ")[0]
    hpo_obj = store.hpo_term(hpo_id)
    if hpo_obj is None:  # user didn't provide a valid HPO term
        flash("Please specify a valid HPO term", "warning")
        return
    subpanel_id = user_form.get("hpo_subpanel_id")
    tree_dict = {}
    checkboxes = model_dict["subpanels"][subpanel_id].get("checkboxes", {})

    if hpo_id in checkboxes:  # Do not include duplicated HPO terms in checkbox items
        flash(f"Subpanel contains already HPO term '{hpo_id}'", "warning")
        return
    if user_form.get("includeChildren"):  # include HPO terms children in the checkboxes
        tree_dict = store.build_phenotype_tree(hpo_id)
        if tree_dict is None:
            flash(f"An error occurred while creating HPO tree from '{hpo_id}'", "danger")
            return
    else:  # include just HPO term as a standalone checkbox:
        tree_dict = dict(name=hpo_obj["_id"], description=hpo_obj["description"])
    tree_dict["checkbox_type"] = "hpo"
    if user_form.get("hpoTermTitle"):
        tree_dict["term_title"] = user_form.get("hpoTermTitle")
    if user_form.get("hpo_custom_name"):
        tree_dict["custom_name"] = user_form.get("hpo_custom_name")
    checkboxes[hpo_id] = tree_dict
    model_dict["subpanels"][subpanel_id]["checkboxes"] = checkboxes
    model_dict["subpanels"][subpanel_id]["updated"] = datetime.datetime.now()
    return model_dict


def _subpanel_checkgroup_remove_one(model_dict, user_form):
    """Remove a checkbox group from a phenotype subpanel

    Args:
        model_dict(dict): a dictionary coresponding to a phenotype model
        user_form(request.form): a POST request form object

    Returns:
        model_dict(dict): an updated phenotype model dictionary to be saved to database
    """
    subpanel_id = user_form.get("checkgroup_remove").split("#")[1]
    remove_field = user_form.get("checkgroup_remove").split("#")[0]

    try:
        model_dict["subpanels"][subpanel_id]["checkboxes"].pop(remove_field, None)
        model_dict["subpanels"][subpanel_id]["updated"] = datetime.datetime.now()
    except Exception as ex:
        flash(ex, "danger")

    return model_dict


def _update_subpanel(subpanel_obj, supb_changes):
    """Update the checkboxes of a subpanel according to checkboxes checked in the model preview.

    Args:
        subpanel_obj(dict): a subpanel object
        supb_changes(dict): terms to keep under a parent term. example: {"HP:0001250": [(HP:0020207, HP:0020215, HP:0001327]}

    Returns:
        subpanel_obj(dict): an updated subpanel object
    """
    checkboxes = subpanel_obj.get("checkboxes", {})
    new_checkboxes = {}
    for parent, children_list in supb_changes.items():
        # create mini tree obj from terms in changes dict. Add all nodes at the top level initially
        root = Node(id="root", name="root", parent=None)
        all_terms = {}
        # loop over the terms to keep into the checboxes dict
        for child in children_list:
            if child.startswith("OMIM"):
                new_checkboxes[child] = checkboxes[child]
                continue
            custom_name = None
            term_title = None
            if child in checkboxes:
                custom_name = checkboxes[child].get("custom_name")
                term_title = checkboxes[child].get("term_title")
            term_obj = store.hpo_term(child)  # else it's an HPO term, and might have nested term:
            node = None
            try:
                node = Node(child, parent=root, description=term_obj["description"])
            except Exception as ex:
                flash(f"Term {child} could not be find in database")
                continue
            all_terms[child] = term_obj
            if custom_name:
                node.custom_name = custom_name
            if term_title:
                node.term_title = term_title

        # Rearrange tree nodes according the HPO ontology
        root = store.organize_tree(all_terms, root)
        LOG.info(f"Updated HPO tree:{root}:\n{RenderTree(root)}")
        exporter = DictExporter()
        for child_node in root.children:
            # export node to dict
            node_dict = exporter.export(child_node)
            new_checkboxes[child_node.name] = node_dict

    subpanel_obj["checkboxes"] = new_checkboxes
    subpanel_obj["updated"] = datetime.datetime.now()
    return subpanel_obj


def phenomodel_checkgroups_filter(model_dict, user_form):
    """Filter the checboxes of one or more subpanels according to preferences specified in the model preview

    Args:
        model_dict(dict): a dictionary coresponding to a phenotype model
        user_form(request.form): a POST request form object

    Returns:
        model_dict(dict): an updated phenotype model dictionary to be saved to database
    """
    subpanels = model_dict.get("subpanels") or {}
    check_list = (
        user_form.getlist("cheked_terms") or []
    )  # a list like this: ["subpanelID.rootTerm_checkedTerm", .. ]
    updates_dict = {}
    # From form values, create a dictionary like this: { "subpanel_id1":{"parent_term1":[children_terms], parent_term2:[children_terms2]}, .. }
    for checked_value in check_list:
        panel_key = checked_value.split(".")[0]
        parent_term = checked_value.split(".")[1]
        child_term = checked_value.split(".")[2]
        if panel_key in updates_dict:
            if parent_term in updates_dict[panel_key]:
                updates_dict[panel_key][parent_term].append(child_term)
            else:
                updates_dict[panel_key][parent_term] = [child_term]
        else:
            updates_dict[panel_key] = {parent_term: [child_term]}

    # loop over the subpanels of the model, and check they need to be updated
    for key, subp in subpanels.items():
        if key in updates_dict:  # if subpanel requires changes
            model_dict["subpanels"][key] = _update_subpanel(subp, updates_dict[key])  # update it

    return model_dict


def _add_subpanel(model_id, model_dict, user_form):
    """Add an empty subpanel to a phenotype model

    Args:
        model_id(str): string of the ID of a phenotype model
        model_dict(dict): a dictionary coresponding to a phenotype model
        user_form(request.form): a POST request form object

    """
    subpanel_key = generate_md5_key([model_id, user_form.get("title")])
    phenomodel_subpanels = model_dict.get("subpanels") or {}

    if subpanel_key in phenomodel_subpanels:
        flash("A model panel with that title already exists", "warning")
        return
    subpanel_obj = {
        "title": user_form.get("title"),
        "subtitle": user_form.get("subtitle"),
        "created": datetime.datetime.now(),
        "updated": datetime.datetime.now(),
    }
    phenomodel_subpanels[subpanel_key] = subpanel_obj
    model_dict["subpanels"] = phenomodel_subpanels
    return model_dict


def edit_subpanel_checkbox(model_id, user_form):
    """Update checkboxes from one or more panels according to the user form
    Args:
        model_id(ObjectId): document ID of the model to be updated
        user_form(request.form): a POST request form object
    """
    model_dict = store.phenomodel(model_id)
    update_model = False
    if model_dict is None:
        return
    if "add_hpo" in user_form:  # add an HPO checkbox to subpanel
        update_model = _subpanel_hpo_checkgroup_add(model_dict, user_form)
    if "add_omim" in user_form:  # add an OMIM checkbox to subpanel
        update_model = _subpanel_omim_checkbox_add(model_dict, user_form)
    if user_form.get("checkgroup_remove"):  # remove a checkbox of any type from subpanel
        update_model = _subpanel_checkgroup_remove_one(model_dict, user_form)

    if update_model:
        store.update_phenomodel(model_id=model_id, model_obj=model_dict)


def update_phenomodel(model_id, user_form):
    """Update a phenotype model according to the user form

    Args:
        model_id(ObjectId): document ID of the model to be updated
        user_form(request.form): a POST request form object
    """
    model_dict = store.phenomodel(model_id)
    update_model = False
    if model_dict is None:
        return
    if user_form.get("update_model"):  # update either model name of description
        update_model = True
        model_dict["name"] = user_form.get("model_name")
        model_dict["description"] = user_form.get("model_desc")
    if user_form.get("subpanel_delete"):  # Remove a phenotype submodel from phenomodel
        subpanels = model_dict["subpanels"]
        # remove panel from subpanels dictionary
        subpanels.pop(user_form.get("subpanel_delete"), None)
        model_dict["subpanels"] = subpanels
        update_model = True
    if user_form.get("add_subpanel"):  # Add a new phenotype submodel
        update_model = _add_subpanel(model_id, model_dict, user_form)
    if user_form.get("model_save"):  # Save model according user preferences in the preview
        update_model = phenomodel_checkgroups_filter(model_dict, user_form)

    if update_model:
        store.update_phenomodel(model_id=model_id, model_obj=model_dict)


def lock_filter(store, user_obj, filter_id):
    """Lock filter and set owner from"""
    filter_obj = store.lock_filter(filter_id, user_obj.email)
    if filter_obj is None:
        flash("Requested filter could not be locked", "warning")
    return filter_obj


def unlock_filter(store, user_obj, filter_id):
    """Unlock filter, unset owner"""
    filter_obj = store.unlock_filter(filter_id, user_obj.email)
    if filter_obj is None:
        flash("Requested filter could not be unlocked.", "warning")
    return filter_obj
