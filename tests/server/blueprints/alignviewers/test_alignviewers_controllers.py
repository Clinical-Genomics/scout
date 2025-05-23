# -*- coding: utf-8 -*-
import responses
from flask import url_for
from flask_login import current_user

from scout.server.blueprints.alignviewers import controllers
from scout.server.extensions import config_igv_tracks, store
from scout.utils.ensembl_rest_clients import RESTAPI_URL


@responses.activate
def test_make_sashimi_tracks_variant_38(app, case_obj, ensembl_liftover_response):
    """Test function that creates splice junction tracks for a variant with genome build 38"""

    # WHEN the gene splice junction track is created for any variant in a gene
    test_variant = store.variant_collection.find_one({"hgnc_symbols": ["POT1"]})

    # GIVEN a patched response from Ensembl liftover API
    url = f'{RESTAPI_URL}/map/human/GRCh37/{test_variant["chromosome"]}:{test_variant["position"]}..{test_variant["end"]}/GRCh38?content-type=application/json'
    responses.add(
        responses.GET,
        url,
        json=ensembl_liftover_response,
        status=200,
    )

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
        display_obj = controllers.make_sashimi_tracks(case_obj, test_variant["_id"])
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
    url = f'{RESTAPI_URL}/map/human/GRCh37/{test_variant["chromosome"]}:{test_variant["position"]}..{test_variant["end"]}/GRCh38?content-type=application/json'
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
        display_obj = controllers.make_sashimi_tracks(case_obj, test_variant["_id"])
        assert display_obj["case"] == case_obj["display_name"]
        assert display_obj["locus"]
        assert display_obj["tracks"][0]["name"]
        assert display_obj["tracks"][0]["coverage_wig"]
        assert display_obj["tracks"][0]["splicej_bed"]
        assert display_obj["tracks"][0]["splicej_bed_index"]
        assert display_obj["reference_track"]  # Reference genome track
        assert display_obj["custom_tracks"]  # Custom tracks include gene track in the right build


def test_set_config_custom_tracks(app):
    """Test function that adds custom tracks taken from the scout config file to the IGV display object."""

    # GIVEN an app with public cloud tracks initialized
    patched_track = {"37": [{"name": "test track"}]}
    config_igv_tracks.tracks = patched_track

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
        controllers.set_config_custom_tracks(display_obj, build)
        assert display_obj["config_custom_tracks"] == patched_track["37"]


def test_make_igv_tracks(app, case_obj, variant_obj):
    """Test function that creates igv track dictionaries"""

    # GIVEN a user that is logged in the app
    with app.test_client() as client:
        client.get(url_for("auto_login"))

        display_obj = controllers.make_igv_tracks(case_obj, variant_obj["_id"], "MT", 100, 101)

        # The function should return a track list with the expected tracks
        assert display_obj["locus"] == "chrM:100-101"
        assert display_obj["display_center_guide"] == True
        assert display_obj["reference_track"]
        assert display_obj["custom_tracks"]
        assert len(display_obj["sample_tracks"]) == 3  # 3 individuals in demo case


def set_case_specific_tracks():
    """Test function that creates tracks based on case-specific files:
    (rhocall files, tiddit coverage files, upd regions and sites files)
    """
    # GIVEN a case with a rhocall bed file and a TIDDIT wig file
    form_data = {
        "rhocall_bed": "rhocall.bed",
        "tiddit_coverage_wig": "tiddit_coverage.wig",
        "minor_allele_frequency_wig": "minor_allele_frequency.wig",
    }
    # THE case_specific_tracks function should return the expected tracks
    display_obj = {}
    controllers.set_case_specific_tracks(display_obj, form_data)
    assert display_obj["rhocall_bed"]["url"] == form_data["rhocall_bed"]
    assert display_obj["tiddit_coverage_wig"] == form_data["tiddit_coverage_wig"]
    assert display_obj["minor_allele_frequency_wig"] == form_data["minor_allele_frequency_wig"]


def test_make_omics_locus(app, case_obj):
    """Test making loci for IGV viewing for OMICS variants."""

    # GIVEN an OMICS variants
    omics_variant = store.omics_variant_collection.find_one({"hgnc_symbols": ["POT1"]})

    # GIVEN that the OMICS variant is the same buid as the case (liftover not triggered)
    build = case_obj["genome_build"]
    omics_variant["build"] = build

    # WHEN asking for a locus for the OMICS variant
    locus_str = controllers.make_locus_from_variant(omics_variant, case_obj, build)
    # THEN a locus is returned on the right chromosome
    assert omics_variant["chromosome"] in locus_str
