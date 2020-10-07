# -*- coding: utf-8 -*-
import logging
from flask_login import current_user
from scout.server.extensions import store, cloud_tracks
from scout.constants import IGV_TRACKS, CASE_SPECIFIC_TRACKS

LOG = logging.getLogger(__name__)
CUSTOM_TRACK_NAMES = ["Genes", "ClinVar", "ClinVar CNVs"]


def make_igv_tracks(name, file_list):
    """ Return a dict according to IGV track format. """
    track_list = []
    for track in file_list:
        track_list.append({"name": name, "url": track, "min": 0.0, "max": 30.0})
    return track_list


def set_common_tracks(display_obj, build, form):
    """Set up tracks common to all cases (Genes, ClinVar ClinVar CNVs) according to user preferences

    Args:
        display_obj(dict) dictionary containing all tracks info
        build(string) "37" or "38"
        form(dict) flask request form dictionary
    """
    user_obj = store.user(email=current_user.email)
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
