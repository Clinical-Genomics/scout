# -*- coding: utf-8 -*-
import pytest
import logging
import datetime
from pprint import pprint as pp

from scout.exceptions import (IntegrityError)

logger = logging.getLogger(__name__)

def test_add_cases(panel_database, case_obj):
    adapter = panel_database
    ## GIVEN an empty database (no cases)
    assert adapter.case_collection.find().count() == 0
    
    ## WHEN adding a new case to the database
    adapter.add_case(case_obj)

    ## THEN it should be populated with the new case
    result = adapter.cases()
    assert result.count() == 1
    for case in result:
        assert case['owner'] == case_obj['owner']

    logger.info("All cases checked")


def test_add_existing_case(panel_database, case_obj):
    adapter = panel_database
    ## GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0

    adapter.add_case(case_obj)
    ## WHEN adding a existing case to the database
    with pytest.raises(IntegrityError):
    ## THEN it should raise integrity error
        adapter.add_case(case_obj)

def test_get_case(panel_database, case_obj):
    adapter = panel_database
    ## GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.case_collection.insert_one(case_obj)
    logger.info("Testing to get case")

    ## WHEN retreiving an existing case from the database
    result = adapter.case(case_id=case_obj['_id'])
    ## THEN we should get the correct case
    assert result['owner'] == case_obj['owner']

def test_get_non_existing_case(panel_database, case_obj):
    adapter = panel_database
    # GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.add_case(case_obj)
    logger.info("Testing to get case")

    # WHEN retreiving an non existing case from the database
    result = adapter.case(case_id='hello')
    # THEN we should get None back
    assert result is None

def test_delete_case(panel_database, case_obj):
    adapter = panel_database
    ## GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.case_collection.insert_one(case_obj)
    assert adapter.cases().count() == 1
    logger.info("Testing to delete case")

    ## WHEN deleting a case from the database
    result = adapter.delete_case(case_id=case_obj['_id'])
    ## THEN there should be no cases left in the database
    assert adapter.cases().count() == 0


def test_update_case_collaborators(panel_database, case_obj):
    adapter = panel_database
    ## GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.case_collection.insert_one(case_obj)
    assert adapter.cases().count() == 1
    assert len(adapter.case(case_obj['_id'])['collaborators']) == 1
    logger.info("Testing to update case")

    coll_1 = case_obj['collaborators'][0]
    coll_2 = 'test'
    coll_3 = 'test2'
    case_obj['collaborators'].append(coll_2)
    case_obj['collaborators'].append(coll_3)
    
    ## WHEN updating a case with new collaborators
    res = adapter.update_case(case_obj)
    
    ## THEN assert collaborator has been added
    assert len(res['collaborators']) == 3
    ## THEN assert all collaborators where added
    assert set(res['collaborators']) == set([coll_1, coll_2, coll_3])

def test_update_case_individuals(panel_database, case_obj):
    adapter = panel_database
    ## GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.case_collection.insert_one(case_obj)
    assert adapter.cases().count() == 1
    logger.info("Testing to update case")

    res = adapter.case(case_obj['_id'])
    assert len(res['individuals']) == 3

    new_individuals = [{
        'individual_id': 'test',
        'display_name': 'test_name',
    }]
    case_obj['individuals'] = new_individuals
    ## WHEN updating a case with new individuals
    res = adapter.update_case(case_obj)
    ## THEN assert that 'individuals' has changed
    
    assert len(res['individuals']) == 1

def test_update_case_analysis_dates(panel_database, case_obj):
    adapter = panel_database
    ## GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.case_collection.insert_one(case_obj)
    assert adapter.cases().count() == 1
    logger.info("Testing to update case")

    res = adapter.case(case_obj['_id'])
    old_date = res['analysis_date']
    old_update = res['updated_at']
    assert len(res['analysis_dates']) == 1

    new_analysis = datetime.datetime.now()
    case_obj['analysis_date'] = new_analysis
    ## WHEN updating a case with new analysis date
    res = adapter.update_case(case_obj)
    
    ## THEN assert that the new analysis date is added to 'analysis_dates'
    assert len(res['analysis_dates']) == 2
    ## THEN assert that 'analysis_date' is set to the new date
    assert res['analysis_date'] > old_date 
    ## THEN assert that 'updated_at' has been changed
    assert res['updated_at'] > old_update

def test_update_case_rerun_status(panel_database, case_obj):
    adapter = panel_database
    case_obj['rerun_requested'] = True
    ## GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.case_collection.insert_one(case_obj)
    assert adapter.cases().count() == 1
    logger.info("Testing to update case")

    res = adapter.case(case_obj['_id'])
    assert res['rerun_requested'] is True

    ## WHEN updating a case 
    res = adapter.update_case(case_obj)
    
    ## THEN assert that 'rerun_requested' is set to False
    assert res['rerun_requested'] is False
