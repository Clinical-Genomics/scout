import logging

from flask import flash, redirect, request, url_for
from flask_login import current_user

from scout.constants import CASE_SEARCH_TERMS
from scout.server.extensions import store
from scout.server.utils import user_institutes

from .forms import DashboardFilterForm

LOG = logging.getLogger(__name__)


def institute_select_choices():
    """Return a list of tuples with institute _id, institute names to populate a form select.

    Returns:
        institute_choices(list). Example:[(cust000, "Institute 1"), ..]
    """
    institute_choices = [("All", "All institutes")] if current_user.is_admin else []
    # Collect only institutes available to the user
    institute_objs = user_institutes(store, current_user)
    for inst in institute_objs:
        institute_choices.append((inst["_id"], inst["display_name"]))
    return institute_choices


def dashboard_form(request_form=None):
    """Retrieve data to be displayed on dashboard page"""
    form = DashboardFilterForm(request_form)
    form.search_institute.choices = institute_select_choices()
    return form


def compose_slice_query(search_type, search_term):
    """Extract a filter query given a form search term and search type

    Args:
        search_type(str): example -> "case:"
        search_term(str): example -> "17867"

    Returns:
        slice_query(str): example case:17867
    """
    slice_query = None
    if search_term and search_type:
        slice_query = "".join([search_type, search_term])

    return slice_query


def populate_dashboard_data(request):
    """Prepate data display object to be returned to the view

    Args:
        request(flask.rquest): request received by the view

    Returns:
        data(dict): data to be diplayed in the template
    """
    data = {"dashboard_form": dashboard_form(request.form), "search_terms": CASE_SEARCH_TERMS}
    if request.method == "GET":
        return data

    allowed_insititutes = [inst[0] for inst in institute_select_choices()]

    institute_id = request.form.get(
        "search_institute", allowed_insititutes[0]
    )  # GET request has no institute, select the first option of the select

    if institute_id and institute_id not in allowed_insititutes:
        flash("Your user is not allowed to visualize this data", "warning")
        redirect(url_for("dashboard.index"))

    if institute_id == "All":
        institute_id = None

    search_term = request.form["search_term"].strip() if request.form.get("search_term") else ""
    slice_query = compose_slice_query(request.form.get("search_type"), search_term)
    get_dashboard_info(store, data, institute_id, slice_query)
    return data


def get_dashboard_info(adapter, data={}, institute_id=None, slice_query=None):
    """Append case data stats to data display object
    Args:
        adapter(adapter.MongoAdapter)
        data(dict): data dictionary to be passed to template
        institute_id(str): institute id
        slice_query(str): example case:55888

    Returns:
        data(dict): data to be diplayed in the template
    """
    # If a slice_query is present then numbers in "General statistics" and "Case statistics" will
    # reflect the data available for the query
    general_sliced_info = get_general_case_info(
        adapter, institute_id=institute_id, slice_query=slice_query
    )

    total_sliced_cases = general_sliced_info["total_cases"]
    data["total_cases"] = total_sliced_cases

    if total_sliced_cases == 0:
        return data

    data["pedigree"] = []
    for ped_info in general_sliced_info["pedigree"].values():
        ped_info["percent"] = ped_info["count"] / total_sliced_cases
        data["pedigree"].append(ped_info)

    data["cases"] = get_case_groups(
        adapter, total_sliced_cases, institute_id=institute_id, slice_query=slice_query
    )

    data["analysis_types"] = get_analysis_types(
        adapter, total_sliced_cases, institute_id=institute_id, slice_query=slice_query
    )

    overview = [
        {
            "title": "Phenotype terms",
            "count": general_sliced_info["phenotype_cases"],
            "percent": general_sliced_info["phenotype_cases"] / total_sliced_cases,
        },
        {
            "title": "Causative variants",
            "count": general_sliced_info["causative_cases"],
            "percent": general_sliced_info["causative_cases"] / total_sliced_cases,
        },
        {
            "title": "Pinned variants",
            "count": general_sliced_info["pinned_cases"],
            "percent": general_sliced_info["pinned_cases"] / total_sliced_cases,
        },
        {
            "title": "Cohort tag",
            "count": general_sliced_info["cohort_cases"],
            "percent": general_sliced_info["cohort_cases"] / total_sliced_cases,
        },
    ]

    data["overview"] = overview

    return data


def get_general_case_info(adapter, institute_id=None, slice_query=None):
    """Return general information about cases

    Args:
        adapter(adapter.MongoAdapter)
        institute_id(str)
        slice_query(str): Query to filter cases to obtain statistics for.

    Returns:
        general(dict)
    """
    general = {}

    # Potentially sensitive slice queries are assumed allowed if we have got this far
    name_query = slice_query

    CASE_GENERAL_INFO_PROJECTION = {
        "phenotype_terms": 1,
        "causatives": 1,
        "suspects": 1,
        "cohorts": 1,
        "individuals": 1,
    }
    cases = adapter.cases(
        owner=institute_id, name_query=name_query, projection=CASE_GENERAL_INFO_PROJECTION
    )

    phenotype_cases = 0
    causative_cases = 0
    pinned_cases = 0
    cohort_cases = 0

    pedigree = {
        1: {"title": "Single", "count": 0},
        2: {"title": "Duo", "count": 0},
        3: {"title": "Trio", "count": 0},
        "many": {"title": "Many", "count": 0},
    }

    case_ids = set()

    total_cases = 0
    for total_cases, case in enumerate(cases, 1):
        case_ids.add(case["_id"])
        if case.get("phenotype_terms"):
            phenotype_cases += 1
        if case.get("causatives"):
            causative_cases += 1
        if case.get("suspects"):
            pinned_cases += 1
        if case.get("cohorts"):
            cohort_cases += 1

        nr_individuals = len(case.get("individuals", []))
        if nr_individuals == 0:
            continue
        if nr_individuals > 3:
            pedigree["many"]["count"] += 1
        else:
            pedigree[nr_individuals]["count"] += 1

    general["total_cases"] = total_cases
    general["phenotype_cases"] = phenotype_cases
    general["causative_cases"] = causative_cases
    general["pinned_cases"] = pinned_cases
    general["cohort_cases"] = cohort_cases
    general["pedigree"] = pedigree
    general["case_ids"] = case_ids

    return general


def get_case_groups(adapter, total_cases, institute_id=None, slice_query=None):
    """Return the information about case groups

    Args:
        store(adapter.MongoAdapter)
        total_cases(int): Total number of cases
        slice_query(str): Query to filter cases to obtain statistics for.

    Returns:
        cases(dict):
    """
    # Create a group with all cases in the database
    cases = [{"status": "all", "count": total_cases, "percent": 1}]
    # Group the cases based on their status
    pipeline = []
    group = {"$group": {"_id": "$status", "count": {"$sum": 1}}}

    subquery = {}
    if institute_id and slice_query:
        subquery = adapter.cases(owner=institute_id, name_query=slice_query, yield_query=True)
    elif institute_id:
        subquery = adapter.cases(owner=institute_id, yield_query=True)
    elif slice_query:
        subquery = adapter.cases(name_query=slice_query, yield_query=True)

    query = {"$match": subquery} if subquery else {}

    if query:
        pipeline.append(query)

    pipeline.append(group)
    res = adapter.case_collection.aggregate(pipeline)

    for status_group in res:
        cases.append(
            {
                "status": status_group["_id"],
                "count": status_group["count"],
                "percent": status_group["count"] / total_cases,
            }
        )

    return cases


def get_analysis_types(adapter, total_cases, institute_id=None, slice_query=None):
    """Return information about analysis types.
        Group cases based on analysis type for the individuals.
    Args:
        adapter(adapter.MongoAdapter)
        total_cases(int): Total number of cases
        institute_id(str)
        slice_query(str): Query to filter cases to obtain statistics for.
    Returns:
        analysis_types array of hashes with name: analysis_type(str), count: count(int)

    """
    # Group cases based on analysis type of the individuals
    query = {}

    subquery = {}
    if institute_id and slice_query:
        subquery = adapter.cases(owner=institute_id, name_query=slice_query, yield_query=True)
    elif institute_id:
        subquery = adapter.cases(owner=institute_id, yield_query=True)
    elif slice_query:
        subquery = adapter.cases(name_query=slice_query, yield_query=True)

    query = {"$match": subquery}

    pipeline = []
    if query:
        pipeline.append(query)

    pipeline.append({"$unwind": "$individuals"})
    pipeline.append({"$group": {"_id": "$individuals.analysis_type", "count": {"$sum": 1}}})
    analysis_query = adapter.case_collection.aggregate(pipeline)
    analysis_types = [{"name": group["_id"], "count": group["count"]} for group in analysis_query]

    return analysis_types
