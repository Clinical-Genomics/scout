import pytest
import logging

from mongoengine import DoesNotExist

from scout.ext.backend import MongoAdapter
from scout.models import (Variant, Case, Event, Institute, PhenotypeTerm, 
                          Institute, User)

logger = logging.getLogger(__name__)

# def test_assign(setup_database, get_institute, get_user, get_case):
#     logger.info("Testing assign a user to a case")
#     setup_database.assign(
#         institute=get_institute,
#         case=get_case,
#         user=get_user,
#         link='assignlink'
#     )
#     #The user should be added as assignee to the case
#     updated_case = Case.objects.get(case_id="acase")
#     assert updated_case.assignee == get_user
#     #Check that the event exists
#     event = Event.objects.get(verb='assign')
#     assert event.link == 'assignlink'
#     event.delete()

#
# def test_unassign(setup_database, get_institute, get_user, get_case):
#     print('')
#     logger.info("Assign a user to a case")
#     setup_database.assign(
#         institute=get_institute,
#         case=get_case,
#         user=get_user,
#         link='assignlink'
#     )
#     #The user should be added as assignee to the case
#     updated_case = Case.objects.get(case_id="acase")
#     assert updated_case.assignee == get_user
#
#     setup_database.unassign(
#         institute=get_institute,
#         case=get_case,
#         user=get_user,
#         link='unassignlink'
#     )
#
#     #The user should have been unassigned from the case
#     updated_case = Case.objects.get(case_id="acase")
#     assert updated_case.assignee == None
#     #Check that the event exists
#     event = Event.objects.get(verb='unassign')
#     assert event.link == 'unassignlink'
#     event.delete()
#
#
# def test_update_synopsis(setup_database, get_institute, get_user, get_case):
#     synopsis = "The updated synopsis"
#     logger.info("Update synopsis for a case")
#     setup_database.update_synopsis(
#         institute=get_institute,
#         case=get_case,
#         user=get_user,
#         link='synopsislink',
#         content=synopsis
#     )
#     #Assert that the synopsis has been added to the case
#     updated_case = Case.objects.get(case_id="acase")
#     assert updated_case.synopsis == synopsis
#
#     #Check that the event exists
#     event = Event.objects.get(verb='synopsis')
#     assert event.content == synopsis
#     event.delete()
#
# def test_archive_case(setup_database, get_institute, get_user, get_case):
#     logger.info("Set a case to archive status")
#     setup_database.archive_case(
#         institute=get_institute,
#         case=get_case,
#         user=get_user,
#         link='archivelink',
#     )
#     #Assert that the synopsis has been added to the case
#     updated_case = Case.objects.get(case_id="acase")
#     assert updated_case.status == 'archived'
#
#     #Check that the event exists
#     event = Event.objects.get(verb='archive')
#     assert event.link == 'archivelink'
#     event.delete()
#
# def test_open_research(setup_database, get_institute, get_user, get_case):
#     logger.info("Open research for a case")
#     setup_database.open_research(
#         institute=get_institute,
#         case=get_case,
#         user=get_user,
#         link='openresearchlink',
#     )
#     #Assert that the synopsis has been added to the case
#     updated_case = Case.objects.get(case_id="acase")
#     assert updated_case.is_research == True
#
#     #Check that the event exists
#     event = Event.objects.get(verb='open_research')
#     assert event.link == 'openresearchlink'
#     event.delete()
#
# def test_add_hpo(setup_database, get_institute, get_user, get_case):
#     logger.info("Add a HPO term for a case")
#     hpo_term = 'HP:0000002'
#     setup_database.add_phenotype(
#         institute=get_institute,
#         case=get_case,
#         user=get_user,
#         link='addhpolink',
#         hpo_term=hpo_term
#     )
#     #Assert that the synopsis has been added to the case
#     updated_case = Case.objects.get(case_id="acase")
#     for term in updated_case.phenotype_terms:
#         assert term.phenotype_id == hpo_term
#
#     #Check that the event exists
#     event = Event.objects.get(verb='add_phenotype')
#     assert event.link == 'addhpolink'
#     event.delete()
#
# def test_add_wrong_hpo(setup_database, get_institute, get_user, get_case):
#     logger.info("Add a HPO term for a case")
#     hpo_term = 'k'
#     with pytest.raises(ValueError):
#         setup_database.add_phenotype(
#             institute=get_institute,
#             case=get_case,
#             user=get_user,
#             link='addhpolink',
#             hpo_term=hpo_term
#         )
#
# def test_add_no_term(setup_database, get_institute, get_user, get_case):
#     logger.info("Try to call event without term")
#     with pytest.raises(ValueError):
#         setup_database.add_phenotype(
#             institute=get_institute,
#             case=get_case,
#             user=get_user,
#             link='addhpolink',
#         )
#
# def test_add_non_existing_mim(setup_database, get_institute, get_user, get_case):
#     logger.info("Add OMIM term for a case")
#     #Non existing mim phenotype
#     mim_term = 'MIM:0000002'
#     setup_database.add_phenotype(
#         institute=get_institute,
#         case=get_case,
#         user=get_user,
#         link='mimlink',
#         omim_term=mim_term
#     )
#     #Assert that the synopsis has been added to the case
#     updated_case = Case.objects.get(case_id="acase")
#     assert len(updated_case.phenotype_terms) == 0
#
#     #Check that the event not exists
#     with pytest.raises(DoesNotExist):
#         event = Event.objects.get(verb='add_phenotype')
#
# def test_add_mim(setup_database, get_institute, get_user, get_case):
#     logger.info("Add OMIM term for a case")
#     #Non existing mim phenotype
#     mim_term = 'MIM:614300'
#     setup_database.add_phenotype(
#         institute=get_institute,
#         case=get_case,
#         user=get_user,
#         link='mimlink',
#         omim_term=mim_term
#     )
#     #Assert that the synopsis has been added to the case
#     updated_case = Case.objects.get(case_id="acase")
#     assert len(updated_case.phenotype_terms) != 0
#
#     #Check that the event not exists
#     for event in Event.objects(verb='add_phenotype'):
#         assert event.link == 'mimlink'
#         event.delete()
#
# def test_remove_hpo(setup_database, get_institute, get_user, get_case):
#     logger.info("Add a HPO term for a case")
#     hpo_term = 'HP:0000002'
#     setup_database.add_phenotype(
#         institute=get_institute,
#         case=get_case,
#         user=get_user,
#         link='addhpolink',
#         hpo_term=hpo_term
#     )
#     #Assert that the synopsis has been added to the case
#     updated_case = Case.objects.get(case_id="acase")
#     for term in updated_case.phenotype_terms:
#         assert term.phenotype_id == hpo_term
#
#     #Check that the event exists
#     event = Event.objects.get(verb='add_phenotype')
#     assert event.link == 'addhpolink'
#     event.delete()
#
#     #Remove the term_
#     setup_database.remove_phenotype(
#         institute=get_institute,
#         case=get_case,
#         user=get_user,
#         link='removehpolink',
#         phenotype_id=hpo_term
#     )
#     #Assert that the synopsis has been added to the case
#     updated_case = Case.objects.get(case_id="acase")
#     assert len(updated_case.phenotype_terms) == 0
#
#     #Check that the event exists
#     event = Event.objects.get(verb='remove_phenotype')
#     assert event.link == 'removehpolink'
#     event.delete()
#
# def test_specific_comment(setup_database, get_institute, get_user, get_case,
#                           get_variant):
#     logger.info("Add specific comment for a variant")
#     content = "hello"
#     setup_database.comment(
#         institute=get_institute,
#         case=get_case,
#         user=get_user,
#         link='commentlink',
#         variant=get_variant,
#         content=content,
#         comment_level='specific'
#     )
#     #Assert that the synopsis has been added to the case
#     updated_variant = Variant.objects.first()
#     assert updated_variant.has_comments(case=get_case) == True
#
#     #Check that the event exists
#     event = Event.objects.get(verb='comment')
#     assert event.link == 'commentlink'
#     event.delete()
