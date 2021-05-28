# -*- coding: utf-8 -*-
import responses
from flask import url_for
from flask_login import current_user

from scout.commands.update.individual import individual as ind_cmd
from scout.server.blueprints.alignviewers import controllers
from scout.server.extensions import cloud_tracks, store


def test_make_sashimi_tracks_variant_38(app, case_obj):
    """Test function that creates splice junction tracks for a variant with genome build 38"""

    # GIVEN a case with genome build 38
    store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"genome_build": "38"}}
    )

    # WHEN the gene splice junction track is created for any variant in a gene
    test_variant = store.variant_collection.find_one({"hgnc_symbols": ["POT1"]})

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # THEN it should return the expected data
        display_obj = controllers.make_sashimi_tracks(
            case_obj["owner"], case_obj["display_name"], test_variant["_id"]
        )
        assert display_obj["case"] == case_obj["display_name"]
        assert display_obj["locus"]
        assert display_obj["tracks"][0]["name"]
        assert display_obj["tracks"][0]["coverage_wig"]
        assert display_obj["tracks"][0]["splicej_bed"]
        assert display_obj["tracks"][0]["splicej_bed_index"]
        assert display_obj["reference_track"]  # Reference genome track
        assert display_obj["custom_tracks"]  # Custom tracks include gene track in the right build


@responses.activate
def test_make_sashimi_tracks_variant_37(app, case_obj, ensembl_liftover_response):
    """Test function that creates splice junction tracks for a variant with genome build 37"""

    # WHEN the gene splice junction track is created for any variant in a gene
    test_variant = store.variant_collection.find_one({"hgnc_symbols": ["POT1"]})

    # GIVEN a patched response from Ensembl liftover API
    url = f'http://grch37.rest.ensembl.org/map/human/GRCh37/{test_variant["chromosome"]}:{test_variant["position"]}..{test_variant["end"]}/GRCh38?content-type=application/json'
    responses.add(
        responses.GET,
        url,
        json=ensembl_liftover_response,
        status=200,
    )

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # THEN it should return the expected data
        display_obj = controllers.make_sashimi_tracks(
            case_obj["owner"], case_obj["display_name"], test_variant["_id"]
        )
        assert display_obj["case"] == case_obj["display_name"]
        assert display_obj["locus"]
        assert display_obj["tracks"][0]["name"]
        assert display_obj["tracks"][0]["coverage_wig"]
        assert display_obj["tracks"][0]["splicej_bed"]
        assert display_obj["tracks"][0]["splicej_bed_index"]
        assert display_obj["reference_track"]  # Reference genome track
        assert display_obj["custom_tracks"]  # Custom tracks include gene track in the right build


def test_set_cloud_public_tracks(app):
    """Test function that adds cloud public tracks to track display object"""

    # GIVEN an app with public cloud tracks initialized
    patched_track = {"37": [{"name": "test track"}]}
    cloud_tracks.public_tracks = patched_track

    display_obj = {}
    build = "37"

    with app.test_client() as client:

        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        # And the user has the test track preselected:
        store.user_collection.find_one_and_update(
            {"email": current_user.email}, {"$set": {"igv_tracks": ["test track"]}}
        )

        # Then the set_cloud_public_tracks controller should add the test track to the display object
        controllers.set_cloud_public_tracks(display_obj, build)
        assert display_obj["cloud_public_tracks"] == patched_track["37"]


def test_make_igv_tracks():
    """Test function that creates custom track dictionaries"""

    # GIVEN a test track with 2 files
    file_list = ["sample_1_file", "sample_2_file"]
    track_list = controllers.make_igv_tracks("test_track", file_list)

    # The function should return a track list with 2 dictionaries
    assert len(track_list) == 2
    # Containing the expected info
    for track in track_list:
        assert track["name"] == "test_track"
        assert track["url"] in file_list


def test_sample_tracks():
    """Test the function that creates case individual tracks"""

    # GIVEN a case with 3 samples alignments
    sample_names = ["sample1", "sample2", "sample3"]
    sample_bams = ["bam1", "bam2", "bam3"]

    form_data = {
        "sample": ",".join(sample_names),
        "align": "bam",
        "bam": ",".join(sample_bams),
        "bai": "bai1,bai2,bai3",
    }

    display_obj = {}
    # WHEN the set_sample_tracks function is invoked:
    controllers.set_sample_tracks(display_obj, form_data)
    # THEN it should return 3 tracks
    assert len(display_obj["sample_tracks"]) == 3
    # Containing the expected fields
    for track in display_obj["sample_tracks"]:
        assert track["name"] in sample_names
        assert track["url"] in sample_bams


def set_case_specific_tracks():
    """Test function that creates tracks based on case-specific files:
    (rhocall files, tiddit coverage files, upd regions and sites files)
    """
    # GIVEN a case with a rhocall bed file and a TIDDIT wig file
    form_data = {"rhocall_bed": "rhocall.bed", "tiddit_coverage_wig": "tiddit_coverage.wig"}
    # THE case_specific_tracks function should return the expected tracks
    display_obj = {}
    controllers.set_case_specific_tracks(display_obj, form_data)
    assert display_obj["rhocall_bed"]["url"] == form_data["rhocall_bed"]
    assert display_obj["tiddit_coverage_wig"] == form_data["tiddit_coverage_wig"]
