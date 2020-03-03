from scout.parse.hpo_terms import build_hpo_tree, get_incomplete_penetrance_genes


def test_build_hpo_tree(hpo_terms_handle):
    """Test function that creates the HPO terms tree from the HPO term lines"""

    # GIVEN an HPO tree dictionary built out of the hp.obo file
    hpo_tree = build_hpo_tree(hpo_terms_handle)
    assert isinstance(hpo_tree, dict)

    # THEN its keys should be HPO ids:
    hpo_ids = list(hpo_tree.keys())
    assert hpo_ids[0].startswith("HP:")

    # and each term should have a standard formar:
    one_term = hpo_tree[hpo_ids[0]]
    assert "aliases" in one_term
    assert "all_ancestors" in one_term
    assert "ancestors" in one_term
    assert "description" in one_term
