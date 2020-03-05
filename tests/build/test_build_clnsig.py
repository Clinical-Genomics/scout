from scout.build.variant.clnsig import build_clnsig


def test_build_clnsig_unknown_value():
    ## GIVEN a parsed clnsig object
    clnsig_info = {
        "value": "not applicable",
        "accession": "some_accession",
        "revstat": "arevstat",
    }
    ## WHEN building a clnsig obj prepared for database
    clsnig_obj = build_clnsig(clnsig_info)

    ## THEN assert that the representation for 'other' (255) is used
    assert clsnig_obj["value"] == 255


def test_build_clnsig_pathogenic_str():
    ## GIVEN a parsed clnsig object
    clnsig_info = {
        "value": "pathogenic",
        "accession": "some_accession",
        "revstat": "arevstat",
    }
    ## WHEN building a clnsig obj prepared for database
    clsnig_obj = build_clnsig(clnsig_info)

    ## THEN assert that the representation for 'other' (255) is used
    assert clsnig_obj["value"] == 5


def test_build_clnsig_pathogenic_int():
    ## GIVEN a parsed clnsig object
    clnsig_info = {"value": 5, "accession": "some_accession", "revstat": "arevstat"}
    ## WHEN building a clnsig obj prepared for database
    clsnig_obj = build_clnsig(clnsig_info)

    ## THEN assert a dictionary is built
    assert isinstance(clsnig_obj, dict)
    ## THEN assert the value for pathogenic (5) is used
    assert clsnig_obj["value"] == 5
