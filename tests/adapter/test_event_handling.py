import pytest
import logging

from mongoengine import DoesNotExist

from scout.adapter import MongoAdapter
from scout.models import (Variant, Case, Event, Institute, PhenotypeTerm, 
                          Institute, User)

logger = logging.getLogger(__name__)

def test_assign(populated_database, institute_obj, case_obj, user_obj):
    logger.info("Testing assign a user to a case")
    # GIVEN a populated database
    institute = populated_database.institute(
        institute_id=institute_obj.internal_id
    )
    case = populated_database.case(
        institute_id=institute_obj.internal_id, 
        case_id=case_obj.display_name
    )
    user = populated_database.user(
        email = user_obj.email
    )
    # WHEN assigning a user to a case
    populated_database.assign(
        institute=institute,
        case=case,
        user=user,
        link='assignlink'
    )
    updated_case = Case.objects.get(case_id=case_obj.case_id)
    # THEN the case should have the user assigned
    assert updated_case.assignee == user
    # THEN an event should have been created
    event = Event.objects.get(verb='assign')
    assert event.link == 'assignlink'


def test_unassign(populated_database, institute_obj, case_obj, user_obj):
    print('')
    institute = populated_database.institute(
        institute_id=institute_obj.internal_id
    )
    case = populated_database.case(
        institute_id=institute_obj.internal_id, 
        case_id=case_obj.display_name
    )
    user = populated_database.user(
        email = user_obj.email
    )
    populated_database.assign(
        institute=institute,
        case=case,
        user=user,
        link='assignlink'
    )
    #The user should be added as assignee to the case
    # GIVEN a assigned case
    updated_case = Case.objects.get(case_id=case_obj.case_id)

    # WHEN unassigning a user from a case
    populated_database.unassign(
        institute=institute,
        case=updated_case,
        user=user,
        link='unassignlink'
    )

    # THEN the case should not be assigned
    updated_case = Case.objects.get(case_id=case_obj.case_id)
    assert updated_case.assignee == None
    # THEN a unassign event should be created
    event = Event.objects.get(verb='unassign')
    assert event.link == 'unassignlink'


def test_update_synopsis(populated_database, institute_obj, case_obj, user_obj):
    synopsis = "The updated synopsis"
    logger.info("Testing assign a user to a case")
    # GIVEN a populated database
    institute = populated_database.institute(
        institute_id=institute_obj.internal_id
    )
    case = populated_database.case(
        institute_id=institute_obj.internal_id, 
        case_id=case_obj.display_name
    )
    user = populated_database.user(
        email = user_obj.email
    )

    # WHEN updating synopsis for a case
    populated_database.update_synopsis(
        institute=institute,
        case=case,
        user=user,
        link='synopsislink',
        content=synopsis
    )
    # THEN the case should have the synopsis added
    updated_case = Case.objects.get(case_id=case_obj.case_id)
    assert updated_case.synopsis == synopsis

    # THEN an event for synopsis should have been added
    event = Event.objects.get(verb='synopsis')
    assert event.content == synopsis

def test_archive_case(populated_database, institute_obj, case_obj, user_obj):
    logger.info("Set a case to archive status")
    # GIVEN a populated database
    institute = populated_database.institute(
        institute_id=institute_obj.internal_id
    )
    case = populated_database.case(
        institute_id=institute_obj.internal_id, 
        case_id=case_obj.display_name
    )
    user = populated_database.user(
        email = user_obj.email
    )
    # WHEN setting a case in archive status
    populated_database.archive_case(
        institute=institute,
        case=case,
        user=user,
        link='archivelink',
    )
    # THEN the case status should be archived
    updated_case = Case.objects.get(case_id=case_obj.case_id)
    assert updated_case.status == 'archived'

    # THEN a event for archiving should be added
    event = Event.objects.get(verb='archive')
    assert event.link == 'archivelink'

def test_open_research(populated_database, institute_obj, case_obj, user_obj):
    logger.info("Open research for a case")
    # GIVEN a populated database
    institute = populated_database.institute(
        institute_id=institute_obj.internal_id
    )
    case = populated_database.case(
        institute_id=institute_obj.internal_id, 
        case_id=case_obj.display_name
    )
    user = populated_database.user(
        email = user_obj.email
    )
    # WHEN setting opening research for a case
    populated_database.open_research(
        institute=institute,
        case=case,
        user=user,
        link='openresearchlink',
    )
    # THEN research_requested should be True
    updated_case = Case.objects.get(case_id=case_obj.case_id)
    assert updated_case.research_requested == True

    # THEN an event for opening research should be created
    event = Event.objects.get(verb='open_research')
    assert event.link == 'openresearchlink'
    event.delete()

def test_add_hpo(populated_database, institute_obj, case_obj, user_obj):
    logger.info("Add a HPO term for a case")
    # GIVEN a populated database
    hpo_term = 'HP:0000878'
    institute = populated_database.institute(
        institute_id=institute_obj.internal_id
    )
    case = populated_database.case(
        institute_id=institute_obj.internal_id, 
        case_id=case_obj.display_name
    )
    user = populated_database.user(
        email = user_obj.email
    )
    # WHEN adding a hpo term for a case
    populated_database.add_phenotype(
        institute=institute,
        case=case,
        user=user,
        link='addhpolink',
        hpo_term=hpo_term
    )
    # THEN the case should have a hpo term
    updated_case = Case.objects.get(case_id=case_obj.case_id)
    for term in updated_case.phenotype_terms:
        assert term.phenotype_id == hpo_term

    # THEN a event should have been created
    event = Event.objects.get(verb='add_phenotype')
    assert event.link == 'addhpolink'
    event.delete()

def test_add_wrong_hpo(populated_database, institute_obj, case_obj, user_obj):
    logger.info("Add a HPO term for a case")
    # GIVEN a populated database
    hpo_term = 'k'
    institute = populated_database.institute(
        institute_id=institute_obj.internal_id
    )
    case = populated_database.case(
        institute_id=institute_obj.internal_id, 
        case_id=case_obj.display_name
    )
    user = populated_database.user(
        email = user_obj.email
    )
    # WHEN adding a wrong hpo term for a case
    with pytest.raises(ValueError):
    # THEN a value error should be raised
        populated_database.add_phenotype(
            institute=institute,
            case=case,
            user=user,
            link='addhpolink',
            hpo_term=hpo_term
        )

def test_add_no_term(populated_database, institute_obj, case_obj, user_obj):
    logger.info("Add a HPO term for a case")
    # GIVEN a populated database
    hpo_term = 'k'
    institute = populated_database.institute(
        institute_id=institute_obj.internal_id
    )
    case = populated_database.case(
        institute_id=institute_obj.internal_id, 
        case_id=case_obj.display_name
    )
    user = populated_database.user(
        email = user_obj.email
    )
    # WHEN adding hpo term without a term
    with pytest.raises(ValueError):
        # THEN a value error should be raised
        populated_database.add_phenotype(
            institute=institute,
            case=case,
            user=user,
            link='addhpolink',
        )

def test_add_non_existing_mim(populated_database, institute_obj, case_obj, user_obj):
    logger.info("Add OMIM term for a case")
    #Non existing mim phenotype
    mim_term = 'MIM:0000002'
    # GIVEN a populated database
    institute = populated_database.institute(
        institute_id=institute_obj.internal_id
    )
    case = populated_database.case(
        institute_id=institute_obj.internal_id, 
        case_id=case_obj.display_name
    )
    user = populated_database.user(
        email = user_obj.email
    )
    # WHEN adding a non existing phenotype term
    populated_database.add_phenotype(
        institute=institute,
        case=case,
        user=user,
        link='mimlink',
        omim_term=mim_term
    )
    # THEN the case should not have any phenotypes
    updated_case = Case.objects.get(case_id=case_obj.case_id)
    assert len(updated_case.phenotype_terms) == 0

    # THEN there should not exist any events
    with pytest.raises(DoesNotExist):
        event = Event.objects.get(verb='add_phenotype')

def test_add_mim(populated_database, institute_obj, case_obj, user_obj):
    logger.info("Add OMIM term for a case")
    #Existing mim phenotype
    mim_term = 'OMIM:613855'
    
    # GIVEN a populated database
    institute = populated_database.institute(
        institute_id=institute_obj.internal_id
    )
    case = populated_database.case(
        institute_id=institute_obj.internal_id, 
        case_id=case_obj.display_name
    )
    user = populated_database.user(
        email = user_obj.email
    )
    # WHEN adding a existing phenotype term
    populated_database.add_phenotype(
        institute=institute,
        case=case,
        user=user,
        link='mimlink',
        omim_term=mim_term
    )
    # THEN the case should have phenotypes
    updated_case = Case.objects.get(case_id=case_obj.case_id)
    assert len(updated_case.phenotype_terms) != 0

    # THEN there should be phenotypes
    for event in Event.objects(verb='add_phenotype'):
        assert event.link == 'mimlink'
        event.delete()

def test_remove_hpo(populated_database, institute_obj, case_obj, user_obj):
    logger.info("Add a HPO term for a case")
    hpo_term = 'HP:0000878'
    institute = populated_database.institute(
        institute_id=institute_obj.internal_id
    )
    case = populated_database.case(
        institute_id=institute_obj.internal_id, 
        case_id=case_obj.display_name
    )
    user = populated_database.user(
        email = user_obj.email
    )
    populated_database.add_phenotype(
        institute=institute,
        case=case,
        user=user,
        link='addhpolink',
        hpo_term=hpo_term
    )
    
    #Assert that the synopsis has been added to the case
    updated_case = Case.objects.get(case_id=case_obj.case_id)
    for term in updated_case.phenotype_terms:
        assert term.phenotype_id == hpo_term

    #Check that the event exists
    event = Event.objects.get(verb='add_phenotype')
    assert event.link == 'addhpolink'
    
    # GIVEN a populated database where a phenotype term was added

    # WHEN removing the phenotype term
    populated_database.remove_phenotype(
        institute=institute,
        case=updated_case,
        user=user,
        link='removehpolink',
        phenotype_id=hpo_term
    )
    # THEN the case should not have phenotype terms
    updated_case = Case.objects.get(case_id=case_obj.case_id)
    assert len(updated_case.phenotype_terms) == 0

    # THEN an event should have been created
    event = Event.objects.get(verb='remove_phenotype')
    assert event.link == 'removehpolink'
    event.delete()

# def test_specific_comment(variant_database, institute_obj, case_obj, user_obj):
#     logger.info("Add specific comment for a variant")
#     content = "hello"
#     # GIVEN a populated database with variants
#     institute = variant_database.institute(
#         institute_id=institute_obj.internal_id
#     )
#     case = variant_database.case(
#         institute_id=institute_obj.internal_id,
#         case_id=case_obj.display_name
#     )
#     user = variant_database.user(
#         email = user_obj.email
#     )
#     variant =  Variant.objects.first()
#     variant_id = variant.id
#
#     # WHEN commenting on a variant
#     variant_database.comment(
#         institute=institute,
#         case=case,
#         user=user,
#         link='commentlink',
#         variant=variant,
#         content=content,
#         comment_level='specific'
#     )
#     # THEN the variant should have comments
#     updated_variant = variant_database.variant(variant_id)
#     assert updated_variant.has_comments(case=case) == True
#
#     # THEN a event should have been created
#     event = Event.objects.get(verb='comment')
#     assert event.link == 'commentlink'
