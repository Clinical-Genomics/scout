import logging
import datetime

from flask import Blueprint, request, redirect, url_for, flash
from flask_login import current_user

from scout.server.extensions import store
from scout.server.utils import templated, user_institutes
from .forms import ManagedVariantsFilterForm, ManagedVariantAddForm, ManagedVariantModifyForm
from . import controllers

LOG = logging.getLogger(__name__)

managed_variants_bp = Blueprint("managed_variants", __name__, template_folder="templates")


@managed_variants_bp.route("/managed_variant", methods=["GET", "POST"])
@templated("managed_variants/managed_variants.html")
def managed_variants():
    page = int(request.form.get("page", 1))

    institutes = list(user_institutes(store, current_user))

    filters_form = ManagedVariantsFilterForm(request.form)
    add_form = ManagedVariantAddForm()
    modify_form = ManagedVariantModifyForm()

    category = request.form.get("category", "snv")

    query_options = {}
    for option in ["chromosome", "sub_category", "position", "end", "description"]:
        if request.form.get(option, None):
            query_options[option] = request.form.get(option)

    managed_variants_query = store.managed_variants(category=category, query_options=query_options)
    variant_count = store.count_managed_variants(category=category, query_options=query_options)
    data = controllers.managed_variants(store, managed_variants_query, variant_count, page)

    return dict(
        filters_form=filters_form,
        add_form=add_form,
        modify_form=modify_form,
        page=page,
        **data,
    )


@managed_variants_bp.route("/upload_csv", methods=["POST"])
def upload_managed_variants():
    institutes = list(user_institutes(store, current_user))

    csv_file = request.files["csv_file"]
    content = csv_file.stream.read()
    lines = None
    try:
        if b"\n" in content:
            lines = content.decode("utf-8-sig", "ignore").split("\n")
        else:
            lines = content.decode("windows-1252").split("\r")
    except Exception as err:
        flash(
            "Something went wrong while parsing the panel CSV file! ({})".format(err),
            "danger",
        )
        return redirect(request.referrer)

    LOG.debug("Loading lines %s", lines)
    result = controllers.upload_managed_variants(store, lines, institutes, current_user._id)
    flash(
        "In total {} new variants out of {} in file added".format(result[0], result[1]), "success"
    )

    return redirect(request.referrer)


@managed_variants_bp.route("/managed_variant/<variant_id>/modify", methods=["POST"])
def modify_managed_variant(variant_id):

    edit_form = ManagedVariantModifyForm(request.form)

    if not controllers.modify_managed_variant(store, variant_id, edit_form):
        flash("Could not modify variant - does the new variant perhaps already exist?", "warning")

    return redirect(request.referrer)


@managed_variants_bp.route("/managed_variant/<variant_id>/remove", methods=["POST"])
def remove_managed_variant(variant_id):
    controllers.remove_managed_variant(store, variant_id)

    return redirect(request.referrer)


@managed_variants_bp.route("/managed_variant/add", methods=["POST"])
def add_managed_variant():

    add_form = ManagedVariantAddForm(request.form)
    LOG.debug("Adding managed variant with form %s", add_form)

    institutes = list(user_institutes(store, current_user))
    current_user_id = current_user._id

    controllers.add_managed_variant(store, add_form, institutes, current_user_id)

    return redirect(request.referrer)
