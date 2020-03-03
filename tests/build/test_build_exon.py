import pytest
from scout.build.genes.exon import build_exon


def test_build_exon(parsed_exon):
    ## GIVEN a dictionary with exon information

    ## WHEN building a exon object
    exon_obj = build_exon(parsed_exon)

    ## THEN assert that a dictionary is returned

    assert isinstance(exon_obj, dict)


def test_build_exon_no_hgnc(parsed_exon):
    ## GIVEN a dictionary with exon information
    parsed_exon.pop("hgnc_id")

    ## WHEN building a exon object
    with pytest.raises(KeyError):
        ## THEN assert that a exception is raised since there is no hgnc_id
        exon_obj = build_exon(parsed_exon)
