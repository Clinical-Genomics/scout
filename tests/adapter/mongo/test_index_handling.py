"""
test_index_handling.py

Tests how the index part of the adapter behaves
"""

from scout.constants import COLLECTIONS

# def test_collections(adapter):
#     ## GIVEN a adapter just initialized
#     i = 0
#     ## WHEN looping over the collection names
#     for i,collection_name in enumerate(adapter.collections()):
#         ## THEN assert all collections are known
#         assert collection_name in COLLECTIONS
#     ## THEN assert there where any collections
#     assert i > 0


def test_indexes_empty(adapter):
    ## GIVEN a adapter just initialized
    i = 0
    ## WHEN looping over the indexes
    for i, index_name in enumerate(adapter.indexes()):
        assert index_name
    ## THEN assert there where no indexes
    assert i == 0


def test_load_indexes(real_adapter):
    adapter = real_adapter
    ## GIVEN a adapter just initialized
    i = 0
    ## WHEN creating the indexes
    adapter.load_indexes()

    for i, index_name in enumerate(adapter.indexes()):
        assert index_name
    ## THEN assert there where indexes created
    assert i > 0


def test_load_indexes_twice(real_adapter):
    adapter = real_adapter
    ## GIVEN a adapter just initialized
    i = 0
    ## WHEN creating the indexes twice
    adapter.load_indexes()
    adapter.load_indexes()

    for i, index_name in enumerate(adapter.indexes()):
        assert index_name
    ## THEN assert there where indexes created
    assert i > 0
