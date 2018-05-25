import logging
import pymongo
from numbers import Number

LOG = logging.getLogger(__name__)

def get_test_submission_object():
    """Returns a test clinvar variant submission object"""

    clivar_subm_obj = {
        '_id' : '5ttcfca5efcd887aab6c20a69367866n',
        '##Local_ID' : '5ttcfca5efcd887aab6c20a69367866n',
        'Reference_allele' : 'T',
        'Alternate_allele' : 'C',
        'Chromosome' : '8',
        'Start' : '34907896',
        'Stop' : '34907896',
        'Clinical_significance' : 'Benign',
        'Condition_ID_value' : 'HP:0001298;HP:0002121',
        'clinvar_submission' : 'SUB777',
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
    adapter.add_clinvar_submission(test_sub_obj, user, institute, case)

    # assert that one variant was actually inserted into the clinvar database collection
    assert adapter.clinvar_collection.find().count() == 1

    # try to insert the same variant once again. It should return an error code (res == 0)
    res = adapter.add_clinvar_submission(test_sub_obj, user, institute, case)
    assert res == 0


def test_get_clinvars_from_variant_id(clinvar_database):
    """Test retrieving one clinvar submission object from mongo database by providing one variant ID"""

    adapter = clinvar_database

    res = adapter.clinvars(variant_ids = ['3eecfca5efea445eec6c19a53299043b'])

    # assert that a database field of that variant corresponds to the one in the query
    assert res[0]['Clinical_significance'] == 'Likely Pathogenic'


def test_get_clinvars_from_case_id(clinvar_database, case_obj):
    """Test retrieving clinvar submission objects from mongo database by providing a case ID"""

    adapter = clinvar_database

    res = adapter.clinvars(case_id = case_obj['_id'])

    # assert that a database field of that variant corresponds to the one in the query
    assert res[0]['Clinical_significance'] == 'Likely Pathogenic'


def test_get_clinvars_from_submission_id(clinvar_database, case_obj):
    """Test retrieving clinvar submission objects from mongo database by providing a clinvar submission ID"""

    adapter = clinvar_database

    res = adapter.clinvars(submission_id = 'SUB666')

    # assert that a database field of that variant corresponds to the one in the query
    assert res[0]['Clinical_significance'] == 'Likely Pathogenic'


def test_add_clinvar_accession(clinvar_database):
    """Updates a clinvar variant submission object with a new 'clinvar_accession' field"""

    adapter = clinvar_database

    variant_id = '3eecfca5efea445eec6c19a53299043b'
    original_doc = adapter.clinvar_collection.find({'_id' : variant_id})

    # assert that before the update the clinvar object does NOT contain a clinvar accession field
    assert 'clinvar_accession' not in original_doc[0]

    updated_doc = adapter.add_clinvar_accession(variant_id, 998888)

    # assert that after the update the clinvar object documents does contain a clinvar accession field
    assert 'clinvar_accession' in updated_doc


def test_delete_clinvar_submission(clinvar_database):
    """Delete all clinvar submission objects with a clinvar submission id"""

    adapter = clinvar_database

    deleted = adapter.delete_clinvar_submission('SUB666')

    # assert that one variant has been deleted
    assert deleted == 1

    # assert that the clinvar_collection in mongo database is now empty
    assert adapter.clinvar_collection.find().count() == 0
