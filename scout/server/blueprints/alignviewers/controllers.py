# -*- coding: utf-8 -*-
import logging
import os.path
from typing import Dict

from flask import flash, session
from flask_login import current_user

from scout.constants import CASE_SPECIFIC_TRACKS, HUMAN_REFERENCE, IGV_TRACKS
from scout.server.extensions import cloud_tracks, store
from scout.server.utils import case_append_alignments, find_index
from scout.utils.ensembl_rest_clients import EnsemblRestApiClient

LOG = logging.getLogger(__name__)
CUSTOM_TRACK_NAMES = ["Genes", "ClinVar", "ClinVar CNVs"]


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


def set_session_tracks(display_obj):
    """Save igv tracks as a session object. This way it's easy to verify that a user is requesting one of these files from remote_static view endpoint

    Args:
        display_obj(dict): A display object containing case name, list of genes, locus and tracks
    """
    session_tracks = list(display_obj.get("reference_track", {}).values())
    for key, track_items in display_obj.items():
        if key not in ["tracks", "custom_tracks", "sample_tracks", "cloud_public_tracks"]:
            continue
        for track_item in track_items:
            session_tracks += list(track_item.values())

    session["igv_tracks"] = session_tracks


def make_igv_tracks(case_obj, variant_id, chrom=None, start=None, stop=None):
    """Create a dictionary containing the required tracks for displaying IGV tracks for case or a group of cases

    Args:
        institute_id(str): institute _id
        case_obj(scout.models.Case)
        variant_id(str): _id of a variant
        chrom(str/None): requested chromosome [1-22], X, Y, [M-MT]
        start(int/None): start of the genomic interval to be displayed
        stop(int/None): stop of the genomic interval to be displayed

    Returns:
        display_obj(dict): A display object containing case name, list of genes, lucus and tracks
    """
    display_obj = {}
    variant_obj = store.variant(document_id=variant_id)

    if variant_obj:
        # Set display locus
        start = start or variant_obj["position"]
        stop = stop or variant_obj["end"]

        chromosome = chrom or variant_obj.get("chromosome")
        chromosome = chromosome.replace("MT", "M")
        display_obj["locus"] = "chr{0}:{1}-{2}".format(chromosome, start, stop)
    else:
        chromosome = "All"

    # Set genome build for displaying alignments:
    if "38" in str(case_obj.get("genome_build", "37")) or chromosome == "M":
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
    set_cloud_public_tracks(display_obj, build)

    display_obj["display_center_guide"] = True

    return display_obj


def make_sashimi_tracks(case_obj, variant_id=None):
    """Create a dictionary containing the required tracks for a splice junction plot

    Args:
        case_obj(scout.models.Case)
        variant_id(str) _id of a variant
    Returns:
        display_obj(dict): A display object containing case name, list of genes, lucus and tracks
    """
    build = "38"  # This feature is only available for RNA tracks in build 38

    locus = "All"
    if variant_id:
        variant_obj = store.variant(document_id=variant_id)
        locus = make_locus_from_variant(variant_obj, case_obj, build)

    display_obj = {"locus": locus, "tracks": []}

    set_common_tracks(display_obj, build)

    # Populate tracks for each individual with splice junction track data
    for ind in case_obj.get("individuals", []):
        if all([ind.get("splice_junctions_bed"), ind.get("rna_coverage_bigwig")]):
            coverage_wig = ind["rna_coverage_bigwig"]
            splicej_bed = ind["splice_junctions_bed"]
            splicej_bed_index = (
                f"{splicej_bed}.tbi" if os.path.isfile(f"{splicej_bed}.tbi") else None
            )
            if splicej_bed_index is None:
                flash(f"Missing bed file index for individual {ind['display_name']}")
            track = {
                "name": ind["display_name"],
                "coverage_wig": coverage_wig,
                "splicej_bed": splicej_bed,
                "splicej_bed_index": splicej_bed_index,
            }
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


def make_locus_from_variant(variant_obj: Dict, case_obj: Dict, build: str) -> str:
    """Given a variant obj, construct a locus string across any gene touched for IGV to display.

    Initialize locus coordinates with variant coordinates so it won't crash if variant gene(s) no longer exist in database.
    Check if variant coordinates are in genome build 38, otherwise do variant coords liftover.
    Use original coordinates only if genome build was already 38 or liftover didn't work.
    Collect locus coordinates. Take into account that variant can hit multiple genes.
    The returned locus will so span all genes the variant falls into.
    """
    locus_start_coords = []
    locus_end_coords = []

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
            locus_start_coords.append(mapped_start)
            locus_end_coords.append(mapped_end)

    if not locus_start_coords:
        locus_start_coords.append(variant_obj.get("position"))
    if not locus_end_coords:
        locus_end_coords.append(variant_obj.get("end"))

    variant_genes_ids = [gene["hgnc_id"] for gene in variant_obj.get("genes", [])]
    for gene_id in variant_genes_ids:
        gene_caption = store.hgnc_gene_caption(hgnc_identifier=gene_id, build=build)
        if gene_caption is None:
            continue
        locus_start_coords.append(gene_caption["start"])
        locus_end_coords.append(gene_caption["end"])

    locus_start = min(locus_start_coords)
    locus_end = max(locus_end_coords)

    return f"{variant_obj['chromosome']}:{locus_start}-{locus_end}"


def set_tracks(name, file_list):
    """Return a dict according to IGV track format."""
    track_list = []
    for track in file_list:
        track_list.append({"name": name, "url": track, "min": 0.0, "max": 30.0})
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

    # if user settings for igv tracks exist -> use these settings, otherwise display all tracks
    custom_tracks_names = (
        user_obj.get("igv_tracks") if "igv_tracks" in user_obj else CUSTOM_TRACK_NAMES
    )

    display_obj["custom_tracks"] = []
    for track in IGV_TRACKS[build]:
        # if track is selected, add it to track display object
        if track["name"] in custom_tracks_names:
            display_obj["custom_tracks"].append(track)


def set_sample_tracks(display_obj, case_groups, chromosome):
    """Set up individual-specific alignment tracks (bam/cram files)

    Args:
        display_obj(dict): dictionary containing all tracks info
        case_groups(list): a list of case dictionaries
        chromosome(str) [1-22],X,Y,M or "All"
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
            sample_tracks.append(
                {
                    "name": sample,
                    "url": case[track_items][count],
                    "indexURL": case[track_index_items][count],
                    "format": case[track_items][count].split(".")[-1],  # "bam" or "cram"
                    "height": 700,
                }
            )
        display_obj["sample_tracks"] = sample_tracks


def set_case_specific_tracks(display_obj, case_obj):
    """Set up tracks from files that might be present or not at the case level
        (rhocall files, tiddit coverage files, upd regions and sites files)
    Args:
        display_obj(dict) dictionary containing all tracks info
        form(dict) flask request form dictionary
    """
    for track, label in CASE_SPECIFIC_TRACKS.items():
        if case_obj.get(track) is None:
            continue
        track_info = set_tracks(label, case_obj.get(track).split(","))
        display_obj[track] = track_info


def set_cloud_public_tracks(display_obj, build):
    """Set up custom public tracks stored in a cloud bucket, according to the user preferences

    Args:
        display_obj(dict) dictionary containing all tracks info
        build(string) "37" or "38"
    """
    user_obj = store.user(email=current_user.email)
    custom_tracks_names = user_obj.get("igv_tracks")

    cloud_public_tracks = []
    if hasattr(cloud_tracks, "public_tracks"):
        build_tracks = cloud_tracks.public_tracks.get(build, [])
        for track in build_tracks:
            # Do not display track if user doesn't want to see it
            if custom_tracks_names and track["name"] not in custom_tracks_names:
                continue
            cloud_public_tracks.append(track)
    if cloud_public_tracks:
        display_obj["cloud_public_tracks"] = cloud_public_tracks
