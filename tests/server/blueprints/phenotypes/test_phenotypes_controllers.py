# -*- coding: utf-8 -*-

from scout.server.blueprints.phenotypes import controllers


def test_hpo_terms(real_adapter):

    adapter = real_adapter

    ## GIVEN a adapter with one hpo term
    hpo_term = dict(
        _id="HP1",  # Same as hpo_id
        hpo_id="HP1",  # Required
        description="First term",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_hpo_term(hpo_term)

    # The phenotypes controller should be able to return that term
    results = controllers.hpo_terms(adapter)
    assert results["phenotypes"] == [hpo_term]
