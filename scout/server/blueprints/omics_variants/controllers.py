import logging

from scout.server.blueprints.variant.utils import update_variant_case_panels
from scout.server.blueprints.variants.utils import update_case_panels
from scout.server.utils import case_has_alignments, case_has_mt_alignments, case_has_rna_tracks

log = logging.getLogger(__name__)


def outliers(
    store, institute_obj, case_obj, omics_variants_query, variant_count, page=1, per_page=50
):
    """Pre-process list of outlier omics variants."""
    skip_count = per_page * max(page - 1, 0)

    more_variants = variant_count > (skip_count + per_page)
    variants = []

    update_case_panels(store, case_obj)

    case_has_alignments(case_obj)
    case_has_mt_alignments(case_obj)
    case_has_rna_tracks(case_obj)

    for variant_obj in omics_variants_query.skip(skip_count).limit(per_page):
        parsed_variant = decorate_omics_variant(
            store,
            institute_obj,
            case_obj,
            variant_obj,
        )

        variants.append(parsed_variant)

    return {"variants": variants, "more_variants": more_variants}


def decorate_omics_variant(store, institute_obj, case_obj, omics_variant_obj):
    """Decorate each variant with a limited selection of variant obj level information for display on variantS page."""

    omics_variant_obj["comments"] = store.events(
        institute_obj,
        case=case_obj,
        variant_id=omics_variant_obj["omics_variant_id"],
        comments=True,
    )

    update_variant_case_panels(case_obj, omics_variant_obj)

    return omics_variant_obj
