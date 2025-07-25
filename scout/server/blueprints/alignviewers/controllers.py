# -*- coding: utf-8 -*-
import logging
import os.path
from typing import Dict, List, Optional

from flask import flash, session
from flask_login import current_user

from scout.constants import CASE_SPECIFIC_TRACKS, HUMAN_REFERENCE, IGV_TRACKS
from scout.server.extensions import config_igv_tracks, store
from scout.server.utils import (
    case_append_alignments,
    find_index,
    get_case_genome_build,
)
from scout.utils.ensembl_rest_clients import EnsemblRestApiClient

LOG = logging.getLogger(__name__)
DEFAULT_TRACK_NAMES = ["Genes", "ClinVar", "ClinVar CNVs"]


def check_session_tracks(resource):
    """Make sure that a user requesting a resource is authenticated and resource is in session IGV tracks

    Args:
        resource(str): a resource on the server or on a remote URL

    Returns
        True is user has access to resource else False
    """
    # Check that user is logged in or that file extension is valid
    if current_user.is_authenticated is False:
        LOG.warning("Unauthenticated user requesting resource via remote_static")
        return False
    if resource not in session.get("igv_tracks", []):
        LOG.warning(f"Requested resource to be displayed in IGV not in session's IGV tracks")
        return False
    return True


def set_session_tracks(display_obj: dict):
    """Save igv tracks as a session object. This way it's easy to verify that a user is requesting one of these files from remote_static view endpoint

    Args:
        display_obj(dict): A display object containing case name, list of genes, locus and tracks
    """

    session_tracks = list(display_obj.get("reference_track", {}).values())
    for key, track_items in display_obj.items():
        if key not in ["tracks", "custom_tracks", "sample_tracks", "config_custom_tracks"] + list(
            CASE_SPECIFIC_TRACKS.keys()
        ):
            continue
        for track_item in track_items:
            session_tracks += list(track_item.values())

    session["igv_tracks"] = session_tracks


def make_igv_tracks(
    case_obj: dict,
    variant_id: str,
    chrom: Optional[str] = None,
    start: Optional[int] = None,
    stop: Optional[int] = None,
) -> dict:
    """Create a dictionary containing the required tracks for displaying IGV tracks for case or a group of cases

    Args:
        institute_id: institute _id
        case_obj(scout.models.Case)
        variant_id: _id of a variant
        chrom: requested chromosome [1-22], X, Y, [M-MT]
        start: start of the genomic interval to be displayed
        stop: stop of the genomic interval to be displayed

    Returns:
        display_obj: A display object containing case name, list of genes, locus and tracks
    """
    display_obj = {}
    variant_obj = store.variant(document_id=variant_id)

    chromosome = "All"
    if variant_obj:
        # Set display locus
        start = start or variant_obj["position"]
        stop = stop or variant_obj["end"]
        chrom = chrom or variant_obj.get("chromosome")

    if all([start, stop, chrom]):
        chromosome = chrom.replace("MT", "M")
        display_obj["locus"] = "chr{0}:{1}-{2}".format(chromosome, start, stop)

    # Set genome build for displaying alignments:

    if get_case_genome_build(case_obj) == "38" or chromosome == "M":
        build = "38"
    else:
        build = "37"

    # Set general tracks (Genes, Clinvar and ClinVar SNVs are shown according to user preferences)
    set_common_tracks(display_obj, build)

    # Build tracks for main case and all connected cases (cases grouped with main case)
    grouped_cases = []
    for group in case_obj.get("group", []):
        group_cases = list(store.cases(group=group))
        for case in group_cases:
            case_append_alignments(case)  # Add track data to connected case dictionary
            grouped_cases.append(case)

    if not grouped_cases:  # Display case individuals tracks only
        case_append_alignments(case_obj)  # Add track data to main case dictionary
        grouped_cases.append(case_obj)

    # Set up bam/cram alignments for case group samples:
    set_sample_tracks(display_obj, grouped_cases, chromosome)

    # When chrom != MT, set up case-specific tracks (might be present according to the pipeline)
    if chrom != "M":
        set_case_specific_tracks(display_obj, case_obj)

    # Set up custom cloud public tracks, if available
    set_config_custom_tracks(display_obj, build)

    display_obj["display_center_guide"] = True

    return display_obj


def make_sashimi_tracks(
    case_obj: dict, variant_id: Optional[str] = None, omics_variant_id: Optional[str] = None
):
    """Create a dictionary containing the required tracks for a splice junction plot
    If a regular variant_id is passed, set display to a particular gene locus.
    If an omics_variant_id is passed, set display to a window surrounding the variant, which can be a
    gene or an affected region.
    Otherwise defaults to whole genome "All" view.

    Returns:
        display_obj(dict): A display object containing case name, list of genes, locus and tracks
    """

    locus = "All"
    build = "37" if "37" in str(case_obj.get("rna_genome_build", "38")) else "38"

    if variant_id:
        variant_obj = store.variant(document_id=variant_id)
        locus = make_locus_from_gene(variant_obj, case_obj, build)
    if omics_variant_id:
        variant_obj = store.omics_variant(variant_id=omics_variant_id)
        locus = make_locus_from_variant(variant_obj, case_obj, build)

    display_obj = {"locus": locus, "tracks": []}

    set_common_tracks(display_obj, build)

    # Populate tracks for each individual with splice junction track data
    for ind in case_obj.get("individuals", []):
        if all([ind.get("splice_junctions_bed"), ind.get("rna_coverage_bigwig")]):
            track = make_merged_splice_track(ind)
            display_obj["tracks"].append(track)
        if ind.get("rna_alignment_path"):
            rna_aln = ind["rna_alignment_path"]
            aln_track = {
                "name": ind["display_name"],
                "url": rna_aln,
                "indexURL": find_index(rna_aln),
                "format": rna_aln.split(".")[-1],  # "bam" or "cram"
                "aln_height": 400,
            }
            display_obj["tracks"].append(aln_track)
    display_obj["case"] = case_obj["display_name"]

    return display_obj


def make_merged_splice_track(ind: dict) -> dict:
    """
    Retrieve individual splice track component and store in a dict for use when generating an IGV.js config.

    Args:
        ind: dict individual (sample)

    Returns:
        track: dict with merged track data for igv configuration
    """
    coverage_wig = ind["rna_coverage_bigwig"]
    splicej_bed = ind["splice_junctions_bed"]
    splicej_bed_index = f"{splicej_bed}.tbi" if os.path.isfile(f"{splicej_bed}.tbi") else None
    if splicej_bed_index is None:
        flash(f"Missing bed file index for individual {ind['display_name']}")
    track = {
        "name": ind["display_name"],
        "coverage_wig": coverage_wig,
        "splicej_bed": splicej_bed,
        "splicej_bed_index": splicej_bed_index,
    }
    return track


def get_locus_from_variant(variant_obj: Dict, case_obj: Dict, build: str) -> tuple:
    """
    Check if variant coordinates are in genome build 38, otherwise do variant coords liftover.
    Use original coordinates only if genome build was already 38 or liftover didn't work.
    Collect locus coordinates.
    """
    MIN_LOCUS_SIZE_OFFSET = 100

    locus_start_coord = variant_obj.get("position")
    locus_end_coord = variant_obj.get("end")

    if build not in str(case_obj.get("genome_build")):
        client = EnsemblRestApiClient()
        mapped_coords = client.liftover(
            case_obj.get("genome_build"),
            variant_obj.get("chromosome"),
            variant_obj.get("position"),
            variant_obj.get("end"),
        )
        if mapped_coords:
            mapped_start = mapped_coords[0]["mapped"].get("start")
            mapped_end = mapped_coords[0]["mapped"].get("end") or mapped_start
            locus_start_coord = mapped_start
            locus_end_coord = mapped_end

    variant_size_offset = (variant_obj.get("end") - variant_obj.get("position")) / 10
    if variant_size_offset < (MIN_LOCUS_SIZE_OFFSET * 2):
        variant_size_offset = MIN_LOCUS_SIZE_OFFSET
    locus_start_coord -= variant_size_offset
    locus_end_coord += variant_size_offset

    return (variant_obj["chromosome"], locus_start_coord, locus_end_coord)


def make_locus_from_variant(variant_obj: Dict, case_obj: Dict, build: str) -> str:
    """Given a variant obj, construct a locus string across variant plus a percent size offset around the variant."""

    (chrom, locus_start, locus_end) = get_locus_from_variant(variant_obj, case_obj, build)
    return f"{chrom}:{locus_start}-{locus_end}"


def make_locus_from_gene(variant_obj: Dict, case_obj: Dict, build: str) -> str:
    """Given a variant obj, construct a locus string across any gene touched for IGV to display.
    Initialize locus coordinates with variant coordinates so it won't crash if variant gene(s) no longer exist in database.
    Check if variant coordinates are in genome build 38, otherwise do variant coords liftover.
    Use original coordinates only if genome build was already 38 or liftover didn't work.
    Collect locus coordinates. Take into account that variant can hit multiple genes.
    The returned locus will so span all genes the variant falls into.
    """

    (chrom, locus_start, locus_end) = get_locus_from_variant(variant_obj, case_obj, build)
    locus_start_coords = [locus_start]
    locus_end_coords = [locus_end]

    variant_genes_ids = [gene["hgnc_id"] for gene in variant_obj.get("genes", [])]
    for gene_id in variant_genes_ids:
        gene_caption = store.hgnc_gene_caption(hgnc_identifier=gene_id, build=build)
        if gene_caption is None:
            continue
        locus_start_coords.append(gene_caption["start"])
        locus_end_coords.append(gene_caption["end"])

    locus_start = min(locus_start_coords)
    locus_end = max(locus_end_coords)

    return f"{chrom}:{locus_start}-{locus_end}"


def get_tracks(name_list: list, file_list: list) -> List[Dict]:
    """Return a list of dict according to IGV track format.

    If an index can be found (e.g. for bam, cram files), use it explicitly.
    If the format is one of those two alignment types, set it explicitly: it will need to be dynamically
    filled into the igv_viewer html template script for igv.js.
    """
    track_list = []
    for name, track in zip(name_list, file_list):
        if track == "missing":
            continue
        track_config = {"name": name, "url": track, "min": 0.0}
        index = find_index(track)
        if index:
            track_config["indexURL"] = index
        file_format_ending = track.split(".")[-1]
        if file_format_ending in ["bam", "cram"]:
            track_config["format"] = file_format_ending
            track_config["autoscaleGroup"] = "alignments"
        track_list.append(track_config)
    return track_list


def set_common_tracks(display_obj, build):
    """Set up tracks common to all cases (Genes, ClinVar ClinVar CNVs) according to user preferences

    Add Genes and reference tracks to display object

    Args:
        display_obj(dict) dictionary containing all tracks info
        build(string) "37" or "38"
    """
    user_obj = store.user(email=current_user.email)

    # Set up IGV tracks that are common for all cases:
    display_obj["reference_track"] = HUMAN_REFERENCE[build]  # Human reference is always present

    # if user settings for igv tracks exist -> use these settings, otherwise display default tracks ---> Genes, ClinVar and ClinVar CNVs
    custom_tracks_names = (
        user_obj.get("igv_tracks") if "igv_tracks" in user_obj else DEFAULT_TRACK_NAMES
    )

    display_obj["custom_tracks"] = []
    for track in IGV_TRACKS[build]:
        # if track is selected, add it to track display object
        if track["name"] in custom_tracks_names:
            display_obj["custom_tracks"].append(track)


def set_sample_tracks(display_obj: dict, case_groups: list, chromosome: str):
    """Set up individual-specific alignment tracks (bam/cram files)

    Given a dictionary containing all tracks info (display_obj), a list of case group dictionaries
    A chromosome string argument is used to check if we should look at mt alignment files for MT.

    A missing file is indicated with the string "missing", and no track is made for such entries.
    """

    sample_tracks = []

    track_items = "mt_bams" if chromosome == "M" else "bam_files"
    track_index_items = "mt_bais" if track_items == "mt_bams" else "bai_files"

    # Loop over a group of cases and add tracks for every individual of every case
    for case in case_groups:
        if None in [
            case.get("sample_names"),
            case.get(track_items),
            case.get(track_index_items),
        ]:
            case["sample_tracks"] = []
            return

        for count, sample in enumerate(case.get("sample_names")):
            if case[track_items][count] == "missing" or case[track_index_items][count] == "missing":
                continue
            sample_tracks.append(
                {
                    "name": sample,
                    "url": case[track_items][count],
                    "indexURL": case[track_index_items][count],
                    "format": case[track_items][count].split(".")[-1],  # "bam" or "cram"
                    "height": 700,
                    "show_soft_clips": case["track_items_soft_clips_settings"][count],
                }
            )
        display_obj["sample_tracks"] = sample_tracks


def set_case_specific_tracks(display_obj, case_obj):
    """Set up tracks from files that might be present for the focus case samples,
        not fetched for all samples in the case group.
        (rhocall files, tiddit coverage files, upd regions and sites files)
    Args:
        display_obj(dict) dictionary containing all tracks info
        form(dict) flask request form dictionary
    """
    for track, label in CASE_SPECIFIC_TRACKS.items():
        if None in [case_obj.get(track), case_obj.get("sample_names")]:
            continue

        display_obj[track] = get_tracks(
            [f"{label} - {sample}" for sample in case_obj.get("sample_names")], case_obj.get(track)
        )


def set_config_custom_tracks(display_obj: dict, build: str):
    """Set up custom public or private tracks stored in a cloud bucket or locally. These tracks were those specified in the Scout config file.
    Respect user's preferences."""
    user_obj = store.user(email=current_user.email)

    config_custom_tracks = []

    if hasattr(config_igv_tracks, "tracks"):
        build_tracks = config_igv_tracks.tracks.get(build, [])
        for track in build_tracks:
            # Do not display track if user doesn't want to see it
            if "igv_tracks" not in user_obj or track["name"] in user_obj.get("igv_tracks"):
                config_custom_tracks.append(track)
    if config_custom_tracks:
        display_obj["config_custom_tracks"] = config_custom_tracks
