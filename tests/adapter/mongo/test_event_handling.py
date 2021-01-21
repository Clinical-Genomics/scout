from pprint import pprint as pp
import pytest
import logging
import datetime
import pymongo

from scout.constants import VERBS_MAP

logger = logging.getLogger(__name__)


def test_create_event(adapter, institute_obj, case_obj, user_obj):
    ## GIVEN a database without any events

    assert sum(1 for i in adapter.event_collection.find()) == 0

    ## WHEN inserting a event
    verb = "status"
    adapter.create_event(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="a link",
        category="case",
        verb=verb,
        subject="a subject",
        level="specific",
    )

    # THEN assert that the event was added to the database

    assert sum(1 for i in adapter.event_collection.find()) == 1
    res = adapter.event_collection.find_one()

    assert res["verb"] == verb


def test_assign(adapter, institute_obj, case_obj, user_obj):
    logger.info("Testing assign a user to a case")
    # GIVEN a populated database without events
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)

    assert sum(1 for i in adapter.event_collection.find()) == 0

    ## WHEN assigning a user to a case
    link = "assignlink"
    updated_case = adapter.assign(institute=institute_obj, case=case_obj, user=user_obj, link=link)
    # THEN the case should have the user assigned
    assert updated_case["assignees"] == [user_obj["_id"]]
    # THEN an event should have been created
    assert sum(1 for i in adapter.event_collection.find()) == 1

    event_obj = adapter.event_collection.find_one()
    assert event_obj["link"] == link


def test_unassign(adapter, institute_obj, case_obj, user_obj):

    case_obj["status"] = "active"

    # GIVEN an adapter to a database with one case
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)

    # assign case to test user
    link = "assignlink"
    updated_case = adapter.assign(institute=institute_obj, case=case_obj, user=user_obj, link=link)

    # Make sure that case is active
    assert updated_case["status"] == "active"
    assert updated_case["assignees"] == [user_obj["_id"]]

    assert sum(1 for i in adapter.event_collection.find()) == 1

    # WHEN unassigning the only user assigned to case
    # and wishes to inactivate it
    updated_case = adapter.unassign(
        institute=institute_obj,
        case=updated_case,
        user=user_obj,
        link="unassignlink",
        inactivate=True,
    )
    # case should become inactive
    assert updated_case["status"] == "inactive"

    # THEN two events should have been created
    assert sum(1 for i in adapter.event_collection.find()) == 2

    # THEN the case should not be assigned
    assert updated_case.get("assignees") == []

    # THEN a unassign event should be created
    event = adapter.event_collection.find_one({"verb": "unassign"})
    assert event["link"] == "unassignlink"


def test_update_synopsis(adapter, institute_obj, case_obj, user_obj):
    ## GIVEN a populated database without events
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    assert sum(1 for i in adapter.event_collection.find()) == 0

    # WHEN updating synopsis for a case
    link = "synopsislink"
    synopsis = "The updated synopsis"
    updated_case = adapter.update_synopsis(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        content=synopsis,
    )
    # THEN the case should have the synopsis added
    assert updated_case["synopsis"] == synopsis

    # THEN an event for synopsis should have been added
    event = adapter.event_collection.find_one({"link": link})
    assert event["content"] == synopsis


def test_archive_case(adapter, institute_obj, case_obj, user_obj):
    logger.info("Set a case to archive status")
    ## GIVEN a populated database without events
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)

    assert sum(1 for i in adapter.event_collection.find()) == 0

    ## WHEN setting a case in archive status
    link = "archivelink"
    updated_case = adapter.archive_case(
        institute=institute_obj, case=case_obj, user=user_obj, link=link
    )
    ## THEN the case status should be archived
    assert updated_case["status"] == "archived"

    ## THEN a event for archiving should be added
    event = adapter.event_collection.find_one({"link": link})
    assert event["link"] == link


def test_open_research(adapter, institute_obj, case_obj, user_obj):
    ## GIVEN a populated database without events
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    assert sum(1 for i in adapter.event_collection.find()) == 0

    case = adapter.case_collection.find_one({"_id": case_obj["_id"]})
    assert case.get("research_requested", False) is False

    ## WHEN setting opening research for a case
    link = "openresearchlink"
    updated_case = adapter.open_research(
        institute=institute_obj, case=case_obj, user=user_obj, link=link
    )
    ## THEN research_requested should be True
    assert updated_case["research_requested"] is True

    ## THEN an event for opening research should be created
    event = adapter.event_collection.find_one({"link": link})
    assert event["link"] == "openresearchlink"


def test_add_hpo(adapter, institute_obj, case_obj, user_obj):
    ## GIVEN a populated database without a gene and a hpo term
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)

    gene_obj = dict(
        hgnc_id=1,
        hgnc_symbol="test",
        ensembl_id="anothertest",
        chromosome="1",
        start=10,
        end=20,
        build="37",
    )
    adapter.load_hgnc_gene(gene_obj)

    hpo_obj = dict(_id="HP:0000878", hpo_id="HP:0000878", description="A term", genes=[1])

    adapter.load_hpo_term(hpo_obj)

    hpo_term = hpo_obj["hpo_id"]

    ## WHEN adding a hpo term for a case
    link = "addhpolink"

    updated_case = adapter.add_phenotype(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        hpo_term=hpo_term,
    )
    ## THEN the case should have a hpo term
    for term in updated_case["phenotype_terms"]:
        assert term["phenotype_id"] == hpo_term

    ## THEN a event should have been created
    event = adapter.event_collection.find_one({"link": link})
    assert event["link"] == link


def test_add_phenotype_group(adapter, institute_obj, case_obj, user_obj):
    ## GIVEN a populated database without a gene and a hpo term
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)

    gene_obj = dict(
        hgnc_id=1,
        hgnc_symbol="test",
        ensembl_id="anothertest",
        chromosome="1",
        start=10,
        end=20,
        build="37",
    )
    adapter.load_hgnc_gene(gene_obj)

    hpo_obj = dict(_id="HP:0000878", hpo_id="HP:0000878", description="A term", genes=[1])

    adapter.load_hpo_term(hpo_obj)

    hpo_term = hpo_obj["hpo_id"]

    # GIVEN a populated database with no events
    assert sum(1 for i in adapter.hpo_term_collection.find()) > 0
    assert adapter.hpo_term_collection.find({"_id": hpo_term})
    assert sum(1 for i in adapter.event_collection.find()) == 0

    ## WHEN adding a phenotype group
    updated_case = adapter.add_phenotype(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="hpolink",
        hpo_term=hpo_term,
        is_group=True,
    )
    # THEN the case should have phenotypes
    assert len(updated_case["phenotype_terms"]) > 0
    assert len(updated_case["phenotype_groups"]) > 0

    # THEN there should be phenotype events
    assert sum(1 for i in adapter.event_collection.find()) > 0


def test_add_wrong_hpo(adapter, institute_obj, case_obj, user_obj):
    ## GIVEN a populated database
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    # WHEN adding a non exoisting hpo term for a case
    hpo_term = "k"
    with pytest.raises(ValueError):
        # THEN a value error should be raised
        adapter.add_phenotype(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link="addhpolink",
            hpo_term=hpo_term,
        )


def test_add_no_term(adapter, institute_obj, case_obj, user_obj):
    logger.info("Add a HPO term for a case")
    ## GIVEN a populated database
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    ## WHEN adding hpo term without a term
    with pytest.raises(ValueError):
        ## THEN a value error should be raised
        adapter.add_phenotype(
            institute=institute_obj, case=case_obj, user=user_obj, link="addhpolink"
        )


def test_add_non_existing_mim(adapter, institute_obj, case_obj, user_obj):
    ## GIVEN a populated database
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    # Non existing mim phenotype
    mim_term = "MIM:0000002"
    # GIVEN a populated database

    # WHEN adding a non existing phenotype term
    updated_case = adapter.add_phenotype(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="mimlink",
        omim_term=mim_term,
    )
    # THEN the case should not have any phenotypes
    assert len(updated_case.get("phenotype_terms", [])) == 0

    # THEN there should not exist any events
    assert sum(1 for i in adapter.event_collection.find()) == 0


def test_add_mim(adapter, institute_obj, case_obj, user_obj):
    ## GIVEN a populated adapter with a disease term
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)

    gene_obj = dict(
        hgnc_id=1,
        hgnc_symbol="test",
        ensembl_id="anothertest",
        chromosome="1",
        start=10,
        end=20,
        build="37",
    )
    adapter.load_hgnc_gene(gene_obj)

    mim_obj = {
        "_id": "OMIM:605606",
        "disease_id": "OMIM:605606",
        "disease_nr": 605606,
        "description": "Psoriasis susceptibility 7",
        "source": "OMIM",
        "genes": [1],
        "inheritance": [],
        "hpo_terms": ["HP:0000878"],
    }
    adapter.disease_term_collection.insert_one(mim_obj)

    hpo_obj = dict(_id="HP:0000878", hpo_id="HP:0000878", description="A term", genes=[1])

    adapter.load_hpo_term(hpo_obj)

    # Existing mim phenotype
    mim_obj = adapter.disease_term_collection.find_one()
    mim_term = mim_obj["_id"]

    assert sum(1 for i in adapter.hpo_term_collection.find()) > 0
    # GIVEN a populated database
    assert sum(1 for i in adapter.event_collection.find()) == 0

    # WHEN adding a existing phenotype term
    updated_case = adapter.add_phenotype(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="mimlink",
        omim_term=mim_term,
    )
    # THEN the case should have phenotypes
    assert len(updated_case["phenotype_terms"]) > 0

    # THEN there should be phenotype events
    assert sum(1 for i in adapter.event_collection.find()) > 0


def test_remove_hpo(hpo_database, institute_obj, case_obj, user_obj):
    adapter = hpo_database
    logger.info("Add a HPO term for a case")
    adapter._add_case(case_obj)

    # GIVEN a populated database
    assert sum(1 for i in adapter.event_collection.find()) == 0

    hpo_term = "HP:0000878"

    updated_case = adapter.add_phenotype(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="addhpolink",
        hpo_term=hpo_term,
    )

    # Assert that the term was added to the case
    assert len(updated_case["phenotype_terms"]) == 1

    # Check that the event exists
    assert sum(1 for i in adapter.event_collection.find()) == 1

    # WHEN removing the phenotype term
    updated_case = adapter.remove_phenotype(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link="removehpolink",
        phenotype_id=hpo_term,
    )
    # THEN the case should not have phenotype terms
    assert len(updated_case["phenotype_terms"]) == 0

    # THEN an event should have been created
    assert sum(1 for i in adapter.event_collection.find()) == 2


def test_add_cohort(adapter, institute_obj, case_obj, user_obj):
    ## GIVEN a populated database
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    assert sum(1 for i in adapter.event_collection.find()) == 0

    cohort_name = "cohort"

    link = "cohortlink"
    ## WHEN adding a cohort to a case
    updated_case = adapter.add_cohort(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        tag=cohort_name,
    )
    # THEN the case should have the cohort saved
    assert set(updated_case["cohorts"]) == set([cohort_name])
    # THEN an event should have been created
    assert sum(1 for i in adapter.event_collection.find()) == 1

    event_obj = adapter.event_collection.find_one()
    assert event_obj["link"] == link


def test_remove_cohort(adapter, institute_obj, case_obj, user_obj):
    ## GIVEN a populated database
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    assert sum(1 for i in adapter.event_collection.find()) == 0

    cohort_name = "cohort"

    link = "cohortlink"
    ## WHEN adding a cohort to a case
    updated_case = adapter.add_cohort(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        tag=cohort_name,
    )
    assert sum(1 for i in adapter.event_collection.find()) == 1

    remove_cohort_link = "removeCohortlink"
    ## WHEN removing a cohort from a case
    updated_case = adapter.remove_cohort(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        tag=cohort_name,
    )
    # THEN the case should have the cohort saved
    assert updated_case["cohorts"] == []
    # THEN an event should have been created
    assert sum(1 for i in adapter.event_collection.find()) == 2


def test_update_clinical_filter_hpo(adapter, institute_obj, case_obj, user_obj):
    # GIVEN a case (and its user, institute)
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    # GIVEN no events in the event collection
    assert sum(1 for i in adapter.event_collection.find()) == 0

    # WHEN calling update function
    hpo_clinical_filter = True
    updated_case = adapter.update_clinical_filter_hpo(
        institute_obj=institute_obj,
        case_obj=case_obj,
        user_obj=user_obj,
        link="update_clinical_filter_hpo_link",
        hpo_clinical_filter=hpo_clinical_filter,
    )
    # THEN hpo_clinical_filter is actually updated
    assert updated_case["hpo_clinical_filter"] == hpo_clinical_filter
    # THEN an event should have been created
    assert sum(1 for i in adapter.event_collection.find()) == 1


def test_filter_stash(adapter, institute_obj, case_obj, user_obj, filter_obj):
    # GIVEN a case, institute and user in a store
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)

    # WHEN asking for filters
    institute_id = institute_obj.get("_id")
    category = "snv"
    filters = adapter.filters(institute_id, category)

    # THEN no filters are returned
    assert sum(1 for i in filters) == 0

    # WHEN no events are yet in the events collection
    assert sum(1 for i in adapter.event_collection.find()) == 0
    # WHEN storing a filter
    filter_id = adapter.stash_filter(
        filter_obj, institute_obj, case_obj, user_obj, category, link="mock_link"
    )
    # THEN a filter id is returned
    assert filter_id
    # THEN an event can be found in the event collection
    assert sum(1 for i in adapter.event_collection.find()) > 0

    # WHEN listing filters
    filters = adapter.filters(institute_id, category)
    # THEN one filter is returned
    assert sum(1 for i in filters) == 1

    # WHEN retrieving a stored filter
    retrieved_filter_obj = adapter.retrieve_filter(filter_id)
    # THEN a filter_obj is retireved
    assert retrieved_filter_obj

    user_id = user_obj.get("_id")
    # WHEN deleting filter
    result = adapter.delete_filter(filter_id, institute_id, user_id)
    # THEN no filters are returned
    filters = adapter.filters(institute_id, category)
    assert sum(1 for i in filters) == 0


def test_update_default_panels(adapter, institute_obj, case_obj, user_obj, dummypanel_obj):
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    adapter.panel_collection.insert_one(dummypanel_obj)
    # GIVEN a case with one gene panel
    case_panels = case_obj["panels"]
    assert len(case_panels) == 1
    panel = case_panels[0]
    assert panel["panel_name"] == "panel1"
    assert panel["is_default"] is True

    new_panel = {
        "_id": "an_id",
        "panel_id": "an_id",
        "panel_name": "panel2",
        "display_name": "Test panel2",
        "version": 1.0,
        "updated_at": datetime.datetime.now(),
        "nr_genes": 263,
        "is_default": False,
    }
    case_obj = adapter.case_collection.find_one_and_update(
        {"_id": case_obj["_id"]},
        {"$addToSet": {"panels": new_panel}},
        return_document=pymongo.ReturnDocument.AFTER,
    )

    assert len(case_obj["panels"]) == 2

    # WHEN updating the default panels

    updated_case = adapter.update_default_panels(
        institute_obj=institute_obj,
        case_obj=case_obj,
        user_obj=user_obj,
        link="update_default_link",
        panel_objs=[new_panel],
    )

    # THEN the the updated case should have panel1 as not default and panel2
    # as default
    for panel in updated_case["panels"]:
        if panel["panel_name"] == "panel1":
            assert panel["is_default"] is False
        elif panel["panel_name"] == "panel2":
            assert panel["is_default"] is True

    # assert sum(1 for i in adapter.event_collection.find()) == 2
    #
    # # THEN the case should not be assigned
    # assert updated_case.get('assignees') == []
    # # THEN a unassign event should be created
    # event = adapter.event_collection.find_one({'verb': 'unassign'})
    # assert event['link'] == 'unassignlink'


def test_update_case_group(adapter, institute_obj, case_obj, user_obj):
    adapter.case_collection.insert_one(case_obj)
    adapter.institute_collection.insert_one(institute_obj)
    adapter.user_collection.insert_one(user_obj)
    # GIVEN no events in the event collection
    assert sum(1 for i in adapter.event_collection.find()) == 0

    group_ids = ["1234", "5678"]

    # WHEN calling update function
    hpo_clinical_filter = True
    updated_case = adapter.update_case_group_ids(
        institute_obj=institute_obj,
        case_obj=case_obj,
        user_obj=user_obj,
        link="update_case_group_link",
        group_ids=group_ids,
    )
    # THEN group ids are actually updated
    assert updated_case["group"] == group_ids
    # THEN an event should have been created
    assert sum(1 for i in adapter.event_collection.find()) == 1
