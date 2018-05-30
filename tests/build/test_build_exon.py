import pytest
from scout.build.genes.exon import build_exon

def test_build_exon():
    ## GIVEN a dictionary with exon information
    exon_info = {
        "exon_id": '1',
        "chrom": '1', 
        "start": 10, 
        "end": 100,     
        "transcript": '12',
        "hgnc_id": 11,
        "rank": 2, # Order of exon in transcript
    }
    
    ## WHEN building a exon object
    exon_obj = build_exon(exon_info)
    
    ## THEN assert that a dictionary is returned
    
    assert isinstance(exon_obj, dict)

def test_build_exon_no_hgnc():
    ## GIVEN a dictionary with exon information
    exon_info = {
        "exon_id": '1',
        "chrom": '1', 
        "start": 10, 
        "end": 100,     
        "transcript": '12',
        "rank": 2, # Order of exon in transcript
    }
    
    ## WHEN building a exon object
    with pytest.raises(KeyError):
        ## THEN assert that a exception is raised since there is no hgnc_id
        exon_obj = build_exon(exon_info)
    