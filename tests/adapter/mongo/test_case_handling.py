import logging
from typing import Any, Dict, List

from scout.constants import REV_ACMG_MAP, REV_CCV_MAP

logger = logging.getLogger(__name__)

import copy

import pytest
from werkzeug.datastructures import ImmutableMultiDict

from scout.exceptions import IntegrityError


def test_add_and_get_case(adapter, case_obj: Dict[str, Any], institute_obj: Dict[str, Any]) -> None:
    """Test adding, retrieving, and preventing duplicate cases."""

    ## GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None

    ## WHEN adding a new case to the database
    adapter.add_case(case_obj, institute_obj)
    loaded_case = adapter.case_collection.find_one({"_id": case_obj["_id"]})
    assert loaded_case["owner"] == case_obj["owner"]
    assert loaded_case["rank_model_version"] == case_obj["rank_model_version"]
    assert loaded_case["sv_rank_model_version"] == case_obj["sv_rank_model_version"]

    # Adding same case again raises IntegrityError
    with pytest.raises(IntegrityError):
        adapter.add_case(case_obj, institute_obj)

    # Retrieving a non-existing case returns None
    assert adapter.case(case_id="non_existing") is None


def test_load_case_integrity(
    adapter, institute_obj: Dict[str, Any], case_obj: Dict[str, Any]
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


def test_case_queries(
    real_adapter: Any,
    hpo_database: Any,
    test_hpo_terms: List[Dict[str, Any]],
    case_obj: Dict[str, Any],
    institute_obj: Dict[str, Any],
    user_obj: Dict[str, Any],
    variant_obj: Dict[str, Any],
) -> None:
    """Consolidated tests for filtering cases by multiple fields."""
    adapter = real_adapter

    # GIVEN a database with  case, user, and institute
    adapter.case_collection.insert_one(case_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.variant_collection.insert_one(variant_obj)

    # Search by synopsis should work
    updated_case = adapter.update_synopsis(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="link",
        content="Recurrent seizures",
    )

    name_query = ImmutableMultiDict({"synopsis": "seizures"})
    syn_cases = list(adapter.cases(collaborator=updated_case["owner"], name_query=name_query))
    assert len(syn_cases) == 1

    # Search by status should return work
    adapter.update_status(institute_obj, updated_case, user_obj, "active", "reason")
    name_query = ImmutableMultiDict({"status": "active"})
    active_cases = list(adapter.cases(collaborator=case_obj["owner"], name_query=name_query))
    assert len(active_cases) == 1

    # Search by research cases should work
    case_obj["is_research"] = True
    adapter.update_case(case_obj)
    research_cases = list(adapter.cases(owner=case_obj["owner"], is_research=True))
    assert len(research_cases) == 1

    # Search by phenotype should work
    case_obj["phenotype_terms"] = test_hpo_terms
    adapter.update_case(case_obj)
    name_query = ImmutableMultiDict({"exact_pheno": test_hpo_terms[0]["phenotype_id"]})
    pheno_cases = list(adapter.cases(collaborator=case_obj["owner"], name_query=name_query))
    assert len(pheno_cases) == 1

    # Search by cohorts should work
    TEST_COHORT = "cohort1"
    adapter.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"cohorts": [TEST_COHORT]}}
    )
    cohort_cases = list(adapter.cases(name_query=ImmutableMultiDict({"cohort": TEST_COHORT})))
    assert len(cohort_cases) == 1

    # Search by tags should work
    TEST_TAG = "diagnostic"
    adapter.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]}, {"$set": {"tags": [TEST_TAG]}}
    )
    tags_cases = list(adapter.cases(name_query=ImmutableMultiDict({"tags": "diagnostic"})))
    assert len(tags_cases) == 1

    # Search by solved within days should work
    adapter.mark_causative(institute_obj, case_obj, user_obj, "link", variant_obj)
    solved_cases = list(adapter.cases(finished=True, within_days=1))
    assert len(solved_cases) == 1

    # Search by verification missing should work
    adapter.order_verification(institute_obj, case_obj, user_obj, "link", variant_obj)
    missing_verifications = adapter.verification_missing_cases(institute_obj["_id"])
    assert len(missing_verifications) == 1

    # Search by cases with associated RNS should work
    assert adapter.rna_cases(owner=case_obj["owner"]) == [case_obj["_id"]]


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
    adapter: Any,
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
    adapter: Any, case_obj: dict, institute_obj: dict, user_obj: dict
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
