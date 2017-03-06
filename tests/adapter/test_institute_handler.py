import pytest

from datetime import datetime

from scout.exceptions import IntegrityError

def test_add_institute(pymongo_adapter, institute_obj):
    
    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0
    
    ## WHEN adding a institute
    
    pymongo_adapter.add_institute(institute_obj)
    
    ## THEN assert the institute has been inserted in the correct way
    print(institute_obj)
    res = pymongo_adapter.institute_collection.find_one({
        '_id': institute_obj['internal_id']
    })
    
    assert res['_id'] == institute_obj['internal_id']
    assert res['internal_id'] == institute_obj['internal_id']
    assert res['display_name'] == institute_obj['display_name']
    assert type(res['updated_at']) == type(datetime.now())
    # assert res['updated_at'] == institute_obj['updated_at']

    ## THEN assert defaults where set
    
    assert res['coverage_cutoff'] == institute_obj['coverage_cutoff']
    assert res['frequency_cutoff'] == institute_obj['frequency_cutoff']

def test_add_institute_twice(pymongo_adapter, institute_obj):
    
    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0
    
    ## WHEN adding the institute twice
    
    pymongo_adapter.add_institute(institute_obj)
    
    ## THEN assert an exception is raised

    with pytest.raises(IntegrityError):
        pymongo_adapter.add_institute(institute_obj)

def test_fetch_institute(pymongo_adapter, institute_obj):
    
    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0
    
    ## WHEN adding a institute
    
    pymongo_adapter.add_institute(institute_obj)
    
    ## THEN assert it gets returned in the proper way

    res = pymongo_adapter.institute(institute_obj['internal_id'])
    
    assert res['_id'] == institute_obj['internal_id']
    assert res['internal_id'] == institute_obj['internal_id']

def test_fetch_non_existing_institute(pymongo_adapter, institute_obj):
    
    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0
    
    ## WHEN adding a institute and trying to fetch another institute
    
    pymongo_adapter.add_institute(institute_obj)
    
    ## THEN assert the adapter returns None

    institute_obj = pymongo_adapter.institute(institute_id='non existing')
    
    assert institute_obj is None

def test_update_institute_sanger(pymongo_adapter, institute_obj):
    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0
    
    ## WHEN adding a institute and updating it
    
    pymongo_adapter.add_institute(institute_obj)
    
    pymongo_adapter.update_institute(
        internal_id=institute_obj['internal_id'],
        sanger_recipient='calrk.kent@mail.com'
    )
    
    ## THEN assert that the institute has been updated

    res = pymongo_adapter.institute(institute_id=institute_obj['internal_id'])
    
    assert len(res['sanger_recipients']) == len(institute_obj.get('sanger_recipients', [])) + 1
    
    ## THEN assert updated_at was updated
    
    assert res['updated_at'] > institute_obj['created_at']

def test_update_institute_coverage_cutoff(pymongo_adapter, institute_obj):
    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0
    
    ## WHEN adding a institute and updating it
    
    pymongo_adapter.add_institute(institute_obj)
    
    new_cutoff = 12.0
    
    pymongo_adapter.update_institute(
        internal_id=institute_obj['internal_id'],
        coverage_cutoff=new_cutoff
    )

    res = pymongo_adapter.institute(institute_id=institute_obj['internal_id'])

    ## THEN assert that the coverage cutoff has been updated
    assert res['coverage_cutoff'] == new_cutoff
    
    ## THEN assert updated_at was updated
    
    assert res['updated_at'] > institute_obj['created_at']

def test_update_institute_sanger_and_cutoff(pymongo_adapter, institute_obj):
    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0
    
    ## WHEN adding a institute and updating it
    
    pymongo_adapter.add_institute(institute_obj)

    new_cutoff = 12.0
    new_mail = 'clark.kent@mail.com'
    
    pymongo_adapter.update_institute(
        internal_id=institute_obj['internal_id'],
        sanger_recipient=new_mail,
        coverage_cutoff=new_cutoff
    )


    res = pymongo_adapter.institute(institute_id=institute_obj['internal_id'])

    ## THEN assert that the coverage cutoff has been updated
    assert res['coverage_cutoff'] == new_cutoff
    
    ## THEN assert that the sanger recipients has been updated
    assert len(res['sanger_recipients']) == len(institute_obj.get('sanger_recipients', [])) + 1
    
    ## THEN assert updated_at was updated
    
    assert res['updated_at'] > institute_obj['created_at']


def test_updating_non_existing_institute(pymongo_adapter, institute_obj):
    ## GIVEN an adapter without any institutes
    assert pymongo_adapter.institutes().count() == 0

    ## WHEN adding a institute and updating the wrong one
    
    pymongo_adapter.add_institute(institute_obj)
    
    ## THEN assert that the update did not add any institutes to the database
    assert pymongo_adapter.institutes().count() == 1
    
    pymongo_adapter.update_institute(
        internal_id='nom existing',
        sanger_recipient='john.doe@mail.com',
    )

    assert pymongo_adapter.institutes().count() == 1

