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


def add_managed_variant(store, add_form, institutes, current_user_id):
    """Add a managed variant."""

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


def modify_managed_variant(store, managed_variant_id, edit_form):
    """Modify a managed variant."""

    managed_variant = store.managed_variant(managed_variant_id)

    if managed_variant is None:
        return

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
    result = store.upsert_managed_variant(updated_variant)

    if result:
        store.delete_managed_variant(managed_variant)

    return result


def remove_managed_variant(store, variant_id):
    """Remove a managed variant."""

    removed_variant = store.delete_managed_variant_id(variant_id)

    return removed_variant
