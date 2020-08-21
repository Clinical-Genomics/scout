from scout.build.hpo import build_hpo_term
import pytest

def test_build_hpo_term(adapter, test_hpo_info):
    ## GIVEN a hpo term
    ## WHEN building the hpo term
    hpo_obj = build_hpo_term(test_hpo_info)
    ## THEN assert that the term has the correct information
    assert hpo_obj["_id"] == hpo_obj["hpo_id"] == test_hpo_info["hpo_id"]
    assert hpo_obj["description"] == test_hpo_info["description"]
    assert len(hpo_obj["genes"]) == 2


@pytest.mark.parametrize("key", ['hpo_id', 'description'])    
def test_build_hpo_term_missing_key(adapter, test_hpo_info, key):
    ## GIVEN a dictionary with hpo information

    ## WHEN deleteing key
    test_hpo_info.pop(key)
    ## THEN calling build_hpo_term() will raise KeyError
    with pytest.raises(KeyError):
        build_hpo_term(test_hpo_info)
