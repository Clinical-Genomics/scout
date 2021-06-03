import pytest

from scout.adapter.mongo.variant_evaluation_term import EvaluationTerm
from scout.server.extensions import store


def test_evaluation_term_no_key():
    """Test creating an evaluation term with no key: should raise ValueError"""
    term_dict = dict(
        term_label="label",
        term_description="description",
        term_category="dismissal_term",
        term_tracks=["rare"],
    )
    with pytest.raises(ValueError):
        EvaluationTerm(term_dict)


def test_evaluation_term_no_label():
    """Test creating an evaluation term with no label: should raise ValueError"""
    term_dict = dict(
        term_key=1,
        term_description="description",
        term_category="dismissal_term",
        term_tracks=["rare"],
    )
    with pytest.raises(ValueError):
        EvaluationTerm(term_dict)


def test_evaluation_term_no_description():
    """Test creating an evaluation term with no description: should raise ValueError"""
    term_dict = dict(
        term_key=1,
        term_label="label",
        term_category="dismissal_term",
        term_tracks=["rare"],
    )
    with pytest.raises(ValueError):
        EvaluationTerm(term_dict)


def test_evaluation_term_wrong_category():
    """Test creating an evaluation term with wrong category: should raise ValueError"""
    term_dict = dict(
        term_key=1,
        term_label="label",
        term_description="description",
        term_category="FOO",
        term_tracks=["rare"],
    )
    with pytest.raises(ValueError):
        EvaluationTerm(term_dict)


def test_evaluation_term_no_tracks():
    """Test creating an evaluation term with no tracks: should raise ValueError"""
    term_dict = dict(
        term_key=1,
        term_label="label",
        term_description="description",
        term_category="dismissal_term",
        term_tracks=[],
    )
    with pytest.raises(ValueError):
        EvaluationTerm(term_dict)


def test_evaluation_term_wrong_track():
    """Test creating an evaluation term with non-standard tracks: should raise ValueError"""
    term_dict = dict(
        term_key=1,
        term_label="label",
        term_description="description",
        term_category="dismissal_term",
        term_tracks=["BAR"],
    )
    with pytest.raises(ValueError):
        EvaluationTerm(term_dict)


def test_evaluation_term_existing_key(adapter):
    """Test creating an evaluation term for a category with a duplicated key: should raise ValueError"""

    # GIVEN a dismissal term present in database with a certain key
    term_category = "dismissal_term"
    term_tracks = ["rare"]
    term_key = 1
    term_value = dict(label="test", description="This is a test term")

    inserted_term = adapter.load_evaluation_term(term_category, term_tracks, term_key, term_value)
    assert inserted_term

    # WHEN another term having the same categoery and key is interted
    # It should return error
    with pytest.raises(ValueError):
        adapter.load_evaluation_term(term_category, term_tracks, term_key, term_value)
