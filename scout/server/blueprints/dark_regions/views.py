import logging

from flask import Blueprint, request
from flask_login import current_user

from scout.server.blueprints.dark_regions.controllers import sma_case as sma_case_controller
from scout.server.blueprints.variants.controllers import (
    activate_case,
    case_default_panels,
    gene_panel_choices,
)
from scout.server.extensions import store
from scout.server.utils import institute_and_case, templated

from ..cases.forms import SmaPanelFilterForm

LOG = logging.getLogger(__name__)

dark_regions_bp = Blueprint(
    "dark_regions",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/dark_regions/static",
)


@dark_regions_bp.route("/<institute_id>/<case_name>/sma", methods=["GET"])
@templated("dark_regions/sma_dark.html")
def sma(institute_id, case_name):
    """Visualize case SMA and other dark region data."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    sma_filter_form = SmaPanelFilterForm(request.args)
    sma_filter_form.gene_panels.choices = gene_panel_choices(store, institute_obj, case_obj)

    selected_gene_panels = sma_filter_form.gene_panels.data or []
    panel_filter_applied = request.args.get("panel_filter_applied") == "1"
    if (
        request.method == "GET"
        and not panel_filter_applied
        and not request.args.getlist("gene_panels")
    ):
        selected_gene_panels = case_default_panels(case_obj)
        sma_filter_form.gene_panels.data = selected_gene_panels

    data = sma_case_controller(
        store,
        institute_obj,
        case_obj,
        selected_gene_panels=selected_gene_panels,
    )

    activate_case(store, institute_obj, case_obj, current_user)

    return dict(
        format="html", sma_filter_form=sma_filter_form, expand_search=panel_filter_applied, **data
    )
