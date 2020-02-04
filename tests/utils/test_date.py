import datetime
import pytest
from scout.utils.date import match_date, get_date


def test_match_date_dash():
    date_str = "2015-05-10"
    assert match_date(date_str)


def test_match_date_dot():
    date_str = "2015.05.10"
    assert match_date(date_str)


def test_match_invalid_date():
    date_str = "20150510"
    assert not match_date(date_str)


def test_match_invalid_date():
    date_str = "hello"
    assert not match_date(date_str)


def test_valid_date():
    date_str = "2015-05-10"
    date_obj = get_date(date_str)
    assert isinstance(date_obj, datetime.datetime)


def test_valid_date_no_date():
    date_str = None
    date_obj = get_date(date_str)
    assert isinstance(date_obj, datetime.datetime)


def test_invalid_date():
    date_str = "20150510"
    with pytest.raises(ValueError):
        date_obj = get_date(date_str)
