import logging
from typing import Any, Dict, List

from scout.constants import REV_ACMG_MAP, REV_CCV_MAP

logger = logging.getLogger(__name__)

import copy

import pytest
from werkzeug.datastructures import ImmutableMultiDict

from scout.adapter.mongo.base import MongoAdapter
from scout.exceptions import IntegrityError


def test_add_and_get_case(
    adapter: MongoAdapter, case_obj: Dict[str, Any], institute_obj: Dict[str, Any]
) -> None:
    """Test adding, retrieving, and preventing duplicate cases."""

    ## GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None

    ## WHEN adding a new case to the database
    adapter.add_case(case_obj, institute_obj)
    loaded_case = adapter.case_collection.find_one({"_id": case_obj["_id"]})
    assert loaded_case["owner"] == case_obj["owner"]
    assert loaded_case["rank_model_version"] == case_obj["rank_model_version"]
    assert loaded_case["sv_rank_model_version"] == case_obj["sv_rank_model_version"]
    assert loaded_case["lims_id"] == case_obj["lims_id"]

    # Adding same case again raises IntegrityError
    with pytest.raises(IntegrityError):
        adapter.add_case(case_obj, institute_obj)

    # Retrieving a non-existing case returns None
    assert adapter.case(case_id="non_existing") is None


def test_load_case_integrity(
    adapter: MongoAdapter, institute_obj: Dict[str, Any], case_obj: Dict[str, Any]
) -> None:
    """Test load_case handles duplicate display names, changed individuals, and names."""

    ## GIVEN a database with one case
    adapter.institute_collection.insert_one(institute_obj)
    adapter.add_case(case_obj, institute_obj)

    # WHEN adding a case with same display_name, different case_id
    config2 = copy.deepcopy(case_obj)
    config2["case_id"] = "different"
    # THEN it should return error
    with pytest.raises(IntegrityError):
        adapter.load_case(config_data=config2)

    # WHEN adding a case with same _id, different display_name
    config2 = copy.deepcopy(case_obj)
    config2["display_name"] = "new_name"
    # THEN it should return error
    with pytest.raises(IntegrityError):
        adapter.load_case(config_data=config2, update=True)

    # WHEN adding a case with same _id, different individuals
    config2 = copy.deepcopy(case_obj)
    config2["individuals"][0]["individual_id"] = "changed_id"
    # THEN it should return error
    with pytest.raises(IntegrityError):
        adapter.load_case(config_data=config2, update=True)


def test_populate_case_query(adapter: MongoAdapter):
    """Test creating a case query using an advanced search containing multiple parameters."""

    query = {}
    # GIVEN an advanced case search with multiple parameters:
    name_query = ImmutableMultiDict(
        {
            "tags": "medical",
            "status": "active",
            "panel": "cardio",
            "cohort": "test_cohort",
            "synopsis": "fever",
            "track": "rare",
            "exact_pheno": "HP:0002315",
            "pheno_group": "HP:0002567",
            "case": "654",
            "exact_dia": "OMIM:607745",
        }
    )
    # THEN the query should be updated with multiple search terms:
    adapter.populate_case_query(query=query, name_query=name_query)
    assert query["tags"] == "medical"
    assert query["status"] == "active"
    assert query["panels"] == {"$elemMatch": {"is_default": True, "panel_name": "cardio"}}
    assert query["cohorts"] == "test_cohort"
    assert query["$text"] == {"$search": "fever"}
    assert query["track"] == "rare"
    assert query["phenotype_terms.phenotype_id"] == {"$in": ["HP:0002315"]}
    assert query["phenotype_groups.phenotype_id"] == "HP:0002567"
    assert query["$or"]  # Contains condition for case 'case' and 'exact_dia' options


def test_case_queries(
    real_adapter: MongoAdapter,
    hpo_database: MongoAdapter,
    test_hpo_terms: List[Dict[str, Any]],
    case_obj: Dict[str, Any],
    institute_obj: Dict[str, Any],
    user_obj: Dict[str, Any],
    variant_obj: Dict[str, Any],
) -> None:
    """Consolidated tests for filtering cases by multiple fields, including similar-case query."""
    adapter = real_adapter

    # -----------------------------
    # GIVEN a database with case, user, and institute
    # -----------------------------
    adapter.case_collection.insert_one(case_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.variant_collection.insert_one(variant_obj)

    # -----------------------------
    # THEN search by display name should work
    # -----------------------------
    name_query = ImmutableMultiDict({"case": case_obj["display_name"]})
    cases = list(adapter.cases(collaborator=case_obj["owner"], name_query=name_query))
    assert len(cases) == 1

    # -----------------------------
    # THEN search by case individual should work
    # -----------------------------
    CASE_INDIVIDUALS = [{"individual_id": "test", "display_name": "test_name"}]
    case_obj["individuals"] = CASE_INDIVIDUALS
    adapter.update_case(case_obj)
    name_query = ImmutableMultiDict({"case": "test_name"})
    cases = list(adapter.cases(collaborator=case_obj["owner"], name_query=name_query))
    assert len(cases) == 1

    # -----------------------------
    # Search by synopsis should work
    # -----------------------------
    updated_case = adapter.update_synopsis(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="link",
        content="Recurrent seizures",
    )
    name_query = ImmutableMultiDict({"synopsis": "seizures"})
    cases = list(adapter.cases(collaborator=updated_case["owner"], name_query=name_query))
    assert len(cases) == 1

    # -----------------------------
    # THEN search by status should return work
    # -----------------------------
    adapter.update_status(institute_obj, updated_case, user_obj, "active", "reason")
    name_query = ImmutableMultiDict({"status": "active"})
    cases = list(adapter.cases(collaborator=case_obj["owner"], name_query=name_query))
    assert len(cases) == 1

    # -----------------------------
    # THEN search by research cases should work
    # -----------------------------
    case_obj["is_research"] = True
    adapter.update_case(case_obj)
    cases = list(adapter.cases(owner=case_obj["owner"], is_research=True))
    assert len(cases) == 1

    # -----------------------------
    # THEN search by phenotype should work
    # -----------------------------
    case_obj["phenotype_terms"] = test_hpo_terms
    adapter.update_case(case_obj)
    name_query = ImmutableMultiDict({"exact_pheno": test_hpo_terms[0]["phenotype_id"]})
    cases = list(adapter.cases(collaborator=case_obj["owner"], name_query=name_query))
    assert len(cases) == 1

    # -----------------------------
    # THEN search by cohorts should work
    # -----------------------------
    TEST_COHORT = "cohort 1"
    adapter.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"cohorts": [TEST_COHORT]}}
    )
    cases = list(
        adapter.cases(
            collaborator=case_obj["owner"], name_query=ImmutableMultiDict({"cohort": TEST_COHORT})
        )
    )
    assert len(cases) == 1

    # -----------------------------
    # THEN search by tags should work
    # -----------------------------
    TEST_TAG = "diagnostic"
    adapter.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"tags": [TEST_TAG]}}
    )
    cases = list(
        adapter.cases(
            collaborator=case_obj["owner"], name_query=ImmutableMultiDict({"tags": TEST_TAG})
        )
    )
    assert len(cases) == 1

    # -----------------------------
    # THEN search by phenotype terms should work
    # -----------------------------
    HPO_TERM = "HP:0002315"
    PHENO_TERM = [{"phenotype_id": HPO_TERM, "feature": "headache"}]
    adapter.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"phenotype_terms": PHENO_TERM}}
    )
    name_query = ImmutableMultiDict({"exact_pheno": ",".join([HPO_TERM])})
    cases = list(adapter.cases(collaborator=case_obj["owner"], name_query=name_query))
    assert len(cases) == 1

    # -----------------------------
    # THEN search by diagnosis should work
    # -----------------------------
    OMIM_TERM = "OMIM:607745"
    adapter.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]},
        {
            "$set": {
                "diagnosis_phenotypes": [
                    {
                        "disease_nr": 607745,
                        "disease_id": OMIM_TERM,
                        "description": "Seizures, benign familial infantile, 3",
                    }
                ]
            }
        },
    )
    name_query = ImmutableMultiDict({"exact_dia": ",".join([OMIM_TERM])})
    cases = list(adapter.cases(collaborator=case_obj["owner"], name_query=name_query))
    assert len(cases) == 1

    # -----------------------------
    # THEN search by assignee should work
    # -----------------------------
    adapter.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"assignees": [user_obj["email"]]}}
    )
    name_query = ImmutableMultiDict({"user": user_obj["name"]})
    cases = list(adapter.cases(collaborator=case_obj["owner"], name_query=name_query))
    assert len(cases) == 1

    # -----------------------------
    # THEN search by solved within days should work
    # -----------------------------
    adapter.mark_causative(institute_obj, case_obj, user_obj, "link", variant_obj)
    cases = list(adapter.cases(collaborator=case_obj["owner"], finished=True, within_days=1))
    assert len(cases) == 1

    # -----------------------------
    # THEN search by verification missing should work
    # -----------------------------
    adapter.order_verification(institute_obj, case_obj, user_obj, "link", variant_obj)
    cases = adapter.verification_missing_cases(institute_obj["_id"])
    assert len(cases) == 1

    # -----------------------------
    # WHEN case has causatives THEN search by causatives should return it
    # -----------------------------
    cases = list(adapter.cases(collaborator=case_obj["owner"], has_causatives=True))
    assert len(cases) == 1
    assert cases[0]["causatives"]

    # -----------------------------
    # WHEN case has no causatives THEN search result should be empty
    # -----------------------------
    adapter.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"causatives": []}}
    )
    cases = list(adapter.cases(collaborator=case_obj["owner"], has_causatives=True))
    assert len(cases) == 0

    # -----------------------------
    # THEN search by cases with associated RNA should work
    # -----------------------------
    assert adapter.rna_cases(owner=case_obj["owner"]) == [case_obj["_id"]]

    # -----------------------------
    # WHEN querying for a similar case
    # -----------------------------
    # Insert another case with slightly different phenotype
    case_2 = copy.deepcopy(case_obj)
    case_2["_id"] = "case_2"
    case_2["phenotype_terms"] = test_hpo_terms[:-1]  # exclude last term
    adapter.case_collection.insert_one(case_2)

    # THEN similar-case query should return only case_2
    name_query = ImmutableMultiDict({"similar_case": case_obj["display_name"]})
    similar_cases = list(adapter.cases(collaborator=case_obj["owner"], name_query=name_query))
    similar_cases = [c for c in similar_cases if c["_id"] != case_obj["_id"]]
    assert len(similar_cases) == 1
    assert similar_cases[0]["_id"] == "case_2"


def test_update_case_rerun_status(
    adapter: MongoAdapter,
    case_obj: Dict[str, Any],
    institute_obj: Dict[str, Any],
    user_obj: Dict[str, Any],
) -> None:
    """Test archiving a case, requesting rerun, and resetting rerun status."""

    # GIVEN a fresh case in the database
    adapter.case_collection.insert_one(case_obj)
    stored_case = adapter.case(case_obj["_id"])
    assert stored_case["status"] == "inactive"

    # WHEN archiving the case
    adapter.archive_case(institute_obj, stored_case, user_obj, link="blank")
    archived_case = adapter.case(case_obj["_id"])
    assert archived_case["status"] == "archived"

    # WHEN requesting rerun
    adapter.update_rerun_status(institute_obj, archived_case, user_obj, link="blank")
    rerun_case = adapter.case(case_obj["_id"])
    assert rerun_case["rerun_requested"] is True
    assert rerun_case["status"] == "archived"
    assert user_obj["email"] in rerun_case["assignees"]

    # WHEN resetting rerun
    adapter.update_rerun_status(institute_obj, rerun_case, user_obj, link="blank")

    # THEN rerun is reset
    refreshed_case = adapter.case(case_obj["_id"])
    assert refreshed_case["rerun_requested"] is False
    # AND status is still archived until case is explicitly updated
    assert refreshed_case["status"] == "archived"

    # WHEN updating case explicitly
    updated_case = adapter.update_case(case_obj)

    # THEN case is inactivated
    assert updated_case["status"] == "inactive"


@pytest.mark.parametrize("initial_dynamic_list", [[], {}])
def test_update_dynamic_gene_list(
    gene_database: MongoAdapter, case_obj: Dict[str, Any], initial_dynamic_list
) -> None:
    """Updating dynamic_gene_list should work from both empty list and invalid dict."""

    adapter = gene_database

    # GIVEN a case with a specific initial dynamic_gene_list
    case_obj["dynamic_gene_list"] = initial_dynamic_list
    adapter.case_collection.insert_one(case_obj)
    stored_case = adapter.case(case_obj["_id"])
    assert stored_case
    assert len(stored_case["dynamic_gene_list"]) == 0

    # GIVEN a gene with a gene symbol in the gene DB
    gene_obj = adapter.hgnc_collection.find_one({"build": "37"})
    assert gene_obj
    hgnc_symbol = gene_obj["hgnc_symbol"]

    # WHEN updating dynamic gene list with that gene
    adapter.update_dynamic_gene_list(case_obj, hgnc_symbols=[hgnc_symbol])

    # THEN the gene list will contain one entry
    updated_case = adapter.case(case_obj["_id"])
    assert len(updated_case["dynamic_gene_list"]) == 1


@pytest.mark.parametrize(
    "update_func, tag_field, tag_value",
    [
        ("update_manual_rank", "manual_rank", 8),
        ("update_dismiss_variant", "dismiss_variant", [2, 11]),
        ("update_mosaic_tags", "mosaic_tags", [1, 3]),
        ("update_cancer_tier", "cancer_tier", "2B"),
        ("update_acmg", "acmg_classification", "likely_pathogenic"),
        ("update_ccv", "ccv_classification", "likely_oncogenic"),
    ],
)
def test_variant_tags_after_reupload(
    adapter: MongoAdapter,
    case_obj: Dict[str, Any],
    variant_obj: Dict[str, Any],
    user_obj: Dict[str, Any],
    institute_obj: Dict[str, Any],
    update_func: str,
    tag_field: str,
    tag_value: Any,
) -> None:
    """Test updating variant custom tags after reupload."""
    old_variant = copy.deepcopy(variant_obj)
    old_variant["_id"] = "old_id"

    # GIVEN a database with  case, user, and variant
    adapter.user_collection.insert_one(user_obj)
    adapter.case_collection.insert_one(case_obj)
    adapter.variant_collection.insert_one(old_variant)

    func = getattr(adapter, update_func)
    if update_func in ["update_manual_rank", "update_cancer_tier"]:
        updated_old = func(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link="link",
            variant=old_variant,
            **(
                {"tier_field": "cancer_tier", "tier_value": tag_value}
                if update_func == "update_cancer_tier"
                else {"manual_rank": tag_value}
            ),
        )
    elif update_func in ["update_acmg", "update_ccv"]:
        updated_old = func(
            institute_obj=institute_obj,
            case_obj=case_obj,
            user_obj=user_obj,
            link="link",
            variant_obj=old_variant,
            **({"acmg_str": tag_value} if update_func == "update_acmg" else {"ccv_str": tag_value}),
        )
    else:
        updated_old = func(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link="link",
            variant=old_variant,
            **(
                {"dismiss_variant": tag_value}
                if update_func == "update_dismiss_variant"
                else {"mosaic_tags": tag_value}
            ),
        )

    adapter.variant_collection.delete_one(old_variant)
    new_variant = variant_obj
    new_variant["_id"] = "new_id"
    adapter.variant_collection.insert_one(new_variant)

    # THEN after reupload, the tags should be conserved
    updated_new = adapter.update_variant_actions(case_obj=case_obj, old_eval_variants=[updated_old])
    assert updated_new[tag_field] == ["new_id"]

    test_variant = adapter.variant_collection.find_one({"_id": "new_id"})
    if update_func in ["update_acmg", "update_ccv"]:
        expected = (
            REV_ACMG_MAP[tag_value] if update_func == "update_acmg" else REV_CCV_MAP[tag_value]
        )
        assert test_variant[tag_field] == expected
    else:
        assert test_variant[tag_field] == tag_value


def test_keep_variant_comments_after_reupload(
    adapter: MongoAdapter,
    case_obj: Dict[str, Any],
    variant_obj: Dict[str, Any],
    user_obj: Dict[str, Any],
    institute_obj: Dict[str, Any],
) -> None:
    """Test that comments of old variants are preserved on new variants after re-upload."""

    # Create a copy of the variant representing the old version
    old_variant = copy.deepcopy(variant_obj)
    old_variant["_id"] = "old_id"
    old_variant["is_commented"] = True

    ## GIVEN a database with a user
    adapter.user_collection.insert_one(user_obj)

    ## AND a case
    adapter.case_collection.insert_one(case_obj)

    # AND a variant with a local comment
    adapter.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="variant_link",
        variant=old_variant,
        content="Hello, locally",
        comment_level="specific",
    )

    # AND a global comment
    adapter.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="variant_link",
        variant=old_variant,
        content="Hello, globally",
        comment_level="global",
    )

    # Ensure the database contains exactly 2 comments
    assert adapter.event_collection.count_documents({}) == 2

    # WHEN the old variant is removed and a new one is inserted
    adapter.variant_collection.delete_one({"_id": old_variant["_id"]})

    new_variant = copy.deepcopy(variant_obj)
    new_variant["_id"] = "new_id"
    adapter.variant_collection.insert_one(new_variant)

    # THEN update_variant_actions should link comments to the new variant
    updated_new_vars = adapter.update_variant_actions(
        case_obj=case_obj,
        old_eval_variants=[old_variant],
    )
    assert updated_new_vars["is_commented"] == [new_variant["_id"]]

    # AND no additional comments should be created
    assert adapter.event_collection.count_documents({}) == 2


def test_update_case_collaborators_individuals(adapter: Any, case_obj: Dict[str, Any]) -> None:
    """Test updating case collaborators and individuals."""
    adapter.case_collection.insert_one(case_obj)
    assert adapter.case_collection.find_one()

    coll_1 = case_obj["collaborators"][0]
    coll_2 = "test"
    coll_3 = "test2"
    case_obj["collaborators"].extend([coll_2, coll_3])
    res = adapter.update_case(case_obj)
    assert set(res["collaborators"]) == {coll_1, coll_2, coll_3}

    new_individuals = [{"individual_id": "test", "display_name": "test_name"}]
    case_obj["individuals"] = new_individuals
    res = adapter.update_case(case_obj)
    assert len(res["individuals"]) == 1


def test_delete_and_archive_cases(
    adapter: MongoAdapter, case_obj: dict, institute_obj: dict, user_obj: dict
) -> None:
    """Test case deletion, archiving, and unarchiving behaviors."""

    # GIVEN an empty database
    assert adapter.case_collection.find_one() is None

    # Insert case, user, and institute
    adapter.case_collection.insert_one(case_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.institute_collection.insert_one(institute_obj)
    assert adapter.case_collection.find_one()

    # --- ARCHIVE ---
    adapter.update_status(
        institute=institute_obj, case=case_obj, user=user_obj, status="archived", link="blank"
    )
    archived_case = adapter.case(case_obj["_id"])
    assert archived_case["status"] == "archived"

    # --- UNARCHIVE ---
    case_obj["assignees"] = []
    adapter.update_status(
        institute=institute_obj, case=archived_case, user=user_obj, status="active", link="blank"
    )
    unarchived_case = adapter.case(case_obj["_id"])
    assert unarchived_case["status"] == "active"
    assert user_obj["email"] in unarchived_case["assignees"]

    # --- DELETE BY ID ---
    adapter.delete_case(case_id=case_obj["_id"])
    assert adapter.case_collection.find_one() is None

    # Re-insert to test delete by display_name
    adapter.case_collection.insert_one(case_obj)
    adapter.delete_case(institute_id=case_obj["owner"], display_name=case_obj["display_name"])
    assert adapter.case_collection.find_one() is None


import pytest


@pytest.mark.parametrize(
    "case_obj",
    [
        {
            "_id": "old_case",
            "owner": "inst1",
            "suspects": ["var1", "var2"],
            "causatives": ["var3"],
        },
        {
            "_id": "old_case2",
            "owner": "inst2",
            "suspects": [],
            "causatives": [],
        },
    ],
)
def test_update_caseid(adapter, mocker, case_obj, variant_obj):
    """Test updating case ID across the database, keeping variant IDs unchanged."""

    FAMILY_ID = "new_case_id"

    # GIVEN mock helper and db event calls
    def fake_variant(variant_id):
        return {"_id": variant_id}

    # Patch get_variantid to return original variant ID (no "_new")
    def fake_get_variantid(variant, family_id):
        return variant["_id"]

    # Mock external methods and collections
    adapter.variant = mocker.MagicMock(side_effect=fake_variant)
    adapter.acmg_collection = mocker.MagicMock()
    adapter.ccv_collection = mocker.MagicMock()
    adapter.event_collection = mocker.MagicMock()
    adapter.case_collection = mocker.MagicMock()
    adapter.institute = mocker.MagicMock(return_value={"_id": case_obj["owner"]})
    adapter.events = mocker.MagicMock(return_value=[{"_id": "evt1", "verb": "updated"}])

    # GIVEN mock find() to return fake objects for ACMG and CCV
    adapter.acmg_collection.find.return_value = [
        {"_id": "acmg1", "classification": "Pathogenic", "variant_specific": "var1"}
    ]
    adapter.ccv_collection.find.return_value = [
        {"_id": "ccv1", "classification": "Likely pathogenic", "variant_specific": "var3"}
    ]

    mocker.patch("scout.adapter.mongo.case.get_variantid", side_effect=fake_get_variantid)

    # WHEN update_caseid is called
    new_case = adapter.update_caseid(case_obj, FAMILY_ID)

    # THEN new case should have the new family ID
    assert new_case["_id"] == FAMILY_ID

    # THEN suspects and causatives should retain original IDs
    assert new_case.get("suspects", []) == case_obj.get("suspects", [])
    assert new_case.get("causatives", []) == case_obj.get("causatives", [])

    # THEN ACMG and CCV collections should be updated
    adapter.acmg_collection.find_one_and_update.assert_called_with(
        {"_id": "acmg1"},
        {"$set": {"case_id": FAMILY_ID, "variant_specific": "var1"}},
    )
    adapter.ccv_collection.find_one_and_update.assert_called_with(
        {"_id": "ccv1"},
        {"$set": {"case_id": FAMILY_ID, "variant_specific": "var3"}},
    )

    # THEN events should be updated with new case ID
    adapter.event_collection.find_one_and_update.assert_called_with(
        {"_id": "evt1"}, {"$set": {"case": FAMILY_ID}}
    )

    # THEN old case should be deleted
    adapter.case_collection.find_one_and_delete.assert_called_with({"_id": case_obj["_id"]})

    # AND new case should be inserted
    adapter.case_collection.insert_one.assert_called_with(new_case)
