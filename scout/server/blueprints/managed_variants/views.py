import datetime
import logging

from flask import Blueprint, flash, redirect, request, url_for
from flask_login import current_user

from scout.server.extensions import store
from scout.server.utils import templated, user_institutes

from . import controllers
from .forms import ManagedVariantModifyForm

LOG = logging.getLogger(__name__)

managed_variants_bp = Blueprint("managed_variants", __name__, template_folder="templates")


@managed_variants_bp.route("/managed_variant", methods=["GET", "POST"])
@templated("managed_variants/managed_variants.html")
def managed_variants():
    """Create and return content for the managed variants page"""
    data = controllers.managed_variants(request)
    return data


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
    """Add a managed variant using form data filled in by user"""
    controllers.add_managed_variant(request)
    return redirect(request.referrer)
