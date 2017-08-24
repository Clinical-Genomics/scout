import pytest
import logging
import datetime
import pymongo

from scout.models.event import VERBS_MAP

logger = logging.getLogger(__name__)

def test_create_event(adapter, institute_obj, case_obj, user_obj):    
    ## GIVEN a database without any events
    
    assert adapter.event_collection.find().count() == 0
    
    ## WHEN inserting a event
    verb = "status"
    adapter.create_event(
        institute=institute_obj, 
        case=case_obj, 
        user=user_obj, 
        link='a link', 
        category='case', 
        verb=verb,
        subject='a subject', 
        level='specific'
    )
    
    # THEN assert that the event was added to the database
    
    adapter.event_collection.find().count() == 1
    res = adapter.event_collection.find_one()
    
    assert res['verb'] == verb

def test_assign(case_database, institute_obj, case_obj, user_obj):
    adapter = case_database
    logger.info("Testing assign a user to a case")
    assert adapter.event_collection.find().count() == 0
    # GIVEN a populated databas
    institute = adapter.institute(
        institute_id=institute_obj['internal_id']
    )
    assert institute

    case = adapter.case(
        case_id=case_obj['_id']
    )
    assert case
    
    user = adapter.user(
        email = user_obj['email']
    )
    assert user

    link = 'assignlink'
    ## WHEN assigning a user to a case
    updated_case = adapter.assign(
        institute=institute,
        case=case,
        user=user,
        link=link
    )
    # THEN the case should have the user assigned
    assert updated_case['assignees'] == [user['_id']]
    # THEN an event should have been created
    assert adapter.event_collection.find().count() == 1
    
    event_obj = adapter.event_collection.find_one()
    assert event_obj['link'] == link

def test_unassign(case_database, institute_obj, case_obj, user_obj):
    adapter = case_database
    print('')
    
    updated_case = adapter.assign(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link='assignlink'
    )
    #The user should be added as assignee to the case
    # GIVEN a assigned case
    assert updated_case['assignees'] == [user_obj['_id']]

    # WHEN unassigning a user from a case
    updated_case = adapter.unassign(
         institute=institute_obj,
         case=case_obj,
         user=user_obj,
         link='unassignlink'
    )

    # THEN the two events should have been created
    assert adapter.event_collection.find().count() == 2
    
    # THEN the case should not be assigned
    assert updated_case.get('assignees') == []
    # THEN a unassign event should be created
    event = adapter.event_collection.find_one({'verb': 'unassign'})
    assert event['link'] == 'unassignlink'

def test_mark_causative(variant_database, institute_obj, case_obj, user_obj):
    adapter = variant_database
    logger.info("Testing mark a variant causative")
    # GIVEN a populated database with variants
    assert adapter.variant_collection.find().count() > 0
    assert adapter.event_collection.find().count() == 0
    
    variant = adapter.variant_collection.find_one()
    # GIVEN a populated databas
    institute = adapter.institute(
        institute_id=institute_obj['internal_id']
    )
    assert institute

    case = adapter.case(
        case_id=case_obj['_id']
    )
    assert case
    assert len(case.get('causatives', [])) == 0
    
    user = adapter.user(
        email = user_obj['email']
    )
    assert user

    link = 'markCausativelink'
    ## WHEN marking a variant as causative
    updated_case = adapter.mark_causative(
        institute=institute,
        case=case,
        user=user,
        link=link,
        variant=variant
    )
    # THEN the case should have a causative variant
    assert len(updated_case['causatives']) == 1
    # THEN two events should have been created, one for the case and one for the variant
    assert adapter.event_collection.find().count() == 2

    # THEN assert that case status is updated to solved
    assert updated_case['status'] == 'solved'
    
    event_obj = adapter.event_collection.find_one()
    assert event_obj['link'] == link

def test_unmark_causative(variant_database, institute_obj, case_obj, user_obj):
    adapter = variant_database
    logger.info("Testing mark a variant causative")
    
    variant = adapter.variant_collection.find_one()
    institute = adapter.institute(
        institute_id=institute_obj['internal_id']
    )
    case = adapter.case(
        case_id=case_obj['_id']
    )
    user = adapter.user(
        email = user_obj['email']
    )
    link = 'markCausativelink'
    updated_case = adapter.mark_causative(
        institute=institute,
        case=case,
        user=user,
        link=link,
        variant=variant
    )
    # GIVEN a populated database with one variant marked causative
    assert len(updated_case['causatives']) == 1
    assert updated_case['status'] == 'solved'
    assert adapter.event_collection.find().count() == 2

    ## WHEN marking a unmarking a variant as causative

    link = 'unMarkCausativelink'
    updated_case = adapter.unmark_causative(
        institute=institute,
        case=updated_case,
        user=user,
        link=link,
        variant=variant
    )
    
    ## THEN assert that the cusative variant is removed
    assert len(updated_case['causatives']) == 0

    ## THEN assert that the status is changed to 'active'
    assert updated_case['status'] == 'active'
    
    # THEN two new events should have been created, one for the case and one for the variant
    assert adapter.event_collection.find().count() == 4

def test_update_synopsis(case_database, institute_obj, case_obj, user_obj):
    adapter = case_database
    synopsis = "The updated synopsis"
    # GIVEN a populated database without events
    assert adapter.event_collection.find().count() == 0

    link = 'synopsislink'
    # WHEN updating synopsis for a case
    updated_case = adapter.update_synopsis(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        content=synopsis
    )
    # THEN the case should have the synopsis added
    assert updated_case['synopsis'] == synopsis

    # THEN an event for synopsis should have been added
    event = adapter.event_collection.find_one({'link': link})
    assert event['content'] == synopsis

def test_archive_case(case_database, institute_obj, case_obj, user_obj):
    adapter = case_database
    logger.info("Set a case to archive status")
    # GIVEN a populated database without events
    assert adapter.event_collection.find().count() == 0
    
    # WHEN setting a case in archive status
    link = 'archivelink'
    updated_case = adapter.archive_case(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
    )
    # THEN the case status should be archived
    assert updated_case['status'] == 'archived'

    # THEN a event for archiving should be added
    event = adapter.event_collection.find_one({'link': link})
    assert event['link'] == link

def test_open_research(case_database, institute_obj, case_obj, user_obj):
    adapter = case_database
    # GIVEN a populated database without events
    assert adapter.event_collection.find().count() == 0
    assert adapter.case_collection.find_one({'_id': case_obj['_id']}).get('research_requested', False) == False 
    
    
    # WHEN setting opening research for a case
    link = 'openresearchlink'
    updated_case = adapter.open_research(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
    )
    # THEN research_requested should be True
    assert updated_case['research_requested'] == True

    # THEN an event for opening research should be created
    event = adapter.event_collection.find_one({'link': link})
    assert event['link'] == 'openresearchlink'

def test_add_hpo(case_database, institute_obj, case_obj, user_obj):
    adapter = case_database
    logger.info("Add a HPO term for a case")
    # GIVEN a populated database
    gene_obj = dict(
        hgnc_id = 1,
        hgnc_symbol = 'test',
        ensembl_id = 'anothertest',
        chromosome = '1',
        start = 10,
        end = 20,
        build = '37'
    )
    adapter.load_hgnc_gene(gene_obj)

    hpo_obj = dict(
        _id = 'HP:0000878',
        hpo_id = 'HP:0000878',
        description = 'A term',
        genes = [1]
    )

    adapter.load_hpo_term(hpo_obj)

    hpo_term = hpo_obj['hpo_id']

    # WHEN adding a hpo term for a case
    link = 'addhpolink'
    
    updated_case = adapter.add_phenotype(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link=link,
        hpo_term=hpo_term
    )
    # THEN the case should have a hpo term
    for term in updated_case['phenotype_terms']:
        assert term['phenotype_id'] == hpo_term

    # THEN a event should have been created
    event = adapter.event_collection.find_one({'link': link})
    assert event['link'] == link

def test_add_phenotype_group(hpo_database, institute_obj, case_obj, user_obj):
    adapter = hpo_database
    logger.info("Add OMIM term for a case")
    adapter._add_case(case_obj)

    hpo_term = 'HP:0000878'
    
    #Existing mim phenotype
    # GIVEN a populated database with no events
    assert adapter.hpo_term_collection.find().count() > 0
    assert adapter.hpo_term_collection.find({'_id':hpo_term})
    assert adapter.event_collection.find().count() == 0

    # WHEN adding a existing phenotype term
    updated_case = adapter.add_phenotype(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link='hpolink',
        hpo_term=hpo_term,
        is_group=True,
    )
    # THEN the case should have phenotypes
    assert len(updated_case['phenotype_terms']) > 0
    assert len(updated_case['phenotype_groups']) > 0

    # THEN there should be phenotype events
    assert adapter.event_collection.find().count() > 0

def test_add_wrong_hpo(populated_database, institute_obj, case_obj, user_obj):
    logger.info("Add a HPO term for a case")
    # GIVEN a populated database
    hpo_term = 'k'
    # WHEN adding a wrong hpo term for a case
    with pytest.raises(ValueError):
    # THEN a value error should be raised
        populated_database.add_phenotype(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link='addhpolink',
            hpo_term=hpo_term
        )

def test_add_no_term(populated_database, institute_obj, case_obj, user_obj):
    logger.info("Add a HPO term for a case")
    # GIVEN a populated database
    # WHEN adding hpo term without a term
    with pytest.raises(ValueError):
        # THEN a value error should be raised
        populated_database.add_phenotype(
            institute=institute_obj,
            case=case_obj,
            user=user_obj,
            link='addhpolink',
        )

def test_add_non_existing_mim(populated_database, institute_obj, case_obj, user_obj):
    adapter = populated_database
    logger.info("Add OMIM term for a case")
    #Non existing mim phenotype
    mim_term = 'MIM:0000002'
    # GIVEN a populated database
    
    # WHEN adding a non existing phenotype term
    updated_case = adapter.add_phenotype(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link='mimlink',
        omim_term=mim_term
    )
    # THEN the case should not have any phenotypes
    assert len(updated_case.get('phenotype_terms', [])) == 0

    # THEN there should not exist any events
    assert adapter.event_collection.find().count() == 0

def test_add_mim(hpo_database, institute_obj, case_obj, user_obj):
    adapter = hpo_database
    logger.info("Add OMIM term for a case")
    adapter._add_case(case_obj)
    
    #Existing mim phenotype
    mim_obj = adapter.disease_term_collection.find_one()
    mim_term = mim_obj['_id']
    
    assert adapter.hpo_term_collection.find().count() > 0
    # GIVEN a populated database
    assert adapter.event_collection.find().count() == 0

    # WHEN adding a existing phenotype term
    updated_case = adapter.add_phenotype(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link='mimlink',
        omim_term=mim_term
    )
    # THEN the case should have phenotypes
    assert len(updated_case['phenotype_terms']) > 0

    # THEN there should be phenotype events
    assert adapter.event_collection.find().count() > 0

def test_remove_hpo(hpo_database, institute_obj, case_obj, user_obj):
    adapter = hpo_database
    logger.info("Add a HPO term for a case")
    adapter._add_case(case_obj)

    # GIVEN a populated database
    assert adapter.event_collection.find().count() == 0

    hpo_term = 'HP:0000878'

    updated_case = adapter.add_phenotype(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link='addhpolink',
        hpo_term=hpo_term
    )

    #Assert that the term was added to the case
    assert len(updated_case['phenotype_terms']) == 1

    #Check that the event exists
    assert adapter.event_collection.find().count() == 1
    
    # WHEN removing the phenotype term
    updated_case = adapter.remove_phenotype(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link='removehpolink',
        phenotype_id=hpo_term
    )
    # THEN the case should not have phenotype terms
    assert len(updated_case['phenotype_terms']) == 0

    # THEN an event should have been created
    assert adapter.event_collection.find().count() == 2

def test_specific_comment(variant_database, institute_obj, case_obj, user_obj):
    adapter = variant_database
    logger.info("Add specific comment for a variant")
    content = "hello"
    # GIVEN a populated database with variants
    assert adapter.variant_collection.find().count() > 0
    assert adapter.event_collection.find().count() == 0
    
    variant = adapter.variant_collection.find_one()
    
    # WHEN commenting on a variant
    updated_variant = variant_database.comment(
        institute=institute_obj,
        case=case_obj,
        user=user_obj,
        link='commentlink',
        variant=variant,
        content=content,
        comment_level='specific'
    )
    # THEN the variant should have comments
    event = adapter.event_collection.find_one()
    assert event['content'] == content

def test_add_cohort(case_database, institute_obj, case_obj, user_obj):
    adapter = case_database
    logger.info("Testing assign a user to a case")
    assert adapter.event_collection.find().count() == 0
    # GIVEN a populated databas
    institute = adapter.institute(
        institute_id=institute_obj['internal_id']
    )
    assert institute

    case = adapter.case(
        case_id=case_obj['_id']
    )
    assert case
    assert case.get('cohorts') == None
    
    user = adapter.user(
        email = user_obj['email']
    )
    assert user

    cohort_name = 'cohort'
    
    link = 'cohortlink'
    ## WHEN adding a cohort to a case
    updated_case = adapter.add_cohort(
        institute=institute,
        case=case,
        user=user,
        link=link,
        tag=cohort_name
    )
    # THEN the case should have the cohort saved
    assert set(updated_case['cohorts']) == set([cohort_name])
    # THEN an event should have been created
    assert adapter.event_collection.find().count() == 1

    event_obj = adapter.event_collection.find_one()
    assert event_obj['link'] == link

def test_remove_cohort(case_database, institute_obj, case_obj, user_obj):
    adapter = case_database
    logger.info("Testing assign a user to a case")

    institute = adapter.institute(
        institute_id=institute_obj['internal_id']
    )
    case = adapter.case(
        case_id=case_obj['_id']
    )
    user = adapter.user(
        email = user_obj['email']
    )

    cohort_name = 'cohort'
    link = 'cohortlink'

    updated_case = adapter.add_cohort(
        institute=institute,
        case=case,
        user=user,
        link=link,
        tag=cohort_name
    )
    assert adapter.event_collection.find().count() == 1
    
    case = adapter.case(
        case_id=case_obj['_id']
    )
    assert case.get('cohorts')
    
    ## WHEN removing a cohort from a case
    updated_case = adapter.remove_cohort(
        institute=institute,
        case=case,
        user=user,
        link=link,
        tag=cohort_name
    )
    # THEN the case should have the cohort saved
    assert updated_case['cohorts'] == []
    # THEN an event should have been created
    assert adapter.event_collection.find().count() == 2

def test_update_default_panels(case_database, institute_obj, case_obj, user_obj):
    adapter = case_database
    print('')
    # GIVEN a case with one gene panel
    assert len(case_obj['panels']) == 1
    
    for panel in case_obj['panels']:
        if panel['panel_name'] == 'panel1':
            assert panel['is_default'] == True
            print(panel)
    
    new_panel = {
        '_id': 'an_id', 
        'panel_id': 'an_id', 
        'panel_name': 'panel2', 
        'display_name': 'Test panel2', 
        'version': 1.0, 
        'updated_at': datetime.datetime.now(), 
        'nr_genes': 263, 
        'is_default': False
    }
    case_obj = adapter.case_collection.find_one_and_update(
        {'_id':case_obj['_id']},
        {
            '$addToSet': {'panels': new_panel},
        },
        return_document = pymongo.ReturnDocument.AFTER
    )
    
    assert len(case_obj['panels']) == 2
    
    # WHEN updating the default panels
    
    updated_case = adapter.update_default_panels(
         institute_obj=institute_obj,
         case_obj=case_obj,
         user_obj=user_obj,
         link='update_default_link',
         panel_objs = [new_panel]
    )

    # THEN the the updated case should have panel1 as not default and panel2 
    # as default
    for panel in updated_case['panels']:
        if panel['panel_name'] == 'panel1':
            assert panel['is_default'] == False
        elif panel['panel_name'] == 'panel2':
            assert panel['is_default'] == True
        
    # assert adapter.event_collection.find().count() == 2
    #
    # # THEN the case should not be assigned
    # assert updated_case.get('assignees') == []
    # # THEN a unassign event should be created
    # event = adapter.event_collection.find_one({'verb': 'unassign'})
    # assert event['link'] == 'unassignlink'
