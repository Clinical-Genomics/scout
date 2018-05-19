# -*- coding: utf-8 -*-
import pytest
import logging
import datetime
from scout.server.blueprints.variants.controllers import variants_filter_by_field, variants_description
from pprint import pprint as pp

from scout.exceptions import (IntegrityError)

logger = logging.getLogger(__name__)

def test_add_cases(panel_database, case_obj):
    adapter = panel_database
    ## GIVEN an empty database (no cases)
    assert adapter.case_collection.find().count() == 0

    ## WHEN adding a new case to the database
    adapter._add_case(case_obj)

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

    adapter._add_case(case_obj)
    ## WHEN adding a existing case to the database
    with pytest.raises(IntegrityError):
    ## THEN it should raise integrity error
        adapter._add_case(case_obj)

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

def test_get_cases(real_panel_database, case_obj):
    adapter = real_panel_database
    ## GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.case_collection.insert_one(case_obj)
    ## WHEN retreiving an existing case from the database
    result = adapter.cases()
    ## THEN we should get the correct case
    assert result.count() == 1

def test_get_cases_no_assignees(real_panel_database, case_obj):
    adapter = real_panel_database
    ## GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.case_collection.insert_one(case_obj)
    ## WHEN retreiving an existing case from the database
    result = adapter.cases(name_query='john')
    ## THEN we should get the correct case
    assert result.count() == 0

def test_get_cases_display_name(real_panel_database, case_obj):
    adapter = real_panel_database
    ## GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.case_collection.insert_one(case_obj)
    ## WHEN retreiving cases by partial display name
    result = adapter.cases(name_query='643')
    ## THEN we should get the correct case
    assert result.count() == 1

def test_get_cases_existing_individual(real_panel_database, case_obj):
    adapter = real_panel_database
    ## GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.case_collection.insert_one(case_obj)
    ## WHEN retreiving cases by partial individual name
    result = adapter.cases(name_query='NA1288')
    ## THEN we should get the correct case
    assert result.count() == 1

def test_get_cases_assignees(real_panel_database, case_obj):
    adapter = real_panel_database
    ## GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0

    user_obj = adapter.user_collection.find_one()
    case_obj['assignees'] = [user_obj['email']]
    adapter.case_collection.insert_one(case_obj)

    ## WHEN retreiving cases by partial individual name
    result = adapter.cases(name_query='john')
    ## THEN we should get the correct case
    assert result.count() == 1

def test_get_cases_non_existing_assignee(real_panel_database, case_obj):
    adapter = real_panel_database
    ## GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0

    user_obj = adapter.user_collection.find_one()
    case_obj['assignees'] = [user_obj['email']]
    adapter.case_collection.insert_one(case_obj)

    ## WHEN retreiving cases by partial individual name
    result = adapter.cases(name_query='damien')
    ## THEN we should get the correct case
    assert result.count() == 0


def test_get_cases_non_existing_individual(real_panel_database, case_obj):
    adapter = real_panel_database
    ## GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter.case_collection.insert_one(case_obj)
    ## WHEN retreiving cases by partial display name
    result = adapter.cases(name_query='hello')
    ## THEN we should get the correct case
    assert result.count() == 0

def test_get_non_existing_case(panel_database, case_obj):
    adapter = panel_database
    # GIVEN an empty database (no cases)
    assert adapter.cases().count() == 0
    adapter._add_case(case_obj)
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

def test_collect_variants_for_case_report(case_obj, institute_obj, real_populated_database, variant_objs, parsed_variant, user_obj):
    """Test to create a dictionary similar to that used for creating a sample report"""

    adapter = real_populated_database

    # GIVEN a populated database without any variants
    assert adapter.variants(case_id=case_obj['_id'], nr_of_variants=-1).count() == 0

    # Add all variants from variant_objs
    for index, variant_obj in enumerate(variant_objs):
        adapter.load_variant(variant_obj)

    # Assert that the collections has variant documents inside
    n_documents = adapter.variant_collection.find().count()
    assert n_documents > 0

    # add useful fields to a parsed variant
    parsed_variant['display_name'] = '1_10_A_C_clinical'
    parsed_variant['case_id'] = '643594' # otherwise it won't be found later
    parsed_variant['category'] = 'snv' # used by variants_description

    # add a 'dismissed' key and value
    parsed_variant['dismiss_variant'] = ['7']
    assert 'dismiss_variant' in parsed_variant

    # upload parsed variant to database
    adapter.load_variant(parsed_variant)

    # assert that it was inserted
    assert adapter.variant_collection.find().count() == n_documents + 1

    # get all variants
    all_variants = adapter.variants(case_id=case_obj['_id'], nr_of_variants=-1)
    assert all_variants.count() > 0

    # Test that there is at least one dismissed variant to upload to the case report for this case.
    # Retrieving variants for the categories 'classified', 'commented' and 'tagged' work exactly in the same way.
    dismissed_variants = variants_filter_by_field(adapter, list(all_variants), 'dismiss_variant')
    assert len(dismissed_variants) > 0
