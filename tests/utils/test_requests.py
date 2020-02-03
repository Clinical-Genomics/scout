# -*- coding: utf-8 -*-

import os
import pytest
from scout.utils.requests import fetch_refseq_version, get_request

TRAVIS = os.getenv("TRAVIS")


def test_get_request_bad_url():
    """Test functions that accepts an url and returns decoded data from it"""

    # test function with a url that is not valid
    url = "fakeyurl"
    with pytest.raises(ValueError) as err:
        # function should raise error
        assert get_request(url)
