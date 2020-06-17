import logging
import os.path

from datetime import date


LOG = logging.getLogger(__name__)


def managed_variants(store, managed_variants_query, page=1, per_page=50):
    """Pre-process list of variants."""
    variant_count = managed_variants_query.count()
    skip_count = per_page * max(page - 1, 0)
    more_variants = True if variant_count > (skip_count + per_page) else False
    managed_variants_res = managed_variants_query.skip(skip_count).limit(per_page)

    managed_variants = [managed_variant for managed_variant in managed_variants_res]

    return {"managed_variants": managed_variants, "more_variants": more_variants}
