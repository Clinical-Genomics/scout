import decimal
import logging
import re
from typing import Any, Dict

import bson
from flask import Response, flash, session, url_for
from flask_login import current_user
from markupsafe import Markup
from pymongo.cursor import CursorType
from pymongo.errors import DocumentTooLarge
from werkzeug.datastructures import Headers, ImmutableMultiDict, MultiDict
from wtforms import DecimalField

from scout.adapter import MongoAdapter
from scout.constants import (
    ACMG_COMPLETE_MAP,
    ACMG_MAP,
    CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
    CANCER_TIER_OPTIONS,
    CHROMOSOMES,
    CHROMOSOMES_38,
    CLINSIG_MAP,
    DISMISS_VARIANT_OPTIONS,
    EXPORTED_VARIANTS_LIMIT,
    MANUAL_RANK_OPTIONS,
    MOSAICISM_OPTIONS,
    SPIDEX_HUMAN,
    VARIANT_FILTERS,
    VARIANTS_TARGET_FROM_CATEGORY,
)
from scout.constants.variants_export import CANCER_EXPORT_HEADER, EXPORT_HEADER
from scout.server.blueprints.variant.utils import (
    callers,
    clinsig_human,
    predictions,
    update_representative_gene,
    update_variant_case_panels,
)
from scout.server.blueprints.variants.forms import BetterDecimalField
from scout.server.links import add_gene_links, cosmic_links, str_source_link
from scout.server.utils import (
    case_has_alignments,
    case_has_mt_alignments,
    institute_and_case,
    user_institutes,
)

from .forms import FILTERSFORMCLASS, CancerSvFiltersForm, FusionFiltersForm, SvFiltersForm
from .utils import update_case_panels

LOG = logging.getLogger(__name__)


def get_variants_page(form=ImmutableMultiDict) -> int:
    """Get current variants page from request data"""
    pages = form.getlist("page")
    if pages:
        return int(Markup.escape(pages[0]))
    else:
        return 1


def get_expand_search(form=ImmutableMultiDict) -> bool:
    """Checks whether to expand filters window or not"""
    pages = form.getlist("page")
    return pages == ["1"]


def populate_force_show_unaffected_vars(institute_obj, form):
    """Whenever a user institute contains the key/value check_show_all_vars=True,
    then all variants (and not only those occurring in affected individuals) should be shown

    Args:
        institute_obj(dict): scout.models.institute
        form(VariantFiltersForm)
    """
    if institute_obj.get("check_show_all_vars"):
        form.show_unaffected.data = True


def populate_chrom_choices(form, case_obj):
    """Populate the option of the chromosome select according to the case genome build"""
    # Populate chromosome choices
    chromosomes = CHROMOSOMES if "37" in str(case_obj.get("genome_build")) else CHROMOSOMES_38
    form.chrom.choices = [(chrom, chrom) for chrom in chromosomes]


def variants(
    store,
    institute_obj,
    case_obj,
    variants_query,
    variant_count,
    page=1,
    per_page=50,
    query_form=None,
):
    """Pre-process list of variants."""

    skip_count = per_page * max(page - 1, 0)
    more_variants = variant_count > (skip_count + per_page)
    variant_res = variants_query.skip(skip_count).limit(per_page)

    genome_build = str(case_obj.get("genome_build", "37"))
    if genome_build not in ["37", "38"]:
        genome_build = "37"

    case_dismissed_vars = store.case_dismissed_variants(institute_obj, case_obj)

    update_case_panels(store, case_obj)

    variants = []
    for variant_obj in variant_res:
        overlapping_svs = list(store.overlapping(variant_obj))
        variant_obj["overlapping"] = overlapping_svs or None

        evaluations = []
        is_research = variant_obj["variant_type"] == "research"
        # Get previous ACMG evaluations of the variant from other cases
        for evaluation_obj in store.get_evaluations(variant_obj):
            if evaluation_obj["case_id"] == case_obj["_id"]:
                continue

            classification = evaluation_obj["classification"]

            evaluation_obj["classification"] = ACMG_COMPLETE_MAP.get(classification)
            evaluations.append(evaluation_obj)

        variant_obj["evaluations"] = evaluations

        variant_obj["dismissals"] = store.get_dismissals(
            variant_obj["variant_id"], exclude_case=case_obj["_id"]
        )

        clinical_var_obj = variant_obj
        if is_research:
            variant_obj["research_assessments"] = get_manual_assessments(variant_obj)

            clinical_var_obj = store.variant(
                case_id=case_obj["_id"],
                simple_id=variant_obj["simple_id"],
                variant_type="clinical",
            )

        variant_obj["clinical_assessments"] = get_manual_assessments(clinical_var_obj)

        if case_obj.get("group"):
            variant_obj["group_assessments"] = _get_group_assessments(store, case_obj, variant_obj)

        update_variant_case_panels(case_obj, variant_obj)

        variants.append(
            parse_variant(
                store,
                institute_obj,
                case_obj,
                variant_obj,
                update=True,
                genome_build=genome_build,
                case_dismissed_vars=case_dismissed_vars,
                query_form=query_form,
            )
        )

    return {"variants": variants, "more_variants": more_variants}


def _get_group_assessments(store, case_obj, variant_obj):
    """Return manual variant assessments for other cases grouped with this one.

    Args:
        case_obj
    Returns:
        group_assessments(list(dict))
    """
    group_assessments = []

    group_case_ids = set()
    for group_id in case_obj.get("group"):
        group_case_ids.update(store.case_ids_from_group_id(group_id))

        for group_case_id in group_case_ids:
            # Returning an extra assessment for variants from the same case is pointless
            if group_case_id == case_obj["_id"]:
                continue

            cohort_var_obj = store.variant(
                case_id=group_case_id,
                simple_id=variant_obj["simple_id"],
                variant_type=variant_obj["variant_type"],
            )
            group_assessments.extend(get_manual_assessments(cohort_var_obj))

    return group_assessments


def sv_variants(store, institute_obj, case_obj, variants_query, variant_count, page=1, per_page=50):
    """Pre-process list of SV variants."""
    skip_count = per_page * max(page - 1, 0)

    more_variants = variant_count > (skip_count + per_page)
    variants = []
    genome_build = str(case_obj.get("genome_build", "37"))
    if genome_build not in ["37", "38"]:
        genome_build = "37"

    case_dismissed_vars = store.case_dismissed_variants(institute_obj, case_obj)

    for variant_obj in variants_query.skip(skip_count).limit(per_page):
        # show previous classifications for research variants
        clinical_var_obj = variant_obj
        if variant_obj["variant_type"] == "research":
            clinical_var_obj = store.variant(
                case_id=case_obj["_id"],
                simple_id=variant_obj["simple_id"],
                variant_type="clinical",
            )
        if clinical_var_obj is not None:
            variant_obj["clinical_assessments"] = get_manual_assessments(clinical_var_obj)

        variants.append(
            parse_variant(
                store,
                institute_obj,
                case_obj,
                variant_obj,
                genome_build=genome_build,
                case_dismissed_vars=case_dismissed_vars,
            )
        )

    return {"variants": variants, "more_variants": more_variants}


def mei_variants(
    store: MongoAdapter,
    institute_obj: Dict,
    case_obj: Dict,
    variants_query: CursorType,
    variant_count: int,
    page: int = 1,
    per_page: int = 50,
) -> Dict[str, Any]:
    """Pre-process list of MEI variants."""
    skip_count = per_page * max(page - 1, 0)

    more_variants = variant_count > (skip_count + per_page)
    variants = []
    genome_build = str(case_obj.get("genome_build", "37"))
    if genome_build not in ["37", "38"]:
        genome_build = "37"

    case_dismissed_vars = store.case_dismissed_variants(institute_obj, case_obj)

    for variant_obj in variants_query.skip(skip_count).limit(per_page):
        # show previous classifications for research variants
        clinical_var_obj = variant_obj
        if variant_obj["variant_type"] == "research":
            clinical_var_obj = store.variant(
                case_id=case_obj["_id"],
                simple_id=variant_obj["simple_id"],
                variant_type="clinical",
            )
        if clinical_var_obj is not None:
            variant_obj["clinical_assessments"] = get_manual_assessments(clinical_var_obj)

        variants.append(
            parse_variant(
                store,
                institute_obj,
                case_obj,
                variant_obj,
                genome_build=genome_build,
                case_dismissed_vars=case_dismissed_vars,
            )
        )

    return {"variants": variants, "more_variants": more_variants}


def str_variants(
    store, institute_obj, case_obj, variants_query, variant_count, page=1, per_page=50
):
    """Pre-process list of STR variants."""

    return_view_data = {}

    # Provide basic info on alignment files availability for this case
    case_has_alignments(case_obj)
    case_has_mt_alignments(case_obj)

    return_view_data.update(
        variants(
            store,
            institute_obj,
            case_obj,
            variants_query,
            variant_count,
            page=page,
            per_page=per_page,
        )
    )

    return return_view_data


def fusion_variants(
    store, institute_obj, case_obj, variants_query, variant_count, page=1, per_page=50
):
    """Pre-process list of fusion variants."""
    skip_count = per_page * max(page - 1, 0)

    more_variants = variant_count > (skip_count + per_page)
    variants = []
    genome_build = str(case_obj.get("genome_build", "38"))
    if genome_build not in ["37", "38"]:
        genome_build = "38"

    case_dismissed_vars = store.case_dismissed_variants(institute_obj, case_obj)

    for variant_obj in variants_query.skip(skip_count).limit(per_page):
        # show previous classifications for research variants
        clinical_var_obj = variant_obj
        if variant_obj["variant_type"] == "research":
            clinical_var_obj = store.variant(
                case_id=case_obj["_id"],
                simple_id=variant_obj["simple_id"],
                variant_type="clinical",
            )
        if clinical_var_obj is not None:
            variant_obj["clinical_assessments"] = get_manual_assessments(clinical_var_obj)

        variants.append(
            parse_variant(
                store,
                institute_obj,
                case_obj,
                variant_obj,
                genome_build=genome_build,
                case_dismissed_vars=case_dismissed_vars,
            )
        )

    return {"variants": variants, "more_variants": more_variants}


def get_manual_assessments(variant_obj):
    """Return manual assessments ready for display.

    An assessment dict of str has keys "title", "label" and "display_class".

    args:
        variant_obj(variant)

    returns:
        assessments(array(dict))
    """

    ## display manual input of interest: classified, commented, tagged, mosaicism or dismissed.
    assessment_keywords = [
        "acmg_classification",
        "manual_rank",
        "cancer_tier",
        "dismiss_variant",
        "mosaic_tags",
    ]

    assessments = []

    if variant_obj is None:
        return assessments

    for assessment_type in assessment_keywords:
        assessment = {}
        if variant_obj.get(assessment_type) is not None:
            if assessment_type == "manual_rank":
                manual_rank = variant_obj[assessment_type]
                assessment["title"] = "Manual rank: {}".format(
                    MANUAL_RANK_OPTIONS[manual_rank]["description"]
                )
                assessment["label"] = MANUAL_RANK_OPTIONS[manual_rank]["label"]
                assessment["display_class"] = MANUAL_RANK_OPTIONS[manual_rank]["label_class"]

            if assessment_type == "cancer_tier":
                cancer_tier = variant_obj[assessment_type]
                assessment["title"] = "Cancer tier: {}".format(
                    CANCER_TIER_OPTIONS[cancer_tier]["description"]
                )
                assessment["label"] = CANCER_TIER_OPTIONS[cancer_tier]["label"]
                assessment["display_class"] = CANCER_TIER_OPTIONS[cancer_tier]["label_class"]

            if assessment_type == "acmg_classification":
                classification = variant_obj[assessment_type]
                if isinstance(classification, int):
                    acmg_code = ACMG_MAP[classification]
                    classification = ACMG_COMPLETE_MAP[acmg_code]

                assessment["title"] = "ACMG: {}".format(classification["label"])
                assessment["label"] = classification["short"]
                assessment["display_class"] = classification["color"]

            if assessment_type == "dismiss_variant":
                dismiss_variant_options = {
                    **DISMISS_VARIANT_OPTIONS,
                    **CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
                }
                assessment["label"] = "Dismissed"
                assessment["title"] = "dismiss:<br>"
                for reason in variant_obj[assessment_type]:
                    reason = int(reason)
                    assessment["title"] += "<strong>{}</strong> - {}<br><br>".format(
                        dismiss_variant_options[reason]["label"],
                        dismiss_variant_options[reason]["description"],
                    )
                assessment["display_class"] = "secondary"

            if assessment_type == "mosaic_tags":
                assessment["label"] = "Mosaicism"
                assessment["title"] = "mosaicism:<br>"
                for reason in variant_obj[assessment_type]:
                    if not isinstance(reason, int):
                        reason = int(reason)
                    assessment["title"] += "<strong>{}</strong> - {}<br><br>".format(
                        MOSAICISM_OPTIONS[reason]["label"],
                        MOSAICISM_OPTIONS[reason]["description"],
                    )
                assessment["display_class"] = "secondary"

            assessments.append(assessment)

    return assessments


def compounds_need_updating(compounds, dismissed):
    """Checks if the list of compounds for a variant needs to be updated.
     Returns True or False.

    Args:
      compounds (list): list of compounds dictionaries
      dismissed (list): list of case dismissed variant ids

    Returns:
      True or False (bool)
    """
    for compound in compounds:
        if "not_loaded" not in compound:  # This key should be always present
            return True

        if compound["variant"] in dismissed and compound.get("is_dismissed") is not True:
            return True

        if compound.get("is_dismissed") and compound["variant"] not in dismissed:
            return True

    return False


def update_compounds(store, variant_obj, case_dismissed_vars):
    """Check if gene symbol or compound info needs updating and sort compounds.
    Args:
        store(scout.adapter.MongoAdapter)
        variant_obj(scout.models.Variant)
        case_dismissed_variants(list): dismissed vars for this case
    Returns:
        has_changed(boolean)
    """
    has_changed = False
    compounds = variant_obj.get("compounds", [])

    if compounds:
        # Check if we need to update compound information
        if compounds_need_updating(compounds, case_dismissed_vars):
            new_compounds = store.update_variant_compounds(variant_obj)
            variant_obj["compounds"] = new_compounds
            has_changed = True

        # sort compounds on combined rank score
        variant_obj["compounds"] = sorted(
            variant_obj["compounds"], key=lambda compound: -compound["combined_score"]
        )

    return has_changed


def update_variant_genes(store, variant_obj, genome_build):
    """Check if variant gene symbols or phenotype needs updating.
    We update the variant if some information was missing from loading.
    Or if gene symbols in reference genes have changed.
    Args:
        store(scout.adapter.MongoAdapter)
        variant_obj(scout.models.Variant)
        genome_build(str)
    Returns:
        has_changed(boolean)
    """
    has_changed = False

    # Update the hgnc symbols if they are incorrect
    variant_genes = variant_obj.get("genes")

    # use hgnc_ids to populate variant genes if missing, e.g. for STR variants
    if not variant_genes and variant_obj.get("hgnc_ids"):
        variant_obj["genes"] = []
        for hgnc_id in variant_obj.get("hgnc_ids"):
            has_changed = True
            variant_gene = {"hgnc_id": hgnc_id}
            variant_obj["genes"].append(variant_gene)

    if variant_genes is not None:
        for gene_obj in variant_genes:
            # If there is no hgnc id there is nothin we can do
            if not gene_obj["hgnc_id"]:
                continue
            # Else we collect the gene object and check the id
            if gene_obj.get("hgnc_symbol") is None or gene_obj.get("phenotypes") is None:
                hgnc_gene = store.hgnc_gene(gene_obj["hgnc_id"], build=genome_build)
                if not hgnc_gene:
                    continue
                has_changed = True
                gene_obj["hgnc_symbol"] = hgnc_gene["hgnc_symbol"]
                # phenotypes may not exist for the hgnc_gene either, but try
                gene_obj["phenotypes"] = hgnc_gene.get("phenotypes")
            add_gene_links(gene_obj, genome_build)

    return has_changed


def update_variant_store(store, variant_obj):
    """
    Update variants in db store if anything changed.
    Args:
        store(scout.adapter.MongoAdapter)
        variant_obj(scout.models.Variant)

        update(boolean): upsert only if this is set true

        get_compounds(bool): if compounds should be added to added to the returned variant object

    """
    try:
        variant_obj = store.update_variant(variant_obj)
    except DocumentTooLarge:
        flash(
            f"An error occurred while updating info for variant: {variant_obj['_id']} (pymongo_errors.DocumentTooLarge: {len(bson.BSON.encode(variant_obj))})",
            "warning",
        )


def _compound_follow_filter_freq(compound, compound_var_obj, query_form):
    """When compound follow filter is selected, apply relevant settings from the query filter onto dismissing compounds.

    There are some similarities between how the query options are filtered that we can reuse, e.g. the freq items
    are filtered the same way.
    Args:
        compound(dict)
        compound_variant_obj(scout.models.Variant)
        query_form(VariantFiltersForm)
    """

    # keys as in form, values as on variant_obj
    compound_follow_freq_items = {
        "gnomad_frequency": "gnomad_frequency",
        "local_obs": "local_obs_old",
        "clingen_ngi": "clingen_ngi",
        "swegen": "swegen",
    }

    for item, compound_item_name in compound_follow_freq_items.items():
        query_form_item = query_form.get(item)
        if query_form_item is None:
            continue

        compound_item = compound_var_obj.get(compound_item_name)
        if compound_item is None:
            continue

        if compound_item >= query_form_item:
            compound["is_dismissed"] = True
            return True

    return False


def _compound_follow_filter_lt(compound, compound_var_obj, query_form):
    """When compound follow filter is selected, apply relevant settings from the query filter onto dismissing compounds.

    There are some similarities between how the query options are filtered that we can reuse, e.g. the positions.

    Args:
        compound(dict)
        compound_variant_obj(scout.models.Variant)
        query_form(VariantFiltersForm)
    Returns boolean, true if the compound was hidden.
    """
    compound_follow_lt_items = ["cadd_score", "end"]

    for item in compound_follow_lt_items:
        query_form_item = query_form.get(item)
        if query_form_item is not None:
            compound_item = compound_var_obj.get(item)
            if compound_item is None or compound_item < query_form_item:
                compound["is_dismissed"] = True
                return True

    return False


def _compound_follow_filter_gt(compound, compound_var_obj, query_form):
    """When compound follow filter is selected, apply relevant settings from the query filter onto dismissing compounds.

    There are some similarities between how the query options are filtered that we can reuse, e.g. the positions.

    Args:
        compound(dict)
        compound_variant_obj(scout.models.Variant)
        query_form(VariantFiltersForm)
    Returns boolean, true if the compound was hidden.
    """

    compound_follow_gt_items = ["position"]

    for item in compound_follow_gt_items:
        query_form_item = query_form.get(item)
        if query_form_item is not None:
            compound_item = compound_var_obj.get(item)
            if compound_item is None or compound_item > query_form_item:
                compound["is_dismissed"] = True
                return True

    return False


def _compound_follow_filter_in(compound, compound_var_obj, query_form):
    """When compound follow filter is selected, apply relevant settings from the query filter onto dismissing compounds.

    There are some similarities between how the query options are filtered that we can reuse, e.g. the ones with
    multiple categories such as sv_type or clin_sig.

    Args:
        compound(dict)
        compound_variant_obj(scout.models.Variant)
        query_form(VariantFiltersForm)
    Returns boolean, true if the compound was hidden.
    """

    # keys as in form, values as on variant_obj
    compound_follow_in_items = {
        "svtype": "sub_category",
    }
    for item, compound_item_name in compound_follow_in_items.items():
        query_form_items = query_form.get(item)
        if query_form_items:
            compound_items = []
            compound_items.append(compound_var_obj.get(compound_item_name))

            LOG.info(
                "item %s compound item %s compound items %s query_form items %s",
                item,
                compound_item_name,
                compound_items,
                query_form_items,
            )
            if not compound_items:
                compound["is_dismissed"] = True
                LOG.info("dismissing it!")
                return True

            if set(compound_items).isdisjoint(set(query_form_items)):
                compound["is_dismissed"] = True
                LOG.info("dismissing it disjoint!")
                return True
    return False


def _compound_follow_filter_in_compound(compound, compound_var_obj, query_form):
    """When compound follow filter is selected, apply relevant settings from the query filter onto dismissing compounds.

    There are some similarities between how the query options are filtered that we can reuse, e.g. the ones with
    multiple categories such as region and functional annotations. These are transferred to the compound dict itself
    upon creation, from the compound_var_obj genes and transcripts.

    Args:
        compound(dict)
        compound_variant_obj(scout.models.Variant)
        query_form(VariantFiltersForm)
    Returns boolean, true if the compound was hidden.
    """
    compound_follow_in_items = [
        "region_annotations",
        "functional_annotations",
    ]
    for item in compound_follow_in_items:
        query_form_items = query_form.get(item)
        if query_form_items:
            compound_items = compound.get(item)
            if not compound_items:
                compound["is_dismissed"] = True
                return True

            split_any_gene_items = [
                possible_gene_item.split(":")[-1]
                for possible_gene_item in compound_items
                if ":" in possible_gene_item
            ]
            if split_any_gene_items:
                compound_items = split_any_gene_items

            if set(compound_items).isdisjoint(set(query_form_items)):
                compound["is_dismissed"] = True
                return True
    return False


def _compound_follow_filter_clnsig(compound, compound_var_obj, query_form):
    """When compound follow filter is selected, apply relevant settings from the query filter onto dismissing compounds.

    There are some filter options that are rather unique, like the ClinVar one.

    If clinsig_confident_always_returned is checked, variants are currently never dismissed on ClinSig alone.

    Args:
        compound(dict)
        compound_variant_obj(scout.models.Variant)
        query_form(VariantFiltersForm)
    Returns boolean, true if the compound was hidden.
    """
    query_rank = []
    query_str_rank = []

    clinsig_always_returned = query_form.get("clinsig_confident_always_returned")
    if clinsig_always_returned:
        return False

    clinsig = query_form.get("clinsig")
    if clinsig:
        for item in clinsig:
            query_rank.append(int(item))
            # also search for human readable clinsig values
            query_rank.append(CLINSIG_MAP[int(item)])
            query_str_rank.append(CLINSIG_MAP[int(item)])

        str_re = re.compile("|".join(query_str_rank))

        compound_clnsig = compound_var_obj.get("clnsig")
        if compound_clnsig:
            for compound_clnsig_item in compound_clnsig:
                clnsig_value = compound_clnsig_item.get("value")
                if clnsig_value in query_rank or (
                    isinstance(clnsig_value, str) and str_re.match(clnsig_value)
                ):
                    return False

        compound["is_dismissed"] = True
        return True

    return False


def _compound_follow_filter_spidex(compound, compound_var_obj, query_form):
    """When compound follow filter is selected, apply relevant settings from the query filter onto dismissing compounds.

    There are some filter options that are rather unique, like the leveled spidex one. SPIDEX score levels are symmetric
    around 0, with different level ranges, so that e.g. the intervals [-1, -2] and [1, 2] are both medium.
    The spidex score on the variant object is a scalar. The user selects one or more levels such as "medium" to filter in
    the query.

    Args:
        compound(dict)
        compound_variant_obj(scout.models.Variant)
        query_form(VariantFiltersForm)
    Returns boolean, true if the compound was hidden.
    """
    spidex_human = query_form.get("spidex_human")
    if spidex_human:
        compound_spidex = compound_var_obj.get("spidex")
        if compound_spidex is not None:
            keep = any(
                level in spidex_human
                and (
                    (
                        compound_spidex > SPIDEX_HUMAN[level]["neg"][0]
                        and compound_spidex < SPIDEX_HUMAN[level]["neg"][1]
                    )
                    or (
                        compound_spidex > SPIDEX_HUMAN[level]["pos"][0]
                        and compound_spidex < SPIDEX_HUMAN[level]["pos"][1]
                    )
                )
                for level in SPIDEX_HUMAN
            )
            if not keep:
                compound["is_dismissed"] = True
                return True

    return False


def compound_follow_filter(compound, compound_var_obj, query_form):
    """When compound follow filter is selected, apply relevant settings from the query filter onto dismissing compounds.

    There are some similarities between how the query options are filtered that we can reuse, e.g. the freq items
    are filtered the same way.
    Args:
        compound(dict)
        compound_variant_obj(scout.models.Variant)
        query_form(VariantFiltersForm)
    """

    if _compound_follow_filter_lt(compound, compound_var_obj, query_form):
        return

    if _compound_follow_filter_gt(compound, compound_var_obj, query_form):
        return

    if _compound_follow_filter_freq(compound, compound_var_obj, query_form):
        return

    if _compound_follow_filter_in(compound, compound_var_obj, query_form):
        return

    if _compound_follow_filter_in_compound(compound, compound_var_obj, query_form):
        return

    if _compound_follow_filter_clnsig(compound, compound_var_obj, query_form):
        return

    if _compound_follow_filter_spidex(compound, compound_var_obj, query_form):
        return


def hide_compounds_query(store, variant_obj, query_form):
    """Check compound against current query form values.
    Check the query hide rank score, and dismiss compound from current view if its rank score is equal or lower.
    If compound follow filter is selected, apply relevant settings from the query filter onto dismissing compounds.
    If a hiding compounds was engaged, non_loaded variants are considered of small interest to the users and also shaded.
    Args:
        store(scout.adapter.MongoAdapter)
        variant_obj(scout.models.Variant)
        query_form(VariantFiltersForm)
    """

    if not query_form:
        return

    for compound in variant_obj.get("compounds", []):
        rank_score = compound.get("rank_score")

        if query_form.get("compound_rank_score") is not None and (
            rank_score is None or rank_score <= query_form.get("compound_rank_score")
        ):
            compound["is_dismissed"] = True
            continue

        if query_form.get("compound_follow_filter"):
            compound_var_obj = store.variant(compound.get("variant"))
            if not compound_var_obj:
                compound["is_dismissed"] = True
                continue
            compound_follow_filter(compound, compound_var_obj, query_form)


def parse_variant(
    store,
    institute_obj,
    case_obj,
    variant_obj,
    update=False,
    genome_build="37",
    get_compounds=True,
    case_dismissed_vars=[],
    query_form=None,
):
    """Parse information about variants.
    - Adds information about compounds and genes
    - Updates some information about compounds if necessary and 'update=True'
    - Hide compound variants if query form filter indicates so.

    Args:
        store(scout.adapter.MongoAdapter)
        institute_obj(scout.models.Institute)
        case_obj(scout.models.Case)
        variant_obj(scout.models.Variant)
        update(bool): If variant should be updated in database
        get_compounds(bool): if compounds should be added to added to the returned variant object
        genome_build(str)
        case_dismissed_vars(list): list of dismissed variants for this case
        query_form(dict): query form for additional compounds filtering
    """

    compounds_have_changed = False
    if get_compounds:
        compounds_have_changed = update_compounds(store, variant_obj, case_dismissed_vars)

    genes_have_changed = update_variant_genes(store, variant_obj, genome_build)

    if update and (compounds_have_changed or genes_have_changed):
        update_variant_store(store, variant_obj)

    variant_obj["comments"] = store.events(
        institute_obj,
        case=case_obj,
        variant_id=variant_obj["variant_id"],
        comments=True,
    )

    variant_obj["matching_tiered"] = store.matching_tiered(
        variant_obj, user_institutes(store, current_user)
    )

    variant_obj["matching_ranked"] = store.get_matching_manual_ranked_variants(
        variant_obj, user_institutes(store, current_user), exclude_cases=[case_obj["_id"]]
    )

    variant_genes = variant_obj.get("genes")
    if variant_genes:
        variant_obj.update(predictions(variant_genes))
        if variant_obj.get("category") == "cancer":
            variant_obj.update(get_variant_info(variant_genes))

    if get_compounds:
        compounds = variant_obj.get("compounds", [])
        for compound_obj in compounds:
            compound_obj.update(predictions(compound_obj.get("genes", [])))

    hide_compounds_query(store, variant_obj, query_form)

    classification = variant_obj.get("acmg_classification")
    if isinstance(classification, int):
        acmg_code = ACMG_MAP[variant_obj["acmg_classification"]]
        variant_obj["acmg_classification"] = ACMG_COMPLETE_MAP[acmg_code]

    # convert length for SV variants
    variant_length = variant_obj.get("length")
    variant_obj["length"] = {100000000000: "inf", -1: "n.d."}.get(variant_length, variant_length)
    if not "end_chrom" in variant_obj:
        variant_obj["end_chrom"] = variant_obj["chromosome"]

    # variant level links shown on variants page
    variant_obj["cosmic_links"] = cosmic_links(variant_obj)
    variant_obj["str_source_link"] = str_source_link(variant_obj)
    # Format clinvar information
    variant_obj["clinsig_human"] = clinsig_human(variant_obj) if variant_obj.get("clnsig") else None

    update_representative_gene(variant_obj, variant_genes)

    # Add display information about callers
    variant_obj["callers"] = callers(variant_obj)

    # annotate filters
    variant_obj["filters"] = [
        VARIANT_FILTERS[f]
        for f in map(lambda x: x.lower(), variant_obj["filters"])
        if f in VARIANT_FILTERS
    ]

    return variant_obj


def download_str_variants(case_obj, variant_objs):
    """Download filtered STR variants for a case to an excel file

    Args:
        case_obj(dict)
        variant_objs(PyMongo cursor)

    Returns:
        an HTTP response containing a csv file
    """

    def generate(header, lines):
        yield header + "\n"
        for line in lines:
            yield line + "\n"

    DOCUMENT_HEADER = [
        "Index",
        "Repeat locus",
        "Repeat unit",
        "Estimated size",
        "Reference size",
        "Status",
        "Genotype",
        "Chromosome",
        "Position",
    ]

    export_lines = []
    for variant in variant_objs.limit(EXPORTED_VARIANTS_LIMIT):
        variant_line = []
        variant_line.append(str(variant.get("variant_rank", "")))  # index
        variant_line.append(variant.get("str_repid"))  # Repeat locus
        variant_line.append(
            variant.get("str_display_ru", variant.get("str_ru", ""))
        )  # Reference repeat unit
        variant_line.append(
            variant.get("alternative", "").replace("STR", "").replace("<", "").replace(">", "")
        )  # Estimated size
        variant_line.append(str(variant.get("str_ref", "")))  # Reference size
        variant_line.append(str(variant.get("str_status", "")))  # Status
        gt_cell = ""
        for sample in variant["samples"]:
            if sample["genotype_call"] == "./.":
                continue
            gt_cell += f"{sample['display_name']}:{sample['genotype_call']} "

        variant_line.append(gt_cell)  # Genotype
        variant_line.append(variant["chromosome"])  # Chromosome
        variant_line.append(str(variant["position"]))  # Position

        export_lines.append(",".join(variant_line))

    headers = Headers()
    headers.add(
        "Content-Disposition",
        "attachment",
        filename=str(case_obj["display_name"]) + "-filtered-str_variants.csv",
    )
    # return a csv with the exported variants
    return Response(
        generate(",".join(DOCUMENT_HEADER), export_lines),
        mimetype="text/csv",
        headers=headers,
    )


def download_variants(store, case_obj, variant_objs):
    """Download filtered variants for a case to an excel file

    Args:
        store(adapter.MongoAdapter)
        case_obj(dict)
        variant_objs(PyMongo cursor)

    Returns:
        an HTTP response containing a csv file
    """
    document_header = variants_export_header(case_obj)
    export_lines = []
    export_lines = variant_export_lines(
        store, case_obj, variant_objs.limit(EXPORTED_VARIANTS_LIMIT)
    )

    def generate(header, lines):
        yield header + "\n"
        for line in lines:
            yield line + "\n"

    headers = Headers()
    headers.add(
        "Content-Disposition",
        "attachment",
        filename=str(case_obj["display_name"]) + "-filtered-variants.csv",
    )
    # return a csv with the exported variants
    return Response(
        generate(",".join(document_header), export_lines),
        mimetype="text/csv",
        headers=headers,
    )


def variant_export_lines(store, case_obj, variants_query):
    """Get variants info to be exported to file, one list (line) per variant.
    Args:
        store(scout.adapter.MongoAdapter)
        case_obj(scout.models.Case)
        variants_query: a list of variant objects, each one is a dictionary
    Returns:
        export_variants: a list of strings. Each string  of the list corresponding to the fields
                         of a variant to be exported to file, separated by comma
    """

    export_variants = []

    for variant in variants_query:
        variant_line = []
        position = variant["position"]
        change = variant["reference"] + ">" + variant["alternative"]
        variant_line.append(variant["rank_score"])
        variant_line.append(variant["chromosome"])
        variant_line.append(position)
        variant_line.append(change)
        variant_line.append("_".join([str(position), change]))

        # gather gene info:
        gene_list = variant.get("genes")  # this is a list of gene objects

        # if variant is in genes
        if gene_list:
            gene_info = variant_export_genes_info(store, gene_list, case_obj.get("genome_build"))
            variant_line += gene_info
        else:
            empty_col = 0
            while empty_col < 4:
                variant_line.append(
                    "-"
                )  # empty HGNC id, empty gene name and empty transcripts columns
                empty_col += 1

        if variant.get("cadd_score"):
            variant_line.append(round(variant["cadd_score"], 2))
        else:
            variant_line.append("N/A")

        if variant.get("gnomad_frequency"):
            variant_line.append(round(variant["gnomad_frequency"], 5))
        else:
            variant_line.append("N/A")

        if case_obj.get("track") == "cancer":
            # Add cancer and normal VAFs
            for sample in ["tumor", "normal"]:
                allele = variant.get(sample)
                if not allele:
                    variant_line.append("-")
                    continue
                alt_freq = round(allele.get("alt_freq", 0), 4)
                alt_depth = allele.get("alt_depth")
                ref_depth = allele.get("ref_depth")

                vaf_sample = f"{alt_freq} ({alt_depth}|{ref_depth})"
                variant_line.append(vaf_sample)

            # ADD eventual COSMIC ID
            cosmic_ids = variant.get("cosmic_ids") or ["-"]
            variant_line.append(" | ".join(cosmic_ids))

        else:
            variant_gts = variant["samples"]  # list of coverage and gt calls for case samples
            for individual in case_obj["individuals"]:
                for variant_gt in variant_gts:
                    if individual["individual_id"] != variant_gt["sample_id"]:
                        continue

                    variant_line.append(variant_gt["genotype_call"])
                    # gather coverage info
                    variant_line.append(variant_gt["allele_depths"][0])  # AD reference
                    variant_line.append(variant_gt["allele_depths"][1])  # AD alternate
                    # gather genotype quality info
                    variant_line.append(variant_gt["genotype_quality"])

        variant_line = [str(i) for i in variant_line]
        export_variants.append(",".join(variant_line))

    return export_variants


def match_gene_txs_variant_txs(variant_gene, hgnc_gene):
    """Match gene transcript with variant transcript to extract primary and canonical tx info

    Args:
        variant_gene(dict): A gene dictionary with limited info present in variant.genes.
                        contains info on which transcript is canonical, hgvs and protein changes
        hgnc_gene(dict): A gene object obtained from the database containing a complete list of transcripts.

    Returns:
        canonical_txs, primary_txs(tuple): columns containing canonical and primary transcript info
    """
    canonical_txs = []
    primary_txs = []

    for tx in hgnc_gene.get("transcripts", []):
        tx_id = tx["ensembl_transcript_id"]

        # collect only primary of refseq trancripts from hgnc_gene gene
        if not tx.get("refseq_identifiers") and tx.get("is_primary") is False:
            continue

        for var_tx in variant_gene.get("transcripts", []):
            if var_tx["transcript_id"] != tx_id:
                continue

            tx_refseq = tx.get("refseq_id")
            hgvs = var_tx.get("coding_sequence_name") or "-"
            pt_change = var_tx.get("protein_sequence_name") or "-"

            # collect info from primary transcripts
            if tx_refseq in hgnc_gene.get("primary_transcripts", []):
                primary_txs.append("/".join([tx_refseq or tx_id, hgvs, pt_change]))

            # collect info from canonical transcript
            if var_tx.get("is_canonical") is True:
                canonical_txs.append("/".join([tx_refseq or tx_id, hgvs, pt_change]))

    return canonical_txs, primary_txs


def variant_export_genes_info(store, gene_list, genome_build="37"):
    """Adds gene info to a list of fields corresponding to a variant to be exported.

    Args:
        gene_list(list) A list of gene objects (with limited info) contained in the variant
        genome_build(str): genome build to export gene list to

    Returns:
        gene_info(list) A list of gene-relates string info
    """
    gene_ids = []
    gene_names = []
    canonical_txs = []
    primary_txs = []
    funct_annos = []
    gene_info = []

    for gene_obj in gene_list:
        hgnc_id = gene_obj["hgnc_id"]
        gene_ids.append(hgnc_id)
        hgnc_gene = store.hgnc_gene(hgnc_id, genome_build)
        if hgnc_gene is None:
            continue
        gene_names.append(hgnc_gene.get("hgnc_symbol"))

        gene_canonical_txs, gene_primary_txs = match_gene_txs_variant_txs(gene_obj, hgnc_gene)

        canonical_txs += gene_canonical_txs
        primary_txs += gene_primary_txs
        funct_anno = gene_obj.get("functional_annotation", "-")
        funct_annos.append(funct_anno.replace("_", " "))

    for item in [gene_ids, gene_names, canonical_txs, primary_txs, funct_annos]:
        gene_info.append(" | ".join(str(x) for x in item))

    return gene_info


def variants_export_header(case_obj):
    """Returns a header for the CSV file with the filtered variants to be exported.
    Args:
        case_obj(scout.models.Case)
    Returns:
        header: includes the fields defined in scout.constants.variants_export EXPORT_HEADER
                + AD_reference, AD_alternate, GT_quality for each sample analysed for a case
    """
    header = []
    if case_obj.get("track") == "cancer":
        header = header + CANCER_EXPORT_HEADER
    else:
        header = header + EXPORT_HEADER
        # Add fields specific for case samples
        for individual in case_obj["individuals"]:
            display_name = str(individual["display_name"])
            header.append("GT_" + display_name)  # Add Genotype filed for a sample
            header.append("AD_reference_" + display_name)  # Add AD reference field for a sample
            header.append("AD_alternate_" + display_name)  # Add AD alternate field for a sample
            header.append("GT_quality_" + display_name)  # Add Genotype quality field for a sample
    return header


def get_variant_info(genes):
    """Get variant information"""
    data = {"canonical_transcripts": []}
    for gene_obj in genes:
        if not gene_obj.get("canonical_transcripts"):
            tx = gene_obj["transcripts"][0]
            tx_id = tx["transcript_id"]
            exon = tx.get("exon", "-")
            c_seq = tx.get("coding_sequence_name", "-")
        else:
            tx_id = gene_obj["canonical_transcripts"]
            exon = gene_obj.get("exon", "-")
            c_seq = gene_obj.get("hgvs_identifier", "-")

        if len(c_seq) > 20:
            c_seq = c_seq[:20] + "..."

        gene_id = gene_obj.get("hgnc_symbol") or str(gene_obj["hgnc_id"])
        value = ":".join([gene_id, tx_id, exon, c_seq])
        data["canonical_transcripts"].append(value)

    return data


def cancer_variants(store, institute_id, case_name, variants_query, variant_count, form, page=1):
    """Fetch data related to cancer variants for a case.

    For each variant, if one or more gene panels are selected, assign the gene present
    in the panel as the second representative gene. If no gene panel is selected don't assign such a gene.
    """

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    case_dismissed_vars = store.case_dismissed_variants(institute_obj, case_obj)
    per_page = 50
    skip_count = per_page * max(page - 1, 0)
    more_variants = True if variant_count > (skip_count + per_page) else False

    variant_res = variants_query.skip(skip_count).limit(per_page)

    gene_panel_lookup = store.gene_to_panels(case_obj)  # build variant object
    variants_list = []
    for variant in variant_res:
        variant_obj = parse_variant(
            store,
            institute_obj,
            case_obj,
            variant,
            update=True,
            case_dismissed_vars=case_dismissed_vars,
        )
        secondary_gene = None

        if (
            "first_rep_gene" in variant_obj
            and variant_obj["first_rep_gene"] is not None
            and variant_obj["first_rep_gene"].get("hgnc_id") not in gene_panel_lookup
        ):
            for gene in variant_obj["genes"]:
                in_panels = set(gene_panel_lookup.get(gene["hgnc_id"], []))

                if len(in_panels & set(form.gene_panels.data)) > 0:
                    secondary_gene = gene
        variant_obj["second_rep_gene"] = secondary_gene
        variant_obj["clinical_assessments"] = get_manual_assessments(variant_obj)
        variants_list.append(variant_obj)

    data = dict(
        page=page,
        more_variants=more_variants,
        institute=institute_obj,
        case=case_obj,
        variants=variants_list,
        manual_rank_options=MANUAL_RANK_OPTIONS,
        cancer_tier_options=CANCER_TIER_OPTIONS,
        form=form,
    )
    return data


def upload_panel(store, institute_id, case_name, stream):
    """Parse out HGNC symbols from a stream."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    raw_symbols = [
        line.strip().split("\t")[0] for line in stream if line and not line.startswith("#")
    ]
    # check if supplied gene symbols exist, search genes by official symbol or alias
    hgnc_symbols = set()
    for raw_symbol in raw_symbols:
        matching_genes = list(
            store.gene_by_symbol_or_aliases(symbol=raw_symbol, build=case_obj.get("genome_build"))
        )
        if not matching_genes:
            flash("HGNC symbol not found: {}".format(raw_symbol), "warning")
            continue
        for gene_dict in matching_genes:
            hgnc_symbols.add(gene_dict.get("hgnc_symbol"))

    return hgnc_symbols


def gene_panel_choices(store, institute_obj, case_obj):
    """Populates the multiselect containing all the gene panels to be used in variants filtering
    Args:
        institute_obj(dict): an institute dictionary
        case_obj(dict): a case dictionary

    Returns:
        panel_list(list): a list of tuples containing the multiselect panel values/display name
    """
    panel_list = []
    # Add case default panels and the institute-specific panels to the panel select options
    for panel in case_obj.get("panels", []):
        latest_panel = store.gene_panel(panel["panel_name"])
        if latest_panel is None or not latest_panel.get("hidden", False):
            panel_option = (panel["panel_name"], panel["display_name"])
            panel_list.append(panel_option)

    panel_list.sort(key=lambda t: t[1])

    institute_choices = institute_obj.get("gene_panels", {})

    institute_panel_list = []
    for panel_name, display_name in institute_choices.items():
        panel_option = (panel_name, display_name)

        if panel_option not in panel_list:
            institute_panel_list.append(panel_option)

    institute_panel_list.sort(key=lambda t: t[1])
    if institute_panel_list:
        panel_list.extend(institute_panel_list)

    # Add HPO panel
    panel_list.append(("hpo", "HPO"))
    return panel_list


def populate_filters_form(store, institute_obj, case_obj, user_obj, category, request_form):
    """Update filter settings if Clinical Filter was requested.
        Ensure that persistent actions get acted on.

    Args:
        store: scout.adapter.MongoAdapter
        institute_obj: scout.models.Institute dict
        case_obj: scout.models.Case dict
        user_obj: scout.models.Users
        category: str
        request_form: FiltersForm

    Returns:
        form: FiltersForm
    """
    form = None
    clinical_filter_panels = []

    default_panels = []
    for panel in case_obj.get("panels", []):
        if panel.get("is_default"):
            default_panels.append(panel["panel_name"])

    if case_obj.get("hpo_clinical_filter"):
        clinical_filter_panels = ["hpo"]
    else:
        clinical_filter_panels = default_panels

    FiltersFormClass = FILTERSFORMCLASS[category]

    if category == "snv":
        clinical_filter_dict = FiltersFormClass.clinical_filter_base
        clinical_filter_dict.update(
            {
                "gnomad_frequency": str(institute_obj["frequency_cutoff"]),
                "gene_panels": clinical_filter_panels,
            }
        )
        clinical_filter = MultiDict(clinical_filter_dict)
    elif category in ("sv", "cancer", "cancer_sv", "mei"):
        clinical_filter_dict = FiltersFormClass.clinical_filter_base
        clinical_filter_dict.update(
            {
                "gene_panels": clinical_filter_panels,
            }
        )
        clinical_filter = MultiDict(clinical_filter_dict)

    if bool(request_form.get("clinical_filter")):
        form = FiltersFormClass(clinical_filter)
    else:
        form = persistent_filter_actions(
            store,
            institute_obj,
            case_obj,
            user_obj,
            category,
            request_form,
            FiltersFormClass,
        )

    return form


def persistent_filter_actions(
    store, institute_obj, case_obj, user_obj, category, request_form, FiltersFormClass
):
    """Act on persistent filter action requests.
        Check request form for what action, call corresponding adapter function and then update Form.

    Args
        store: scout.adapter.MongoAdapter
        institute_obj: scout.models.Institute dict
        case_obj: scout.models.Case dict
        user_obj: scout.models.Users
        category: str
        request_form: FiltersForm
        FiltersFormClass: FiltersFormClass

    Returns:
        form: FiltersForm
    """

    form = None

    if bool(request_form.get("lock_filter")):
        filter_id = request_form.get("filters")

        filter_obj = store.retrieve_filter(filter_id)
        if not filter_obj:
            flash("Requested filter could not be found", "warning")
            return form

        if filter_obj.get("lock"):
            filter_obj = store.unlock_filter(filter_id, current_user.email)
        else:
            filter_obj = store.lock_filter(filter_id, current_user.email)

        if filter_obj is not None:
            form = FiltersFormClass(request_form)
        else:
            flash("Requested filter lock could not be toggled", "warning")
            form = FiltersFormClass(request_form)

    if bool(request_form.get("audit_filter")):
        filter_id = request_form.get("filters")
        audit_for = dict(
            category=category, variant_type=request_form.get("variant_type", "clinical")
        )
        link: str = url_for(
            VARIANTS_TARGET_FROM_CATEGORY.get(category),
            case_name=case_obj.get("display_name"),
            institute_id=institute_obj.get("_id"),
            **audit_for,
        )
        filter_obj = store.audit_filter(
            filter_id=filter_id,
            institute_obj=institute_obj,
            case_obj=case_obj,
            user_obj=user_obj,
            category=category,
            link=link,
        )
        if filter_obj is not None:
            filter_obj = store.retrieve_filter(filter_id)
            form = FiltersFormClass(MultiDict(filter_obj))
        else:
            flash("Requested filter could not be audited.", "warning")
            form = FiltersFormClass(request_form)

    if bool(request_form.get("save_filter")):
        # The form should be applied and remain set the page after saving
        form = FiltersFormClass(request_form)
        # Stash the filter to db to make available for this institute
        filter_obj = request_form
        store.stash_filter(filter_obj, institute_obj, case_obj, user_obj, category)

    if bool(request_form.get("load_filter")):
        filter_id = request_form.get("filters")
        filter_obj = store.retrieve_filter(filter_id)
        if filter_obj is not None:

            def _coerce_formdata(filter: dict) -> MultiDict:
                """According to wtforms docs https://wtforms.readthedocs.io/en/3.1.x/forms/#the-form-class,
                formdata passed to Form init needs to be pre-coerced to types. Hence especially the replacement
                of locale specific chars in numbers on class process_formdata would not be enough for the
                better_decimal form fields.

                Check all filters in the current FiltersFormClass by making an instance, finding any BetterDecimalField
                or DecimalFields. Replace "," with "." in any string value, and check that the remaining string will
                convert to a number before finally instantiating the form with values.
                """

                test_form = FiltersFormClass()
                for decimal_value_form_field in dir(FiltersFormClass):
                    if decimal_value_form_field not in filter:
                        continue

                    if not isinstance(
                        test_form[decimal_value_form_field],
                        (BetterDecimalField, DecimalField),
                    ):
                        continue

                    if type(filter[decimal_value_form_field][0]) is not str:
                        continue

                    target_value = filter[decimal_value_form_field][0].replace(",", ".")
                    if not target_value.replace(".", "", 1).isnumeric():
                        flash(
                            f"Requested filter field {decimal_value_form_field} not numeric",
                            "warning",
                        )
                        del filter[decimal_value_form_field]
                        continue

                    raw_value = decimal.Decimal(target_value)
                    filter[decimal_value_form_field] = [raw_value]

                return MultiDict(filter)

            form = FiltersFormClass(_coerce_formdata(filter_obj))
        else:
            flash("Requested filter was not found", "warning")

    if bool(request_form.get("delete_filter")):
        filter_id = request_form.get("filters")
        institute_id = institute_obj.get("_id")
        filter_obj = store.delete_filter(filter_id, institute_id, current_user.email)
        if filter_obj is not None:
            form = FiltersFormClass(request_form)
        else:
            flash("Requested filter was locked or not found", "warning")

    if form is None:
        form = FiltersFormClass(request_form)

    return form


def case_default_panels(case_obj):
    """Get a list of case default panels from a case dictionary

    Args:
        case_obj(dict): a case object

    Returns:
        case_panels(list): a list of panels (panel_name)
    """
    case_panels = [
        panel["panel_name"]
        for panel in case_obj.get("panels", [])
        if panel.get("is_default", None) is True
    ]
    return case_panels


def populate_sv_filters_form(store, institute_obj, case_obj, category, request_obj):
    """Populate a filters form object of the type SvFiltersForm

    Accepts:
        store(adapter.MongoAdapter)
        institute_obj(dict)
        case_obj(dict)
        category(str)
        request_obj(Flask.requests obj)

    Returns:
        form(SvFiltersForm)
    """

    form = SvFiltersForm(request_obj.args)
    user_obj = store.user(current_user.email)

    if request_obj.method == "GET":
        if category == "sv":
            form = SvFiltersForm(request_obj.args)
        elif category == "cancer_sv":
            form = CancerSvFiltersForm(request_obj.args)
        variant_type = request_obj.args.get("variant_type", "clinical")
        form.variant_type.data = variant_type
        # set chromosome to all chromosomes
        form.chrom.data = request_obj.args.get("chrom", "")
        if form.gene_panels.data == [] and variant_type == "clinical":
            form.gene_panels.data = case_default_panels(case_obj)

    else:  # POST
        form = populate_filters_form(
            store, institute_obj, case_obj, user_obj, category, request_obj.form
        )

    populate_force_show_unaffected_vars(institute_obj, form)

    # populate available panel choices
    form.gene_panels.choices = gene_panel_choices(store, institute_obj, case_obj)

    return form


def populate_fusion_filters_form(store, institute_obj, case_obj, category, request_obj):
    """Populate a filters form object of the type FusionFiltersForm

    Accepts:
        store(adapter.MongoAdapter)
        institute_obj(dict)
        case_obj(dict)
        category(str)
        request_obj(Flask.requests obj)

    Returns:
        form(FusionFiltersForm)
    """

    form = FusionFiltersForm(request_obj.args)
    user_obj = store.user(current_user.email)

    if request_obj.method == "GET":
        if category == "fusion":
            form = FusionFiltersForm(request_obj.args)
        variant_type = request_obj.args.get("variant_type", "clinical")
        form.variant_type.data = variant_type
        # set chromosome to all chromosomes
        form.chrom.data = request_obj.args.get("chrom", "")
        if form.gene_panels.data == [] and variant_type == "clinical":
            form.gene_panels.data = case_default_panels(case_obj)

    else:  # POST
        form = populate_filters_form(
            store, institute_obj, case_obj, user_obj, category, request_obj.form
        )

    populate_force_show_unaffected_vars(institute_obj, form)

    # populate available panel choices
    form.gene_panels.choices = gene_panel_choices(store, institute_obj, case_obj)

    return form


def _flash_gene_symbol_errors(
    non_clinical_symbols, not_found_symbols, not_found_ids, outdated_symbols, aliased_symbols
):
    """Flash error messages to make user aware that submitted gene symbols could not be directly used in variants search
    Args:
        non_clinical_symbols(set)
        not_found_symbols(set)
        not_found_ids(set)
        not_found_ids(set)
        outdated_symbols(set)
        aliased_symbols(set)
    """

    errors = {
        "non_clinical_symbols": {
            "message": "Genes not included in gene panel versions in use when loading this case (clinical list)",
            "gene_list": non_clinical_symbols,
            "label": "info",
        },
        "not_found_symbols": {
            "message": "HGNC symbols not present in database's genes collection",
            "gene_list": not_found_symbols,
            "label": "warning",
        },
        "not_found_ids": {
            "message": "HGNC ids not present in database's genes collection",
            "gene_list": not_found_ids,
            "label": "warning",
        },
        "outdated_symbols": {
            "message": "Outdated gene symbols found in the clinical panels loaded for the analysis.",
            "gene_list": outdated_symbols,
            "label": "info",
        },
        "aliased_symbols": {
            "message": "Outdated gene symbols found in the search - alias used.",
            "gene_list": aliased_symbols,
            "label": "info",
        },
    }

    # warn user if gene symbols are corresponding to any current gene,
    for error in errors.values():
        if not error["gene_list"]:
            continue
        flash(f'{error["message"]}:{error["gene_list"]}', error["label"])


def check_form_gene_symbols(
    store, case_obj, is_clinical, genome_build, hgnc_symbols, not_found_ids
):
    """Check that gene symbols provided by user exist and are up to date.
       Flash a warning if gene is not found, gene symbol present in panel is outdated
       or is not found in clinical list when search is performed on clinical variants

     Args:
        store(adapter.MongoAdapter)
        case_obj(dict)
        is_clinical(bool): type of variants (clinical, research)
        genome_build(str): "37" or "38"
        hgnc_symbols(list): list of gene symbols (strings)
        not_found_ids(list): list of HGNC IDs not found if user provided numberical HGNC IDs in search form

    Returns:
        updated_hgnc_symbols(list): List of gene symbols that are found in database and are up to date
    """
    non_clinical_symbols = set()
    not_found_symbols = set()
    outdated_symbols = set()
    aliased_symbols = set()
    updated_hgnc_symbols = set()

    clinical_hgnc_ids = store.clinical_hgnc_ids(case_obj) if case_obj else []
    clinical_symbols = store.clinical_symbols(case_obj) if case_obj else []

    # if no clinical symbols / panels were found loaded, warnings are treated as with research
    if len(clinical_hgnc_ids) == 0 and len(clinical_symbols) == 0:
        is_clinical = False

    for hgnc_symbol in hgnc_symbols:
        # Retrieve a gene with "hgnc_symbol" as hgnc symbol or a list of genes where hgnc_symbol is among the aliases
        hgnc_genes = store.gene_by_symbol_or_aliases(symbol=hgnc_symbol, build=genome_build)

        if (
            isinstance(hgnc_genes, list) is False
        ):  # Gene was not found using provided symbol, aliases were returned
            hgnc_genes = list(hgnc_genes)
            if hgnc_genes:
                aliased_symbols.add(hgnc_symbol)

        if not hgnc_genes:
            not_found_symbols.add(hgnc_symbol)
            continue

        for hgnc_gene in hgnc_genes:
            gene_symbol = hgnc_gene.get("hgnc_symbol")

            # collect queried symbols for both clinical variants and research variants
            if hgnc_gene["hgnc_id"] in clinical_hgnc_ids or is_clinical is False:
                updated_hgnc_symbols.add(gene_symbol)

                # research variants
                if is_clinical is False:
                    continue

                # warn if queried symbol or corresponding gene symbol in panel is outdated
                if hgnc_symbol not in clinical_symbols:
                    outdated_symbols.add(hgnc_symbol)

            else:
                non_clinical_symbols.add(gene_symbol)

    _flash_gene_symbol_errors(
        non_clinical_symbols, not_found_symbols, not_found_ids, outdated_symbols, aliased_symbols
    )

    return updated_hgnc_symbols


def update_form_hgnc_symbols(store, case_obj, form):
    """Update variants filter form with HGNC symbols from HPO, and check if any non-clinical genes for the case were
    requested. If so, flash a warning to the user.

    Accepts:
        store(adapter.MongoAdapter)
        case_obj(dict)
        form(FiltersForm)

    Returns:
        form(FiltersForm)
    """

    hgnc_symbols = []
    not_found_ids = []
    genome_build = None
    case_obj = case_obj or {}

    for build in ["37", "38"]:
        if build in str(case_obj.get("genome_build", "")):
            genome_build = build
            break

    # retrieve current symbols from form
    if form.hgnc_symbols.data:
        # if symbols are numeric HGNC id, translate to current symbols
        for hgnc_symbol in form.hgnc_symbols.data:
            if hgnc_symbol.isdigit():
                hgnc_gene_caption = store.hgnc_gene_caption(int(hgnc_symbol), genome_build)
                if hgnc_gene_caption is None:
                    not_found_ids.append(hgnc_symbol)
                    continue
                hgnc_symbols.append(hgnc_gene_caption.get("hgnc_symbol", hgnc_symbol))
                continue

            hgnc_symbols.append(hgnc_symbol)

    # add HPO genes to list, if they were missing
    if "hpo" in form.data.get("gene_panels", []):
        hpo_symbols = list(
            set(term_obj["hgnc_symbol"] for term_obj in case_obj.get("dynamic_gene_list", []))
        )

        current_symbols = set(hgnc_symbols)
        current_symbols.update(hpo_symbols)

        hgnc_symbols = list(current_symbols)

    # check if supplied gene symbols exist and are clinical
    is_clinical = form.data.get("variant_type", "clinical") == "clinical"

    updated_hgnc_symbols = check_form_gene_symbols(
        store, case_obj, is_clinical, genome_build, hgnc_symbols, not_found_ids
    )
    form.hgnc_symbols.data = sorted(updated_hgnc_symbols)
    return form


def activate_case(store, institute_obj, case_obj, current_user):
    """Activate case when visited for the first time.

    Args:
        store(adapter.MongoAdapter)
        institute_obj(dict) a scout institutet object
        case_obj(dict) a scout case object
        current_user(UserMixin): a scout user
    """

    # update status of case if visited for the first time
    if case_obj["status"] == "inactive" and not current_user.is_admin:
        flash("You just activated this case!", "info")

        user_obj = store.user(current_user.email)
        case_link = url_for(
            "cases.case",
            institute_id=institute_obj["_id"],
            case_name=case_obj["display_name"],
        )
        store.update_status(institute_obj, case_obj, user_obj, "active", case_link)


def reset_all_dimissed(store, institute_obj, case_obj):
    """Reset all dismissed variants for a case.

    Args:
        store(adapter.MongoAdapter)
        institute_obj(dict): an institute dictionary
        case_obj(dict): a case dictionary
    """
    evaluated_vars = store.evaluated_variants(
        case_id=case_obj["_id"], institute_id=case_obj["owner"]
    )
    user_obj = store.user(current_user.email)
    # Create an associated case-level event
    link = url_for(
        "cases.case",
        institute_id=institute_obj["_id"],
        case_name=case_obj["display_name"],
    )
    store.order_dismissed_variants_reset(institute_obj, case_obj, user_obj, link)

    # Reset dismissed for each single dismissed variant
    for variant in evaluated_vars:
        if not variant.get("dismiss_variant"):  # not a dismissed variant
            continue
        link_page = (
            "variant.sv_variant"
            if variant.get("category") in ("sv", "cancer_sv")
            else "variant.variant"
        )
        link = url_for(
            link_page,
            institute_id=institute_obj["_id"],
            case_name=case_obj["display_name"],
            variant_id=variant["_id"],
        )
        store.update_dismiss_variant(institute_obj, case_obj, user_obj, link, variant, [])


def dismiss_variant_list(store, institute_obj, case_obj, link_page, variants_list, dismiss_reasons):
    """Dismiss a list of variants for a case

    Args:
        store(adapter.MongoAdapter)
        institute_obj(dict): an institute dictionary
        case_obj(dict): a case dictionary
        link_page(str): "variant.variant" for snvs, "variant.sv_variant" for SVs and so on
        variants_list(list): list of variant._ids (strings)
        dismiss_reasons(list): list of dismiss options.
    """
    user_obj = store.user(current_user.email)
    for variant_id in variants_list:
        variant_obj = store.variant(variant_id)
        if variant_obj is None:
            continue
        # create variant link
        link = url_for(
            link_page,
            institute_id=institute_obj["_id"],
            case_name=case_obj["display_name"],
            variant_id=variant_id,
        )
        # dismiss variant
        store.update_dismiss_variant(
            institute_obj, case_obj, user_obj, link, variant_obj, dismiss_reasons
        )


def get_show_dismiss_block():
    """Return the contents of this user session show dismiss block setting.
    The first time around it may be undefined / None, and in that case we set it to True
    to default to showing the dismiss bar.
    """

    show_dismiss_block = session.get("show_dismiss_block")
    if show_dismiss_block is None:
        show_dismiss_block = True
        session["show_dismiss_block"] = show_dismiss_block

    return show_dismiss_block
