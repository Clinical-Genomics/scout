from flask import Blueprint, request
from flask_login import current_user
from markupsafe import Markup

from scout.server.blueprints.variants.controllers import (
    activate_case,
    get_variants_page,
    populate_chrom_choices,
    populate_filters_form,
)
from scout.server.extensions import store
from scout.server.utils import institute_and_case, templated

from . import controllers

omics_variants_bp = Blueprint(
    "omics_variants",
    __name__,
    template_folder="templates",
)


@omics_variants_bp.route(
    "/<institute_id>/<case_name>/omics_variants/outliers", methods=["GET", "POST"]
)
@templated("omics_variants/outliers.html")
def outliers(institute_id, case_name):
    """Display a list of outlier omics variants."""

    page = get_variants_page(request.form)
    category = "outlier"
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_type = Markup.escape(
        request.args.get("variant_type", request.form.get("variant_type", "clinical"))
    )
    if variant_type not in ["clinical", "research"]:
        variant_type = "clinical"
    variants_stats = store.case_variants_count(case_obj["_id"], institute_id, variant_type, False)

    if request.form.get("hpo_clinical_filter"):
        case_obj["hpo_clinical_filter"] = True

    # update status of case if visited for the first time
    activate_case(store, institute_obj, case_obj, current_user)
    form = populate_filters_form(store, institute_obj, case_obj, category, request)

    # populate filters dropdown
    available_filters = list(store.filters(institute_obj["_id"], category))
    form.filters.choices = [
        (filter.get("_id"), filter.get("display_name")) for filter in available_filters
    ]

    # Populate chromosome select choices
    populate_chrom_choices(form, case_obj)

    genome_build = "38" if "38" in str(case_obj.get("genome_build", "37")) else "37"
    cytobands = store.cytoband_by_chrom(genome_build)

    #    controllers.update_form_hgnc_symbols(store, case_obj, form)

    variants_query = store.variants(
        case_obj["_id"], category=category, query=form.data, build=genome_build
    )

    result_size = store.count_variants(case_obj["_id"], form.data, None, category)

    data = controllers.outliers(store, institute_obj, case_obj, variants_query, result_size, page)

    return dict(
        case=case_obj,
        cytobands=cytobands,
        expand_search=controllers.get_expand_search(request.form),
        filters=available_filters,
        form=form,
        institute=institute_obj,
        page=page,
        result_size=result_size,
        total_variants=variants_stats.get(variant_type, {}).get(category, "NA"),
        variant_type=variant_type,
        **data,
    )
