import logging
from datetime import date

from flask import url_for
from flask_login import current_user

from scout.constants import (
    ACMG_COMPLETE_MAP,
    ACMG_CRITERIA,
    ACMG_MAP,
    ACMG_OPTIONS,
    CANCER_SPECIFIC_VARIANT_DISMISS_OPTIONS,
    CANCER_TIER_OPTIONS,
    CLINVAR_INHERITANCE_MODELS,
    DISMISS_VARIANT_OPTIONS,
    IGV_TRACKS,
    MANUAL_RANK_OPTIONS,
    MOSAICISM_OPTIONS,
    VERBS_MAP,
)
from scout.server.blueprints.variant.utils import update_representative_gene
from scout.server.extensions import cloud_tracks, gens
from scout.server.links import ensembl, get_variant_links
from scout.server.utils import (
    case_append_alignments,
    institute_and_case,
    user_institutes,
    variant_case,
)
from scout.utils.scout_requests import fetch_refseq_version

from .utils import (
    add_gene_info,
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


def tx_overview(variant_obj):
    """Prepares the content of the transcript overview to be shown on variant and general report pages.
       Basically show transcripts that contain RefSeq or are canonical.

    Args:
        variant_obj(dict)
    """
    overview_txs = []  # transcripts to be shown in transcripts overview
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
                elif ovw_tx["mane_plus"] and ovw_tx["mane_plus"].starstwith(refseq_id):
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
            ovw_tx["tp53_link"] = tx.get("tp53_link")
            ovw_tx["cbioportal_link"] = tx.get("cbioportal_link")
            ovw_tx["mycancergenome_link"] = tx.get("mycancergenome_link")

            overview_txs.append(ovw_tx)

    # sort txs for the presence of "mane_select_transcript" and "mane_plus_clinical_transcript"
    variant_obj["overview_transcripts"] = sorted(
        overview_txs, key=lambda tx: (tx["mane"], tx["mane_plus"]), reverse=True
    )


def has_rna_tracks(case_obj):
    """Returns True if one of more individuals of the case contain RNA-seq data

    Args:
        case_obj(dict)
    Returns
        True or False (bool)
    """
    # Display junctions track if available for any of the individuals
    for ind in case_obj.get("individuals", []):
        # Track contains 2 files and they should both be present
        if all([ind.get("splice_junctions_bed"), ind.get("rna_coverage_bigwig")]):
            return True
    return False


def get_igv_tracks(build="37"):
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
    store,
    institute_id,
    case_name,
    variant_id=None,
    variant_obj=None,
    add_case=True,
    add_other=True,
    get_overlapping=True,
    add_compounds=True,
    variant_category=None,
    variant_type=None,
    case_obj=None,
    institute_obj=None,
):
    """Pre-process a single variant for the detailed variant view.

    Adds information from case and institute that is not present on the variant
    object

    Args:
        store(scout.adapter.MongoAdapter)
        institute_id(str)
        case_name(str)
        variant_id(str)
        variant_obj(dict)
        add_case(bool): If info about files case should be added
        add_other(bool): If information about other causatives should be added
        get_overlapping(bool): If overlapping variants should be collected
        variant_type(str): in ["clinical", "research"]
        variant_category(str): ["snv", "str", "sv", "cancer", "cancer_sv"]
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
        }

    """
    if not (institute_obj and case_obj):
        institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    # If the variant is already collected we skip this part
    if not variant_obj:
        # NOTE this will query with variant_id == document_id, not the variant_id.
        variant_obj = store.variant(variant_id)

    if variant_obj is None:
        return None

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
    variant_obj = add_gene_info(store, variant_obj, gene_panels=panels, genome_build=genome_build)

    # Add information about bam files and create a region vcf
    if add_case:
        variant_case(store, case_obj, variant_obj)

    # Fetch ids for grouped cases and prepare alignment display
    case_groups = {}
    if case_obj.get("group"):
        for group in case_obj.get("group"):
            case_groups[group] = list(store.cases(group=group))
            for grouped_case in case_groups[group]:
                case_append_alignments(grouped_case)

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
    if variant_category in ["snv", "cancer"]:
        # This is to convert a summary of frequencies to a string
        variant_obj["frequency"] = frequency(variant_obj)
    # Format clinvar information
    variant_obj["clinsig_human"] = clinsig_human(variant_obj) if variant_obj.get("clnsig") else None

    variant_genes = variant_obj.get("genes", [])
    update_representative_gene(variant_obj, variant_genes)

    # Add display information about callers
    variant_obj["callers"] = callers(variant_obj, category=variant_category)

    # Convert affection status to strings for the template
    is_affected(variant_obj, case_obj)

    if variant_obj.get("genetic_models"):
        variant_models = set(model.split("_", 1)[0] for model in variant_obj["genetic_models"])
        all_models = variant_obj.get("all_models", set())
        variant_obj["is_matching_inheritance"] = set.intersection(variant_models, all_models)

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

    tx_overview(variant_obj)

    return {
        "institute": institute_obj,
        "case": case_obj,
        "case_groups": case_groups,
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
        "igv_tracks": get_igv_tracks(genome_build),
        "splice_junctions_tracks": has_rna_tracks(case_obj),
        "gens_info": gens.connection_settings(genome_build),
        "evaluations": evaluations,
    }


def observations(store, loqusdb, case_obj, variant_obj):
    """Query observations for a variant.

    Check if variant_obj have been observed before ni the loqusdb instance.
    If not return empty dictionary.

    We need to add links to the variant in other cases where the variant has been observed.
    First we need to make sure that the user has access to these cases. The user_institute_ids holds
    information about what institutes the user has access to.

    Loop over the case ids from loqusdb and check if they exist in the scout instance.
    Also make sure that we do not link to the observation that is the current variant.

    Args:
        store (scout.adapter.MongoAdapter)
        loqusdb (scout.server.extensions.LoqusDB)
        case_obj (scout.models.Case)
        variant_obj (scout.models.Variant)

    Returns:
        obs_data(dict)
    """
    chrom = variant_obj["chromosome"]
    end_chrom = variant_obj.get("end_chrom", chrom)
    pos = variant_obj["position"]
    end = variant_obj["end"]
    ref = variant_obj["reference"]
    alt = variant_obj["alternative"]
    var_case_id = variant_obj["case_id"]
    var_type = variant_obj.get("variant_type", "clinical")
    category = variant_obj["category"]
    if category == "cancer":
        category = "snv"
    if category == "cancer_sv":
        category = "sv"

    composite_id = "{0}_{1}_{2}_{3}".format(chrom, pos, ref, alt)
    variant_query = {
        "_id": composite_id,
        "chrom": chrom,
        "end_chrom": end_chrom,
        "pos": pos,
        "end": end,
        "length": variant_obj.get("length", 0),
        "variant_type": variant_obj.get("sub_category", "").upper(),
        "category": category,
    }

    institute_id = variant_obj["institute"]
    institute_obj = store.institute(institute_id)
    loqusdb_id = institute_obj.get("loqusdb_id") or "default"
    obs_data = loqusdb.get_variant(variant_query, loqusdb_id=loqusdb_id)

    if not obs_data:
        obs_data["total"] = loqusdb.case_count(variant_category=category, loqusdb_id=loqusdb_id)
        return obs_data

    user_institutes_ids = set([inst["_id"] for inst in user_institutes(store, current_user)])

    obs_data["cases"] = []
    for i, case_id in enumerate(obs_data.get("families", [])):
        if i > 10:
            break
        if case_id == var_case_id:
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
            # If the user does not have access to the information we skip it
            continue

        other_variant = store.variant(
            case_id=other_case["_id"], document_id=variant_obj["variant_id"]
        )

        # IF variant is SV variant, look for variants with different sub_category occurring at the same coordinates
        if other_variant is None and category == "sv":
            other_variant = store.overlapping_sv_variant(other_case["_id"], variant_obj)

        obs_data["cases"].append(dict(case=other_case, variant=other_variant))

    return obs_data


def variant_acmg(store, institute_id, case_name, variant_id):
    """Collect data relevant for rendering ACMG classification form.

    Args:
        store(scout.adapter.MongoAdapter)
        institute_id(str): institute_obj['_id']
        case_name(str): case_obj['display_name']
        variant_id(str): variant_obj['document_id']

    Returns:
        data(dict): Things for the template
    """
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    return dict(
        institute=institute_obj,
        case=case_obj,
        variant=variant_obj,
        CRITERIA=ACMG_CRITERIA,
        ACMG_OPTIONS=ACMG_OPTIONS,
    )


def variant_acmg_post(store, institute_id, case_name, variant_id, user_email, criteria):
    """Calculate an ACMG classification based on a list of criteria.

    Args:
        store(scout.adapter.MongoAdapter)
        institute_id(str): institute_obj['_id']
        case_name(str): case_obj['display_name']
        variant_id(str): variant_obj['document_id']
        user_mail(str)
        criteris()

    Returns:
        data(dict): Things for the template

    """
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
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


def clinvar_export(store, institute_id, case_name, variant_id):
    """Gather the required data for creating the clinvar submission form

    Args:
        store(scout.adapter.MongoAdapter)
        institute_id(str): Institute ID
        case_name(str): case ID
        variant_id(str): variant._id

    Returns:
        data(dict): all the required data (case and variant level) to pre-fill in fields
                    in the clinvar submission form

    """
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    pinned = [
        store.variant(variant_id) or variant_id for variant_id in case_obj.get("suspects", [])
    ]
    variant_obj = store.variant(variant_id)

    # gather missing transcript info from entrez (refseq id version)
    for pinned_var in pinned:
        # Exclude variants that aren't loaded
        if isinstance(pinned_var, str):
            continue
        for gene in pinned_var.get("genes", []):
            for transcript in gene.get("transcripts"):
                refseq_id = transcript.get("refseq_id")
                if not refseq_id:
                    continue
                transcript["refseq_id"] = fetch_refseq_version(refseq_id)

    return dict(
        today=str(date.today()),
        institute=institute_obj,
        case=case_obj,
        variant=variant_obj,
        pinned_vars=pinned,
        inheritance_models=CLINVAR_INHERITANCE_MODELS,
    )
