from flask import url_for
from werkzeug.datastructures import ImmutableMultiDict

from scout.server.extensions import store


def test_clinvar_add_variant(app, institute_obj, case_obj, variant_obj):
    """Test endpoint that displays the user form to add a new ClinVar variant"""

    # GIVEN a database with a variant
    assert store.variant_collection.find_one()

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # WHEN sending a post request to add a variant to ClinVar
        data = {"var_id": variant_obj["_id"]}
        resp = client.post(
            url_for(
                "clinvar.clinvar_add_variant",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=data,
        )
        # THEN the form page should work as expected
        assert resp.status_code == 200


def test_clinvar_save(app, institute_obj, case_obj):
    """Test the second step of saving a new variant to a ClinVar submission object:
    saving to database the fields submitted in the clinvar_add_variant form by the user
    """
    # GIVEN a database with no ClinVar submissions
    assert store.clinvar_submission_collection.find_one() is None
    assert store.clinvar_collection.find_one() is None
    # GIVEN a form submitted by the user
    data = ImmutableMultiDict(
        {
            "case_id": "internal_id",
            "category": "snv",
            "local_id": "4c7d5c70d955875504db72ef8e1abe77",
            "linking_id": "4c7d5c70d955875504db72ef8e1abe77",
            "chromosome": "7",
            "ref": "C",
            "alt": "A",
            "start": "124491972",
            "stop": "124491972",
            "gene_symbol": "POT1",
            "last_evaluated": "2022-09-19",
            "inheritance_mode": "Autosomal dominant inheritance",
            "assertion_method": "ACMG Guidelines, 2015",
            "assertion_method_cit": "PMID:25741868",
            "variations_ids": "rs116916706",
            "clinsig": "Likely pathogenic, low penetrance",
            "clinsig_comment": "test clinsig comment",
            "clinsig_cit": "test clinsig cit",
            "hpo_terms": "HP:0001298",
            "condition_comment": "test condition comment",
            "include_ind": ["NA12882"],
            "individual_id": ["NA12882", "NA12877", "NA12878"],
            "affected_status": ["yes", "no", "no"],
            "allele_of_origin": ["germline", "germline" "germline"],
            "collection_method": ["clinical testing", "clinical testing", "clinical testing"],
        }
    )

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # WHEN data is submitted to the clinvar_save endpoint
        resp = client.post(
            url_for(
                "clinvar.clinvar_save",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
            ),
            data=data,
        )
        # THEN the form should be submitted and the page should redirect
        assert resp.status_code == 302

        # AND a general submission should be saved in the database
        assert store.clinvar_submission_collection.find_one()

        # AND 2 submission objects (Variant, Casedata) should be saved in
        subms = list(store.clinvar_collection.find())
        assert len(subms) == 2
