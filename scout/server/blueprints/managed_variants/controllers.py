import logging
import os.path

from scout.build import build_managed_variant

LOG = logging.getLogger(__name__)


def managed_variants(store, managed_variants_query, page=1, per_page=50):
    """Pre-process list of variants."""
    variant_count = managed_variants_query.count()
    skip_count = per_page * max(page - 1, 0)
    more_variants = True if variant_count > (skip_count + per_page) else False
    managed_variants_res = managed_variants_query.skip(skip_count).limit(per_page)

    managed_variants = [managed_variant for managed_variant in managed_variants_res]

    return {"managed_variants": managed_variants, "more_variants": more_variants}


def add_managed_variant(store, add_form, current_institute_id, current_user_id):
    """Add a managed variant."""

    managed_variant_obj = build_managed_variant(
        dict(
            chromosome=add_form["chromosome"],
            position=add_form["position"],
            end=add_form["end"],
            reference=add_form["reference"],
            alternative=add_form["alternative"],
            institute=current_institute_id,
            maintainer=[current_user_id],
            category=add_form.get("category", "snv"),
            sub_category=add_form.get("category", "sub_category"),
            description=add_form.get("description", None),
        )
    )

    upsert_managed_variant(store, managed_variant_obj)
    return


def modify_managed_variant(store, managed_variant, edit_form):
    """Modify a managed variant."""

    return


def remove_managed_variant(store, variant_id):
    """Remove a managed variant."""

    return
