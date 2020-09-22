# -*- coding: utf-8 -*-
import pytest
import copy
import pymongo
import logging
from pprint import pprint as pp

from scout.constants import INDEXES, REV_ACMG_MAP
from scout.exceptions import IntegrityError

logger = logging.getLogger(__name__)


def test_add_cases(adapter, case_obj):
    ## GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None

    ## WHEN adding a new case to the database
    adapter._add_case(case_obj)

    ## THEN it should be populated with the new case
    result = adapter.cases()
    assert sum(1 for i in result) == 1
    for case in result:
        assert case["owner"] == case_obj["owner"]


def test_add_existing_case(adapter, case_obj):
    ## GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None

    adapter._add_case(case_obj)
    ## WHEN adding a existing case to the database
    with pytest.raises(IntegrityError):
        ## THEN it should raise integrity error
        adapter._add_case(case_obj)


def test_get_case(adapter, case_obj):
    ## GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None
    adapter.case_collection.insert_one(case_obj)
    logger.info("Testing to get case")

    ## WHEN retreiving an existing case from the database
    result = adapter.case(case_id=case_obj["_id"])
    ## THEN we should get the correct case
    assert result["owner"] == case_obj["owner"]


def test_get_cases(adapter, case_obj):
    ## GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None
    adapter.case_collection.insert_one(case_obj)
    ## WHEN retreiving an existing case from the database
    result = adapter.cases()
    ## THEN we should get the correct case
    assert sum(1 for i in result) == 1


def test_get_prioritized_cases(adapter, case_obj, institute_obj):
    ## GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None
    # WHEN inserting a prioritized case
    case_obj["status"] = "prioritized"
    adapter.case_collection.insert_one(case_obj)

    # WHEN retrieving prioritized casese for the institute
    result = adapter.prioritized_cases(institute_id=institute_obj["_id"])

    # THEN one prioritized case is returned
    assert sum(1 for i in result) == 1


def test_nr_cases(adapter, case_obj):
    ## GIVEN an empty database (no cases)
    ## WHEN adding one case to the case collection
    adapter.case_collection.insert_one(case_obj)
    ## THEN the function nr_cases should return number of cases = 1
    result = adapter.nr_cases(institute_id=case_obj["owner"])
    assert result == 1


def test_search_active_case(real_adapter, case_obj, institute_obj, user_obj):
    adapter = real_adapter

    ## GIVEN a real database with no cases
    assert adapter.case_collection.find_one() is None

    ## When inserting a case
    adapter.case_collection.insert_one(case_obj)
    assert adapter.case_collection.find_one()

    # WHEN flagging the case as active
    adapter.update_status(institute_obj, case_obj, user_obj, "active", "blank")

    # WHEN querying for active cases,
    name_query = "status:active"
    # THEN a case should be returned
    cases = adapter.cases(collaborator=case_obj["owner"], name_query=name_query)
    assert sum(1 for i in cases) == 1

    # BUT WHEN querying for inactive cases
    name_query = "status:inactive"
    # THEN no case should be returned.
    inactive_cases = adapter.cases(collaborator=case_obj["owner"], name_query=name_query)
    assert sum(1 for i in inactive_cases) == 0


def test_get_research_case(real_adapter, case_obj, institute_obj):
    adapter = real_adapter

    # GIVEN a real database with no cases
    assert adapter.case_collection.find_one() is None

    # WHEN flagging case_obj as research
    case_obj["is_research"] = True

    # AND WHEN inserting such case
    adapter.case_collection.insert_one(case_obj)
    ## THEN assert that the case was inserted
    assert adapter.case_collection.find_one()

    # THEN searching for reasearch cases should return one case
    research_cases = adapter.cases(owner=case_obj["owner"], is_research=True)
    assert sum(1 for i in research_cases) == 1


def test_get_cases_no_synopsis(real_adapter, case_obj, institute_obj, user_obj):

    adapter = real_adapter
    # GIVEN a real database with no cases
    assert adapter.case_collection.find_one() is None

    # Insert a case
    adapter.case_collection.insert_one(case_obj)
    assert sum(1 for i in adapter.case_collection.find()) == 1

    # WHEN providing an empty value for synopsis:
    assert case_obj["synopsis"] == ""
    name_query = "synopsis:"
    # Then case should be returned
    cases = adapter.cases(collaborator=case_obj["owner"], name_query=name_query)
    assert sum(1 for i in cases) == 1

    # After adding synopsis to case
    link = "synopsislink"
    synopsis = "Recurrent seizures"
    updated_case = adapter.update_synopsis(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        content=synopsis,
    )

    # WHEN providing an empty value for synopsis:
    assert case_obj["synopsis"] == ""
    name_query = "synopsis:"
    # Then case should NOT be returned
    cases = adapter.cases(collaborator=case_obj["owner"], name_query=name_query)
    assert sum(1 for i in cases) == 0

    # but if a term contained in case synopsis is provided in name query:
    name_query = "synopsis:seizures"

    # Then updated case should be returned
    cases = adapter.cases(collaborator=updated_case["owner"], name_query=name_query)
    assert sum(1 for i in cases) == 1


def test_get_cases_no_HPO(adapter, case_obj):
    # GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None
    adapter.case_collection.insert_one(case_obj)

    # WHEN providing an empty value for term HP:
    name_query = "exact_pheno:"
    # Then case should be returned
    cases = adapter.cases(collaborator=case_obj["owner"], name_query=name_query)
    assert sum(1 for i in cases) == 1

    # WHEN providing an empty value for phenotype group:
    name_query = "pheno_group:"
    # Then case should be returned
    cases = adapter.cases(collaborator=case_obj["owner"], name_query=name_query)
    assert sum(1 for i in cases) == 1

    # Add phenotype group and HPO term to case object:
    adapter.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]},
        {
            "$set": {
                "phenotype_groups": [{"phenotype_id": "test_pg"}],
                "phenotype_terms": [{"phenotype_id": "test_hp"}],
            }
        },
    )
    # WHEN providing an empty value for term HP:
    name_query = "exact_pheno:"
    # Then case should NOT be returned
    cases = adapter.cases(collaborator=case_obj["owner"], name_query=name_query)
    assert sum(1 for i in cases) == 0

    # WHEN providing an empty value for phenotype group:
    name_query = "pheno_group:"
    # Then case should NOT be returned
    cases = adapter.cases(collaborator=case_obj["owner"], name_query=name_query)
    assert sum(1 for i in cases) == 0


def test_get_cases_no_assignees(real_adapter, case_obj):
    adapter = real_adapter
    # GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None
    adapter.case_collection.insert_one(case_obj)
    # WHEN retreiving an existing case from the database
    result = adapter.cases(name_query="user:john")
    # THEN we should get the correct case
    assert sum(1 for i in result) == 0


def test_get_cases_display_name(real_adapter, case_obj):
    adapter = real_adapter
    # GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None
    adapter.case_collection.insert_one(case_obj)

    other_case = case_obj
    other_case["_id"] = "other_case"
    other_case["display_name"] = "other_case"
    adapter.case_collection.insert_one(other_case)

    # WHEN retreiving cases by partial display name
    result = adapter.cases(name_query="case:643")
    # THEN we should get the correct case
    assert sum(1 for i in result) == 1


def test_get_cases_existing_individual(real_adapter, case_obj):
    adapter = real_adapter
    # GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None
    adapter.case_collection.insert_one(case_obj)
    # WHEN retreiving cases by partial individual name
    result = adapter.cases(name_query="case:NA1288")
    # THEN we should get the correct case
    assert sum(1 for i in result) == 1


def test_get_cases_assignees(real_adapter, case_obj, user_obj):
    adapter = real_adapter
    # GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None

    adapter.user_collection.insert_one(user_obj)

    user_obj = adapter.user_collection.find_one()
    case_obj["assignees"] = [user_obj["email"]]
    adapter.case_collection.insert_one(case_obj)

    # WHEN retreiving cases by partial individual name
    result = adapter.cases(name_query="user:john")
    # THEN we should get the correct case
    assert sum(1 for i in result) == 1


def test_get_cases_non_existing_assignee(real_adapter, case_obj, user_obj):
    adapter = real_adapter
    # GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None

    adapter.user_collection.insert_one(user_obj)

    user_obj = adapter.user_collection.find_one()
    case_obj["assignees"] = [user_obj["email"]]
    adapter.case_collection.insert_one(case_obj)

    # WHEN retreiving cases by partial individual name
    result = adapter.cases(name_query="user:damien")
    # THEN we should get the correct case
    assert sum(1 for i in result) == 0


def test_get_cases_causatives(adapter, case_obj):
    # GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None

    # Add a causative
    case_obj["causatives"] = ["a variant"]
    # Insert the case
    adapter.case_collection.insert_one(case_obj)

    # WHEN retreiving cases that have causatives
    result = adapter.cases(has_causatives=True)
    # THEN we should find one case
    assert sum(1 for i in result) == 1


def test_get_cases_causatives_no_causatives(adapter, case_obj):
    # GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None

    # Insert a case without causatives
    adapter.case_collection.insert_one(case_obj)

    # WHEN retreiving all cases that have causatives
    result = adapter.cases(has_causatives=True)
    # THEN we should get the correct case
    assert sum(1 for i in result) == 0


def test_get_cases_empty_causatives(adapter, case_obj):
    # GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None

    # Add a empty list as causatives
    case_obj["causatives"] = []
    # Insert the case
    adapter.case_collection.insert_one(case_obj)

    # WHEN retreiving all cases that have causatives
    result = adapter.cases(has_causatives=True)
    # THEN we should not find any cases
    assert sum(1 for i in result) == 0


def test_get_cases_non_existing_display_name(real_adapter, case_obj):
    adapter = real_adapter
    # GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None
    adapter.case_collection.insert_one(case_obj)
    # WHEN retreiving cases by partial display name
    result = adapter.cases(name_query="case:hello")
    # THEN we should get the correct case
    assert sum(1 for i in result) == 0


def test_get_non_existing_case(adapter, case_obj):
    # GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None
    adapter._add_case(case_obj)
    logger.info("Testing to get case")

    # WHEN retreiving an non existing case from the database
    result = adapter.case(case_id="hello")
    # THEN we should get None back
    assert result is None


def test_delete_case_by_id(adapter, case_obj):
    # GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None
    adapter.case_collection.insert_one(case_obj)

    # WHEN deleting a case from the database using case _id
    result = adapter.delete_case(case_id=case_obj["_id"])
    # THEN there should be no cases left in the database
    assert sum(1 for i in adapter.cases()) == 0


def test_delete_case_by_display_name(adapter, case_obj):
    # GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None
    adapter.case_collection.insert_one(case_obj)

    # WHEN deleting a case from the database using display_name
    result = adapter.delete_case(
        institute_id=case_obj["owner"], display_name=case_obj["display_name"]
    )
    # THEN there should be no cases left in the database
    assert sum(1 for i in adapter.cases()) == 0


def test_update_case_collaborators(adapter, case_obj):
    # GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None
    adapter.case_collection.insert_one(case_obj)
    assert adapter.case_collection.find_one()
    assert len(adapter.case(case_obj["_id"])["collaborators"]) == 1
    logger.info("Testing to update case")

    coll_1 = case_obj["collaborators"][0]
    coll_2 = "test"
    coll_3 = "test2"
    case_obj["collaborators"].append(coll_2)
    case_obj["collaborators"].append(coll_3)

    # WHEN updating a case with new collaborators
    res = adapter.update_case(case_obj)

    # THEN assert collaborator has been added
    assert len(res["collaborators"]) == 3
    # THEN assert all collaborators where added
    assert set(res["collaborators"]) == set([coll_1, coll_2, coll_3])


def test_update_dynamic_gene_list(gene_database, case_obj):
    # GIVEN an populated gene database,
    adapter = gene_database

    # GIVEN a case with an empty dynamic_gene_list
    adapter.case_collection.insert_one(case_obj)
    assert adapter.case_collection.find_one()
    assert len(adapter.case(case_obj["_id"])["dynamic_gene_list"]) == 0

    # GIVEN a gene with a gene symobl
    gene_obj = gene_database.hgnc_collection.find_one({"build": "37"})
    assert gene_obj
    hgnc_symbol = gene_obj.get("hgnc_symbol")
    assert hgnc_symbol

    # WHEN updating dynamic gene list with gene
    adapter.update_dynamic_gene_list(case_obj, hgnc_symbols=[hgnc_symbol])
    # THEN a the gene list will contain a gene
    assert len(adapter.case(case_obj["_id"])["dynamic_gene_list"]) == 1


def test_update_dynamic_gene_list_with_bad_dict_entry(gene_database, case_obj):

    # GIVEN an populated gene database,
    adapter = gene_database

    # GIVEN an **incorrectly** assigned dict instead of list as dynamic panel
    case_obj["dynamic_gene_list"] = {}

    # GIVEN a case with an empty dynamic_gene_list
    adapter.case_collection.insert_one(case_obj)
    assert adapter.case_collection.find_one()
    assert len(adapter.case(case_obj["_id"])["dynamic_gene_list"]) == 0

    # GIVEN a gene with a gene symobl
    gene_obj = gene_database.hgnc_collection.find_one({"build": "37"})
    assert gene_obj
    hgnc_symbol = gene_obj.get("hgnc_symbol")
    assert hgnc_symbol

    # WHEN updating dynamic gene list with gene
    adapter.update_dynamic_gene_list(case_obj, hgnc_symbols=[hgnc_symbol])
    # THEN a the gene list will contain a gene
    assert len(adapter.case(case_obj["_id"])["dynamic_gene_list"]) == 1


def test_update_case_individuals(adapter, case_obj):
    # GIVEN an empty database (no cases)
    assert adapter.case_collection.find_one() is None
    adapter.case_collection.insert_one(case_obj)
    assert adapter.case_collection.find_one()
    logger.info("Testing to update case")

    res = adapter.case(case_obj["_id"])
    assert len(res["individuals"]) == 3

    new_individuals = [{"individual_id": "test", "display_name": "test_name"}]
    case_obj["individuals"] = new_individuals
    # WHEN updating a case with new individuals
    res = adapter.update_case(case_obj)
    # THEN assert that 'individuals' has changed

    assert len(res["individuals"]) == 1


def test_archive_unarchive_case(adapter, case_obj, institute_obj, user_obj):
    ## GIVEN an empty adapter
    assert adapter.case_collection.find_one() is None

    ## WHEN inserting case, user and institute
    adapter.case_collection.insert_one(case_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.institute_collection.insert_one(institute_obj)
    ## THEN assert that a case was inserted
    assert adapter.case_collection.find_one()

    # Test that when case is unarchived the users gets assigned to it:
    # flag case as 'archived'
    adapter.update_status(institute_obj, case_obj, user_obj, "archived", "blank")
    res = adapter.case(case_obj["_id"])
    assert res["status"] == "archived"

    # if user decides to unarchive it
    case_obj["assignees"] = []
    adapter.update_status(institute_obj, res, user_obj, "active", "blank")
    res = adapter.case(case_obj["_id"])
    # case becomes active
    assert res["status"] == "active"
    # and user becomes assignee
    assert user_obj["email"] in res["assignees"]


def test_update_case_rerun_status(adapter, case_obj, institute_obj, user_obj):

    # GIVEN an empty database (no cases)
    assert sum(1 for i in adapter.cases()) == 0
    adapter.case_collection.insert_one(case_obj)
    assert sum(1 for i in adapter.cases()) == 1

    res = adapter.case(case_obj["_id"])
    assert res["status"] == "inactive"

    # archive case
    adapter.archive_case(institute_obj, res, user_obj, "blank")
    res = adapter.case(case_obj["_id"])
    # and make sure it's archived
    assert res["status"] == "archived"

    # request rerun for test case
    adapter.request_rerun(institute_obj, res, user_obj, "blank")
    res = adapter.case(case_obj["_id"])
    # THEN rerun_requested is flagged
    assert res["rerun_requested"] is True
    # Make sure case is still archived
    assert res["status"] == "archived"

    # Make sure user becomes assignee of the case
    assert user_obj["email"] in res["assignees"]

    # And that a new rerun request triggers an error:
    with pytest.raises(ValueError):
        adapter.request_rerun(institute_obj, res, user_obj, "blank")

    # and WHEN updating the case again
    res = adapter.update_case(case_obj)

    # THEN it is inactivated
    res = adapter.case(case_obj["_id"])
    assert res["status"] == "inactive"


def test_cases_by_phenotype(hpo_database, test_hpo_terms, case_obj):
    adapter = hpo_database

    # Make sure database contains HPO terms
    assert sum(1 for i in adapter.hpo_terms())

    # update test case using test HPO terms
    case_obj["phenotype_terms"] = test_hpo_terms
    adapter.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]},
        {"$set": {"phenotype_terms": test_hpo_terms}},
        return_document=pymongo.ReturnDocument.AFTER,
    )
    # insert case into database
    adapter.case_collection.insert_one(case_obj)
    assert sum(1 for i in adapter.case_collection.find()) == 1

    # Add another case with slightly different phenotype
    case_2 = copy.deepcopy(case_obj)
    case_2["_id"] = "case_2"
    case_2["phenotype_terms"] = test_hpo_terms[:-1]  # exclude last term

    # insert this case in database:
    adapter.case_collection.insert_one(case_2)
    assert sum(1 for i in adapter.case_collection.find()) == 2

    # Add another case with phenotype very different from case_obj
    case_3 = copy.deepcopy(case_obj)
    case_3["_id"] = "case_3"
    case_3["phenotype_terms"] = [
        {"phenotype_id": "HP:0000533", "feature": "Recurrent skin infections"}
    ]

    # insert this case in database:
    adapter.case_collection.insert_one(case_3)
    assert sum(1 for i in adapter.case_collection.find()) == 3

    hpo_query_terms = [term["phenotype_id"] for term in test_hpo_terms]
    similar_cases = adapter.cases_by_phenotype(hpo_query_terms, case_obj["owner"], case_obj["_id"])
    # make sure that the function returns a list of tuples
    assert isinstance(similar_cases, list)
    assert isinstance(similar_cases[0], tuple)

    # and the first element of the list has a score higher or equal than the second
    assert similar_cases[0][1] > similar_cases[1][1]


def test_get_similar_cases_by_name_query(hpo_database, test_hpo_terms, case_obj):
    adapter = hpo_database

    # Make sure database contains HPO terms
    assert sum(1 for i in adapter.hpo_terms())

    # Give the case HPO terms
    case_obj["phenotype_terms"] = test_hpo_terms
    adapter.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]},
        {"$set": {"phenotype_terms": test_hpo_terms}},
        return_document=pymongo.ReturnDocument.AFTER,
    )

    # Insert a case into the db
    adapter.case_collection.insert_one(case_obj)
    assert sum(1 for i in adapter.case_collection.find()) == 1

    # Add another case with slightly different phenotype:

    case_2 = copy.deepcopy(case_obj)
    case_2["_id"] = "case_2"
    case_2["phenotype_terms"] = test_hpo_terms[:-1]  # exclude last term

    # insert this case in database:
    adapter.case_collection.insert_one(case_2)
    assert sum(1 for i in adapter.case_collection.find()) == 2

    # WHEN querying for a similar case
    name_query = f"similar_case:{case_obj['display_name']}"
    # THEN one case should be returned
    cases = list(adapter.cases(collaborator=case_obj["owner"], name_query=name_query))
    assert len(cases) == 1


def test_get_cases_cohort(real_adapter, case_obj, user_obj):
    adapter = real_adapter
    # GIVEN an empty database (no cases)
    assert sum(1 for i in adapter.cases()) == 0

    cohort_name = "cohort"

    case_obj["cohorts"] = [cohort_name]
    adapter.case_collection.insert_one(case_obj)

    # WHEN retreiving cases by a cohort name query
    result = adapter.cases(name_query="cohort:{}".format(cohort_name))
    # THEN we should get the case returned
    assert sum(1 for i in result) == 1


def test_get_cases_solved_since(real_adapter, case_obj, user_obj, institute_obj, variant_obj):
    adapter = real_adapter
    # GIVEN an empty database (no cases)
    adapter.case_collection.insert_one(case_obj)

    # WHEN querying for cases solved within 1 day
    # THEN no case are found
    assert len([case for case in adapter.cases(within_days=1)]) == 0

    # GIVEN a marked causative
    adapter.mark_causative(institute_obj, case_obj, user_obj, "link", variant_obj)

    # WHEN querying for cases solved within 1 day
    # THEN one case is found
    assert len([case for case in adapter.cases(finished=True, within_days=1)]) == 1


def test_keep_manual_rank_tag_after_reupload(
    adapter, case_obj, variant_obj, user_obj, institute_obj
):
    """Test the code that updates custom tags (manual_rank) of new variants according to the old."""

    old_variant = copy.deepcopy(variant_obj)
    old_variant["_id"] = "old_id"

    ## GIVEN a database with a user
    adapter.user_collection.insert_one(user_obj)

    ## AND a case
    adapter.case_collection.insert_one(case_obj)

    ## WHEN the variant is manual ranked
    adapter.variant_collection.insert_one(old_variant)
    updated_old = adapter.update_manual_rank(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="variant_link",
        variant=old_variant,
        manual_rank=8,
    )
    assert updated_old

    # THEN replaced by a new variant
    adapter.variant_collection.delete_one(old_variant)

    new_variant = variant_obj
    new_variant["_id"] = "new_id"
    adapter.variant_collection.insert_one(new_variant)

    # THE update actions function should return the id of the new variant
    updated_new_vars = adapter.update_variant_actions(
        institute_obj=institute_obj,
        case_obj=case_obj,
        old_eval_variants=[updated_old],
    )
    assert updated_new_vars["manual_rank"] == ["new_id"]

    # and the new variant should have a the same manual rank
    test_variant = adapter.variant_collection.find_one({"_id": "new_id"})
    assert test_variant["manual_rank"] == 8


def test_keep_dismiss_variant_tag_after_reupload(
    adapter, case_obj, variant_obj, user_obj, institute_obj
):
    """Test the code that updates custom tags (dismiss_variant) of new variants according to the old."""

    old_variant = copy.deepcopy(variant_obj)
    old_variant["_id"] = "old_id"

    ## GIVEN a database with a user
    adapter.user_collection.insert_one(user_obj)

    ## AND a case
    adapter.case_collection.insert_one(case_obj)

    ## WHEN the variant is manual dismissed
    adapter.variant_collection.insert_one(old_variant)
    updated_old = adapter.update_dismiss_variant(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="variant_link",
        variant=old_variant,
        dismiss_variant=[2, 11],  # provide 2 dismiss reasons
    )
    assert updated_old

    # THEN replaced by a new variant
    adapter.variant_collection.delete_one(old_variant)

    new_variant = variant_obj
    new_variant["_id"] = "new_id"
    adapter.variant_collection.insert_one(new_variant)

    # THE update actions function should return the id of the new variant
    updated_new_vars = adapter.update_variant_actions(
        institute_obj=institute_obj,
        case_obj=case_obj,
        old_eval_variants=[updated_old],
    )
    assert updated_new_vars["dismiss_variant"] == ["new_id"]

    # and the new variant should have a the same dismiss_variant
    test_variant = adapter.variant_collection.find_one({"_id": "new_id"})
    assert test_variant["dismiss_variant"] == [2, 11]


def test_keep_mosaic_tags_after_reupload(adapter, case_obj, variant_obj, user_obj, institute_obj):
    """Test the code that updates custom tags (mosaic tags) of new variants according to the old."""

    old_variant = copy.deepcopy(variant_obj)
    old_variant["_id"] = "old_id"

    ## GIVEN a database with a user
    adapter.user_collection.insert_one(user_obj)

    ## AND a case
    adapter.case_collection.insert_one(case_obj)

    ## WHEN mosaic tag(s) are assigned to the variant
    adapter.variant_collection.insert_one(old_variant)
    updated_old = adapter.update_mosaic_tags(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="variant_link",
        variant=old_variant,
        mosaic_tags=[1, 3],  # provide 2 mosaic tags
    )
    assert updated_old

    # THEN the variant is replaced by a new variant
    adapter.variant_collection.delete_one(old_variant)

    new_variant = variant_obj
    new_variant["_id"] = "new_id"
    adapter.variant_collection.insert_one(new_variant)

    # THE update actions function should return the id of the new variant
    updated_new_vars = adapter.update_variant_actions(
        institute_obj=institute_obj,
        case_obj=case_obj,
        old_eval_variants=[updated_old],
    )
    assert updated_new_vars["mosaic_tags"] == ["new_id"]

    # and the new variant should have a the same mosaic tags
    test_variant = adapter.variant_collection.find_one({"_id": "new_id"})
    assert test_variant["mosaic_tags"] == [1, 3]


def test_keep_cancer_tier_after_reupload(adapter, case_obj, variant_obj, user_obj, institute_obj):
    """Test the code that updates cancer tier of new variants according to the old."""

    old_variant = copy.deepcopy(variant_obj)
    old_variant["_id"] = "old_id"

    ## GIVEN a database with a user
    adapter.user_collection.insert_one(user_obj)

    ## AND a case
    adapter.case_collection.insert_one(case_obj)

    ## WHEN cancer tier is assigned to the variant
    adapter.variant_collection.insert_one(old_variant)
    updated_old = adapter.update_cancer_tier(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="variant_link",
        variant=old_variant,
        cancer_tier="2C",
    )
    assert updated_old

    # THEN the variant is replaced by a new variant
    adapter.variant_collection.delete_one(old_variant)

    new_variant = variant_obj
    new_variant["_id"] = "new_id"
    adapter.variant_collection.insert_one(new_variant)

    # THE update actions function should return the id of the new variant
    updated_new_vars = adapter.update_variant_actions(
        institute_obj=institute_obj,
        case_obj=case_obj,
        old_eval_variants=[updated_old],
    )
    assert updated_new_vars["cancer_tier"] == ["new_id"]

    # and the new variant should have a the same mosaic tags
    test_variant = adapter.variant_collection.find_one({"_id": "new_id"})
    assert test_variant["cancer_tier"] == "2C"


def test_keep_manual_acmg_after_reupload(adapter, case_obj, variant_obj, user_obj, institute_obj):
    """Test the code that updates acmg classification of new variants according to the old."""

    old_variant = copy.deepcopy(variant_obj)
    old_variant["_id"] = "old_id"

    ## GIVEN a database with a user
    adapter.user_collection.insert_one(user_obj)

    ## AND a case
    adapter.case_collection.insert_one(case_obj)

    ## WHEN manual acmg is assigned to the variant
    adapter.variant_collection.insert_one(old_variant)
    updated_old = adapter.update_acmg(
        institute_obj=institute_obj,
        case_obj=case_obj,
        user_obj=user_obj,
        link="variant_link",
        variant_obj=old_variant,
        acmg_str="likely_pathogenic",
    )
    assert updated_old

    # THEN the variant is replaced by a new variant
    adapter.variant_collection.delete_one(old_variant)

    new_variant = variant_obj
    new_variant["_id"] = "new_id"
    adapter.variant_collection.insert_one(new_variant)

    # THE update actions function should return the id of the new variant
    updated_new_vars = adapter.update_variant_actions(
        institute_obj=institute_obj,
        case_obj=case_obj,
        old_eval_variants=[updated_old],
    )
    assert updated_new_vars["acmg_classification"] == ["new_id"]

    # and the new variant should have a the same classification
    test_variant = adapter.variant_collection.find_one({"_id": "new_id"})
    assert test_variant["acmg_classification"] == REV_ACMG_MAP["likely_pathogenic"]


def test_keep_variant_comments_after_reupload(
    adapter, case_obj, variant_obj, user_obj, institute_obj
):
    """Test the code that updates comments of new variants according to the old."""

    old_variant = copy.deepcopy(variant_obj)
    old_variant["_id"] = "old_id"
    old_variant["is_commented"] = True

    ## GIVEN a database with a user
    adapter.user_collection.insert_one(user_obj)

    ## AND a case
    adapter.case_collection.insert_one(case_obj)

    # AND a variant with local comment
    adapter.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="variant_link",
        variant=old_variant,
        content="Hello, locally",
        comment_level="specific",
    )

    # and a global comment
    adapter.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="variant_link",
        variant=old_variant,
        content="Hello, globally",
        comment_level="global",
    )
    assert sum(1 for i in adapter.event_collection.find()) == 2

    # WHEN the variant is re-uploaded
    adapter.variant_collection.delete_one(old_variant)

    new_variant = variant_obj
    new_variant["_id"] = "new_id"
    adapter.variant_collection.insert_one(new_variant)

    # THE update actions function should return the id of the new variant
    updated_new_vars = adapter.update_variant_actions(
        institute_obj=institute_obj,
        case_obj=case_obj,
        old_eval_variants=[old_variant],
    )

    assert updated_new_vars["is_commented"] == [new_variant["_id"]]

    # and 2 new comments should be created in the database
    assert sum(1 for i in adapter.event_collection.find()) == 4
