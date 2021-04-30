from scout.load import load_evaluation_term


def test_load_default_evaluation_term(adapter):
    # Assert empty database
    assert sum(1 for i in adapter.evaluation_terms()) == 0

    test_entry = {
        "internal_id": "test-entry",
        "name": "test entry",
        "description": "an entry to test the import",
        "term_category": "dismissal_term",
    }
    load_evaluation_term(adapter, **test_entry)
    # test if loaded
    assert sum(1 for i in adapter.evaluation_terms()) == 1
    # test assignment of data
    entry = adapter.get_evaluation_term("dismissal_term", term_id="test-entry")
    assert "last_modified" in entry and "rank" in entry
    assert all(test_key in entry.keys() for test_key in test_entry)
    # assert assignment of rank
    assert entry["rank"] == 1


def test_load_evaluation_terms_kwargs(adapter):
    # Assert empty database
    assert sum(1 for i in adapter.evaluation_terms()) == 0

    test_entry = {
        "internal_id": "test-entry",
        "name": "test entry",
        "description": "an entry to test the import",
        "term_category": "dismissal_term",
        "custom_term_one": "foo",
        "custom_term_two": "bar",
    }
    load_evaluation_term(adapter, **test_entry)
    # test if loaded
    assert sum(1 for i in adapter.evaluation_terms()) == 1
    # test assignment of data
    entry = adapter.get_evaluation_term("dismissal_term", term_id="test-entry")
    assert "last_modified" in entry
    assert all(test_key in entry.keys() for test_key in test_entry)


def test_load_evaluation_terms_rank_increment(adapter):
    # Assert empty database
    assert sum(1 for i in adapter.evaluation_terms()) == 0

    test_entry_one = {
        "internal_id": "test-entry-one",
        "name": "test entry",
        "description": "an entry to test the import",
        "term_category": "dismissal_term",
        "rank": 0,
    }
    test_entry_two = {
        "internal_id": "test-entry-two",
        "name": "test entry",
        "description": "an entry to test the import",
        "term_category": "dismissal_term",
    }
    load_evaluation_term(adapter, **test_entry_one)
    load_evaluation_term(adapter, **test_entry_two)
    # test assignment of data
    entry = adapter.get_evaluation_term("dismissal_term", term_id="test-entry-two")
    assert entry["rank"] == 1
