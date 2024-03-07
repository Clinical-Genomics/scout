# -*- coding: utf-8 -*-
import datetime
import logging
from typing import Dict, List, Optional, Tuple

from flask import Response, current_app, flash, url_for
from flask_login import current_user
from pymongo import ASCENDING, DESCENDING
from pymongo.cursor import Cursor
from werkzeug.datastructures import Headers, MultiDict

from scout.adapter.mongo.base import MongoAdapter
from scout.constants import (
    CASE_SEARCH_TERMS,
    CASE_STATUSES,
    DATE_DAY_FORMATTER,
    ID_PROJECTION,
    PHENOTYPE_GROUPS,
)
from scout.server.blueprints.variant.utils import predictions, update_representative_gene
from scout.server.extensions import beacon, store
from scout.server.utils import institute_and_case, user_institutes

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


def decorate_institute_variant(variant_obj: dict) -> Optional[dict]:
    """Fetch data relative to causative/verified variants to be displayed in the institute pages."""

    case_obj = store.case(variant_obj["case_id"])
    if not case_obj:
        return
    variant_genes = variant_obj.get("genes", [])
    if variant_obj["category"] in ["snv", "cancer"]:
        update_representative_gene(
            variant_obj, variant_genes
        )  # required to display cDNA and protein change
    variant_obj.update(predictions(variant_genes))
    variant_obj["case_obj"] = {
        "display_name": case_obj["display_name"],
        "individuals": case_obj["individuals"],
        "status": case_obj.get("status"),
        "partial_causatives": case_obj.get("partial_causatives", []),
        "rank_model_version": case_obj.get("rank_model_version"),
        "sv_rank_model_version": case_obj.get("sv_rank_model_version"),
    }
    return variant_obj


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

    for variant_obj in store.institute_causatives(institute_obj=institute_obj, limit_genes=hgnc_id):
        decorated_variant = decorate_institute_variant(variant_obj)
        if decorated_variant:
            causatives.append(variant_obj)

    return causatives


def verified_vars(institute_id):
    """Create content to be displayed on institute verified page

    Args:
        institute_id(str): institute["_id"] value

    Returns:
        verified(list): list of variant objects (True positive or False Positive)
    """
    verified = []
    for variant_obj in store.verified(institute_id=institute_id):
        decorated_variant = decorate_institute_variant(variant_obj)
        if decorated_variant:
            verified.append(variant_obj)

    return verified


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
                "case_count": sum(
                    1 for i in store.cases(collaborator=ins_obj["_id"], projection=ID_PROJECTION)
                ),
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
                (
                    institute_build,
                    f"{institute_obj['_id']} public dataset - Genome build {build}",
                )
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
            institutes_tuples.append((inst["_id"], f'{inst["display_name"]} - {inst["_id"]}'))

    form.display_name.default = institute_obj.get("display_name")
    form.institutes.choices = institutes_tuples
    form.coverage_cutoff.default = institute_obj.get("coverage_cutoff")
    form.frequency_cutoff.default = institute_obj.get("frequency_cutoff")
    form.show_all_cases_status.data = institute_obj.get("show_all_cases_status") or ["prioritized"]

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

    institute_users: List[Tuple] = [
        (user["name"], user["email"]) for user in store.users(institute=institute_obj["_id"])
    ]
    form.clinvar_emails.choices = institute_users

    return default_phenotypes


def get_sanger_recipients(form: MultiDict) -> List[str]:
    """
    Return list of Sanger recipients from form multiselect.
    """
    sanger_recipients = []
    for email in form.getlist("sanger_emails"):
        sanger_recipients.append(email.strip())

    return sanger_recipients


def get_clinvar_submitters(form: MultiDict) -> Optional[List[str]]:
    """
    Return list of ClinVar sumbitters from form multiselect.
    This is not available on the form for unprivileged users, only admin.
    """

    clinvar_submitters = None
    if current_user.is_admin:
        clinvar_submitters = []
        for email in form.getlist("clinvar_emails"):
            clinvar_submitters.append(email.strip())
    return clinvar_submitters


def get_loqusdb_ids(form: MultiDict) -> Optional[List[str]]:
    """
    Return loqusdb ids from the form multiselect.
    This is not available on the form for unprivileged users, only admin.
    """
    if current_user.is_admin is False:
        return None

    return form.getlist("loqusdb_id")


def get_gene_panels(store: MongoAdapter, form: MultiDict, tag: str) -> Dict:
    """
    Return gene panel objects checked in the corresponding form multiselect.

    tag as in the form e.g. "gene_panels" or "gene_panels_matching".
    """
    return store.gene_panels_dict(panel_names=form.getlist(tag))


def update_institute_settings(store: MongoAdapter, institute_obj: Dict, form: MultiDict) -> Dict:
    """Update institute settings with data collected from institute form."""

    sharing_institutes = []
    for inst in form.getlist("institutes"):
        sharing_institutes.append(inst)

    phenotype_groups = []
    group_abbreviations = []

    for pheno_group in form.getlist("pheno_groups"):
        phenotype_groups.append(pheno_group.split(" ,")[0])
        group_abbreviations.append(pheno_group[pheno_group.find("( ") + 2 : pheno_group.find(" )")])

    if form.get("hpo_term") and form.get("pheno_abbrev"):
        phenotype_groups.append(form["hpo_term"].split(" |")[0])
        group_abbreviations.append(form["pheno_abbrev"])

    cohorts = []
    for cohort in form.getlist("cohorts"):
        cohorts.append(cohort.strip())

    updated_institute = store.update_institute(
        internal_id=institute_obj["_id"],
        sanger_recipients=get_sanger_recipients(form),
        coverage_cutoff=int(form.get("coverage_cutoff")),
        frequency_cutoff=float(form.get("frequency_cutoff")),
        show_all_cases_status=form.getlist("show_all_cases_status"),
        display_name=form.get("display_name"),
        phenotype_groups=phenotype_groups,
        gene_panels=get_gene_panels(store, form, "gene_panels"),
        gene_panels_matching=get_gene_panels(store, form, "gene_panels_matching"),
        group_abbreviations=group_abbreviations,
        add_groups=False,
        sharing_institutes=sharing_institutes,
        cohorts=cohorts,
        loqusdb_ids=get_loqusdb_ids(form),
        alamut_key=form.get("alamut_key"),
        alamut_institution=form.get("alamut_institution"),
        check_show_all_vars=form.get("check_show_all_vars"),
        clinvar_key=form.get("clinvar_key"),
        clinvar_submitters=get_clinvar_submitters(form),
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
            [
                request.args.get("search_type"),
                request.args["search_term"].strip(),
            ]
        )
    data["name_query"] = name_query
    limit = int(request.args.get("search_limit")) if request.args.get("search_limit") else 100
    data["form"] = populate_case_filter_form(request.args)

    ALL_CASES_PROJECTION = {
        "analysis_date": 1,
        "assignees": 1,
        "beacon": 1,
        "case_id": 1,
        "display_name": 1,
        "individuals": 1,
        "is_rerun": 1,
        "is_research": 1,
        "mme_submission": 1,
        "owner": 1,
        "panels": 1,
        "status": 1,
        "track": 1,
        "vcf_files": 1,
    }

    data["status_ncases"] = store.nr_cases_by_status(institute_id=institute_id)
    data["nr_cases"] = sum(data["status_ncases"].values())
    data["sanger_unevaluated"] = get_sanger_unevaluated(store, institute_id, current_user.email)

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

    case_groups = {status: [] for status in CASE_STATUSES}

    nr_cases_showall_statuses = (
        0  # Nr of cases for the case statuses where all cases should be shown
    )
    # In institute settings, retrieve all case status categories for which all cases should be displayed
    status_show_all_cases: List[str] = institute_obj.get("show_all_cases_status") or ["prioritized"]
    for status in status_show_all_cases:
        cases_in_status = store.cases_by_status(
            institute_id=institute_id, status=status, projection=ALL_CASES_PROJECTION
        )
        cases_in_status = _sort_cases(data, request, cases_in_status)
        for case_obj in cases_in_status:
            populate_case_obj(case_obj)
            nr_cases_showall_statuses += 1
            case_groups[status].append(case_obj)

    # Retrieve cases for the remaining status categories
    all_cases = store.cases(
        collaborator=institute_id,
        name_query=name_query,
        skip_assigned=request.args.get("skip_assigned"),
        is_research=request.args.get("is_research"),
        has_rna_data=request.args.get("has_rna"),
        verification_pending=request.args.get("validation_ordered"),
        has_clinvar_submission=request.args.get("clinvar_submitted"),
        projection=ALL_CASES_PROJECTION,
    )
    all_cases = _sort_cases(data, request, all_cases)

    nr_cases = 0
    for case_obj in all_cases:
        case_status = case_obj["status"]
        if case_status in status_show_all_cases:
            continue
        if nr_cases == limit:
            break
        populate_case_obj(case_obj)
        case_groups[case_status].append(case_obj)
        nr_cases += 1

    data["cases"] = [(status, case_groups[status]) for status in CASE_STATUSES]
    data["found_cases"] = nr_cases + nr_cases_showall_statuses
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
        CASE_SANGER_UNEVALUATED_PROJECTION = {"display_name": 1}
        case_obj = store.case(case_id=case_id, projection=CASE_SANGER_UNEVALUATED_PROJECTION)

        if not case_obj:  # the case might have been removed
            continue

        case_display_name = case_obj.get("display_name")

        # List of variant document ids
        varid_list = item["vars"]

        unevaluated_by_case = {case_display_name: []}
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


def export_gene_variants(
    store: MongoAdapter, gene_symbol: str, pymongo_cursor: Cursor, variant_count: int
) -> Response:
    """Export 500 gene variants for an institute resulting from a customer query"""

    def generate(header, lines):
        yield header + "\n"
        for line in lines:
            yield line + "\n"

    data: dict = gene_variants(
        store=store,
        pymongo_cursor=pymongo_cursor,
        variant_count=variant_count,
        per_page=500,
    )

    DOCUMENT_HEADER = [
        "Case Display Name",
        "Institute",
        "Position",
        "Score",
        "Genes",
        "GnomAD Frequency",
        "CADD Score",
        "Region",
        "Function",
        "HGVS",
    ]

    export_lines = []
    for variant in data.get("variants", []):
        variant_line = []
        variant_line.append(variant.get("case_display_name"))  # Case Display Name
        variant_line.append(variant.get("institute"))  # Institute
        variant_line.append(variant.get("display_name"))  # Position
        variant_line.append(str(variant.get("rank_score", "")))  # Score
        variant_genes = [
            gene.get("hgnc_symbol", gene.get("hgnc_id")) for gene in variant.get("genes", [])
        ]
        variant_line.append(" | ".join(variant_genes))  # Genes

        gnomad_freq = []
        if "gnomad_mt_homoplasmic_frequency" in variant:
            gnomad_freq.append(
                f"gnomAD(MT) hom:{str(round(variant.get('gnomad_mt_homoplasmic_frequency'),4))}"
            )
        if "gnomad_mt_heteroplasmic_frequency" in variant:
            gnomad_freq.append(
                f"gnomAD(MT) het:{str(round(variant.get('gnomad_mt_heteroplasmic_frequency'),4))}"
            )
        if "gnomad_frequency" in variant:
            gnomad_freq.append(f"gnomAD:{str(round(variant.get('gnomad_frequency'),4))}")
        if "max_gnomad_frequency" in variant:
            gnomad_freq.append(f"gnomAD (max):{str(round(variant.get('max_gnomad_frequency'),4))}")
        variant_line.append(" | ".join(gnomad_freq) if gnomad_freq else "-")  # GnomAD Frequency

        variant_line.append(
            str(round(variant.get("cadd_score"), 1)) if variant.get("cadd_score") else "-"
        )  # CADD score
        variant_line.append(" | ".join(variant.get("region_annotations", [])))  # Region
        variant_line.append(" | ".join(variant.get("functional_annotations", [])))  # Function
        variant_line.append(variant.get("hgvs", "-"))  # HGVS

        export_lines.append(",".join(variant_line))

    headers = Headers()
    today = datetime.datetime.now().strftime(DATE_DAY_FORMATTER)
    headers.add(
        "Content-Disposition",
        "attachment",
        filename=f"{gene_symbol}_gene_variants_{today}.csv",
    )
    # return a csv with the exported variants
    return Response(
        generate(",".join(DOCUMENT_HEADER), export_lines),
        mimetype="text/csv",
        headers=headers,
    )


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
    gene_symbols = []
    canonical_transcripts = []
    functional_annotations = []
    region_annotations = []

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

        gene_symbols.append(gene_obj["hgnc_symbol"])

        # ensure annotations are populated
        functional_annotations.append(gene_obj.get("functional_annotation"))
        region_annotations.append(gene_obj.get("region_annotation"))

        # gather HGVS info from gene transcripts
        (canonical_transcript, hgvs_nucleotide, hgvs_protein) = get_hgvs(gene_obj)

        canonical_transcripts.append(canonical_transcript)
        hgvs_c.append(hgvs_nucleotide)
        hgvs_p.append(hgvs_protein)

    variant_obj["hgvs"] = hgvs_str(gene_symbols, canonical_transcripts, hgvs_p, hgvs_c)
    variant_obj["region_annotations"] = get_annotations(gene_symbols, region_annotations)
    variant_obj["functional_annotations"] = get_annotations(gene_symbols, functional_annotations)


def get_genome_build(variant_case_obj):
    """Find genom build in `variant_case_obj`. If not found use build #37"""
    build = str(variant_case_obj.get("genome_build"))
    if build in ["37", "38"]:
        return build
    return "37"


def get_hgvs(gene_obj: Dict) -> Tuple[str, str, str]:
    """Analyse gene object for hgvs info
    Return:
       (canonical_transcript, hgvs_nucleotide, hgvs_protein)"""
    canonical_transcript = ""
    hgvs_nucleotide = "-"
    hgvs_protein = ""

    transcripts_list = gene_obj.get("transcripts")
    for transcript_obj in transcripts_list:
        if transcript_obj.get("is_canonical") is True:
            canonical_transcript = transcript_obj.get("transcript_id")
            hgvs_nucleotide = str(transcript_obj.get("coding_sequence_name"))
            hgvs_protein = str(transcript_obj.get("protein_sequence_name"))
            break
    return (canonical_transcript, hgvs_nucleotide, hgvs_protein)


def get_annotations(gene_symbols: List, gene_annotations: List) -> List:
    """Get annotations for variant from the db transcript level from each gene
    and make a final string. Only add gene symbols if there is more than one gene for the variant.
    """
    if len(gene_annotations) == 1:
        return gene_annotations

    variant_annotations = set()
    for gene_symbol, gene_annotation in zip(gene_symbols, gene_annotations):
        variant_annotations.add(gene_symbol + ":" + gene_annotation)
    return sorted(list(variant_annotations))


def hgvs_str(gene_symbols, canonical_transcripts, hgvs_ps, hgvs_cs):
    """Produce HGVS string from canonical transcripts, gene symbols, dna and protein changes."""
    hgvs = "-"
    for transcript, gene, hgvs_c, hgvs_p in zip(
        canonical_transcripts, gene_symbols, hgvs_cs, hgvs_ps
    ):
        hgvs = f"{transcript} ({gene})"

        if hgvs_c != "None":
            hgvs += " " + hgvs_c
        if hgvs_p != "None":
            hgvs += " " + hgvs_p

    return hgvs


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
