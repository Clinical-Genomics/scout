import logging
import os
from typing import Dict, List, Optional

import requests
from flask import Markup, abort, current_app, flash, url_for
from flask_login import current_user

from scout.adapter import MongoAdapter
from scout.constants import (
    ACMG_COMPLETE_MAP,
    ACMG_CRITERIA,
    ACMG_MAP,
    ACMG_OPTIONS,
    CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
    CANCER_TIER_OPTIONS,
    CASE_TAGS,
    DISMISS_VARIANT_OPTIONS,
    IGV_TRACKS,
    INHERITANCE_PALETTE,
    MANUAL_RANK_OPTIONS,
    MOSAICISM_OPTIONS,
    VERBS_MAP,
)
from scout.server.blueprints.variant.utils import (
    update_representative_gene,
    update_variant_case_panels,
)
from scout.server.blueprints.variants.utils import update_case_panels
from scout.server.extensions import LoqusDB, cloud_tracks, gens
from scout.server.links import disease_link, get_variant_links
from scout.server.utils import (
    case_has_alignments,
    case_has_mt_alignments,
    case_has_rna_tracks,
    user_institutes,
    variant_institute_and_case,
)

from .utils import (
    add_gene_info,
    associate_variant_genes_with_case_panels,
    callers,
    clinsig_human,
    default_panels,
    end_position,
    evaluation,
    frequencies,
    frequency,
    is_affected,
    predictions,
)

LOG = logging.getLogger(__name__)


def tx_overview(variant_obj: dict):
    """Prepares the content of the transcript overview to be shown on variant and general report pages.
       Basically show transcripts that contain RefSeq or are canonical.

    Args:
        variant_obj(dict)
    """
    overview_txs = []  # transcripts to be shown in transcripts overview
    if variant_obj.get("genes") is None:
        variant_obj["overview_transcripts"] = []
        return
    for gene in variant_obj.get("genes", []):
        for tx in gene.get("transcripts", []):
            ovw_tx = {}

            if "refseq_identifiers" not in tx and tx.get("is_canonical", False) is False:
                continue  # collect only RefSeq or canonical transcripts

            # ---- create content for the gene column -----#
            ovw_tx["hgnc_symbol"] = (
                gene["common"].get("hgnc_symbol", gene.get("hgnc_id"))
                if gene.get("common")
                else gene.get("hgnc_id")
            )
            ovw_tx["hgnc_id"] = gene.get("hgnc_id")

            # ---- create content for the Refseq IDs column -----#
            ovw_tx["mane"] = tx.get("mane_select_transcript", "")
            ovw_tx["mane_plus"] = tx.get("mane_plus_clinical_transcript", "")

            ovw_tx["decorated_refseq_ids"] = []
            ovw_tx["muted_refseq_ids"] = []

            for refseq_id in tx.get("refseq_identifiers", []):
                decorated_tx = None
                if ovw_tx["mane"] and ovw_tx["mane"].startswith(refseq_id):
                    decorated_tx = ovw_tx["mane"]
                elif ovw_tx["mane_plus"] and ovw_tx["mane_plus"].startswith(refseq_id):
                    decorated_tx = ovw_tx["mane_plus"]
                elif refseq_id.startswith("XM"):
                    ovw_tx["muted_refseq_ids"].append(refseq_id)
                    continue
                else:
                    decorated_tx = refseq_id
                ovw_tx["decorated_refseq_ids"].append(decorated_tx)

            # ---- create content for ID column -----#
            ovw_tx["transcript_id"] = tx.get("transcript_id")
            ovw_tx["is_primary"] = (
                True
                if tx.get("refseq_id") in gene.get("common", {}).get("primary_transcripts", [])
                else False
            )
            ovw_tx["is_canonical"] = tx.get("is_canonical")

            # ---- create content for HGVS description column -----#
            ovw_tx["coding_sequence_name"] = tx.get("coding_sequence_name")
            ovw_tx["protein_sequence_name"] = tx.get("protein_sequence_name")

            # ---- create content for links column -----#
            ovw_tx["varsome_link"] = tx.get("varsome_link")
            ovw_tx["mutalyzer_link"] = tx.get("mutalyzer_link")
            ovw_tx["tp53_link"] = tx.get("tp53_link")
            ovw_tx["cbioportal_link"] = tx.get("cbioportal_link")
            ovw_tx["mycancergenome_link"] = tx.get("mycancergenome_link")

            overview_txs.append(ovw_tx)

    # sort txs for the presence of "mane_select_transcript" and "mane_plus_clinical_transcript"
    variant_obj["overview_transcripts"] = sorted(
        overview_txs, key=lambda tx: (tx["mane"], tx["mane_plus"]), reverse=True
    )


def get_igv_tracks(build: str = "37") -> set:
    """Return all available IGV tracks for the given genome build, as a set

    Args:
        build(str): "37" or "38"

    Returns:
        igv_tracks(set): A set of track names for a given genome build
    """
    igv_tracks = set()
    # Collect hardcoded tracks, common for all Scout instances
    for track in IGV_TRACKS.get(build, []):
        igv_tracks.add(track.get("name"))
    # Collect instance-specif cloud public tracks, if available
    if hasattr(cloud_tracks, "public_tracks"):
        for track in cloud_tracks.public_tracks.get(build, []):
            igv_tracks.add(track.get("name"))
    return igv_tracks


def variant(
    store: MongoAdapter,
    variant_id: Optional[str],
    institute_id: str = None,
    case_name: str = None,
    variant_obj: dict = None,
    add_other: bool = True,
    get_overlapping: bool = True,
    variant_type: str = None,
    case_obj: dict = None,
    institute_obj: dict = None,
) -> Optional[dict]:
    """Pre-process a single variant for the detailed variant view.

    Adds information from case and institute that is not present on the variant
    object

    Args:
        store(scout.adapter.MongoAdapter)
        institute_id(str)
        case_name(str)
        variant_id(str)
        variant_obj(dict)
        add_other(bool): If information about other causatives should be added
        get_overlapping(bool): If overlapping variants should be collected
        variant_type(str): in ["clinical", "research"]
        institute_obj(scout.models.Institute)
        case_obj(scout.models.Case)

    Returns:
        variant_info(dict): {
            'variant': <variant_obj>,
            'causatives': <list(other_causatives)>,
            'events': <list(events)>,
            'overlapping_svs': <list(overlapping svs)>,
            'manual_rank_options': MANUAL_RANK_OPTIONS,
            'cancer_tier_options': CANCER_TIER_OPTIONS,
            'dismiss_variant_options': DISMISS_VARIANT_OPTIONS,
            'ACMG_OPTIONS': ACMG_OPTIONS,
            'igv_tracks': IGV_TRACKS,
            'gens_info': <dict>,
            'evaluations': <list(evaluations)>,
            'rank_score_results': <list(rank_score_results)>,
        }

    """

    # If the variant is already collected we skip this part
    if not variant_obj:
        # NOTE this will query with variant_id == document_id, not the variant_id.
        variant_obj = store.variant(variant_id)

    if not variant_obj:
        return abort(404)

    if not (institute_obj and case_obj):
        (institute_obj, case_obj) = variant_institute_and_case(
            store, variant_obj, institute_id, case_name
        )

    variant_type = variant_type or variant_obj.get("variant_type", "clinical")

    # request category specific variant display
    variant_category = variant_obj.get("category", "snv")
    LOG.debug("Variant category {}".format(variant_category))

    variant_id = variant_obj["variant_id"]

    genome_build = str(case_obj.get("genome_build", "37"))
    if genome_build not in ["37", "38"]:
        genome_build = "37"

    # is variant located on the mitochondria
    variant_obj["is_mitochondrial"] = any(
        [
            (genome_build == "38" and variant_obj["chromosome"] == "M"),
            (genome_build == "37" and variant_obj["chromosome"] == "MT"),
        ]
    )

    # add default panels extra gene information
    panels = default_panels(store, case_obj)

    add_gene_info(store, variant_obj, gene_panels=panels, genome_build=genome_build)

    # Update some case panels info from db and populate it on variant to avoid showing removed panels
    update_case_panels(store, case_obj)
    # The hierarchical call order is relevant: cases are used to populate variants
    update_variant_case_panels(case_obj, variant_obj)

    associate_variant_genes_with_case_panels(store, variant_obj)

    # Provide basic info on alignment files availability for this case
    case_has_alignments(case_obj)
    case_has_mt_alignments(case_obj)

    # Collect all the events for the variant
    events = list(store.events(institute_obj, case=case_obj, variant_id=variant_id))
    for event in events:
        event["verb"] = VERBS_MAP.get(event["verb"], "did %s for".format(event["verb"]))

    # Comments are not on case level so these needs to be fetched on their own
    variant_obj["comments"] = store.events(
        institute_obj, case=case_obj, variant_id=variant_id, comments=True
    )

    # Adds information about other causative variants
    other_causatives = []
    if add_other:
        other_causatives = [
            causative for causative in store.other_causatives(case_obj, variant_obj)
        ]

    managed_variant = store.find_managed_variant_id(variant_obj["variant_id"])

    if variant_obj.get("category") == "cancer":
        variant_obj["matching_tiered"] = store.matching_tiered(
            variant_obj, user_institutes(store, current_user)
        )

    variant_obj["matching_ranked"] = store.get_matching_manual_ranked_variants(
        variant_obj,
        user_institutes(store, current_user),
        exclude_cases=[case_obj["_id"]],
    )

    # Gather display information for the genes
    variant_obj.update(predictions(variant_obj.get("genes", [])))

    # Prepare classification information for visualisation
    classification = variant_obj.get("acmg_classification")
    if isinstance(classification, int):
        acmg_code = ACMG_MAP[variant_obj["acmg_classification"]]
        variant_obj["acmg_classification"] = ACMG_COMPLETE_MAP[acmg_code]

    # sort compounds on combined rank score
    compounds = variant_obj.get("compounds", [])
    if compounds:
        # Gather display information for the compounds
        for compound_obj in compounds:
            compound_obj.update(predictions(compound_obj.get("genes", [])))

        variant_obj["compounds"] = sorted(
            variant_obj["compounds"], key=lambda compound: -compound["combined_score"]
        )

    variant_obj["end_position"] = end_position(variant_obj)

    # Add general variant links
    variant_obj.update(get_variant_links(institute_obj, variant_obj, int(genome_build)))
    variant_obj["frequencies"] = frequencies(variant_obj)
    if variant_category in ["snv", "cancer", "mei"]:
        # This is to convert a summary of frequencies to a string
        variant_obj["frequency"] = frequency(variant_obj)
    # Format clinvar information
    variant_obj["clinsig_human"] = clinsig_human(variant_obj) if variant_obj.get("clnsig") else None

    variant_genes = variant_obj.get("genes", [])
    update_representative_gene(variant_obj, variant_genes)

    # Add display information about callers
    variant_obj["callers"] = callers(variant_obj)

    # Convert affection status to strings for the template
    is_affected(variant_obj, case_obj)

    if variant_obj.get("genetic_models"):
        variant_models = set(model.split("_", 1)[0] for model in variant_obj["genetic_models"])
        omim_models = variant_obj.get("omim_models", set())
        variant_obj["is_matching_inheritance"] = set.intersection(variant_models, omim_models)

    # Prepare classification information for visualisation
    classification = variant_obj.get("acmg_classification")
    if isinstance(classification, int):
        acmg_code = ACMG_MAP[variant_obj["acmg_classification"]]
        variant_obj["acmg_classification"] = ACMG_COMPLETE_MAP[acmg_code]

    evaluations = []
    for evaluation_obj in store.get_evaluations(variant_obj):
        evaluation(store, evaluation_obj)
        evaluations.append(evaluation_obj)

    case_clinvars = store.case_to_clinVars(case_obj.get("display_name"))

    if variant_id in case_clinvars:
        variant_obj["clinvar_clinsig"] = case_clinvars.get(variant_id)["clinsig"]

    overlapping_vars = []
    if get_overlapping:
        for var in store.overlapping(variant_obj):
            var.update(predictions(var.get("genes", [])))
            overlapping_vars.append(var)
    variant_obj["end_chrom"] = variant_obj.get("end_chrom", variant_obj["chromosome"])

    dismiss_options = DISMISS_VARIANT_OPTIONS
    if case_obj.get("track") == "cancer":
        dismiss_options = {
            **DISMISS_VARIANT_OPTIONS,
            **CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
        }

    for gene in variant_obj.get("genes", []):
        for disease in gene.get("disease_terms", []):
            disease["disease_link"] = disease_link(disease_id=disease["_id"])

    tx_overview(variant_obj)

    return {
        "institute": institute_obj,
        "case": case_obj,
        "variant": variant_obj,
        variant_category: True,
        "causatives": other_causatives,
        "managed_variant": managed_variant,
        "events": events,
        "overlapping_vars": overlapping_vars,
        "manual_rank_options": MANUAL_RANK_OPTIONS,
        "cancer_tier_options": CANCER_TIER_OPTIONS,
        "dismiss_variant_options": dismiss_options,
        "mosaic_variant_options": MOSAICISM_OPTIONS,
        "ACMG_OPTIONS": ACMG_OPTIONS,
        "case_tag_options": CASE_TAGS,
        "inherit_palette": INHERITANCE_PALETTE,
        "igv_tracks": get_igv_tracks(genome_build),
        "has_rna_tracks": case_has_rna_tracks(case_obj),
        "gens_info": gens.connection_settings(genome_build),
        "evaluations": evaluations,
        "rank_score_results": variant_rank_scores(store, case_obj, variant_obj),
    }


def variant_rank_scores(store: MongoAdapter, case_obj: dict, variant_obj: dict) -> list:
    """Retrive rank score values and ranges for the variant

    Args:
        store(scout.adapter.MongoAdapter)
        case_obj(dict)
        variant_obj(dict)

    Returns:
        rank_score_results(list)
    """
    rank_score_results = []

    if variant_obj.get(
        "rank_score_results"
    ):  # Retrieve rank score results saved in variant document
        rank_score_results = variant_obj.get("rank_score_results")

    if variant_obj.get("category") == "sv":
        rank_model_version = case_obj.get("sv_rank_model_version")
        rm_link_prefix = current_app.config.get("SV_RANK_MODEL_LINK_PREFIX")
        rm_file_extension = current_app.config.get("SV_RANK_MODEL_LINK_POSTFIX")
    else:  # snv, cancer
        rank_model_version = case_obj.get("rank_model_version")
        rm_link_prefix = current_app.config.get("RANK_MODEL_LINK_PREFIX")
        rm_file_extension = current_app.config.get("RANK_MODEL_LINK_POSTFIX")
    if all(
        [rank_model_version, rm_link_prefix, rm_file_extension]
    ):  # Try to retrieve rank model param ranges to display on variant page
        rank_model = store.rank_model_from_url(
            rm_link_prefix, rank_model_version, rm_file_extension
        )
        # Loop over each rank score category and collect model explanation to display on variant page
        if rank_model:
            for score in rank_score_results:
                category = score.get("category")  # examples: Splicing, Consequence, Deleteriousness
                score["model_ranges"] = store.get_ranges_info(rank_model, category)
                (score["min"], score["max"]) = store.range_span(score["model_ranges"])

    return rank_score_results


def get_loqusdb_obs_cases(
    store: MongoAdapter, variant_obj: dict, category: str, obs_families: list = []
) -> List[dict]:
    """Get a list of cases where variant observations occurred. These are only the cases the user has access to.
    We need to add links to the variant in other cases where the variant has been observed.
    First we need to make sure that the user has access to these cases. The user_institute_ids holds
    information about what institutes the user has access to.
    """
    obs_cases = []
    user_institutes_ids = set([inst["_id"] for inst in user_institutes(store, current_user)])
    for i, case_id in enumerate(obs_families):
        if len(obs_cases) == 10:
            break
        if case_id == variant_obj["case_id"]:
            continue
        # other case might belong to same institute, collaborators or other institutes
        other_case = store.case(case_id)
        if not other_case:
            # Case could have been removed
            LOG.debug("Case %s could not be found in database", case_id)
            continue
        other_institutes = set([other_case.get("owner")])
        other_institutes.update(set(other_case.get("collaborators", [])))

        if user_institutes_ids.isdisjoint(other_institutes):
            # If the user does not have access to the information we skip it. Admins allowed by user_institutes.
            continue

        other_variant = store.variant(
            case_id=other_case["_id"], document_id=variant_obj["variant_id"]
        )

        # IF variant is SV variant, look for variants with different sub_category occurring at the same coordinates
        if other_variant is None and category == "sv":
            other_variant = store.overlapping_sv_variant(other_case["_id"], variant_obj)

        obs_cases.append(dict(case=other_case, variant=other_variant))

    return obs_cases


def observations(store: MongoAdapter, loqusdb: LoqusDB, variant_obj: dict) -> Dict[str, dict]:
    """Check if variant_obj have been observed before in the loqusdb instances available in the institute settings.
    If not return empty dictionary.
    """
    obs_data = {}
    institute_id = variant_obj["institute"]
    institute_obj = store.institute(institute_id)

    inst_loqus_ids = institute_obj.get("loqusdb_id", [])

    # institute_obj.get("loqusdb_id") was a string initially because only one instance of loqus could be associated to a institute
    if isinstance(inst_loqus_ids, str):
        inst_loqus_ids = [inst_loqus_ids]

    # Compose variant query to submit to one or more loqusdb instances
    category = variant_obj["category"]
    if category == "cancer":
        category = "snv"
    if category == "cancer_sv":
        category = "sv"
    loqus_query = loqusdb.get_loqus_query(variant_obj, category)

    for loqus_id in inst_loqus_ids:  # Loop over all loqusdb instances of an institute
        obs_data[loqus_id] = {}
        loqus_settings = loqusdb.loqusdb_settings.get(loqus_id)

        if loqus_settings is None:  # An instance might have been renamed or removed
            flash(
                f"Could not connect to the preselected loqusdb '{loqus_id}' instance",
                "warning",
            )
            obs_data[loqus_id]["total"] = "N/A"
            continue
        obs_data[loqus_id] = loqusdb.get_variant(
            loqus_query, loqusdb_id=loqus_id
        )  # collect observation on that loqus instance

        if not obs_data[loqus_id]:  # data is an empty dictionary
            # Collect count of variants in variant's case
            obs_data[loqus_id] = loqusdb.get_variant(loqus_query, loqusdb_id=loqus_id)
            if obs_data[loqus_id].get("total"):
                obs_data[loqus_id]["observations"] = 0
            continue

        # collect cases where observations occurred
        obs_data[loqus_id]["cases"] = get_loqusdb_obs_cases(
            store, variant_obj, category, obs_data[loqus_id].get("families", [])
        )

    return obs_data


def str_variant_reviewer(
    store: MongoAdapter,
    case_obj: dict,
    variant_id: str,
) -> dict:
    """Controller populating data and calling REViewer Service to fetch svg.
    Returns:
        data(dict): {"individuals": list(dict())}}
            individual dicts being dict with keys:
                svg(str): image Markup text
                display_name(str): display name
                individual_id(str): internal id
    """

    variant_obj = store.variant(variant_id)

    str_repid = variant_obj.get("str_repid")
    print("str_variants_reviewer", str_repid)

    url = current_app.config.get("SCOUT_REVIEWER_URL")

    display_individuals = []
    for ind in case_obj.get("individuals"):
        display_individual = {
            "display_name": ind.get("display_name"),
            "individual_id": ind.get("individual_id"),
        }

        ind_reviewer = ind.get("reviewer")
        if not url or not str_repid or not ind_reviewer:
            display_individual["svg"] = Markup("<SVG></SVG>")
            display_individuals.append(display_individual)
            continue

        srs_query_data = {
            "reads": ind_reviewer.get("alignment"),
            "vcf": ind_reviewer.get("vcf"),
            "catalog": ind_reviewer.get("catalog"),
            "locus": str_repid,
        }

        if ind_reviewer.get("alignment_index"):
            srs_query_data["reads_index"] = ind_reviewer.get("alignment_index")
        elif os.path.exists(ind_reviewer.get("alignment") + ".bai"):
            srs_query_data["reads_index"] = f"{ind_reviewer.get('alignment')}.bai"

        try:
            resp = requests.post(url, json=srs_query_data)
            display_individual["svg"] = Markup(resp.text)
        except Exception as err:
            flash(f"An error occurred while connecting to Scout-REViewer-Service: {err}")
            display_individual["svg"] = Markup("<SVG></SVG>")

        display_individuals.append(display_individual)

    return {
        "individuals": display_individuals,
        "str_repid": str_repid,
    }


def variant_acmg(store: MongoAdapter, institute_id: str, case_name: str, variant_id: str):
    """Collect data relevant for rendering ACMG classification form.

    Args:
        store(scout.adapter.MongoAdapter)
        institute_id(str): institute_obj['_id']
        case_name(str): case_obj['display_name']
        variant_id(str): variant_obj['document_id']

    Returns:
        data(dict): Things for the template
    """
    variant_obj = store.variant(variant_id)

    if not variant_obj:
        return abort(404)

    institute_obj, case_obj = variant_institute_and_case(
        store, variant_obj, institute_id, case_name
    )

    return dict(
        institute=institute_obj,
        case=case_obj,
        variant=variant_obj,
        CRITERIA=ACMG_CRITERIA,
        ACMG_OPTIONS=ACMG_OPTIONS,
    )


def check_reset_variant_classification(
    store: MongoAdapter, evaluation_obj: dict, link: str
) -> bool:
    """Check if this was the last ACMG evaluation left on the variant.
    If there is still a classification we want to remove the classification.

    Args:
            stores(cout.adapter.MongoAdapter)
            evaluation_obj(dict): ACMG evaluation object
            link(str): link for event

    Returns: reset(bool) - True if classification reset was attempted

    """

    if list(store.get_evaluations_case_specific(evaluation_obj["variant_specific"])):
        return False

    variant_obj = store.variant(document_id=evaluation_obj["variant_specific"])

    if not variant_obj:
        return abort(404)

    acmg_classification = variant_obj.get("acmg_classification")

    if not isinstance(acmg_classification, int):
        return False

    institute_obj, case_obj = variant_institute_and_case(
        store,
        variant_obj,
        evaluation_obj["institute"]["_id"],
        evaluation_obj["case"]["display_name"],
    )
    user_obj = store.user(current_user.email)

    new_acmg = None
    store.submit_evaluation(
        variant_obj=variant_obj,
        user_obj=user_obj,
        institute_obj=institute_obj,
        case_obj=case_obj,
        link=link,
        classification=new_acmg,
    )
    return True


def variant_acmg_post(
    store: MongoAdapter,
    institute_id: str,
    case_name: str,
    variant_id: str,
    user_email: str,
    criteria: list,
) -> dict:
    """Calculate an ACMG classification based on a list of criteria.

    Args:
        store(scout.adapter.MongoAdapter)
        institute_id(str): institute_obj['_id']
        case_name(str): case_obj['display_name']
        variant_id(str): variant_obj['document_id']
        user_mail(str)
        criteria()

    Returns:
        data(dict): Things for the template

    """
    variant_obj = store.variant(variant_id)

    if not variant_obj:
        return abort(404)

    institute_obj, case_obj = variant_institute_and_case(
        store, variant_obj, institute_id, case_name
    )

    user_obj = store.user(user_email)
    variant_link = url_for(
        "variant.variant",
        institute_id=institute_id,
        case_name=case_name,
        variant_id=variant_id,
    )
    classification = store.submit_evaluation(
        institute_obj=institute_obj,
        case_obj=case_obj,
        variant_obj=variant_obj,
        user_obj=user_obj,
        link=variant_link,
        criteria=criteria,
    )
    return classification
