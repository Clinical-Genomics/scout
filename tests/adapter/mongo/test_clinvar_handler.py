import logging
import pymongo
from scout.parse.clinvar import clinvar_submission_header,clinvar_submission_lines

LOG = logging.getLogger(__name__)

def get_test_submission_variant():
    """Returns a test clinvar variant submission object"""

    variant_subm_obj = {
        '_id' : "case1_a99ab86f2cb3bc18b993d740303ba27f",
        'csv_type' : "variant",
        'case_id' : "case1",
        'category' : "snv",
        'local_id' : "a99ab86f2cb3bc18b993d740303ba27f",
        'linking_id' : "a99ab86f2cb3bc18b993d740303ba27f",
        'chromosome' : "5",
        'start' : "7666888",
        'stop' : "7666888",
        'ref' : "A",
        'alt' : "T",
        'clinsig' : "Pathogenic"
    }
    return variant_subm_obj


def get_test_submission_case():
    """Returns a test casedata submission object"""

    casedata_subm_obj = {
        '_id' : "case1_a99ab86f2cb3bc18b993d740303ba27f_subj1",
        'csv_type': "casedata",
        'case_id' : "case1",
        'linking_id' : "a99ab86f2cb3bc18b993d740303ba27f",
        'individual_id' : "subj1",
        'clin_features' : "HP:0001392"
    }
    return casedata_subm_obj


def get_new_submission(adapter, user_obj, institute_obj):

    # Given a valid user id
    user_id = user_obj['_id']
    assert user_id

    # And a valid institute id
    institute_id = institute_obj['_id']
    assert institute_id

    # Check that a new clinvar submission can be created
    new_submission_id = adapter.create_submission( user_id=user_id, institute_id=institute_id)
    return new_submission_id


def test_create_submission(adapter, user_obj, institute_obj):
    """Test create a clinvar submission"""

    # Assert that a new submission can be created
    submission_id = get_new_submission(adapter, user_obj, institute_obj)
    assert submission_id

    # Check that submission is returned when collecting submissions by user_id and institute_id
    submissions = adapter.clinvar_submissions(user_obj['_id'], institute_obj['_id'])
    assert submissions[0]['_id'] == submission_id


def test_delete_submission(adapter, user_obj, institute_obj):
    """Test delete a clinvar submission providing its ID"""
    # Get the ID of an existing submission
    submission_id = get_new_submission(adapter, user_obj, institute_obj)

    # Check that it is possible to delete the submission
    deleted_objects = adapter.delete_submission(submission_id)
    assert deleted_objects == (0,1) # deleted 1 submission with 0 objects inside


def test_clinvar_submission_status(adapter, user_obj, institute_obj):
    """Test the function that returns an open clinvar submission object"""

    user_id = user_obj['_id']
    institute_id = institute_obj['_id']

    # Check that a new clinvar submission can be created
    submission_obj = adapter.get_open_clinvar_submission( user_id=user_id, institute_id=institute_id)
    assert submission_obj

    # And that its 'status' is set to "open"
    assert submission_obj['status'] == "open"

    # Update submission status to 'closed'
    updated_submission = adapter.update_clinvar_submission_status(user_id , submission_obj['_id'], "closed")

    # And that now its 'status' is set to "closed"
    assert updated_submission['status'] == "closed"


def test_update_clinvar_id(adapter, user_obj, institute_obj):
    """record an official clinvar submission name for a submission"""

    submission_id = get_new_submission(adapter, user_obj, institute_obj)

    # Update the submission with the official clinvar name
    updated_submission = adapter.update_clinvar_id(clinvar_id='SUB0001', submission_id=submission_id)

    # Assert that the submission was updated
    assert adapter.get_clinvar_id(submission_id) == "SUB0001"


def test_add_remove_subm_objects(adapter, user_obj, institute_obj):
    """Test adding variant and casedata objects to a submission"""

    # Get the ID of an existing submission
    submission_obj = adapter.get_open_clinvar_submission( user_id=user_obj['_id'], institute_id=institute_obj['_id'])

    # Given a test variant and its associated casedata
    variant_data = [ get_test_submission_variant() ] # a list of 1 dictionary element
    case_data = [ get_test_submission_case() ] # a list of 1 dictionary element
    subm_objs = (variant_data, case_data)

    # assert that clinvar collection in database is empty
    submission_objects = list(adapter.clinvar_collection.find())
    assert len(submission_objects) == 0

    # Add objects to submission
    updated_subm = adapter.add_to_submission( submission_obj['_id'], subm_objs)

    # Assert that 'variant_data' value of submission is updated
    assert updated_subm['variant_data'] == [variant_data[0].get('_id')]

    # Assert that 'case_data' value of submission is updated
    assert updated_subm['case_data'] == [case_data[0].get('_id')]

    # assert that clinvar collection in database has now 2 elements
    submission_objects = list(adapter.clinvar_collection.find())
    assert len(submission_objects) == 2

    # check if it is possible to create CSV files header for variant and casedata objects
    variants_file_header = clinvar_submission_header(submission_objects, 'variant_data')
    assert len(variants_file_header.keys()) > 0
    casedata_file_header = clinvar_submission_header(submission_objects, 'case_data')
    assert len(casedata_file_header.keys()) > 0

    # check if it is possible to create CSV files lines for variant and casedata objects
    variants_file_lines = clinvar_submission_lines(submission_objects, variants_file_header)
    assert len(variants_file_lines[0].split(',')) == len(variants_file_header.keys()) # variant file header and line have the same number of columns
    casedata_file_lines = clinvar_submission_lines(submission_objects, casedata_file_header)
    assert len(casedata_file_lines[0].split(',')) == len(casedata_file_header.keys()) # casedata file header and line have the same number of columns

    # assert that one of these objects is the variant object
    assert variant_data == adapter.clinvar_objs(submission_obj['_id'], 'variant_data')

    # assert that one of these objects is the case data object
    assert case_data == adapter.clinvar_objs(submission_obj['_id'], 'case_data')

    # assert that a variant is present for case 'case1'
    assert adapter.case_to_clinVars('case1') == {variant_data[0]['local_id'] : variant_data[0]}

    # Removal of clinvar objects from submission and from clinvar collection in database
    # remove case_data object
    updated_submission = adapter.delete_clinvar_object(object_id=case_data[0]['_id'], object_type='case_data', submission_id=submission_obj['_id'])
    assert updated_submission['case_data'] == []

    # remove variant object
    updated_submission = adapter.delete_clinvar_object(object_id=variant_data[0]['_id'], object_type='variant_data', submission_id=submission_obj['_id'])
    assert updated_submission['variant_data'] == []

    # assert that there are no objects left in clinvar collection
    submission_objects = list(adapter.clinvar_collection.find())
    assert len(submission_objects) == 0
