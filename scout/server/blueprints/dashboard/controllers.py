import logging
from typing import Dict, List, Set

from flask import flash, redirect, request, url_for
from flask_login import current_user
from werkzeug.datastructures.structures import ImmutableMultiDict
from werkzeug.local import LocalProxy

from scout.adapter import MongoAdapter
from scout.constants import CASE_TAGS
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
        institute_choices.append((inst["_id"], f'{inst["display_name"]} ({inst["_id"]})'))
    return institute_choices


def dashboard_form(request_form=None):
    """Retrieve data to be displayed on dashboard page"""
    form = DashboardFilterForm(request_form)
    form.search_institute.choices = institute_select_choices()
    return form


def populate_dashboard_data(request: LocalProxy) -> dict:
    """Collect data to display on the dashboard page"""

    data = {"dashboard_form": dashboard_form(request.form)}
    if request.method == "GET":
        return data

    allowed_institutes = [inst[0] for inst in institute_select_choices()]

    institute_id = request.form.get(
        "search_institute", allowed_institutes[0]
    )  # GET request has no institute, select the first option of the select

    if institute_id and institute_id not in allowed_institutes:
        flash("Your user is not allowed to visualize this data", "warning")
        redirect(url_for("dashboard.index"))

    if institute_id == "All":
        institute_id = None

    get_dashboard_info(adapter=store, data=data, institute_id=institute_id, cases_form=request.form)
    return data


def get_dashboard_info(
    adapter: MongoAdapter, data: dict = None, institute_id: str = None, cases_form=None
) -> dict:
    """Append case data stats to data display object"""

    if not data:
        data = {}

    # Filter data using eventual filter provided in cases filters form
    filtered_cases_info = get_general_case_info(
        adapter=adapter, institute_id=institute_id, cases_form=cases_form
    )

    total_filtered_cases = filtered_cases_info["total_cases"]
    data["total_cases"] = total_filtered_cases

    if total_filtered_cases == 0:
        return data

    data["pedigree"] = []
    for ped_info in filtered_cases_info["pedigree"].values():
        ped_info["percent"] = ped_info["count"] / total_filtered_cases
        data["pedigree"].append(ped_info)

    data["cases"] = get_case_groups(
        adapter=adapter,
        total_cases=total_filtered_cases,
        institute_id=institute_id,
        name_query=cases_form,
    )

    data["analysis_types"] = get_analysis_types(
        adapter=adapter, institute_id=institute_id, name_query=cases_form
    )

    overview = [
        {
            "title": "Phenotype terms",
            "count": filtered_cases_info["phenotype_cases"],
            "percent": filtered_cases_info["phenotype_cases"] / total_filtered_cases,
        },
        {
            "title": "Causative variants",
            "count": filtered_cases_info["causative_cases"],
            "percent": filtered_cases_info["causative_cases"] / total_filtered_cases,
        },
        {
            "title": "Pinned variants",
            "count": filtered_cases_info["pinned_cases"],
            "percent": filtered_cases_info["pinned_cases"] / total_filtered_cases,
        },
        {
            "title": "Cohort tag",
            "count": filtered_cases_info["cohort_cases"],
            "percent": filtered_cases_info["cohort_cases"] / total_filtered_cases,
        },
        {
            "title": "Case status tag",
            "count": filtered_cases_info["tagged_cases"],
            "percent": filtered_cases_info["tagged_cases"] / total_filtered_cases,
        },
    ]

    for stats_tag in CASE_TAGS.keys():
        overview.append(
            {
                "title": CASE_TAGS[stats_tag]["label"] + " status tag",
                "count": filtered_cases_info[stats_tag + "_cases"],
                "percent": filtered_cases_info[stats_tag + "_cases"] / total_filtered_cases,
            }
        )

    data["overview"] = overview

    return data


def get_general_case_info(
    adapter, institute_id: str = None, cases_form: ImmutableMultiDict = None
) -> dict:
    """Return general information about cases."""

    CASE_GENERAL_INFO_PROJECTION = {
        "phenotype_terms": 1,
        "causatives": 1,
        "suspects": 1,
        "cohorts": 1,
        "individuals": 1,
        "tags": 1,
    }

    cases = adapter.cases(
        owner=institute_id, name_query=cases_form, projection=CASE_GENERAL_INFO_PROJECTION
    )

    # Initialize counters and structures
    case_counter_keys = ["phenotype", "causative", "pinned", "cohort", "tagged"] + list(
        CASE_TAGS.keys()
    )
    case_counter = initialize_case_counter(case_counter_keys)
    pedigree = initialize_pedigree()

    case_ids: Set[str] = set()
    total_cases = 0

    # Process each case
    for total_cases, case in enumerate(cases, 1):
        case_ids.add(case["_id"])
        update_case_counters(case, case_counter, case_counter_keys)
        update_pedigree(case, pedigree)

    # Prepare general info dictionary
    general = {
        "total_cases": total_cases,
        "pedigree": pedigree,
        "case_ids": case_ids,
        **{f"{key}_cases": count for key, count in case_counter.items()},
    }

    return general


def initialize_case_counter(case_counter_keys) -> Dict[str, int]:
    """Initialize the case counter dictionary with the given keys set to zero."""
    return {key: 0 for key in case_counter_keys}


def initialize_pedigree() -> Dict:
    """Initialize the pedigree structure with counts set to zero."""
    return {
        1: {"title": "Single", "count": 0},
        2: {"title": "Duo", "count": 0},
        3: {"title": "Trio", "count": 0},
        "many": {"title": "Many", "count": 0},
    }


def update_case_counters(case: dict, case_counter: Dict[str, int], case_counter_keys):
    """Update case counter based on the case's attributes."""
    if case.get("phenotype_terms"):
        case_counter["phenotype"] += 1
    if case.get("causatives"):
        case_counter["causative"] += 1
    if case.get("suspects"):
        case_counter["pinned"] += 1
    if case.get("cohorts"):
        case_counter["cohort"] += 1
    if case.get("tags"):
        case_counter["tagged"] += 1
        for tag in case.get("tags", []):
            if tag in case_counter_keys:  # Ensure tag is in the predefined keys
                case_counter[tag] += 1


def update_pedigree(case: dict, pedigree: Dict):
    """Update pedigree information based on the number of individuals in the case."""
    nr_individuals = len(case.get("individuals", []))
    if nr_individuals == 0:
        return
    if nr_individuals > 3:
        pedigree["many"]["count"] += 1
    else:
        pedigree[nr_individuals]["count"] += 1


def get_case_groups(
    adapter: MongoAdapter,
    total_cases: int,
    institute_id: str = None,
    name_query: ImmutableMultiDict = None,
) -> List[dict]:
    """Return the information about case groups"""
    # Create a group with all cases in the database
    cases = [{"status": "all", "count": total_cases, "percent": 1}]
    # Group the cases based on their status
    pipeline = []
    group = {"$group": {"_id": "$status", "count": {"$sum": 1}}}

    subquery = {}
    if institute_id and name_query:
        subquery = adapter.cases(owner=institute_id, name_query=name_query, yield_query=True)
    elif institute_id:
        subquery = adapter.cases(owner=institute_id, yield_query=True)
    elif name_query:
        subquery = adapter.cases(name_query=name_query, yield_query=True)

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


def get_analysis_types(
    adapter: MongoAdapter, institute_id: str = None, name_query: ImmutableMultiDict = None
) -> List[dict]:
    """Group cases based on analysis type of the individuals."""

    subquery = {}
    if institute_id and name_query:
        subquery = adapter.cases(owner=institute_id, name_query=name_query, yield_query=True)
    elif institute_id:
        subquery = adapter.cases(owner=institute_id, yield_query=True)
    elif name_query:
        subquery = adapter.cases(name_query=name_query, yield_query=True)

    query = {"$match": subquery}

    pipeline = []
    if query:
        pipeline.append(query)

    pipeline.append({"$unwind": "$individuals"})
    pipeline.append({"$group": {"_id": "$individuals.analysis_type", "count": {"$sum": 1}}})
    analysis_query = adapter.case_collection.aggregate(pipeline)
    analysis_types = [{"name": group["_id"], "count": group["count"]} for group in analysis_query]

    return analysis_types
