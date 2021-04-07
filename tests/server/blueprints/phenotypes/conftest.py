"""Fixtures for phenotypes"""

import pytest


@pytest.fixture
def hpo_term():
    hpo_term = dict(
        _id="HP1",  # Same as hpo_id
        hpo_id="HP1",  # Required
        description="First term",
        genes=[1],  # List with integers that are hgnc_ids
    )
    return hpo_term
