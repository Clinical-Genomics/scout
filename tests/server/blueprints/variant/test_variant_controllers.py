import copy
import logging
from pprint import pprint as pp

from flask import current_app, url_for
from flask_login import current_user

from scout.constants import IGV_TRACKS
from scout.server.blueprints.variant.controllers import (
    get_igv_tracks,
    has_rna_tracks,
    observations,
    tx_overview,
    variant,
)
from scout.server.extensions import cloud_tracks, loqusdb, store

LOG = logging.getLogger(__name__)


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


def test_has_rna_tracks(case_obj):
    """Test the function that returns True if any individual of a case has RNA tracks available"""

    # GIVEN a case with an individual with RNA tracks:
    for ind in case_obj["individuals"]:
        if ind["phenotype"] == 1:  # Lets's assume only the affected individuals has RNA data
            continue
        ind["splice_junctions_bed"] = "test.bed"
        ind["rna_coverage_bigwig"] = "test.BigWig"

    assert has_rna_tracks(case_obj) is True


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


def test_observations_controller_non_existing(app, case_obj, loqusdb):
    ## GIVEN a database and a loqusdb mock without the variant
    var_obj = store.variant_collection.find_one()
    assert var_obj

    ## WHEN updating the case_id for the variant
    var_obj["case_id"] = "internal_id2"

    data = None
    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        data = observations(store, loqusdb, case_obj, var_obj)

    ## THEN assert that the number of cases is still returned
    assert data["total"] == loqusdb.nr_cases
    ## THEN assert the cases variable is in data
    assert "cases" in data
    ## THEN assert there are no case information returned
    assert data["cases"] == []


def test_observations_controller_snv(app, case_obj, loqusdb):
    """Testing observation controller to retrieve observations for one SNV variant"""
    # GIVEN a database with a case with a specific SNV variant
    case_obj = store.case_collection.find_one()
    var_obj = store.variant_collection.find_one()
    assert var_obj

    loqusdb._add_variant(var_obj)

    # WHEN the same variant is in another case
    var_obj["case_id"] = "internal_id2"

    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        data = observations(store, loqusdb, case_obj, var_obj)

        ## THEN loqus should return the occurrence from the first case
        assert case_obj["_id"] in data["families"]
        assert data["cases"][0]["case"] == case_obj
        assert data["cases"][0]["variant"]["_id"] == var_obj["_id"]


def test_observations_controller_sv(app, sv_variant_obj, loqusdb):
    """Testing observations controller to retrieve observations for one SV variant.
    Test that SV variant similar to a given one from another case is returned
    """
    # GIVEN a database with a case with a specific SV variant
    case_obj = store.case_collection.find_one()
    store.variant_collection.insert_one(sv_variant_obj)
    loqusdb._add_variant(sv_variant_obj)

    # WHEN the same variant is in another case
    sv_variant_obj["case_id"] = "internal_id2"
    # And has a different variant_id
    sv_variant_obj["variant_id"] = "someOtherVarID"

    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        # THEN the observation of the original case should be found
        data = observations(store, loqusdb, case_obj, sv_variant_obj)

        ## THEN loqus should return the occurrence from the first case
        assert case_obj["_id"] in data["families"]
        assert data["cases"][0]["case"] == case_obj
        assert data["cases"][0]["variant"]["_id"] == sv_variant_obj["_id"]


def test_case_variant_check_causatives(app, real_variant_database):
    adapter = real_variant_database

    # GIVEN a populated database with variants
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
    # insert this case into database
    adapter.case_collection.insert_one(other_case)

    # GIVEN that the other case shares a variant with the original case,
    other_variant = copy.deepcopy(variant_obj)
    other_variant["case_id"] = "other_case"
    other_variant["_id"] = "other_variant"
    adapter.variant_collection.insert_one(other_variant)

    LOG.debug("other variant: {}".format(other_variant))
    assert sum(1 for i in adapter.event_collection.find()) == 0

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

    # THEN an app will find the matching causative
    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        other_causatives = adapter.check_causatives(
            case_obj=other_case, institute_obj=institute_obj
        )
        LOG.debug("other causatives: {}".format(other_causatives))
        assert sum(1 for i in other_causatives) > 0


def test_case_variant_check_causatives_carrier(app, real_variant_database):
    # GIVEN a case with a causative variant flagged,

    adapter = real_variant_database

    # GIVEN a populated database with variants
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
    # GIVEN another case with the same variant for an unaffected individual,
    other_case["individuals"][0]["phenotype"] = 1
    other_case["individuals"][1]["phenotype"] = 1
    other_case["individuals"][2]["phenotype"] = 1
    # insert this case into database
    adapter.case_collection.insert_one(other_case)

    # GIVEN that the other case shares a variant with the original case,
    other_variant = copy.deepcopy(variant_obj)
    other_variant["case_id"] = "other_case"
    other_variant["_id"] = "other_variant"
    adapter.variant_collection.insert_one(other_variant)

    LOG.debug("other variant: {}".format(other_variant))
    assert sum(1 for i in adapter.event_collection.find()) == 0

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

    # THEN an app will find the matching causative
    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        other_causatives = adapter.check_causatives(
            case_obj=other_case, institute_obj=institute_obj
        )
        LOG.debug("other causatives: {}".format(other_causatives))
        assert sum(1 for i in other_causatives) == 0


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
            institute_id,
            case_name,
            variant_id=var_id,
            add_case=True,
            add_other=True,
            get_overlapping=True,
            add_compounds=True,
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
            institute_id,
            case_name,
            variant_id=var_id,
            add_case=True,
            add_other=True,
            get_overlapping=True,
            add_compounds=True,
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
            institute_id,
            case_name,
            variant_id=var_id,
            add_case=True,
            add_other=True,
            get_overlapping=True,
            add_compounds=True,
            variant_type=category,
        )

    ## THEN assert the data is on correct format

    assert "overlapping_vars" in data
