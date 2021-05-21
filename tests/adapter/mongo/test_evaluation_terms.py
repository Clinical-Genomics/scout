import pytest


def test_insert_evaluation_term(adapter):
    ##GIVEN a empty adapter
    assert sum(1 for i in adapter.evaluation_terms()) == 0

    ##WHEN inserting a transcript
    evaluation_term_obj = {
        "internal_id": "test-a",
        "name": "test a",
        "description": "a test term",
        "term_category": "dismissal_term",
        "rank": 0,
        "institute": "all",
        "analysis_type": "all",
        "label": "test a",
        "evidence": [],
    }
    obj_id = adapter.add_evaluation_term(evaluation_term_obj)

    ##THEN assert that the transcript is there
    assert sum(1 for i in adapter.evaluation_terms()) == 1


@pytest.mark.parametrize("param_name", ["institute", "analysis_type"])
def test_get_institute_exclusive_evaluation_term(adapter, param_name):
    ##GIVEN a empty adapter
    assert sum(1 for i in adapter.evaluation_terms()) == 0

    base_term = {
        "internal_id": "test-a",
        "name": "test a",
        "description": "a test term",
        "term_category": "dismissal_term",
        "rank": 0,
        "institute": "all",
        "analysis_type": "all",
        "label": "test a",
        "evidence": [],
    }
    ## override an exclusive param
    generic_term = base_term.copy()
    obj_id = adapter.add_evaluation_term(generic_term)

    ## institute
    exclusive_term_obj = base_term.copy()
    exclusive_term_obj[param_name] = "foobar"
    obj_id = adapter.add_evaluation_term(exclusive_term_obj)

    ##THEN assert that the generic term is there
    assert sum(1 for i in adapter.evaluation_terms()) == 1

    ##THEN assert that the exclusive term is there
    param_name = "institute_id" if param_name == "institute" else param_name
    query = {param_name: "foobar"}
    assert sum(1 for i in adapter.evaluation_terms(**query)) == 2
