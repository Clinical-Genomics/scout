# -*- coding: utf-8 -*-
from flask import url_for
from flask_login import current_user

from scout.server.extensions import store

OVERVIEW_GENE_VARIANTS_ENDPOINT = "overview.gene_variants"


def test_gene_variants(app, user_obj, institute_obj):
    """Test the page that returns all SNPs and INDELs given a gene provided by user"""

    # GIVEN a form filled in by the user
    form_data = {
        "hgnc_symbols": "POT1",
        "variant_type": [],  # This will set variant type to ["clinical"] in the endpoint function
        "category": "snv",
        "rank_score": 5,
    }

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # WHEN form is submitted by POST request
        resp = client.post(
            url_for(
                OVERVIEW_GENE_VARIANTS_ENDPOINT,
                institute_id=institute_obj["internal_id"],
            ),
            data=form_data,
        )
        # THEN it should return a valid page
        assert resp.status_code == 200

        # containing the expected results
        assert "POT1" in str(resp.data)


def test_gene_variants_export(app, user_obj, institute_obj):
    """Test that the SNPs and INDELs page exports data given a gene provided by user"""

    # GIVEN a form filled in by the user
    form_data = {
        "hgnc_symbols": "POT1",
        "variant_type": [],  # This will set variant type to ["clinical"] in the endpoint function
        "category": "snv",
        "rank_score": 5,
        "filter_export_variants": "yes",
    }

    # GIVEN an initialized app
    with app.test_client() as client:
        # WITH a logged user
        client.get(url_for("auto_login"))

        # WHEN form is submitted by POST request
        resp = client.post(
            url_for(
                OVERVIEW_GENE_VARIANTS_ENDPOINT,
                institute_id=institute_obj["internal_id"],
            ),
            data=form_data,
        )
        # THEN response should be successful
        assert resp.status_code == 200

        # containing a text file
        assert resp.mimetype == "text/csv"


def test_events_timeline(app, user_obj, institute_obj, case_obj):
    """Test the wiew that returns the last 100 groups of events for a user"""

    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        # GIVEN one user event present in the database
        store.assign(institute=institute_obj, case=case_obj, user=user_obj, link="test_link")
        assert store.event_collection.find_one()

        resp = client.get(
            url_for(
                "overview.timeline",
            )
        )
        # THEN the page should not return error
        assert resp.status_code == 200

        # AND the event should be displayed on the timeline page
        assert "assigned" in str(resp.data)


def test_institute_settings(app, user_obj, institute_obj):
    """Test function that creates institute update form and updates an institute"""

    # GIVEN a gene panel
    test_panel = store.panel_collection.find_one()
    assert test_panel

    # AND 2 mock HPO terms in database
    mock_disease_terms = [
        {"_id": "HP:0001298", "description": "Encephalopathy", "hpo_id": "HP:0001298"},
        {"_id": "HP:0001250", "description": "Seizures", "hpo_id": "HP:0001250"},
    ]
    for term in mock_disease_terms:
        store.load_hpo_term(term)
        assert store.hpo_term(term["_id"])

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        client.get(url_for("auto_login"))

        # WHEN accessing the cases page (GET method)
        resp = client.get(
            url_for("overview.institute_settings", institute_id=institute_obj["internal_id"])
        )

        # THEN it should return a page
        assert resp.status_code == 200

        # WHEN updating an institute using the following form
        form_data = {
            "display_name": "updated name",
            "sanger_emails": ["john@doe.com"],
            "coverage_cutoff": "15",
            "frequency_cutoff": "0.001",
            "cohorts": ["test cohort 1", "test cohort 2"],
            "institutes": ["cust111", "cust222"],
            "pheno_groups": [
                "HP:0001298 , Encephalopathy ( ENC )",
                "HP:0001250 , Seizures ( EP )",
            ],
            "gene_panels": [test_panel["panel_name"]],
            "alamut_key": "test_alamut_key",
            "clinvar_key": "test_clinvar_key",
            "clinvar_emails": ["john@doe.com"],
        }

        # via POST request
        resp = client.post(
            url_for("overview.institute_settings", institute_id=institute_obj["internal_id"]),
            data=form_data,
        )
        assert resp.status_code == 200

        # THEN the institute object should be updated with the provided form data
        updated_institute = store.institute_collection.find_one()
        assert updated_institute["display_name"] == form_data["display_name"]
        assert updated_institute["sanger_recipients"] == form_data["sanger_emails"]
        assert updated_institute["coverage_cutoff"] == int(form_data["coverage_cutoff"])
        assert updated_institute["frequency_cutoff"] == float(form_data["frequency_cutoff"])
        assert updated_institute["cohorts"] == form_data["cohorts"]
        assert updated_institute["collaborators"] == form_data["institutes"]
        assert len(updated_institute["phenotype_groups"]) == 2  # one for each HPO term
        assert updated_institute["gene_panels"] == {
            test_panel["panel_name"]: test_panel["display_name"]
        }
        assert updated_institute["alamut_key"] == form_data["alamut_key"]
        assert updated_institute["clinvar_key"] == form_data["clinvar_key"]
        assert updated_institute["clinvar_submitters"] == form_data["clinvar_emails"]


def test_cases(app, institute_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the cases page
        resp = client.get(url_for("overview.cases", institute_id=institute_obj["internal_id"]))

        # THEN it should return a page
        assert resp.status_code == 200

        # test query passing parameters in seach form
        request_data = {
            "limit": "100",
            "skip_assigned": "on",
            "is_research": "on",
            "query": "case_id",
        }
        resp = client.get(
            url_for(
                "overview.cases",
                institute_id=institute_obj["internal_id"],
                params=request_data,
            )
        )
        # response should return a page
        assert resp.status_code == 200

        sorting_options = ["analysis_date", "track", "status"]
        for option in sorting_options:
            # test query passing the sorting option to the cases view
            request_data = {"sort": option}
            resp = client.get(
                url_for(
                    "overview.cases",
                    institute_id=institute_obj["internal_id"],
                    params=request_data,
                )
            )
            # response should return a page
            assert resp.status_code == 200


def test_cases_query_case_name(app, case_obj, institute_obj):
    """Test cases filtering by case display name"""

    slice_query = f"case:{case_obj['display_name']}"

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the cases page with a query
        resp = client.get(
            url_for(
                "overview.cases",
                query=slice_query,
                institute_id=institute_obj["internal_id"],
            )
        )

        # THEN it should return a page with the case
        assert resp.status_code == 200
        assert case_obj["display_name"] in str(resp.data)


def test_cases_panel_query(app, case_obj, parsed_panel, institute_obj):
    """Test cases filtering by gene panel"""

    slice_query = f"panel:{parsed_panel['panel_id']}"

    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the cases page with a query
        resp = client.get(
            url_for(
                "overview.cases",
                query=slice_query,
                institute_id=institute_obj["internal_id"],
            )
        )

        # THEN it should return a page with the case
        assert resp.status_code == 200
        assert case_obj["display_name"] in str(resp.data)


def test_cases_by_pinned_gene_query(app, case_obj, institute_obj):
    """Test cases filtering by providing the gene of one of its pinned variants"""

    # GIVEN a test variant hitting POT1 gene (hgnc_id:17284)
    suspects = []
    test_variant = store.variant_collection.find_one({"genes.hgnc_id": {"$in": [17284]}})
    assert test_variant

    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # GIVEN a case with this variant pinned
        form = {
            "action": "ADD",
        }
        client.post(
            url_for(
                "cases.pin_variant",
                institute_id=institute_obj["internal_id"],
                case_name=case_obj["display_name"],
                variant_id=test_variant["_id"],
            ),
            data=form,
        )
        updated_case = store.case_collection.find_one({"suspects": {"$in": [test_variant["_id"]]}})
        assert updated_case

        # WHEN the case search is performed using the POT1 gene
        slice_query = f"pinned:POT1"

        resp = client.get(
            url_for(
                "overview.cases",
                query=slice_query,
                institute_id=institute_obj["internal_id"],
            )
        )

        # THEN it should return a page with the case
        assert resp.status_code == 200
        assert case_obj["display_name"] in str(resp.data)


def test_cases_exact_phenotype_query(app, case_obj, institute_obj, test_hpo_terms):
    """Test cases filtering by providing one HPO term"""

    # GIVEN a case with some HPO terms
    store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]},
        {"$set": {"phenotype_terms": test_hpo_terms}},
    )
    one_hpo_term = test_hpo_terms[0]["phenotype_id"]
    slice_query = f"exact_pheno:{one_hpo_term}"

    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the cases page with the query
        resp = client.get(
            url_for(
                "overview.cases",
                query=slice_query,
                institute_id=institute_obj["internal_id"],
            )
        )

        # THEN it should return a page with the case
        assert resp.status_code == 200
        assert case_obj["display_name"] in str(resp.data)


def test_cases_similar_phenotype_query(app, case_obj, institute_obj, test_hpo_terms):
    """Test cases filtering by providing HPO terms that are related to case phenotype"""

    # GIVEN a case with some HPO terms
    store.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]},
        {"$set": {"phenotype_terms": test_hpo_terms}},
    )

    # WHEN similar but distinct HPO terms are used in the query
    similar_hpo_terms = ["HP:0012047", "HP:0000618"]
    for term in test_hpo_terms:
        assert term["phenotype_id"] not in similar_hpo_terms

    similar_hpo_terms = ",".join(similar_hpo_terms)
    slice_query = f"similar_pheno:{similar_hpo_terms}"

    with app.test_client() as client:
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the cases page with the query
        resp = client.get(
            url_for(
                "overview.cases",
                query=slice_query,
                institute_id=institute_obj["internal_id"],
            )
        )

        # THEN it should return a page with the case
        assert resp.status_code == 200
        assert case_obj["display_name"] in str(resp.data)


def test_verified(app, institute_obj, case_obj, user_obj, variant_obj):
    """Test the endpoint that returns the list of verified variants for an institute"""
    # GIVEN an initialized app
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        client.get(url_for("auto_login"))

        # GIVEN a verified variant:
        store.validate(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link="link",
            variant=variant_obj,
            validate_type="False positive",
        )

        # WHEN accessing the verified variants page
        resp = client.get(url_for("overview.verified", institute_id=institute_obj["internal_id"]))
        assert resp.status_code == 200

        # The variant should be found:
        assert variant_obj["_id"] in str(resp.data)


def test_causatives(app, user_obj, institute_obj, case_obj):
    # GIVEN an initialized app
    # GIVEN a valid user and institute
    # There should be no causative variants for test case:
    assert "causatives" not in case_obj
    var1_id = "4c7d5c70d955875504db72ef8e1abe77"  # in POT1 gene
    var2_id = "e24b65bf27feacec6a81c8e9e19bd5f1"  # in TBX1 gene
    var_ids = [var1_id, var2_id]

    # for each variant
    for var_id in var_ids:
        # update case by marking variant as causative:
        variant_obj = store.variant(document_id=var_id)
        store.mark_causative(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link="causative_var_link/{}".format(variant_obj["_id"]),
            variant=variant_obj,
        )
    updated_case = store.case_collection.find_one({"_id": case_obj["_id"]})
    # The above variants should be registered as causatives in case object
    assert updated_case["causatives"] == var_ids

    # Call scout causatives view and check if the above causatives are displayed
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # WHEN accessing the case page
        resp = client.get(url_for("overview.causatives", institute_id=institute_obj["internal_id"]))

        # THEN it should return a page
        assert resp.status_code == 200
        # with variant 1
        assert var1_id in str(resp.data)
        # and variant 2
        assert var2_id in str(resp.data)

        # Filter causatives by gene (POT1)
        resp = client.get(
            url_for(
                "overview.causatives",
                institute_id=institute_obj["internal_id"],
                query="17284 | POT1 (DKFZp586D211, hPot1, POT1)",
            )
        )
        # THEN it should return a page
        assert resp.status_code == 200
        # with variant 1
        assert var1_id in str(resp.data)
        # but NOT variant 2
        assert var2_id not in str(resp.data)


def test_gene_variants_filter(app, institute_obj, case_obj):
    """Test the function that allows searching SNVs and INDELS using filters"""

    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))
        assert resp.status_code == 200

        # When user submits a query for a variants in a specific gene and a rank score
        filter_query = {
            "hgnc_symbols": "POT1",
            "variant_type": ["clinical"],
            "rank_score": 11,
        }

        resp = client.post(
            url_for(OVERVIEW_GENE_VARIANTS_ENDPOINT, institute_id=institute_obj["internal_id"]),
            data=filter_query,
        )
        # THEN it should return a page
        assert resp.status_code == 200

        # containing  variants in that genes
        assert "POT1" in str(resp.data)


def test_institute_users(app, institute_obj, user_obj):
    """Test the link to all institute users"""
    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        # WHEN accessing the cases page
        resp = client.get(
            url_for("overview.institute_users", institute_id=institute_obj["internal_id"])
        )

        # THEN it should return a page
        assert resp.status_code == 200

        # Containing the test user's name
        assert user_obj["name"] in str(resp.data)


def test_filters(app, institute_obj, user_obj, case_obj, filter_obj):
    """Test the link to all institute users"""
    # GIVEN an initialized app
    # GIVEN a valid user and institute
    with app.test_client() as client:
        # GIVEN that the user could be logged in
        resp = client.get(url_for("auto_login"))

        category = "snv"
        filter_id = store.stash_filter(filter_obj, institute_obj, case_obj, user_obj, category)
        store.lock_filter(filter_id, user_obj.get("email"))

        # WHEN accessing the cases page
        resp = client.get(url_for("overview.filters", institute_id=institute_obj["internal_id"]))

        # THEN it should return a page
        assert resp.status_code == 200

        # Containing the test user's name
        assert user_obj["name"] in str(resp.data)
