import pytest

from scout.exceptions import DataNotFoundError, IntegrityError
from scout.load.report import load_cnv_report, load_coverage_qc_report, load_delivery_report


def test_load_delivery_report_bad_case_id(adapter):

    ## GIVEN no cases in database
    assert adapter.case_collection.find_one() is None

    ## WHEN trying to load a report for a case_id that does not exist in the data base
    case_id = "id_of_non_existing_case"
    report_path = "a_fakey_path"

    ## THEN an exception should be raised
    with pytest.raises(DataNotFoundError):
        load_delivery_report(adapter=adapter, case_id=case_id, report_path=report_path)


def test_load_delivery_report_using_case_id_without_update_fail(adapter, case_obj):

    adapter.case_collection.insert_one(case_obj)
    ## GIVEN a case exist, with a delivery report
    case_obj = adapter.case_collection.find_one()
    assert case_obj.get("delivery_report")

    ## WHEN trying to load a report for a case_id that does exist in the data base without update
    # flag
    case_id = case_obj["_id"]
    report_path2 = "report_test_path2"

    ## THEN a report should not have been added to that case
    with pytest.raises(IntegrityError):
        load_delivery_report(
            adapter=adapter,
            case_id=case_id,
            report_path=report_path2,
        )

    updated_case_obj = adapter.case_collection.find_one()
    assert updated_case_obj.get("delivery_report") != report_path2


def test_load_delivery_report_using_case_id_with_update_success(adapter, case_obj):

    adapter.case_collection.insert_one(case_obj)
    ## GIVEN a case exist, with a delivery report
    case_obj = adapter.case_collection.find_one()
    assert case_obj.get("delivery_report")

    ## WHEN trying to load a report for a case_id that does exist in the data base
    case_id = case_obj["_id"]
    report_path = "report_test_path"
    update = True

    load_delivery_report(
        adapter=adapter,
        case_id=case_id,
        report_path=report_path,
        update=update,
    )

    # THEN a report should have been added to that case
    updated_case_obj = adapter.case_collection.find_one()
    assert updated_case_obj["delivery_report"] == report_path


def test_load_cnv_report_using_case_id_with_update_success(adapter, cancer_case_obj):

    adapter.case_collection.insert_one(cancer_case_obj)
    ## GIVEN a case exist, with a delivery report
    cancer_case_obj = adapter.case_collection.find_one()
    assert cancer_case_obj.get("cnv_report")

    ## WHEN trying to load a report for a case_id that does exist in the data base
    case_id = cancer_case_obj["_id"]
    report_path = "report_test_path"
    update = True

    load_cnv_report(
        adapter=adapter,
        case_id=case_id,
        report_path=report_path,
        update=update,
    )

    # THEN a report should have been added to that case
    updated_case_obj = adapter.case_collection.find_one()
    assert updated_case_obj["cnv_report"] == report_path


def test_load_coverage_qc_report_using_case_id_with_update_success(adapter, cancer_case_obj):

    adapter.case_collection.insert_one(cancer_case_obj)
    ## GIVEN a case exist, with a delivery report
    cancer_case_obj = adapter.case_collection.find_one()
    assert cancer_case_obj.get("coverage_qc_report")

    ## WHEN trying to load a report for a case_id that does exist in the data base
    case_id = cancer_case_obj["_id"]
    report_path = "report_test_path"
    update = True

    load_coverage_qc_report(
        adapter=adapter,
        case_id=case_id,
        report_path=report_path,
        update=update,
    )

    # THEN a report should have been added to that case
    updated_case_obj = adapter.case_collection.find_one()
    assert updated_case_obj["coverage_qc_report"] == report_path
