import pytest

from scout.adapter.mongo.variant_evaluation_term import EvaluationTerm


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


def test_evaluation_term_wrong_trac k():
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
