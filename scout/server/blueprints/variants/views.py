"""Views for the variants"""
import datetime
import io
import logging
import os.path
import pathlib
import shutil
import zipfile

import pymongo
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    request,
    send_file,
    url_for,
)
from flask_login import current_user

from scout.constants import (
    CANCER_TIER_OPTIONS,
    MANUAL_RANK_OPTIONS,
    SEVERE_SO_TERMS,
    DISMISS_VARIANT_OPTIONS,
    CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
)
from scout.server.extensions import store
from scout.server.utils import institute_and_case, templated

from . import controllers
from .forms import CancerFiltersForm, FiltersForm, StrFiltersForm, SvFiltersForm

LOG = logging.getLogger(__name__)

variants_bp = Blueprint(
    "variants",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/variants/static",
)


@variants_bp.route("/<institute_id>/<case_name>/variants", methods=["GET", "POST"])
@templated("variants/variants.html")
def variants(institute_id, case_name):
    """Display a list of SNV variants."""
    page = int(request.form.get("page", 1))
    category = "snv"
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_type = request.args.get("variant_type", "clinical")
    variants_stats = store.case_variants_count(case_obj["_id"], institute_id, False)

    if request.form.get("hpo_clinical_filter"):
        case_obj["hpo_clinical_filter"] = True

    user_obj = store.user(current_user.email)
    if request.method == "POST":
        if request.form.getlist("dismiss"):  # dismiss a list of variants
            controllers.dismiss_variant_list(
                store,
                institute_obj,
                case_obj,
                "variant.variant",
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

    # populate filters dropdown
    available_filters = store.filters(institute_id, category)
    form.filters.choices = [
        (filter.get("_id"), filter.get("display_name")) for filter in available_filters
    ]

    # populate available panel choices
    form.gene_panels.choices = controllers.gene_panel_choices(institute_obj, case_obj)

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

    # check if supplied gene symbols exist
    hgnc_symbols = []
    non_clinical_symbols = []
    not_found_symbols = []
    not_found_ids = []
    if (form.hgnc_symbols.data) and len(form.hgnc_symbols.data) > 0:
        is_clinical = form.data.get("variant_type", "clinical") == "clinical"
        clinical_symbols = store.clinical_symbols(case_obj) if is_clinical else None
        for hgnc_symbol in form.hgnc_symbols.data:
            if hgnc_symbol.isdigit():
                hgnc_gene = store.hgnc_gene(int(hgnc_symbol), case_obj["genome_build"])
                if hgnc_gene is None:
                    not_found_ids.append(hgnc_symbol)
                else:
                    hgnc_symbols.append(hgnc_gene["hgnc_symbol"])
            elif sum(1 for i in store.hgnc_genes(hgnc_symbol)) == 0:
                not_found_symbols.append(hgnc_symbol)
            elif is_clinical and (hgnc_symbol not in clinical_symbols):
                non_clinical_symbols.append(hgnc_symbol)
            else:
                hgnc_symbols.append(hgnc_symbol)

    if not_found_ids:
        flash("HGNC id not found: {}".format(", ".join(not_found_ids)), "warning")
    if not_found_symbols:
        flash("HGNC symbol not found: {}".format(", ".join(not_found_symbols)), "warning")
    if non_clinical_symbols:
        flash(
            "Gene not included in clinical list: {}".format(", ".join(non_clinical_symbols)),
            "warning",
        )
    form.hgnc_symbols.data = hgnc_symbols

    # handle HPO gene list separately
    if "hpo" in form.data["gene_panels"]:
        hpo_symbols = list(
            set(term_obj["hgnc_symbol"] for term_obj in case_obj["dynamic_gene_list"])
        )

        current_symbols = set(hgnc_symbols)
        current_symbols.update(hpo_symbols)
        form.hgnc_symbols.data = list(current_symbols)

    cytobands = store.cytoband_by_chrom(case_obj.get("genome_build"))

    variants_query = store.variants(case_obj["_id"], query=form.data, category=category)
    result_size = store.count_variants(case_obj["_id"], form.data, None, category)

    if request.form.get("export"):
        return controllers.download_variants(store, case_obj, variants_query)

    data = controllers.variants(store, institute_obj, case_obj, variants_query, result_size, page)
    expand_search = request.method == "POST" and request.form.get("expand_search") in ["True", ""]
    return dict(
        institute=institute_obj,
        case=case_obj,
        form=form,
        manual_rank_options=MANUAL_RANK_OPTIONS,
        dismiss_variant_options=DISMISS_VARIANT_OPTIONS,
        cancer_tier_options=CANCER_TIER_OPTIONS,
        severe_so_terms=SEVERE_SO_TERMS,
        cytobands=cytobands,
        page=page,
        expand_search=expand_search,
        result_size=result_size,
        total_variants=variants_stats.get(variant_type, {}).get(category, "NA"),
        **data,
    )


@variants_bp.route("/<institute_id>/<case_name>/str/variants", methods=["GET", "POST"])
@templated("variants/str-variants.html")
def str_variants(institute_id, case_name):
    """Display a list of STR variants."""
    page = int(request.form.get("page", 1))
    variant_type = request.args.get("variant_type", "clinical")
    category = "str"

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variants_stats = store.case_variants_count(case_obj["_id"], institute_id, False)

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

    # populate filters dropdown
    available_filters = store.filters(institute_id, category)
    form.filters.choices = [
        (filter.get("_id"), filter.get("display_name")) for filter in available_filters
    ]

    # populate available panel choices
    form.gene_panels.choices = controllers.gene_panel_choices(institute_obj, case_obj)

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

    data = controllers.str_variants(
        store, institute_obj, case_obj, variants_query, result_size, page
    )
    return dict(
        institute=institute_obj,
        case=case_obj,
        dismiss_variant_options=DISMISS_VARIANT_OPTIONS,
        variant_type=variant_type,
        manual_rank_options=MANUAL_RANK_OPTIONS,
        cytobands=cytobands,
        form=form,
        page=page,
        expand_search=str(request.method == "POST"),
        result_size=result_size,
        total_variants=variants_stats.get(variant_type, {}).get(category, "NA"),
        **data,
    )


@variants_bp.route("/<institute_id>/<case_name>/sv/variants", methods=["GET", "POST"])
@templated("variants/sv-variants.html")
def sv_variants(institute_id, case_name):
    """Display a list of structural variants."""

    page = int(request.form.get("page", 1))
    variant_type = request.args.get("variant_type", "clinical")
    category = "sv"
    # Define case and institute objects
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variants_stats = store.case_variants_count(case_obj["_id"], institute_id, False)

    if request.form.get("hpo_clinical_filter"):
        case_obj["hpo_clinical_filter"] = True

    if request.form.getlist("dismiss"):  # dismiss a list of variants
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
    cytobands = store.cytoband_by_chrom(case_obj.get("genome_build"))

    variants_query = store.variants(case_obj["_id"], category=category, query=form.data)

    result_size = store.count_variants(case_obj["_id"], form.data, None, category)

    # if variants should be exported
    if request.form.get("export"):
        return controllers.download_variants(store, case_obj, variants_query)

    data = controllers.sv_variants(
        store, institute_obj, case_obj, variants_query, result_size, page
    )
    expand_search = request.method == "POST" and request.form.get("expand_search") in ["True", ""]
    return dict(
        institute=institute_obj,
        case=case_obj,
        dismiss_variant_options=DISMISS_VARIANT_OPTIONS,
        variant_type=variant_type,
        form=form,
        cytobands=cytobands,
        severe_so_terms=SEVERE_SO_TERMS,
        manual_rank_options=MANUAL_RANK_OPTIONS,
        page=page,
        expand_search=expand_search,
        result_size=result_size,
        total_variants=variants_stats.get(variant_type, {}).get(category, "NA"),
        **data,
    )


@variants_bp.route("/<institute_id>/<case_name>/cancer/variants", methods=["GET", "POST"])
@templated("variants/cancer-variants.html")
def cancer_variants(institute_id, case_name):
    """Show cancer variants overview."""
    category = "cancer"
    variant_type = request.args.get("variant_type", "clinical")
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variants_stats = store.case_variants_count(case_obj["_id"], institute_id, False)

    user_obj = store.user(current_user.email)
    if request.method == "POST":
        if request.form.getlist("dismiss"):  # dismiss a list of variants
            controllers.dismiss_variant_list(
                store,
                institute_obj,
                case_obj,
                "variant.variant",
                request.form.getlist("dismiss"),
                request.form.getlist("dismiss_choices"),
            )

        form = controllers.populate_filters_form(
            store, institute_obj, case_obj, user_obj, category, request.form
        )

        # if user is not loading an existing filter, check filter form
        if request.form.get("load_filter") is None and form.validate_on_submit() is False:
            # Flash a message with errors
            for field, err_list in form.errors.items():
                for err in err_list:
                    flash(f"Content of field '{field}' has not a valid format", "warning")
            # And do not submit the form
            return redirect(
                url_for(
                    ".cancer_variants",
                    institute_id=institute_id,
                    case_name=case_name,
                    expand_search=True,
                )
            )
        page = int(request.form.get("page", 1))

    else:
        page = int(request.args.get("page", 1))
        form = CancerFiltersForm(request.args)
        # set chromosome to all chromosomes
        form.chrom.data = request.args.get("chrom", "")
        if form.gene_panels.data == []:
            form.gene_panels.data = controllers.case_default_panels(case_obj)

    # update status of case if visited for the first time
    controllers.activate_case(store, institute_obj, case_obj, current_user)

    # populate filters dropdown
    available_filters = store.filters(institute_id, category)
    form.filters.choices = [
        (filter.get("_id"), filter.get("display_name")) for filter in available_filters
    ]

    form.gene_panels.choices = controllers.gene_panel_choices(institute_obj, case_obj)

    cytobands = store.cytoband_by_chrom(case_obj.get("genome_build"))

    variants_query = store.variants(case_obj["_id"], category="cancer", query=form.data)
    result_size = store.count_variants(case_obj["_id"], form.data, None, category)

    if request.form.get("export"):
        return controllers.download_variants(store, case_obj, variants_query)

    data = controllers.cancer_variants(
        store, institute_id, case_name, variants_query, result_size, form, page=page
    )
    expand_search = request.method == "POST" and request.form.get("expand_search") in ["True", ""]
    return dict(
        variant_type=variant_type,
        cytobands=cytobands,
        dismiss_variant_options={
            **DISMISS_VARIANT_OPTIONS,
            **CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
        },
        expand_search=expand_search,
        result_size=result_size,
        total_variants=variants_stats.get(variant_type, {}).get(category, "NA"),
        **data,
    )


@variants_bp.route("/<institute_id>/<case_name>/cancer/sv-variants", methods=["GET", "POST"])
@templated("variants/cancer-sv-variants.html")
def cancer_sv_variants(institute_id, case_name):
    """Display a list of cancer structural variants."""

    page = int(request.form.get("page", 1))
    variant_type = request.args.get("variant_type", "clinical")
    category = "cancer_sv"
    # Define case and institute objects
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variants_stats = store.case_variants_count(case_obj["_id"], institute_id, False)

    if request.form.get("hpo_clinical_filter"):
        case_obj["hpo_clinical_filter"] = True

    if request.form.getlist("dismiss"):  # dismiss a list of variants
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
    cytobands = store.cytoband_by_chrom(case_obj.get("genome_build"))
    variants_query = store.variants(case_obj["_id"], category=category, query=form.data)

    result_size = store.count_variants(case_obj["_id"], form.data, None, category)

    # if variants should be exported
    if request.form.get("export"):
        return controllers.download_variants(store, case_obj, variants_query)

    data = controllers.sv_variants(
        store, institute_obj, case_obj, variants_query, result_size, page
    )
    expand_search = request.method == "POST" and request.form.get("expand_search") in ["True", ""]
    return dict(
        institute=institute_obj,
        case=case_obj,
        dismiss_variant_options={
            **DISMISS_VARIANT_OPTIONS,
            **CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
        },
        variant_type=variant_type,
        form=form,
        severe_so_terms=SEVERE_SO_TERMS,
        cancer_tier_options=CANCER_TIER_OPTIONS,
        manual_rank_options=MANUAL_RANK_OPTIONS,
        cytobands=cytobands,
        page=page,
        expand_search=expand_search,
        result_size=result_size,
        total_variants=variants_stats.get(variant_type, {}).get(category, "NA"),
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
            url_for(".sv_variants", institute_id=institute_id, case_name=case_name, **form.data),
            code=307,
        )
    return redirect(
        url_for(".variants", institute_id=institute_id, case_name=case_name, **form.data), code=307
    )


@variants_bp.route("/verified", methods=["GET"])
def download_verified():
    """Download all verified variants for user's cases"""
    user_obj = store.user(current_user.email)
    user_institutes = user_obj.get("institutes")
    temp_excel_dir = os.path.join(variants_bp.static_folder, "verified_folder")
    os.makedirs(temp_excel_dir, exist_ok=True)

    written_files = controllers.verified_excel_file(store, user_institutes, temp_excel_dir)
    if written_files:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        # zip the files on the fly and serve the archive to the user
        data = io.BytesIO()
        with zipfile.ZipFile(data, mode="w") as z:
            for f_name in pathlib.Path(temp_excel_dir).iterdir():
                z.write(f_name, os.path.basename(f_name))
        data.seek(0)

        # remove temp folder with excel files in it
        shutil.rmtree(temp_excel_dir)

        return send_file(
            data,
            mimetype="application/zip",
            as_attachment=True,
            attachment_filename="_".join(["scout", "verified_variants", today]) + ".zip",
            cache_timeout=0,
        )
    flash("No verified variants could be exported for user's institutes", "warning")
    return redirect(request.referrer)
