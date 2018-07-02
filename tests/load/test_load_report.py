import pytest
from scout.load.report import load_delivery_report
from scout.exceptions import DataNotFoundError, IntegrityError


def test_load_delivery_report_bad_case_id(panel_database):
    adapter = panel_database

    # GIVEN no cases in database
    assert adapter.cases().count() == 0

    # WHEN trying to load a report for a case_id that does not exist in the data base
    case_id = 'id_of_non_existing_case'
    report_path = 'a_dummy_path'

    # THEN an exception should be raised
    with pytest.raises(DataNotFoundError):
        load_delivery_report(adapter=adapter, case_id=case_id,
                             report_path=report_path)


def test_load_delivery_report_using_case_id_without_update_fail(case_database):
    adapter = case_database

    # GIVEN a case exist, with a delivery report
    assert adapter.cases().count() > 0
    case_obj = adapter.cases()[0]
    assert case_obj.get('delivery_report')

    # WHEN trying to load a report for a case_id that does exist in the data base without update
    # flag
    case_id = case_obj['_id']
    report_path2 = 'report_test_path2'

    # THEN a report should not have been added to that case
    with pytest.raises(IntegrityError):
        load_delivery_report(adapter=adapter, case_id=case_id,
                             report_path=report_path2)

    updated_case_obj = adapter.cases()[0]
    assert updated_case_obj.get('delivery_report') != report_path2


def test_load_delivery_report_using_case_id_with_update_success(case_database):
    adapter = case_database

    # GIVEN a case exist, without a delivery report for the given analysis date
    assert adapter.cases().count() > 0
    case_obj = adapter.cases()[0]
    assert case_obj.get('delivery_report')

    # WHEN trying to load a report for a case_id that does exist in the data base
    case_id = case_obj['_id']
    report_path = 'report_test_path'
    update = True

    load_delivery_report(adapter=adapter, case_id=case_id,
                         report_path=report_path, update=update)

    # THEN a report should have been added to that case
    updated_case_obj = adapter.cases()[0]
    assert updated_case_obj['delivery_report'] == report_path
