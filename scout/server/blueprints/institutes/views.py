# -*- coding: utf-8 -*-
import json
import logging

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from pymongo import DESCENDING

from scout.constants import ACMG_COMPLETE_MAP, ACMG_MAP, CALLERS, VERBS_ICONS_MAP, VERBS_MAP
from scout.server.blueprints.variants.controllers import update_form_hgnc_symbols
from scout.server.extensions import beacon, loqusdb, store
from scout.server.utils import institute_and_case, jsonconverter, templated, user_institutes

from . import controllers
from .forms import GeneVariantFiltersForm, InstituteForm

LOG = logging.getLogger(__name__)

blueprint = Blueprint(
    "overview",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/overview/static",
)


@blueprint.route("/overview/timeline", methods=["GET"])
@templated("overview/timeline.html")
def timeline():
    data = {"events": controllers.get_timeline_data(request.args.get("limit") or "50")}
    data["verbs_map"] = VERBS_MAP
    data["verbs_icons"] = VERBS_ICONS_MAP
    return dict(**data)


@blueprint.route("/api/v1/institutes", methods=["GET"])
def api_institutes():
    """API endpoint that returns institutes data"""
    data = dict(institutes=controllers.institutes())
    return jsonify(data)


@blueprint.route("/api/v1/institutes/<institute_id>/cases", methods=["GET", "POST"])
def api_cases(institute_id):
    """API endpoint that returns all cases for a given institute"""
    case_data = controllers.cases(store, request, institute_id)
    json_cases = json.dumps({"cases": case_data}, default=jsonconverter)
    return json_cases


@blueprint.route("/<institute_id>/cases", methods=["GET", "POST"])
@templated("overview/cases.html")
def cases(institute_id):
    """Display a list of cases for an institute."""
    return controllers.cases(store, request, institute_id)


@blueprint.route("/<institute_id>/verified")
@templated("overview/verified.html")
def verified(institute_id):
    institute_obj = institute_and_case(store, institute_id)
    verified_vars = controllers.verified_vars(institute_id)
    verified_stats = controllers.verified_stats(institute_id, verified_vars)
    return dict(
        institute=institute_obj,
        verified=verified_vars,
        verified_stats=verified_stats,
        acmg_map={key: ACMG_COMPLETE_MAP[value] for key, value in ACMG_MAP.items()},
        callers=CALLERS,
    )


@blueprint.route("/<institute_id>/causatives")
@templated("overview/causatives.html")
def causatives(institute_id):
    institute_obj = institute_and_case(store, institute_id)
    return dict(
        institute=institute_obj,
        causatives=controllers.causatives(institute_obj, request),
        acmg_map={key: ACMG_COMPLETE_MAP[value] for key, value in ACMG_MAP.items()},
        callers=CALLERS,
    )


@blueprint.route("/<institute_id>/filters", methods=["GET"])
@templated("overview/filters.html")
def filters(institute_id):
    form = request.form

    institute_obj = institute_and_case(store, institute_id)

    filters = controllers.filters(store, institute_id)

    return dict(institute=institute_obj, form=form, filters=filters)


@blueprint.route("/<institute_id>/lock_filter/<filter_id>", methods=["POST"])
def lock_filter(institute_id, filter_id):
    filter_lock = request.form.get("filter_lock", "False")
    LOG.debug(
        "Attempting to toggle lock %s for %s with status %s",
        filter_id,
        institute_id,
        filter_lock,
    )

    if filter_lock == "True":
        filter_obj = controllers.unlock_filter(store, current_user, filter_id)

    if filter_lock == "False" or not filter_lock:
        filter_obj = controllers.lock_filter(store, current_user, filter_id)

    return redirect(request.referrer)


@blueprint.route("/<institute_id>/gene_variants", methods=["GET", "POST"])
@templated("overview/gene_variants.html")
def gene_variants(institute_id):
    """Display a list of SNV variants."""

    page = int(request.form.get("page", 1))
    result_size = None
    institute_obj = institute_and_case(store, institute_id)

    data = {}

    if request.method == "GET":
        form = GeneVariantFiltersForm(request.args)
    else:  # POST
        form = GeneVariantFiltersForm(request.form)
        if form.variant_type.data == []:
            form.variant_type.data = ["clinical"]

        variant_type = form.data.get("variant_type")

        update_form_hgnc_symbols(store=store, case_obj=None, form=form)

        # If no valid gene is provided, redirect to form
        if not form.hgnc_symbols.data:
            flash("Provided gene symbols could not be used in variants' search", "warning")
            return redirect(request.referrer)

        variants_query = store.build_variant_query(
            query=form.data,
            institute_ids=[inst["_id"] for inst in user_institutes(store, current_user)],
            category="snv",
            variant_type=variant_type,
        )  # This is the actual query dictionary, not the cursor with results

        results = store.variant_collection.find(variants_query).sort(
            [("rank_score", DESCENDING)]
        )  # query results

        result_size = store.variant_collection.count_documents(variants_query)

        if request.form.get("filter_export_variants"):
            return controllers.export_gene_variants(
                store=store,
                gene_symbol=request.form.get("hgnc_symbols").split(",")[0].strip(),
                pymongo_cursor=results,
                variant_count=result_size,
            )

        data = controllers.gene_variants(
            store, results, result_size, page
        )  # decorated variant results, max 50 in a page

    return dict(institute=institute_obj, form=form, page=page, result_size=result_size, **data)


# MOST OF THE CONTENT OF THIS ENDPOINT WILL BE REMOVED AND INCLUDED INTO THE BEACON EXTENSION UNDER SERVER/EXTENSIONS
@blueprint.route("/overview/<institute_id>/add_beacon_dataset", methods=["POST"])
def add_beacon_dataset(institute_id):
    """Add a dataset to Beacon for a given institute"""
    if current_user.is_admin is False:
        flash(
            "Only an admin can create a new Beacon dataset",
            "warning",
        )
        return redirect(request.referrer)

    dataset_id = request.form.get("beacon_dataset")
    institute_obj = store.institute(institute_id)

    beacon.add_dataset(institute_obj, dataset_id)
    return redirect(request.referrer)


@blueprint.route("/overview/<institute_id>/settings", methods=["GET", "POST"])
def institute_settings(institute_id):
    """Show institute settings page"""

    if institute_id not in current_user.institutes and current_user.is_admin is False:
        flash(
            "Current user doesn't have the permission to modify this institute",
            "warning",
        )
        return redirect(request.referrer)

    institute_obj = store.institute(institute_id)
    institute_form = InstituteForm(request.form)

    beacon_form = controllers.populate_beacon_form(institute_obj)

    # if institute is to be updated
    if request.method == "POST" and institute_form.validate_on_submit():
        institute_obj = controllers.update_institute_settings(store, institute_obj, request.form)
        if isinstance(institute_obj, dict):
            flash("institute was updated ", "success")
        else:  # an error message was retuned
            flash(institute_obj, "warning")
            return redirect(request.referrer)

    data = controllers.institute(store, institute_id)
    loqus_instances = loqusdb.loqus_ids if hasattr(loqusdb, "loqus_ids") else []
    default_phenotypes = controllers.populate_institute_form(institute_form, institute_obj)

    return render_template(
        "/overview/institute_settings.html",
        form=institute_form,
        beacon_form=beacon_form,
        default_phenotypes=default_phenotypes,
        loqus_instances=loqus_instances,
        panel=1,
        **data,
    )


@blueprint.route("/overview/<institute_id>/users", methods=["GET"])
def institute_users(institute_id):
    """Should institute users list"""

    if institute_id not in current_user.institutes and current_user.is_admin is False:
        flash(
            "Current user doesn't have the permission to modify this institute",
            "warning",
        )
        return redirect(request.referrer)
    data = controllers.institute(store, institute_id)
    return render_template("/overview/users.html", panel=2, **data)
