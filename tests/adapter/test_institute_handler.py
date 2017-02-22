import pytest

from datetime import datetime

from scout.exceptions import IntegrityError

def test_add_institute(pymongo_adapter):
    institute_info = {
        'internal_id': 'test-institute',
        'display_name': 'test',
    }
    
    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0
    
    ## WHEN adding a institute
    
    pymongo_adapter.add_institute(institute_info)
    
    ## THEN assert the institute has been inserted in the correct way
    
    institute_obj = pymongo_adapter.institute_collection.find_one({
        '_id': institute_info['internal_id']
    })
    
    assert institute_obj['_id'] == institute_info['internal_id']
    assert institute_obj['internal_id'] == institute_info['internal_id']
    assert institute_obj['display_name'] == institute_info['display_name']
    assert type(institute_obj['updated_at']) == type(datetime.now())
    assert institute_obj['updated_at'] == institute_obj['updated_at']

    ## THEN assert defaults where set
    
    assert institute_obj['coverage_cutoff'] == 10
    assert institute_obj['frequency_cutoff'] == 0.01

def test_add_institute_twice(pymongo_adapter):
    institute_info = {
        'internal_id': 'test-institute',
        'display_name': 'test',
    }
    
    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0
    
    ## WHEN adding the institute twice
    
    pymongo_adapter.add_institute(institute_info)
    
    ## THEN assert an exception is raised

    with pytest.raises(IntegrityError):
        pymongo_adapter.add_institute(institute_info)

def test_fetch_institute(pymongo_adapter):
    institute_info = {
        'internal_id': 'test-institute',
        'display_name': 'test',
    }
    
    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0
    
    ## WHEN adding a institute
    
    pymongo_adapter.add_institute(institute_info)
    
    ## THEN assert it gets returned in the proper way

    institute_obj = pymongo_adapter.institute(institute_info['internal_id'])
    
    assert institute_obj['_id'] == institute_info['internal_id']
    assert institute_obj['internal_id'] == institute_info['internal_id']

def test_fetch_non_existing_institute(pymongo_adapter):
    institute_info = {
        'internal_id': 'test-institute',
        'display_name': 'test',
    }
    
    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0
    
    ## WHEN adding a institute and trying to fetch another institute
    
    pymongo_adapter.add_institute(institute_info)
    
    ## THEN assert the adapter returns None

    institute_obj = pymongo_adapter.institute(institute_id='non existing')
    
    assert institute_obj is None

def test_update_institute_sanger(pymongo_adapter):
    institute_info = {
        'internal_id': 'test-institute',
        'display_name': 'test',
    }
    
    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0
    
    ## WHEN adding a institute and updating it
    
    pymongo_adapter.add_institute(institute_info)
    
    pymongo_adapter.update_institute(
        internal_id=institute_info['internal_id'],
        sanger_recipient='john.doe@mail.com'
    )
    
    ## THEN assert that the institute has been updated

    institute_obj = pymongo_adapter.institute(institute_id=institute_info['internal_id'])
    
    assert institute_obj['sanger_recipients'] == ['john.doe@mail.com']
    
    ## THEN assert updated_at was updated
    
    assert institute_obj['updated_at'] > institute_obj['created_at']

def test_update_institute_coverage_cutoff(pymongo_adapter):
    institute_info = {
        'internal_id': 'test-institute',
        'display_name': 'test',
    }
    
    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0
    
    ## WHEN adding a institute and updating it
    
    pymongo_adapter.add_institute(institute_info)
    
    new_cutoff = 12.0
    
    pymongo_adapter.update_institute(
        internal_id=institute_info['internal_id'],
        coverage_cutoff=new_cutoff
    )
    


    institute_obj = pymongo_adapter.institute(institute_id=institute_info['internal_id'])

    ## THEN assert that the coverage cutoff has been updated
    assert institute_obj['coverage_cutoff'] == new_cutoff
    
    ## THEN assert updated_at was updated
    
    assert institute_obj['updated_at'] > institute_obj['created_at']

def test_update_institute_sanger_and_cutoff(pymongo_adapter):
    institute_info = {
        'internal_id': 'test-institute',
        'display_name': 'test',
    }
    
    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0
    
    ## WHEN adding a institute and updating it
    
    pymongo_adapter.add_institute(institute_info)

    new_cutoff = 12.0
    
    pymongo_adapter.update_institute(
        internal_id=institute_info['internal_id'],
        sanger_recipient='john.doe@mail.com',
        coverage_cutoff=new_cutoff
    )


    institute_obj = pymongo_adapter.institute(institute_id=institute_info['internal_id'])

    ## THEN assert that the coverage cutoff has been updated
    assert institute_obj['coverage_cutoff'] == new_cutoff
    
    ## THEN assert that the sanger recipients has been updated
    assert institute_obj['sanger_recipients'] == ['john.doe@mail.com']
    
    ## THEN assert updated_at was updated
    
    assert institute_obj['updated_at'] > institute_obj['created_at']


def test_updating_non_existing_institute(pymongo_adapter):
    institute_info = {
        'internal_id': 'test-institute',
        'display_name': 'test',
    }

    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0

    ## WHEN adding a institute and trying to fetch another institute

    institute_info = {
        'internal_id': 'test-institute',
        'display_name': 'test',
    }
    
    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0
    
    ## WHEN adding a institute and updating the wrong one
    
    pymongo_adapter.add_institute(institute_info)

    new_cutoff = 12.0
    
    ## THEN assert that the update did not add any institutes to the database
    assert pymongo_adapter.institutes().count() == 1
    
    pymongo_adapter.update_institute(
        internal_id='mom existing',
        sanger_recipient='john.doe@mail.com',
    )

    assert pymongo_adapter.institutes().count() == 1

