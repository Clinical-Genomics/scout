from scout.utils.dict_utils import remove_empty_list, remove_nonetype


def test_remove_nonetype_no_change():
    # WHEN a dict *not* containing a None value
    d = {"a": "1", "b": 2, "c": 3}

    # THEN calling removeNoneValues(dict) will not change dict
    assert d == remove_nonetype(d)


def test_remove_nonetype():
    # WHEN a dict containing a value which is None
    d = {"a": "1", "b": 2, "c": None}

    # THEN calling removeNoneValues(dict) will remove key-value pair
    # where value=None
    assert {"a": "1", "b": 2} == remove_nonetype(d)


def test_remove_empty_list_no_change():
    # WHEN a dict *not* containing an empty list, []
    d = {"a": "1", "b": 2, "c": [3]}

    # THEN calling removeNoneValues(dict) will not change dict
    assert d == remove_empty_list(d)


def test_remove_empty_list():
    # WHEN a dict containing a value which is []
    d = {"a": "1", "b": 2, "c": []}

    # THEN calling removeNoneValues(dict) will remove key-value pair
    # where value=None
    assert {"a": "1", "b": 2} == remove_empty_list(d)
