from datetime import datetime
from dateutil.parser import parse as parse_date

from scout.load.report import load_delivery_report
from scout.exceptions import DataNotFoundError, IntegrityError


def test_load_delivery_report_bad_case_id(panel_database):
    adapter = panel_database

    # GIVEN no cases in database
    assert adapter.cases().count() == 0

    # WHEN trying to load a report for a case_id that does not exist in the data base
    case_id = 'id_of_non_existing_case'
    institute_id = None
    display_name = None
    report_path = 'a_dummy_path'

    try:
        load_delivery_report(adapter=adapter, case_id=case_id, institute_id=institute_id,
                             display_name=display_name,
                             report_path=report_path)
        assert False
    except DataNotFoundError:
        # THEN an exception should be raised
        assert True


def test_load_delivery_report_bad_institute_id(case_database):
    adapter = case_database

    # GIVEN cases in database
    assert adapter.cases().count() > 0
    case_obj = adapter.cases()[0]

    # WHEN trying to load a report for an institute that does not exist in the data base
    case_id = None
    institute_id = 'id_of_non_existing_institute'
    display_name = case_obj['display_name']
    report_path = 'a_dummy_path'

    try:
        load_delivery_report(adapter=adapter, case_id=case_id, institute_id=institute_id,
                             display_name=display_name,
                             report_path=report_path)
        assert False
    except DataNotFoundError:
        # THEN an exception should be raised
        assert True


def test_load_delivery_report_bad_display_name(case_database):
    adapter = case_database

    # GIVEN cases in database
    assert adapter.cases().count() > 0
    case_obj = adapter.cases()[0]

    # WHEN trying to load a report for an display name that does not exist in the data base
    case_id = None
    institute_id = case_obj['owner']
    display_name = 'id_of_non_existing_display'
    report_path = 'a_dummy_path'

    try:
        load_delivery_report(adapter=adapter, case_id=case_id, institute_id=institute_id,
                             display_name=display_name,
                             report_path=report_path)
        assert False
    except DataNotFoundError:
        # THEN an exception should be raised
        assert True


def test_load_delivery_report_without_date_sucess(case_database):
    adapter = case_database

    # GIVEN a case exist, without a delivery report for the given analysis date
    assert adapter.cases().count() > 0
    case_obj = adapter.cases()[0]
    assert not case_obj.get('analyses')

    # WHEN trying to load a report for a case_id that does exist in the data base
    case_id = case_obj['_id']
    report_path = 'report_test_path'

    load_delivery_report(adapter=adapter, case_id=case_id,
                         report_path=report_path)

    # THEN a report should have been added to that case
    updated_case_obj = adapter.cases()[0]
    assert updated_case_obj['delivery_report'] == report_path


def test_load_delivery_report_using_case_id_with_date_sucess(case_database):
    adapter = case_database

    # GIVEN a case exist, without a delivery report for the given analysis date
    assert adapter.cases().count() > 0
    case_obj = adapter.cases()[0]
    assert not case_obj.get('analyses')

    # WHEN trying to load a report for a case_id that does exist in the data base
    case_id = case_obj['_id']
    analysis_date = '2017-10-10 08:59:14'
    report_path = 'report_test_path'

    load_delivery_report(adapter=adapter, case_id=case_id,
                         analysis_date=analysis_date,
                         report_path=report_path)

    # THEN a report should have been added to that case
    updated_case_obj = adapter.cases()[0]
    assert updated_case_obj['analyses'][0]['delivery_report'] == report_path
    assert updated_case_obj['analyses'][0]['date'] == parse_date(analysis_date)


def test_load_delivery_report_using_optional_id_with_date_sucess(case_database):
    adapter = case_database

    # GIVEN a case exist, without a delivery report for the given analysis date
    assert adapter.cases().count() > 0
    case_obj = adapter.cases()[0]
    assert not case_obj.get('analyses')

    # WHEN trying to load a report for a case_id that does exist in the data base
    institute_id = case_obj['owner']
    display_name = case_obj['display_name']
    analysis_date = '2017-10-10 08:59:14'
    report_path = 'report_test_path'

    load_delivery_report(adapter=adapter, institute_id=institute_id,
                                             display_name=display_name,
                         analysis_date=analysis_date,
                         report_path=report_path)

    # THEN a report should have been added to that case
    updated_case_obj = adapter.cases()[0]
    assert updated_case_obj['analyses'][0]['delivery_report'] == report_path


def test_load_delivery_report_second_report_fail(case_database):
    adapter = case_database

    # GIVEN a case exist, with a delivery report for the given analysis date
    assert adapter.cases().count() > 0
    case_obj = adapter.cases()[0]
    assert not case_obj.get('analyses')

    case_id = case_obj['_id']
    analysis_date = '2017-10-10 08:59:14'
    report_path = 'report_test_path'
    report_path2 = 'report_test_path2'

    load_delivery_report(adapter=adapter, case_id=case_id,
                         analysis_date=analysis_date,
                         report_path=report_path)

    # WHEN trying to load a report for a case_id that does exist in the data base and update
    # parameter is unspecified
    try:
        load_delivery_report(adapter=adapter, case_id=case_id,
                             analysis_date=analysis_date,
                             report_path=report_path2)
        assert False
    except IntegrityError:
        # THEN an exception should have been raised
        assert True


def test_load_delivery_report_second_report_update_success(case_database):
    adapter = case_database

    # GIVEN a case exist, with a delivery report for the given analysis date
    assert adapter.cases().count() > 0
    case_obj = adapter.cases()[0]
    assert not case_obj.get('analyses')

    case_id = case_obj['_id']
    analysis_date = '2017-10-10 08:59:14'
    report_path = 'report_test_path'
    report_path2 = 'report_test_path2'

    load_delivery_report(adapter=adapter, case_id=case_id,
                         analysis_date=analysis_date,
                         report_path=report_path)

    # WHEN trying to load a report for a case_id that does exist in the data base and update =
    # True
    load_delivery_report(adapter=adapter, case_id=case_id,
                         analysis_date=analysis_date,
                         report_path=report_path2,
                         update=True)

    # THEN the report should have been overwritten for that particular analysis for the case
    updated_case_obj = adapter.cases()[0]
    assert updated_case_obj['analyses'][0]['delivery_report'] == report_path2
    assert updated_case_obj['analyses'][0]['date'] == parse_date(analysis_date)


def test_load_delivery_report_second_report_with_new_date_success(case_database):
    adapter = case_database

    # GIVEN a case exist, with a delivery report for the given analysis date
    assert adapter.cases().count() > 0
    case_obj = adapter.cases()[0]
    assert not case_obj.get('analyses')

    case_id = case_obj['_id']
    analysis_date = '2017-10-10 08:59:14'
    analysis_date2 = '2017-10-11 08:59:14'
    report_path = 'report_test_path'
    report_path2 = 'report_test_path2'

    load_delivery_report(adapter=adapter, case_id=case_id,
                         analysis_date=analysis_date,
                         report_path=report_path)

    # WHEN trying to load a report for a case_id that does exist in the data base with another date
    load_delivery_report(adapter=adapter, case_id=case_id,
                         analysis_date=analysis_date2,
                         report_path=report_path2)

    # THEN the case should have two delivery reports
    updated_case_obj = adapter.cases()[0]
    assert updated_case_obj['analyses'][0]['delivery_report'] == report_path
    assert updated_case_obj['analyses'][0]['date'] == parse_date(analysis_date)
    assert updated_case_obj['analyses'][1]['delivery_report'] == report_path2
    assert updated_case_obj['analyses'][1]['date'] == parse_date(analysis_date2)




