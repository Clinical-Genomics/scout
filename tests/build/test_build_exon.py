import pytest
from scout.build.genes.exon import build_exon


def test_build_exon(parsed_exon):
    ## GIVEN a dictionary with exon information

    ## WHEN building a exon object
    exon_obj = build_exon(parsed_exon)

    ## THEN assert that a dictionary is returned
    assert isinstance(exon_obj, dict)


@pytest.mark.parametrize("key", ["hgnc_id", "start", "end", "rank", "strand", "hgnc_id"])
def test_build_exon_inappropriate_type(parsed_exon, key):
    ## GIVEN a dictionary with exon information

    # WHEN setting key to None
    parsed_exon[key] = None
    # THEN calling build_exon() will raise TypeError
    with pytest.raises(TypeError):
        build_exon(parsed_exon)


@pytest.mark.parametrize(
    "key",
    [
        "hgnc_id",
        "start",
        "end",
        "rank",
        "strand",
        "hgnc_id",
        "transcript",
        "exon_id",
        "chrom",
        "ens_exon_id",
    ],
)
def test_build_exon_missing_key(parsed_exon, key):
    ## GIVEN a dictionary with exon information

    # WHEN key is deleted from dict
    parsed_exon.pop(key)
    # THEN calling build_exon() will raise KeyError
    with pytest.raises(KeyError):
        build_exon(parsed_exon)
