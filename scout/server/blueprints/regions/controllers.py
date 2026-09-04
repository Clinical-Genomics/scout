import logging

LOG = logging.getLogger(__name__)


def regions(store):
    """Fetch regions overview statistics"""
    data = {
        "counts": store.region_type_count(),
    }
    return data


def isca_region(store, isca_id, build):
    """Fetch a single region"""
    region_query_result = store.get_isca_region(isca_id, build)
    return region_query_result
