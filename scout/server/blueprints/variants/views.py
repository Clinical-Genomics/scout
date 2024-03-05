"""Views for the variants"""
import io
import logging

import pymongo
from flask import Blueprint, flash, redirect, request, session, url_for
from flask_login import current_user
from markupsafe import Markup

from scout.constants import (
    CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
    CANCER_TIER_OPTIONS,
    DISMISS_VARIANT_OPTIONS,
    GENETIC_MODELS_PALETTE,
    MANUAL_RANK_OPTIONS,
    SEVERE_SO_TERMS,
    SEVERE_SO_TERMS_SV,
)
from scout.server.extensions import store
from scout.server.utils import institute_and_case, templated

from . import controllers
from .forms import (
    CancerFiltersForm,
    FiltersForm,
    FusionFiltersForm,
    MeiFiltersForm,
    StrFiltersForm,
    SvFiltersForm,
)

LOG = logging.getLogger(__name__)

VARIANT_PAGE = "variant.variant"

variants_bp = Blueprint(
    "variants",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/variants/static",
)


@variants_bp.route("/<institute_id>/<case_name>/reset_dismissed", methods=["GET"])
def reset_dismissed(institute_id, case_name):
    """Reset all dismissed variants for a case"""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    controllers.reset_all_dimissed(store, institute_obj, case_obj)
    return redirect(request.referrer)


@variants_bp.route("/<institute_id>/<case_name>/variants", methods=["GET", "POST"])
@templated("variants/variants.html")
def variants(institute_id, case_name):
    """Display a list of SNV variants."""
    page = controllers.get_variants_page(request.form)
    category = "snv"
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_type = Markup.escape(
        request.args.get("variant_type", request.form.get("variant_type", "clinical"))
    )
    if variant_type not in ["clinical", "research"]:
        variant_type = "clinical"

    variants_stats = store.case_variants_count(case_obj["_id"], institute_id, variant_type, False)

    if request.form.get("hpo_clinical_filter"):
        case_obj["hpo_clinical_filter"] = True

    user_obj = store.user(current_user.email)
    if request.method == "POST":
        if "dismiss_submit" in request.form:  # dismiss a list of variants
            controllers.dismiss_variant_list(
                store,
                institute_obj,
                case_obj,
                VARIANT_PAGE,
                request.form.getlist("dismiss"),
                request.form.getlist("dismiss_choices"),
            )

        form = controllers.populate_filters_form(
            store, institute_obj, case_obj, user_obj, category, request.form
        )
    else:
        form = FiltersForm(request.args)
        # set form variant data type the first time around
        form.variant_type.data = variant_type
        # set chromosome to all chromosomes
        form.chrom.data = request.args.get("chrom", "")

        if form.gene_panels.data == [] and variant_type == "clinical":
            form.gene_panels.data = controllers.case_default_panels(case_obj)

    controllers.populate_force_show_unaffected_vars(institute_obj, form)

    # populate filters dropdown
    available_filters = list(store.filters(institute_id, category))
    form.filters.choices = [
        (filter.get("_id"), filter.get("display_name")) for filter in available_filters
    ]
    # Populate chromosome select choices
    controllers.populate_chrom_choices(form, case_obj)

    # populate available panel choices
    form.gene_panels.choices = controllers.gene_panel_choices(store, institute_obj, case_obj)

    # update status of case if visited for the first time
    controllers.activate_case(store, institute_obj, case_obj, current_user)

    # upload gene panel if symbol file exists
    if request.files:
        file = request.files[form.symbol_file.name]

    if request.files and file and file.filename != "":
        LOG.debug("Upload file request files: {0}".format(request.files.to_dict()))
        try:
            stream = io.StringIO(file.stream.read().decode("utf-8"), newline=None)
        except UnicodeDecodeError as error:
            flash("Only text files are supported!", "warning")
            return redirect(request.referrer)

        hgnc_symbols_set = set(form.hgnc_symbols.data)
        LOG.debug("Symbols prior to upload: {0}".format(hgnc_symbols_set))
        new_hgnc_symbols = controllers.upload_panel(store, institute_id, case_name, stream)
        hgnc_symbols_set.update(new_hgnc_symbols)
        form.hgnc_symbols.data = hgnc_symbols_set
        # reset gene panels
        form.gene_panels.data = ""

    controllers.update_form_hgnc_symbols(store, case_obj, form)

    cytobands = store.cytoband_by_chrom(case_obj.get("genome_build"))

    variants_query = store.variants(case_obj["_id"], query=form.data, category=category)
    result_size = store.count_variants(case_obj["_id"], form.data, None, category)

    if request.form.get("export"):
        return controllers.download_variants(store, case_obj, variants_query)

    data = controllers.variants(
        store,
        institute_obj,
        case_obj,
        variants_query,
        result_size,
        page,
        query_form=form.data,
    )

    return dict(
        cancer_tier_options=CANCER_TIER_OPTIONS,
        case=case_obj,
        cytobands=cytobands,
        dismiss_variant_options=DISMISS_VARIANT_OPTIONS,
        expand_search=controllers.get_expand_search(request.form),
        filters=available_filters,
        form=form,
        genetic_models_palette=GENETIC_MODELS_PALETTE,
        institute=institute_obj,
        manual_rank_options=MANUAL_RANK_OPTIONS,
        page=page,
        severe_so_terms=SEVERE_SO_TERMS,
        show_dismiss_block=controllers.get_show_dismiss_block(),
        result_size=result_size,
        total_variants=variants_stats.get(variant_type, {}).get(category, "NA"),
        **data,
    )


@variants_bp.route("/<institute_id>/<case_name>/str/variants", methods=["GET", "POST"])
@templated("variants/str-variants.html")
def str_variants(institute_id, case_name):
    """Display a list of STR variants."""
    page = controllers.get_variants_page(request.form)
    category = "str"
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)

    variant_type = Markup.escape(request.args.get("variant_type", "clinical"))
    if variant_type not in ["clinical", "research"]:
        variant_type = "clinical"

    variants_stats = store.case_variants_count(case_obj["_id"], institute_id, variant_type, False)

    user_obj = store.user(current_user.email)

    if request.method == "POST":
        form = controllers.populate_filters_form(
            store, institute_obj, case_obj, user_obj, category, request.form
        )
    else:
        form = StrFiltersForm(request.args)

        if form.gene_panels.data == [] and variant_type == "clinical":
            form.gene_panels.data = controllers.case_default_panels(case_obj)

        # set form variant data type the first time around
        form.variant_type.data = variant_type
        # set chromosome to all chromosomes
        form.chrom.data = request.args.get("chrom", "")

    controllers.populate_force_show_unaffected_vars(institute_obj, form)
    controllers.update_form_hgnc_symbols(store, case_obj, form)

    # populate filters dropdown
    available_filters = list(store.filters(institute_id, category))
    form.filters.choices = [
        (filter.get("_id"), filter.get("display_name")) for filter in available_filters
    ]

    # Populate chromosome select choices
    controllers.populate_chrom_choices(form, case_obj)

    # populate available panel choices
    form.gene_panels.choices = controllers.gene_panel_choices(store, institute_obj, case_obj)

    controllers.activate_case(store, institute_obj, case_obj, current_user)

    cytobands = store.cytoband_by_chrom(case_obj.get("genome_build"))

    query = form.data
    query["variant_type"] = variant_type

    variants_query = store.variants(case_obj["_id"], category=category, query=query).sort(
        [
            ("str_repid", pymongo.ASCENDING),
            ("chromosome", pymongo.ASCENDING),
            ("position", pymongo.ASCENDING),
        ]
    )

    result_size = store.count_variants(case_obj["_id"], query, None, category)

    if request.form.get("export"):
        return controllers.download_str_variants(case_obj, variants_query)

    data = controllers.str_variants(
        store, institute_obj, case_obj, variants_query, result_size, page
    )

    return dict(
        case=case_obj,
        cytobands=cytobands,
        dismiss_variant_options=DISMISS_VARIANT_OPTIONS,
        expand_search=controllers.get_expand_search(request.form),
        filters=available_filters,
        form=form,
        institute=institute_obj,
        manual_rank_options=MANUAL_RANK_OPTIONS,
        page=page,
        result_size=result_size,
        show_dismiss_block=controllers.get_show_dismiss_block(),
        total_variants=variants_stats.get(variant_type, {}).get(category, "NA"),
        variant_type=variant_type,
        **data,
    )


@variants_bp.route("/<institute_id>/<case_name>/sv/variants", methods=["GET", "POST"])
@templated("variants/sv-variants.html")
def sv_variants(institute_id, case_name):
    """Display a list of structural variants."""
    page = controllers.get_variants_page(request.form)
    category = "sv"
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_type = Markup.escape(
        request.args.get("variant_type", request.form.get("variant_type", "clinical"))
    )
    if variant_type not in ["clinical", "research"]:
        variant_type = "clinical"
    variants_stats = store.case_variants_count(case_obj["_id"], institute_id, variant_type, False)

    if request.form.get("hpo_clinical_filter"):
        case_obj["hpo_clinical_filter"] = True

    if "dismiss_submit" in request.form:  # dismiss a list of variants
        controllers.dismiss_variant_list(
            store,
            institute_obj,
            case_obj,
            "variant.sv_variant",
            request.form.getlist("dismiss"),
            request.form.getlist("dismiss_choices"),
        )

    # update status of case if visited for the first time
    controllers.activate_case(store, institute_obj, case_obj, current_user)
    form = controllers.populate_sv_filters_form(store, institute_obj, case_obj, category, request)

    # populate filters dropdown
    available_filters = list(store.filters(institute_obj["_id"], category))
    form.filters.choices = [
        (filter.get("_id"), filter.get("display_name")) for filter in available_filters
    ]

    # Populate chromosome select choices
    controllers.populate_chrom_choices(form, case_obj)

    genome_build = "38" if "38" in str(case_obj.get("genome_build")) else "37"
    cytobands = store.cytoband_by_chrom(genome_build)

    controllers.update_form_hgnc_symbols(store, case_obj, form)

    variants_query = store.variants(case_obj["_id"], category=category, query=form.data)

    result_size = store.count_variants(case_obj["_id"], form.data, None, category)

    # if variants should be exported
    if request.form.get("export"):
        return controllers.download_variants(store, case_obj, variants_query)

    data = controllers.sv_variants(
        store, institute_obj, case_obj, variants_query, result_size, page
    )

    return dict(
        case=case_obj,
        cytobands=cytobands,
        dismiss_variant_options=DISMISS_VARIANT_OPTIONS,
        expand_search=controllers.get_expand_search(request.form),
        filters=available_filters,
        form=form,
        institute=institute_obj,
        manual_rank_options=MANUAL_RANK_OPTIONS,
        page=page,
        result_size=result_size,
        severe_so_terms=SEVERE_SO_TERMS_SV,
        show_dismiss_block=controllers.get_show_dismiss_block(),
        total_variants=variants_stats.get(variant_type, {}).get(category, "NA"),
        variant_type=variant_type,
        **data,
    )


@variants_bp.route("/<institute_id>/<case_name>/mei/variants", methods=["GET", "POST"])
@templated("variants/mei-variants.html")
def mei_variants(institute_id, case_name):
    """Display a list of mobile element insertion (MEI) variants."""
    page = controllers.get_variants_page(request.form)
    category = "mei"
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_type = Markup.escape(
        request.args.get("variant_type", request.form.get("variant_type", "clinical"))
    )
    variants_stats = store.case_variants_count(case_obj["_id"], institute_id, variant_type, False)

    if request.form.get("hpo_clinical_filter"):
        case_obj["hpo_clinical_filter"] = True

    if "dismiss_submit" in request.form:  # dismiss a list of variants
        controllers.dismiss_variant_list(
            store,
            institute_obj,
            case_obj,
            "variant.sv_variant",
            request.form.getlist("dismiss"),
            request.form.getlist("dismiss_choices"),
        )

    # update status of case if visited for the first time
    controllers.activate_case(store, institute_obj, case_obj, current_user)

    user_obj = store.user(current_user.email)
    if request.method == "POST":
        form = controllers.populate_filters_form(
            store, institute_obj, case_obj, user_obj, category, request.form
        )
    else:
        form = MeiFiltersForm(request.args)

        if form.gene_panels.data == [] and variant_type == "clinical":
            form.gene_panels.data = controllers.case_default_panels(case_obj)

        # set form variant data type the first time around
        form.variant_type.data = variant_type
        # set chromosome to all chromosomes
        form.chrom.data = request.args.get("chrom", "")

    # populate filters dropdown
    available_filters = list(store.filters(institute_obj["_id"], category))
    form.filters.choices = [
        (filter.get("_id"), filter.get("display_name")) for filter in available_filters
    ]

    # Populate chromosome select choices
    controllers.populate_chrom_choices(form, case_obj)

    # populate available panel choices
    form.gene_panels.choices = controllers.gene_panel_choices(store, institute_obj, case_obj)

    genome_build = "38" if "38" in str(case_obj.get("genome_build")) else "37"
    cytobands = store.cytoband_by_chrom(genome_build)

    controllers.update_form_hgnc_symbols(store, case_obj, form)

    variants_query = store.variants(case_obj["_id"], category=category, query=form.data)

    result_size = store.count_variants(case_obj["_id"], form.data, None, category)

    # if variants should be exported
    if request.form.get("export"):
        return controllers.download_variants(store, case_obj, variants_query)

    data = controllers.mei_variants(
        store, institute_obj, case_obj, variants_query, result_size, page
    )

    return dict(
        case=case_obj,
        cytobands=cytobands,
        dismiss_variant_options=DISMISS_VARIANT_OPTIONS,
        expand_search=controllers.get_expand_search(request.form),
        filters=available_filters,
        form=form,
        institute=institute_obj,
        manual_rank_options=MANUAL_RANK_OPTIONS,
        page=page,
        result_size=result_size,
        severe_so_terms=SEVERE_SO_TERMS_SV,
        show_dismiss_block=controllers.get_show_dismiss_block(),
        total_variants=variants_stats.get(variant_type, {}).get(category, "NA"),
        variant_type=variant_type,
        **data,
    )


@variants_bp.route("/<institute_id>/<case_name>/cancer/variants", methods=["GET", "POST"])
@templated("variants/cancer-variants.html")
def cancer_variants(institute_id, case_name):
    """Show cancer variants overview."""

    page = controllers.get_variants_page(request.form)

    category = "cancer"
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_type = Markup.escape(
        request.args.get("variant_type", request.form.get("variant_type", "clinical"))
    )
    if variant_type not in ["clinical", "research"]:
        variant_type = "clinical"
    variants_stats = store.case_variants_count(case_obj["_id"], institute_id, variant_type, False)

    user_obj = store.user(current_user.email)
    if request.method == "POST":
        if "dismiss_submit" in request.form:  # dismiss a list of variants
            controllers.dismiss_variant_list(
                store,
                institute_obj,
                case_obj,
                VARIANT_PAGE,
                request.form.getlist("dismiss"),
                request.form.getlist("dismiss_choices"),
            )

        form = controllers.populate_filters_form(
            store, institute_obj, case_obj, user_obj, category, request.form
        )

        # if user is not loading an existing filter, check filter form
        if (
            request.form.get("load_filter") is None
            and request.form.get("audit_filter") is None
            and form.validate_on_submit() is False
        ):
            # Flash a message with errors
            for field, err_list in form.errors.items():
                for err in err_list:
                    flash(
                        f"Content of field '{field}' does not have a valid format",
                        "warning",
                    )
            # And do not submit the form
            return redirect(
                url_for(".cancer_variants", institute_id=institute_id, case_name=case_name)
            )
    else:
        form = CancerFiltersForm(request.args)
        # set chromosome to all chromosomes
        form.chrom.data = request.args.get("chrom", "")
        if form.gene_panels.data == []:
            form.gene_panels.data = controllers.case_default_panels(case_obj)

    controllers.populate_force_show_unaffected_vars(institute_obj, form)

    # update status of case if visited for the first time
    controllers.activate_case(store, institute_obj, case_obj, current_user)

    # populate filters dropdown
    available_filters = list(store.filters(institute_id, category))
    form.filters.choices = [
        (filter.get("_id"), filter.get("display_name")) for filter in available_filters
    ]

    # Populate chromosome select choices
    controllers.populate_chrom_choices(form, case_obj)

    form.gene_panels.choices = controllers.gene_panel_choices(store, institute_obj, case_obj)
    genome_build = "38" if "38" in str(case_obj.get("genome_build")) else "37"
    cytobands = store.cytoband_by_chrom(genome_build)

    controllers.update_form_hgnc_symbols(store, case_obj, form)

    variants_query = store.variants(
        case_obj["_id"], category="cancer", query=form.data, build=genome_build
    )
    result_size = store.count_variants(case_obj["_id"], form.data, None, category)

    if request.form.get("export"):
        return controllers.download_variants(store, case_obj, variants_query)

    data = controllers.cancer_variants(
        store,
        institute_id,
        case_name,
        variants_query,
        result_size,
        form,
        page=page,
    )

    return dict(
        cytobands=cytobands,
        dismiss_variant_options={
            **DISMISS_VARIANT_OPTIONS,
            **CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
        },
        expand_search=controllers.get_expand_search(request.form),
        filters=available_filters,
        result_size=result_size,
        show_dismiss_block=controllers.get_show_dismiss_block(),
        total_variants=variants_stats.get(variant_type, {}).get(category, "NA"),
        variant_type=variant_type,
        **data,
    )


@variants_bp.route("/<institute_id>/<case_name>/cancer/sv-variants", methods=["GET", "POST"])
@templated("variants/cancer-sv-variants.html")
def cancer_sv_variants(institute_id, case_name):
    """Display a list of cancer structural variants."""

    page = controllers.get_variants_page(request.form)
    category = "cancer_sv"
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_type = Markup.escape(
        request.args.get("variant_type", request.form.get("variant_type", "clinical"))
    )
    if variant_type not in ["clinical", "research"]:
        variant_type = "clinical"
    variants_stats = store.case_variants_count(case_obj["_id"], institute_id, variant_type, False)

    if request.form.get("hpo_clinical_filter"):
        case_obj["hpo_clinical_filter"] = True

    if "dismiss_submit" in request.form:  # dismiss a list of variants
        controllers.dismiss_variant_list(
            store,
            institute_obj,
            case_obj,
            "variant.sv_variant",
            request.form.getlist("dismiss"),
            request.form.getlist("dismiss_choices"),
        )

    # update status of case if visited for the first time
    controllers.activate_case(store, institute_obj, case_obj, current_user)
    form = controllers.populate_sv_filters_form(store, institute_obj, case_obj, category, request)

    # populate filters dropdown
    available_filters = list(store.filters(institute_obj["_id"], category))
    form.filters.choices = [
        (filter.get("_id"), filter.get("display_name")) for filter in available_filters
    ]

    # Populate chromosome select choices
    controllers.populate_chrom_choices(form, case_obj)

    genome_build = "38" if "38" in str(case_obj.get("genome_build")) else "37"
    cytobands = store.cytoband_by_chrom(genome_build)

    controllers.update_form_hgnc_symbols(store, case_obj, form)

    variants_query = store.variants(case_obj["_id"], category=category, query=form.data)

    result_size = store.count_variants(case_obj["_id"], form.data, None, category)

    # if variants should be exported
    if request.form.get("export"):
        return controllers.download_variants(store, case_obj, variants_query)

    data = controllers.sv_variants(
        store, institute_obj, case_obj, variants_query, result_size, page
    )

    return dict(
        case=case_obj,
        cancer_tier_options=CANCER_TIER_OPTIONS,
        cytobands=cytobands,
        dismiss_variant_options={
            **DISMISS_VARIANT_OPTIONS,
            **CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
        },
        expand_search=controllers.get_expand_search(request.form),
        filters=available_filters,
        form=form,
        institute=institute_obj,
        manual_rank_options=MANUAL_RANK_OPTIONS,
        page=page,
        result_size=result_size,
        severe_so_terms=SEVERE_SO_TERMS,
        show_dismiss_block=controllers.get_show_dismiss_block(),
        total_variants=variants_stats.get(variant_type, {}).get(category, "NA"),
        variant_type=variant_type,
        **data,
    )


@variants_bp.route("/<institute_id>/<case_name>/fusion/variants", methods=["GET", "POST"])
@templated("variants/fusion-variants.html")
def fusion_variants(institute_id, case_name):
    """Display a list of fusion variants."""

    page = controllers.get_variants_page(request.form)
    category = "fusion"
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_type = Markup.escape(
        request.args.get("variant_type", request.form.get("variant_type", "clinical"))
    )
    if variant_type not in ["clinical", "research"]:
        variant_type = "clinical"
    variants_stats = store.case_variants_count(case_obj["_id"], institute_id, variant_type, False)

    if request.form.get("hpo_clinical_filter"):
        case_obj["hpo_clinical_filter"] = True

    if "dismiss_submit" in request.form:  # dismiss a list of variants
        controllers.dismiss_variant_list(
            store,
            institute_obj,
            case_obj,
            VARIANT_PAGE,
            request.form.getlist("dismiss"),
            request.form.getlist("dismiss_choices"),
        )

    # update status of case if visited for the first time
    controllers.activate_case(store, institute_obj, case_obj, current_user)
    form = controllers.populate_fusion_filters_form(
        store, institute_obj, case_obj, category, request
    )

    # populate filters dropdown
    available_filters = list(store.filters(institute_obj["_id"], category))
    form.filters.choices = [
        (filter.get("_id"), filter.get("display_name")) for filter in available_filters
    ]

    # Populate chromosome select choices
    controllers.populate_chrom_choices(form, case_obj)

    genome_build = "38"
    cytobands = store.cytoband_by_chrom(genome_build)

    controllers.update_form_hgnc_symbols(store, case_obj, form)

    variants_query = store.variants(case_obj["_id"], category=category, query=form.data)

    result_size = store.count_variants(case_obj["_id"], form.data, None, category)

    # if variants should be exported
    if request.form.get("export"):
        return controllers.download_variants(store, case_obj, variants_query)

    data = controllers.fusion_variants(
        store, institute_obj, case_obj, variants_query, result_size, page
    )

    return dict(
        case=case_obj,
        cancer_tier_options=CANCER_TIER_OPTIONS,
        cytobands=cytobands,
        dismiss_variant_options={
            **DISMISS_VARIANT_OPTIONS,
        },
        expand_search=controllers.get_expand_search(request.form),
        filters=available_filters,
        form=form,
        institute=institute_obj,
        manual_rank_options=MANUAL_RANK_OPTIONS,
        page=page,
        result_size=result_size,
        severe_so_terms=SEVERE_SO_TERMS,
        show_dismiss_block=controllers.get_show_dismiss_block(),
        total_variants=variants_stats.get(variant_type, {}).get(category, "NA"),
        variant_type=variant_type,
        **data,
    )


@variants_bp.route("/<institute_id>/<case_name>/upload", methods=["POST"])
def upload_panel(institute_id, case_name):
    """Parse gene panel file and fill in HGNC symbols for filter."""
    panel_file = request.form.symbol_file.data

    if panel_file.filename == "":
        flash("No selected file", "warning")
        return redirect(request.referrer)

    try:
        stream = io.StringIO(panel_file.stream.read().decode("utf-8"), newline=None)
    except UnicodeDecodeError as error:
        flash("Only text files are supported!", "warning")
        return redirect(request.referrer)

    category = request.args.get("category")

    if category == "sv":
        form = SvFiltersForm(request.args)
    elif category == "fusion":
        form = FusionFiltersForm(request.args)
    else:
        form = FiltersForm(request.args)

    hgnc_symbols = set(form.hgnc_symbols.data)
    new_hgnc_symbols = controllers.upload_panel(store, institute_id, case_name, stream)
    hgnc_symbols.update(new_hgnc_symbols)
    form.hgnc_symbols.data = ",".join(hgnc_symbols)
    # reset gene panels
    form.gene_panels.data = ""
    # HTTP redirect code 307 asks that the browser preserves the method of request (POST).
    if category == "sv":
        return redirect(
            url_for(
                ".sv_variants",
                institute_id=institute_id,
                case_name=case_name,
                **form.data,
            ),
            code=307,
        )
    return redirect(
        url_for(".variants", institute_id=institute_id, case_name=case_name, **form.data),
        code=307,
    )


@variants_bp.route("/variants/toggle_show_dismiss_block", methods=["GET"])
def toggle_show_dismiss_block():
    """Endpoint to toggle the show dismiss block session variable."""
    session["show_dismiss_block"] = not session.get("show_dismiss_block")
    return f"Toggled to {session['show_dismiss_block']}"
