# -*- coding: utf-8 -*-

from scout.server.blueprints.phenotypes import controllers


def test_hpo_terms(real_adapter, hpo_term):

    adapter = real_adapter

    ## GIVEN a adapter with one hpo term
    adapter.load_hpo_term(hpo_term)

    # The phenotypes controller should be able to return that term
    results = controllers.hpo_terms(adapter)
    assert results["phenotypes"] == [hpo_term]
