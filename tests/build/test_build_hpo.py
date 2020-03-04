from scout.build.hpo import build_hpo_term


def test_build_hpo_term(adapter):
    ## GIVEN a hpo term
    hpo_info = {
        "hpo_id": "HP:0000878",
        "description": "11 pairs of ribs",
        "genes": [1, 2],
    }
    ## WHEN building the hpo term
    hpo_obj = build_hpo_term(hpo_info)
    ## THEN assert that the term has the correct information
    assert hpo_obj["_id"] == hpo_obj["hpo_id"] == hpo_info["hpo_id"]
    assert hpo_obj["description"] == hpo_info["description"]
    assert len(hpo_obj["genes"]) == 2
