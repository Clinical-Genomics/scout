import logging

from flask import flash, redirect, request, url_for
from flask_login import current_user

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
    data = {"dashboard_form": dashboard_form(request.form)}
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

    slice_query = compose_slice_query(
        request.form.get("search_type"), request.form.get("search_term")
    )
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

    # Data from "Variant statistics tab" is not filtered by slice_query and numbers will
    # reflect verified variants in all available cases for an institute
    general_info = get_general_case_info(adapter, institute_id=institute_id)
    total_cases = general_info["total_cases"]
    sliced_case_ids = general_sliced_info["case_ids"]
    verified_query = {
        "verb": {"$in": ["validate", "sanger"]},
    }
    if institute_id:  # filter by institute if users wishes so
        verified_query["institute"] = institute_id

    # Case level information
    sliced_validation_cases = set()
    sliced_validated_cases = set()

    # Variant level information
    validated_tp = set()
    validated_fp = set()
    var_valid_orders = (
        0  # use this counter to count 'True Positive', 'False positive' and 'Not validated' vars
    )

    validate_events = adapter.event_collection.find(verified_query)
    for validate_event in list(validate_events):
        case_id = validate_event.get("case")
        var_obj = adapter.variant(case_id=case_id, document_id=validate_event["variant_id"])
        if var_obj:  # Don't take into account variants which have been removed from db
            var_valid_orders += 1
            if case_id in sliced_case_ids:
                sliced_validation_cases.add(
                    case_id
                )  # add to the set. Can't add same id twice since it'a a set

            validation = var_obj.get("validation")
            if validation and validation in ["True positive", "False positive"]:
                if case_id in sliced_case_ids:
                    sliced_validated_cases.add(case_id)
                if validation == "True positive":
                    validated_tp.add(var_obj["_id"])
                elif validation == "False positive":
                    validated_fp.add(var_obj["_id"])

    n_validation_cases = len(sliced_validation_cases)
    n_validated_cases = len(sliced_validated_cases)

    # append
    overview.append(
        {
            "title": "Validation ordered",
            "count": n_validation_cases,
            "percent": n_validation_cases / total_sliced_cases,
        }
    )
    overview.append(
        {
            "title": "Validated cases (TP + FP)",
            "count": n_validated_cases,
            "percent": n_validated_cases / total_sliced_cases,
        }
    )

    data["overview"] = overview

    variants = []
    nr_validated = len(validated_tp) + len(validated_fp)
    variants.append({"title": "Validation ordered", "count": var_valid_orders, "percent": 1})

    # taking into account that var_valid_orders might be 0:
    percent_validated_tp = 0
    percent_validated_fp = 0

    if var_valid_orders:
        percent_validated_tp = len(validated_tp) / var_valid_orders
        percent_validated_fp = len(validated_fp) / var_valid_orders

    variants.append(
        {
            "title": "Validated True Positive",
            "count": len(validated_tp),
            "percent": percent_validated_tp,
        }
    )

    variants.append(
        {
            "title": "Validated False Positive",
            "count": len(validated_fp),
            "percent": percent_validated_fp,
        }
    )

    data["variants"] = variants
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

    cases = adapter.cases(owner=institute_id, name_query=name_query)

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
