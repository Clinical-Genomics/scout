# -*- coding: utf-8 -*-
import logging
import os.path

from flask import flash
from flask_login import current_user

from scout.constants import CASE_SPECIFIC_TRACKS, HUMAN_REFERENCE, IGV_TRACKS
from scout.server.extensions import cloud_tracks, store
from scout.server.utils import institute_and_case
from scout.utils.ensembl_rest_clients import EnsemblRestApiClient

LOG = logging.getLogger(__name__)
CUSTOM_TRACK_NAMES = ["Genes", "ClinVar", "ClinVar CNVs"]


def make_sashimi_tracks(institute_id, case_name, variant_id):
    """Create a dictionary containing the required tracks for a splice junction plot

    Accepts:
        institute_id(str): institute _id
        case_name(str): case display name
        variant_id(str) _id of a variant
    Returns:
        display_obj(dict): A display object containing case name, list of genes, lucus and tracks
    """
    build = "38"  # This feature is only available for RNA tracks in build 38

    variant_obj = store.variant(document_id=variant_id)
    _, case_obj = institute_and_case(store, institute_id, case_name)

    # Initialize locus coordinates it with variant coordinates so it won't crash if variant gene(s) no longer exist in database
    locus_start_coords = []
    locus_end_coords = []

    # Check if variant coordinates are in genome build 38
    # Otherwise do variant coords liftover
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

    # Use original coordinates only genome build was already 38 or liftover didn't work
    if not locus_start_coords:
        locus_start_coords.append(variant_obj.get("position"))
    if not locus_end_coords:
        locus_end_coords.append(variant_obj.get("end"))

    # Collect locus coordinates. Take into account that variant can hit multiple genes
    variant_genes_ids = [gene["hgnc_id"] for gene in variant_obj.get("genes", [])]
    for gene_id in variant_genes_ids:
        gene_obj = store.hgnc_gene(hgnc_identifier=gene_id, build=build)
        if gene_obj is None:
            continue
        locus_start_coords.append(gene_obj["start"])
        locus_end_coords.append(gene_obj["end"])

    locus_start = min(locus_start_coords)
    locus_end = max(locus_end_coords)

    locus = f"{variant_obj['chromosome']}:{locus_start}-{locus_end}"  # Locus will span all genes the variant falls into
    display_obj = {"locus": locus, "tracks": []}

    # Add Genes and reference tracks to display object
    set_common_tracks(display_obj, build)

    # Populate tracks for each individual with splice junction track data
    for ind in case_obj.get("individuals", []):
        if not all([ind.get("splice_junctions_bed"), ind.get("rna_coverage_bigwig")]):
            continue

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
        display_obj["tracks"].append(track)

    display_obj["case"] = case_obj["display_name"]

    return display_obj


def make_igv_tracks(name, file_list):
    """Return a dict according to IGV track format."""
    track_list = []
    for track in file_list:
        track_list.append({"name": name, "url": track, "min": 0.0, "max": 30.0})
    return track_list


def set_common_tracks(display_obj, build):
    """Set up tracks common to all cases (Genes, ClinVar ClinVar CNVs) according to user preferences

    Args:
        display_obj(dict) dictionary containing all tracks info
        build(string) "37" or "38"
    """
    user_obj = store.user(email=current_user.email)

    # Set up IGV tracks that are common for all cases:
    display_obj["reference_track"] = HUMAN_REFERENCE[build]  # Human reference is always present

    # if user settings for igv tracks exist -> use these settings, otherwise display all tracks
    custom_tracks_names = user_obj.get("igv_tracks") or CUSTOM_TRACK_NAMES

    display_obj["custom_tracks"] = []
    for track in IGV_TRACKS[build]:
        # if track is selected, add it to track display object
        if track["name"] in custom_tracks_names:
            display_obj["custom_tracks"].append(track)


def set_sample_tracks(display_obj, form):
    """Set up individual-specific alignment tracks (bam/cram files)

    Args:
        display_obj(dict) dictionary containing all tracks info
        form(dict) flask request form dictionary
    """
    samples = form.get("sample").split(",")
    sample_tracks = []
    bam_files = None
    bai_files = None
    if form.get("align") == "mt_bam":
        bam_files = form.get("mt_bam").split(",")
        bai_files = form.get("mt_bai").split(",")
    elif form.get("align") == "bam":
        bam_files = form.get("bam").split(",")
        bai_files = form.get("bai").split(",")

    counter = 0
    for sample in samples:
        # some samples might not have an associated bam file, take care if this
        if len(bam_files) > counter and bam_files[counter]:
            sample_tracks.append(
                {
                    "name": sample,
                    "url": bam_files[counter],
                    "format": bam_files[counter].split(".")[-1],  # "bam" or "cram"
                    "indexURL": bai_files[counter],
                    "height": 700,
                }
            )
        counter += 1
    display_obj["sample_tracks"] = sample_tracks


def set_case_specific_tracks(display_obj, form):
    """Set up tracks from files that might be present or not at the case level
        (rhocall files, tiddit coverage files, upd regions and sites files)
    Args:
        display_obj(dict) dictionary containing all tracks info
        form(dict) flask request form dictionary
    """
    for track, label in CASE_SPECIFIC_TRACKS.items():
        if form.get(track):
            track_info = make_igv_tracks(label, form.get(track).split(","))
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
