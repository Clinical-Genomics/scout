# -*- coding: utf-8 -*-
import logging

LOG = logging.getLogger(__name__)

def get_test_submission_object():
    """Returns a test clinvar variant submission object"""

    clivar_subm_obj = {
        '_id' : '3eecfca5efea445eec6c19a53299043b',
        '##Local_ID' : '3eecfca5efea445eec6c19a53299043b',
        'Reference_allele' : 'C',
        'Alternate_allele' : 'A',
        'Chromosome' : '7',
        'Start' : '124491972',
        'Stop' : '124491972',
        'Clinical_significance' : 'Likely Pathogenic',
        'Condition_ID_value' : 'HP:0001298;HP:0002121',
        'clinvar_submission' : 'SUB666',
    }

    return clivar_subm_obj


def test_add_clinvar_submission(adapter, user_obj, institute_obj, case_obj):
    """Test adding a clinvar submission into mongo database"""
    ## GIVEN a database without any clinvar submission, check that it's empty
    assert adapter.clinvar_collection.find().count() == 0

    # prepare a test list with one submission get_test_submission_object
    test_sub_obj = [get_test_submission_object()]
    user = user_obj['email']
    institute = institute_obj['internal_id']
    case = case_obj['_id']

    ## Test adding a clinvar submission object, it should return a list of inserted ids (one in this case)
    res = adapter.add_clinvar_submission(test_sub_obj, user, institute, case)
    LOG.info('insert result is %s', res)
    assert type(res) == list

    # assert that one variant was actually inserted into the clinvar database collection
    assert adapter.clinvar_collection.find().count() == 1

    # try to insert the same variant once again. It should return an error code (res == 0)
    res = adapter.add_clinvar_submission(test_sub_obj, user, institute, case)
    assert res == 0


def test_get_clinvars_from_variant_id(adapter):
    """Test retrieving one clinvar submission object from mongo database by providing one variant ID"""

    res = adapter.clinvars(variant_ids = ['3eecfca5efea445eec6c19a53299043b'])

    # assert that one clinvar variant object is returned
    assert len(res) == 1


def test_get_clinvars_from_case_id(adapter, case_obj):
    """Test retrieving clinvar submission objects from mongo database by providing a case ID"""

    res = adapter.clinvars(case_id = case_obj['_id'])

    # assert that one clinvar variant object is returned
    assert len(res) == 1


def test_get_clinvars_from_submission_id(adapter):
    """Test retrieving clinvar submission objects from mongo database by providing a clinvar submission ID"""

    res = adapter.clinvars(submission_id = 'SUB666')

    # assert that one clinvar variant object is returned
    assert len(res) == 1


def test_add_clinvar_accession(adapter):
    """Updates a clinvar variant submission object with a new 'clinvar_accession' field"""

    variant_id = '3eecfca5efea445eec6c19a53299043b'
    original_doc = adapter.clinvar_collection.find({'_id' : variant_id})
    updated_doc = adapter.add_clinvar_accession(variant_id, 34568)

    # assert that the updated document in the database contains an extra field after the update
    assert len(updated_doc) == len(original_doc) + 1


def test_delete_clinvar_submission(adapter):
    """Delete all clinvar submission objects with a clinvar submission id"""

    deleted = adapter.delete_clinvar_submission('SUB666')

    # assert that one variant has been deleted
    assert deleted == 1

    # assert that the clinvar_collection in mongo database is now empty
    assert adapter.clinvar_collection.find().count() == 0
