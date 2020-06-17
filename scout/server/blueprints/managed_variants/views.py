import logging
import datetime

from flask import abort, Blueprint, request, redirect, url_for, flash, render_template
from flask_weasyprint import HTML, render_pdf
from flask_login import current_user

from scout.server.extensions import store
from scout.server.utils import templated, user_institutes
from .forms import ManagedVariantsFilterForm
from . import controllers

LOG = logging.getLogger(__name__)

managed_variants_bp = Blueprint("managed_variants", __name__, template_folder="templates")


@managed_variants_bp.route("/managed_variant", methods=["GET", "POST"])
@templated("managed_variants/managed_variants.html")
def managed_variants():

    institutes = list(user_institutes(store, current_user))

    category = request.form.get("category", "snv")

    form = ManagedVariantsFilterForm(request.form)

    managed_variants_query = store.managed_variants(category=category)
    data = controllers.managed_variants(store, managed_variants_query)

    LOG.debug("MVS: %s", data["managed_variants"])
    return dict(form=form, **data)
