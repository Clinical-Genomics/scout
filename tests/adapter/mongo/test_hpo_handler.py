import pytest

from scout.exceptions import IntegrityError

#########################################################
################### Hpo tests #######################
#########################################################


def test_add_hpo_term(adapter):
    ## GIVEN a empty adapter
    assert len([term for term in adapter.hpo_terms()]) == 0

    hpo_term = dict(
        _id="HP1",  # Same as hpo_id
        hpo_id="HP1",  # Required
        description="First term",
        genes=[1],  # List with integers that are hgnc_ids
    )
    ## WHEN loading a hpo term
    adapter.load_hpo_term(hpo_term)

    ## THEN assert that the term have been loaded
    assert len([term for term in adapter.hpo_terms()]) == 1


def test_add_hpo_term_twice(adapter):
    ## GIVEN a empty adapter
    assert len([term for term in adapter.hpo_terms()]) == 0

    hpo_term = dict(
        _id="HP1",  # Same as hpo_id
        hpo_id="HP1",  # Required
        description="First term",
        genes=[1],  # List with integers that are hgnc_ids
    )
    ## WHEN loading a hpo term
    adapter.load_hpo_term(hpo_term)
    with pytest.raises(IntegrityError):
        adapter.load_hpo_term(hpo_term)


def test_fetch_term(adapter):
    ## GIVEN a adapter with one hpo term
    assert len([term for term in adapter.hpo_terms()]) == 0

    hpo_term = dict(
        _id="HP1",  # Same as hpo_id
        hpo_id="HP1",  # Required
        description="First term",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_hpo_term(hpo_term)

    ## WHEN fetching the hpo terms
    res = adapter.hpo_term(hpo_term["_id"])

    ## THEN assert the term was fetched
    assert res["_id"] == hpo_term["_id"]


def test_fetch_non_existing_hpo_term(adapter):
    ## GIVEN a adapter with one hpo term
    assert len([term for term in adapter.hpo_terms()]) == 0

    hpo_term = dict(
        _id="HP1",  # Same as hpo_id
        hpo_id="HP1",  # Required
        description="First term",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_hpo_term(hpo_term)

    ## WHEN fetching the hpo terms
    res = adapter.hpo_term("non existing")

    ## THEN assert resut is None
    assert res is None


def test_fetch_all_hpo_terms(adapter):
    ## GIVEN a adapter with one hpo term
    assert len([term for term in adapter.hpo_terms()]) == 0

    hpo_term = dict(
        _id="HP1",  # Same as hpo_id
        hpo_id="HP1",  # Required
        description="First term",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_hpo_term(hpo_term)

    ## WHEN fetching the hpo terms
    res = [term for term in adapter.hpo_terms()]

    ## THEN assert the term was fetched
    assert len(res) == 1


def test_fetch_all_hpo_terms_query(real_adapter):
    adapter = real_adapter
    ## GIVEN a adapter with one hpo term
    assert len([term for term in adapter.hpo_terms()]) == 0

    hpo_term = dict(
        _id="HP1",  # Same as hpo_id
        hpo_id="HP1",  # Required
        description="First term",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_hpo_term(hpo_term)

    hpo_term2 = dict(
        _id="HP2",  # Same as hpo_id
        hpo_id="HP2",  # Required
        description="Second term",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_hpo_term(hpo_term2)

    ## WHEN fetching the hpo terms with partial query
    res = [term for term in adapter.hpo_terms(query="1")]

    ## THEN assert only one term was matched
    assert len(res) == 1


def test_fetch_all_hpo_terms_query_description(real_adapter):
    adapter = real_adapter
    ## GIVEN a adapter with one hpo term
    assert len([term for term in adapter.hpo_terms()]) == 0

    hpo_term = dict(
        _id="HP1",  # Same as hpo_id
        hpo_id="HP1",  # Required
        description="First term",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_hpo_term(hpo_term)

    hpo_term2 = dict(
        _id="HP2",  # Same as hpo_id
        hpo_id="HP2",  # Required
        description="Second term",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_hpo_term(hpo_term2)

    ## WHEN fetching the hpo terms with partial query
    res = [term for term in adapter.hpo_terms(query="second")]

    ## THEN assert only one term was matched
    assert len(res) == 1
    for term in res:
        assert term["_id"] == "HP2"


def test_fetch_all_hpo_terms_query_description_term(real_adapter):
    adapter = real_adapter
    ## GIVEN a adapter with one hpo term
    assert len([term for term in adapter.hpo_terms()]) == 0

    hpo_term = dict(
        _id="HP1",  # Same as hpo_id
        hpo_id="HP1",  # Required
        description="First term",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_hpo_term(hpo_term)

    hpo_term2 = dict(
        _id="HP2",  # Same as hpo_id
        hpo_id="HP2",  # Required
        description="Second term",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_hpo_term(hpo_term2)

    ## WHEN fetching the hpo terms with partial query
    res = adapter.hpo_terms(query="term")

    ## THEN assert only one term was matched
    assert len([term for term in res]) == 2
