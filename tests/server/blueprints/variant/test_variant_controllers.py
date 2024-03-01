import copy
import datetime
import logging

import responses
from flask import url_for
from flask_login import current_user

from scout.constants import IGV_TRACKS
from scout.server.app import create_app
from scout.server.blueprints.variant.controllers import (
    check_reset_variant_classification,
    get_igv_tracks,
    observations,
    tx_overview,
    variant,
    variant_rank_scores,
)
from scout.server.blueprints.variant.utils import evaluation
from scout.server.extensions import cloud_tracks, loqusdb, store
from scout.server.utils import case_has_rna_tracks

LOG = logging.getLogger(__name__)


def test_check_reset_variant_classification(app, case_obj, variant_obj):
    """Test the check_reset_variant_classification controller
    Assume we are in the situation when it will trigger to clear classifications,
    and make sure it does clear the classification."""

    # GIVEN an app with a current user
    with app.test_client() as client:
        client.get(url_for("auto_login"))

        # GIVEN a variant classified according to ACMG
        assert store.variant_collection.find_one_and_update(
            {"_id": variant_obj["_id"]},
            {"$set": {"acmg_classification": 1}},
        )

        # WHEN retrieving the variant again,
        current_variant = store.variant(variant_obj["_id"])
        # THEN the classification was acutally set
        assert current_variant.get("acmg_classification") is not None

        # GIVEN that there are no separate evaluations stored for the variant
        assert len(list(store.get_evaluations_case_specific(variant_obj["document_id"]))) == 0

        # GIVEN an evaluation object for this classification that is not stored
        deleted_evaluation = dict(
            variant_specific=variant_obj["document_id"],
            variant_id=variant_obj["variant_id"],
            institute_id=case_obj["owner"],
            case_id=case_obj["case_id"],
            classification="LP",
            criteria=[],
            user_id=current_user.email,
            user_name=current_user.name,
            created_at=datetime.datetime.now(),
        )
        deleted_evaluation_obj = evaluation(store, deleted_evaluation)

        # WHEN checking if variant evaluations have been removed,
        # THEN it returns true
        assert check_reset_variant_classification(store, deleted_evaluation_obj, "link")

        # WHEN retrieving the variant again,
        current_variant = store.variant(variant_obj["_id"])
        # THEN the classification has now been cleared
        assert current_variant.get("acmg_classification") is None


def test_variant_rank_scores(case_obj, variant_obj):
    """Test the function that retrieves variant rank scores and info regrding the rank score model applied"""

    # GIVEN a case with SNV variants with rank score model
    assert case_obj["rank_model_version"]
    # GIVEN a snv variant
    assert variant_obj["category"] == "snv"
    # GIVEN that the variant has rank scores:
    variant_obj["rank_score_results"] = [
        {"category": "Splicing", "score": 0},
        {"category": "Inheritance_Models", "score": -12},
        {"category": "Consequence", "score": 1},
    ]

    # GIVEN a test app containing config params to retrieve a genetic model
    test_app = create_app(
        config=dict(
            TESTING=True,
            DEBUG=True,
            MONGO_DBNAME="TEST_DB",
            DEBUG_TB_ENABLED=False,
            LOGIN_DISABLED=True,
            RANK_MODEL_LINK_PREFIX="https://raw.githubusercontent.com/Clinical-Genomics/reference-files/master/rare-disease/rank_model/rank_model_-v",
            RANK_MODEL_LINK_POSTFIX="-.ini",
        )
    )
    with test_app.app_context():
        # THEN the rank score results of the variant should be returned by the function
        rank_score_results = variant_rank_scores(store, case_obj, variant_obj)
        assert isinstance(rank_score_results, list)
        # WITH the relative model ranges values
        assert rank_score_results[0]["model_ranges"]


def test_tx_overview(app):
    """Tests function that collects RefSeq or canonical transcripts to show in the variant view"""
    # GIVEN a variant populated with genes having more than 1 transcripts:
    test_variant = store.variant_collection.find_one({"hgnc_symbols": "POT1"})
    assert len(test_variant["genes"][0]["transcripts"]) > 1

    # WHEN the variant is used to prepare the transcript overview table using the controllers function
    tx_overview(test_variant)
    # THEN variant should be populated with overview_transcripts
    # Overview transcripts should contain the expected keys
    for tx in test_variant["overview_transcripts"]:
        for key in [
            "hgnc_symbol",
            "hgnc_id",
            "decorated_refseq_ids",
            "muted_refseq_ids",
            "transcript_id",
            "is_primary",
            "is_canonical",
            "coding_sequence_name",
            "protein_sequence_name",
            "varsome_link",
            "tp53_link",
            "cbioportal_link",
            "mycancergenome_link",
            "mane",
            "mane_plus",
        ]:
            assert key in tx


def test_has_rna_tracks(case_obj, tmpdir):
    """Test the function that returns True if any individual of a case has RNA tracks available"""

    # GIVEN an individual with splice junctions bed file and rna coverage track
    splicej_bed = tmpdir.join("test.bed")
    rna_cov_bw = tmpdir.join("test.BigWig")
    splicej_bed.write("content")
    rna_cov_bw.write("content")

    for ind in case_obj["individuals"]:
        if ind["phenotype"] == 1:  # Lets's assume only the affected individuals has RNA data
            continue

        ind["splice_junctions_bed"] = str(splicej_bed)
        ind["rna_coverage_bigwig"] = str(rna_cov_bw)

    # THEN case should result having RNA tracks
    assert case_has_rna_tracks(case_obj) is True


def test_get_igv_tracks():
    """Test function that collects IGV tracks to be used for customising user tracks"""

    # GIVEN an app with public cloud tracks initialized
    patched_track = {"37": [{"name": "test track"}]}
    cloud_tracks.public_tracks = patched_track

    # THEN the get_igv_tracks controller should return the default tracks
    igv_tracks = get_igv_tracks()
    for track in IGV_TRACKS["37"]:
        assert track["name"] in igv_tracks

    # and the name of the public cloud track
    assert "test track" in igv_tracks


@responses.activate
def test_observations_controller_non_existing(app, institute_obj, case_obj, loqusdburl):
    # GIVEN an app with a connected loqusdb instance
    loqus_id = "test"
    assert app.config["LOQUSDB_SETTINGS"][loqus_id]

    var_obj = store.variant_collection.find_one()
    assert var_obj

    ## GIVEN patched request to the loqusdbapi instance
    n_cases = 102
    var_name = f"{var_obj['chromosome']}_{var_obj['position']}_{var_obj['reference']}_{var_obj['alternative']}"
    responses.add(
        responses.GET,
        f"{loqusdburl}/variants/{var_name}",
        json={"total": n_cases, "cases": []},
        status=200,
    )

    # GIVEN that the institute is associated to the same loqusdb instance
    store.institute_collection.find_one_and_update(
        {"_id": institute_obj["_id"]}, {"$set": {"loqusdb_id": loqus_id}}
    )

    ## WHEN updating the case_id for the variant
    var_obj["case_id"] = "internal_id2"

    with app.test_client() as client:
        client.get(url_for("auto_login"))
        data = observations(store, loqusdb, var_obj)

    ## THEN assert that the number of cases is still returned
    assert data[loqus_id]["total"] == n_cases
    ## THEN assert the cases variable is in data but it's an empty list
    assert data[loqus_id]["cases"] == []


@responses.activate
def test_observations_controller_snv(app, institute_obj, loqusdburl):
    """Testing observation controller to retrieve observations for one SNV variant"""

    case_obj = store.case_collection.find_one()

    # GIVEN an app with a connected loqusdb instance
    loqus_id = "test"
    assert app.config["LOQUSDB_SETTINGS"][loqus_id]

    var_obj = store.variant_collection.find_one()
    assert var_obj["category"] == "snv"
    assert var_obj

    ## GIVEN patched request to the loqusdbapi instance
    var_name = f"{var_obj['chromosome']}_{var_obj['position']}_{var_obj['reference']}_{var_obj['alternative']}"

    responses.add(
        responses.GET,
        f"{loqusdburl}/variants/{var_name}",
        json={"families": [var_obj["case_id"]], "observations": 1},
        status=200,
    )

    # GIVEN that the institute is associated to the same loqusdb instance
    store.institute_collection.find_one_and_update(
        {"_id": institute_obj["_id"]}, {"$set": {"loqusdb_id": loqus_id}}
    )

    ## WHEN updating the case_id for the variant
    var_obj["case_id"] = "internal_id2"

    with app.test_client() as client:
        client.get(url_for("auto_login"))
        data = observations(store, loqusdb, var_obj)

    ## THEN loqus should return the occurrence from the first case
    assert case_obj["_id"] in data[loqus_id]["families"]
    assert data[loqus_id]["cases"][0]["case"] == case_obj
    assert data[loqus_id]["cases"][0]["variant"]["_id"] == var_obj["_id"]


@responses.activate
def test_observations_controller_sv(app, sv_variant_obj, institute_obj, loqusdburl):
    """Testing observations controller to retrieve observations for one SV variant.
    Test that SV variant similar to a given one from another case is returned
    """
    case_obj = store.case_collection.find_one()

    # GIVEN an app with a connected loqusdb instance
    loqus_id = "test"
    assert app.config["LOQUSDB_SETTINGS"][loqus_id]

    # GIVEN that the institute is associated to the same loqusdb instance
    store.institute_collection.find_one_and_update(
        {"_id": institute_obj["_id"]}, {"$set": {"loqusdb_id": loqus_id}}
    )

    # GIVEN a database with a case with a specific SV variant
    store.variant_collection.insert_one(sv_variant_obj)

    ## GIVEN patched request to the loqusdbapi instance
    req_url = f"{loqusdburl}/svs/?chrom={sv_variant_obj['chromosome']}&end_chrom={sv_variant_obj['end_chrom']}&pos={sv_variant_obj['position']}&end={sv_variant_obj['end']}&sv_type={sv_variant_obj['sub_category'].upper()}"
    responses.add(
        responses.GET,
        req_url,
        json={"families": [sv_variant_obj["case_id"]], "observations": 1},
        status=200,
    )

    # WHEN the same variant is in another case
    sv_variant_obj["case_id"] = "internal_id2"
    # And has a different variant_id
    sv_variant_obj["variant_id"] = "someOtherVarID"

    with app.test_client() as client:
        client.get(url_for("auto_login"))
        # THEN the observation of the original case should be found
        data = observations(store, loqusdb, sv_variant_obj)

    ## THEN loqus should return the occurrence from the first case
    assert case_obj["_id"] in data[loqus_id]["families"]
    assert data[loqus_id]["cases"][0]["case"] == case_obj
    assert data[loqus_id]["cases"][0]["variant"]["_id"] == sv_variant_obj["_id"]


def test_case_matching_causatives(app, real_variant_database):
    """Testing the case_matching_causatives function, that returns variants for a case that
    were found causatives in other cases from the same institutet.
    - given that the variant is found in an affected individual of the case
    """
    # GIVEN a populated database
    adapter = real_variant_database
    case_obj = adapter.case_collection.find_one()
    assert case_obj
    institute_obj = adapter.institute_collection.find_one()
    assert institute_obj
    user_obj = adapter.user_collection.find_one()
    assert user_obj
    variant_obj = adapter.variant_collection.find_one()
    assert variant_obj

    # WHEN inserting another case into the database,
    other_case = copy.deepcopy(case_obj)
    other_case["_id"] = "other_case"
    other_case["internal_id"] = "other_case"
    other_case["display_name"] = "other_case"
    # GIVEN that the other case contains the variant in one affected individual
    for ind in other_case["individuals"]:
        ind["phenotype"] = 2  # affected

    adapter.case_collection.insert_one(other_case)

    # GIVEN that the other case shares a variant with the original case,
    other_variant = copy.deepcopy(variant_obj)
    other_variant["case_id"] = "other_case"
    other_variant["_id"] = "other_variant"
    adapter.variant_collection.insert_one(other_variant)

    assert sum(1 for _ in adapter.event_collection.find()) == 0

    # WHEN the original case has a causative variant flagged,
    link = "junk/{}".format(variant_obj["_id"])
    updated_case = adapter.mark_causative(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=variant_obj,
    )

    # THEN an event object should have been created linking the variant
    event_obj = adapter.event_collection.find_one()
    assert event_obj["link"] == link

    # THEN an function will find the matching causative
    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        other_causatives = adapter.case_matching_causatives(
            case_obj=other_case,
        )
        assert sum(1 for _ in other_causatives) == 1


def test_case_matching_causatives_carrier(app, real_variant_database):
    """Testing the case_matching_causatives function, which should NOT return matching causatives
    when the the case has not affected individuals with the variant"""

    # GIVEN a populated database
    adapter = real_variant_database
    case_obj = adapter.case_collection.find_one()
    assert case_obj
    institute_obj = adapter.institute_collection.find_one()
    assert institute_obj
    user_obj = adapter.user_collection.find_one()
    assert user_obj
    variant_obj = adapter.variant_collection.find_one()
    assert variant_obj

    # WHEN inserting another case into the database,
    other_case = copy.deepcopy(case_obj)
    other_case["_id"] = "other_case"
    other_case["internal_id"] = "other_case"
    other_case["display_name"] = "other_case"

    # GIVEN that the another case has the variant in an unaffected individual
    for ind in other_case["individuals"]:
        ind["phenotype"] = 1  # unaffected

    # insert this case into database
    adapter.case_collection.insert_one(other_case)

    # GIVEN that the other case shares a variant with the original case,
    other_variant = copy.deepcopy(variant_obj)
    other_variant["case_id"] = "other_case"
    other_variant["_id"] = "other_variant"
    adapter.variant_collection.insert_one(other_variant)

    # WHEN the original case has a causative variant flagged,
    link = "junk/{}".format(variant_obj["_id"])
    updated_case = adapter.mark_causative(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        variant=variant_obj,
    )

    # THEN the function will NOT return the matching causative from the first case
    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        other_causatives = adapter.case_matching_causatives(
            case_obj=other_case,
        )
        assert sum(1 for _ in other_causatives) == 0


def test_variant_controller_with_compounds(app, institute_obj, case_obj):
    ## GIVEN a populated database with a variant that have compounds
    variant_obj = store.variant_collection.find_one({"compounds": {"$exists": True}})
    assert variant_obj
    assert isinstance(variant_obj["compounds"], list)
    assert len(variant_obj["compounds"]) > 0

    category = "snv"
    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))

        institute_id = institute_obj["_id"]
        case_name = case_obj["display_name"]

        var_id = variant_obj["_id"]

        ## WHEN fetching the variant from the controller
        data = variant(
            store,
            institute_id=institute_id,
            case_name=case_name,
            variant_id=var_id,
            add_other=True,
            get_overlapping=True,
            variant_type=category,
        )

    ## THEN assert that the compounds are sorted
    combined_score = None
    prev_score = None
    for compound in data["variant"]["compounds"]:
        combined_score = compound["combined_score"]
        if prev_score is None:
            prev_score = combined_score
            continue
        assert combined_score <= prev_score
        prev_score = combined_score


def test_variant_controller_with_clnsig(app, institute_obj, case_obj):
    ## GIVEN a populated database with a variant
    variant_obj = store.variant_collection.find_one({"clnsig": {"$exists": True}})
    assert variant_obj
    assert "clinsig_human" not in variant_obj
    category = "snv"
    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))

        institute_id = institute_obj["_id"]
        case_name = case_obj["display_name"]

        var_id = variant_obj["_id"]

        ## WHEN fetching the variant from the controller
        data = variant(
            store,
            variant_id=var_id,
            institute_id=institute_id,
            case_name=case_name,
            add_other=True,
            get_overlapping=True,
            variant_type=category,
        )

    ## THEN assert the data is on correct format

    assert "clinsig_human" in data["variant"]
    assert data["variant"]["clinsig_human"] is not None


def test_variant_controller(app, institute_obj, case_obj, variant_obj):
    ## GIVEN a populated database with a variant
    category = "snv"
    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))

        institute_id = institute_obj["_id"]
        case_name = case_obj["display_name"]

        var_id = variant_obj["_id"]

        ## WHEN fetching the variant from the controller
        data = variant(
            store,
            variant_id=var_id,
            institute_id=institute_id,
            case_name=case_name,
            add_other=True,
            get_overlapping=True,
            variant_type=category,
        )

    ## THEN assert the data is on correct format

    assert "overlapping_vars" in data
