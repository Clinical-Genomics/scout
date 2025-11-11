import logging

from flask import flash
from flask_login import current_user

from scout.build import build_managed_variant
from scout.constants import CHROMOSOMES, CHROMOSOMES_38
from scout.parse.variant.managed_variant import parse_managed_variant_lines
from scout.server.extensions import store
from scout.server.utils import user_institutes
from scout.utils.vcf import (
    is_symbolic_alt,
    validate_bnd_alt,
    validate_ref_alt,
    validate_snv_alt,
    validate_symbolic_alt,
)

from .forms import (
    CATEGORY_CHOICES,
    SUBCATEGORY_CHOICES,
    ManagedVariantAddForm,
    ManagedVariantModifyForm,
    ManagedVariantsFilterForm,
)

LOG = logging.getLogger(__name__)

VARS_PER_PAGE = 50


def set_query_coordinates(query_options, request_form):
    """Set query coordinates based on submitted form

    Args:
        query_options(dict): managed variants optional params
        request_form(ImmutableMultiDict): form submitted by user to filter managed variants
    """
    chrom = request_form.get("chromosome")
    if chrom is None or chrom == "All":
        return
    query_options["chromosome"] = chrom
    if request_form.get("position"):
        query_options["position"] = int(request_form.get("position"))
    if request_form.get("end"):
        query_options["end"] = int(request_form.get("end"))


def managed_variants(request):
    """Create and return managed variants' data

    Args:
        request(werkzeug.local.LocalProxy): request containing form data

    Returns
        data(dict): data to be displayed in template page
    """

    page = int(request.form.get("page", 1))
    skip_count = VARS_PER_PAGE * max(page - 1, 0)

    # Retrieve form data for the 3 types of form present on the managed variants page
    filters_form = ManagedVariantsFilterForm(request.form)
    add_form = ManagedVariantAddForm()
    modify_form = ManagedVariantModifyForm()

    # Retrieve form data to compose variants query
    categories = request.form.getlist("category") or [cat[0] for cat in CATEGORY_CHOICES]

    query_options = {"sub_category": []}
    # Set variant sub-category in query_options
    for sub_cat in request.form.getlist("sub_category") or [
        subcat[0] for subcat in SUBCATEGORY_CHOICES
    ]:
        query_options["sub_category"].append(sub_cat)

    if request.form.get("description") is not None and request.form.get("description") != "":
        query_options["description"] = request.form["description"]

    # Set requested variant coordinates in query options
    set_query_coordinates(query_options, request.form)

    # Get all variants according to the selected fields in filter form
    managed_variants_query = store.managed_variants(
        category=categories, query_options=query_options
    )

    variant_count = store.count_managed_variants(category=categories, query_options=query_options)
    managed_variants_res = managed_variants_query.skip(skip_count).limit(VARS_PER_PAGE)
    managed_variants = [managed_variant for managed_variant in managed_variants_res]

    return {
        "page": page,
        "filters_form": filters_form,
        "add_form": add_form,
        "modify_form": modify_form,
        "managed_variants": managed_variants,
        "result_size": variant_count,
        "cytobands_37": store.cytoband_by_chrom("37"),
        "cytobands_38": store.cytoband_by_chrom("38"),
        "chromosomes_37": CHROMOSOMES,
        "chromosomes_38": CHROMOSOMES_38,
        "subcategory_choices": [[choice[1], choice[0]] for choice in SUBCATEGORY_CHOICES],
    }


def add_managed_variant(request):
    """Add a managed variant.

    Args:
        request(werkzeug.local.LocalProxy): request containing form data
    """

    add_form = ManagedVariantAddForm(request.form)
    institutes = list(user_institutes(store, current_user))
    current_user_id = current_user._id

    if not add_form.validate():
        for error, message in add_form.errors.items():
            flash(f"Error in field {error}: {message}", "danger")
        return False

    managed_variant_obj = build_managed_variant(
        dict(
            chromosome=add_form["chromosome"].data,
            position=add_form["position"].data,
            end=add_form["end"].data,
            reference=add_form["reference"].data,
            alternative=add_form["alternative"].data,
            institutes=institutes,
            maintainer=[current_user_id],
            category=add_form["category"].data,
            sub_category=add_form["sub_category"].data,
            description=add_form["description"].data,
        )
    )

    return store.upsert_managed_variant(managed_variant_obj)


def upload_managed_variants(store, lines, institutes, current_user_id):
    """Add managed variants from a CSV file"""

    total_variant_lines = 0
    new_managed_variants = 0

    try:
        for managed_variant_info in parse_managed_variant_lines(lines):
            total_variant_lines += 1

            status, message = validate_managed_variant(managed_variant_info)
            if not status:
                flash(
                    f"❌ Managed variant info line {total_variant_lines} has errors {message} ({managed_variant_info})",
                    "warning",
                )
                continue

            managed_variant_info.update({"maintainer": [current_user_id], "institutes": institutes})
            managed_variant_obj = build_managed_variant(managed_variant_info)

            if store.upsert_managed_variant(managed_variant_obj):
                new_managed_variants += 1

    except UnboundLocalError:
        flash(
            f"Invalid format on variant file. Line {total_variant_lines}",
            "warning",
        )

    return new_managed_variants, total_variant_lines


def validate_managed_variant(managed_variant_info: dict) -> tuple[bool, str]:
    """
    Validate managed variants. Returns True, None for successful
    """
    mandatory_fields = [
        "chromosome",
        "position",
        "reference",
        "alternative",
        "category",
        "sub_category",
    ]

    for mandatory_field in mandatory_fields:
        if not managed_variant_info.get(mandatory_field):
            return False, f"Missing mandatory field {mandatory_field}"

    ref = managed_variant_info.get("reference")
    alt = managed_variant_info.get("alternative")
    sub_category = managed_variant_info.get("sub_category")

    status, msg = validate_ref_alt(alt=alt, ref=ref)
    if not status:
        return (status, msg)

    alt_validator = None

    match sub_category.upper():
        case "SNV" | "INDEL":
            alt_validator = validate_snv_alt
        case "BND":
            alt_validator = validate_bnd_alt

    if is_symbolic_alt(alt):
        alt_validator = validate_symbolic_alt

    return alt_validator(alt) if alt_validator else (True, None)


def modify_managed_variant(store, managed_variant_id, edit_form):
    """Modify a managed variant."""

    managed_variant = store.find_managed_variant(managed_variant_id)

    if managed_variant is None:
        return

    original_obj_id = managed_variant["_id"]

    managed_variant.update(
        {
            "chromosome": edit_form["chromosome"].data,
            "position": edit_form["position"].data,
            "end": edit_form["end"].data,
            "reference": edit_form["reference"].data,
            "alternative": edit_form["alternative"].data,
            "category": edit_form["category"].data,
            "sub_category": edit_form["sub_category"].data,
            "description": edit_form["description"].data,
        }
    )

    # new ids must be built upon update
    updated_variant = build_managed_variant(managed_variant)

    LOG.debug(
        "Updated variant has mvid %s and old id is %s.",
        updated_variant["managed_variant_id"],
        original_obj_id,
    )

    result = store.upsert_managed_variant(updated_variant, original_obj_id)

    return result


def remove_managed_variant(store, managed_variant_id):
    """Remove a managed variant."""

    removed_variant = store.delete_managed_variant(managed_variant_id)
    return removed_variant
