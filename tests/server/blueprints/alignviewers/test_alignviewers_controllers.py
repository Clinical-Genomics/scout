from scout.server.blueprints.alignviewers import controllers

BUILD37 = "37"
BUILD38 = "38"

CHROM = "22"


def test_clinvar_track_build37():
    """Test function that returns clinVar track as a dictionary when build is 37"""

    # WHEN clinVar track controller is invoked with genome build 37
    track = controllers.clinvar_track(BUILD37, CHROM)

    # THEN it should return a dictionary with the right keys/values
    assert track["name"] == "ClinVar"
    assert track["type"] == "annotation"
    assert track["sourceType"] == "file"
    assert "hg19" in track["url"]


def test_clinvar_track_build38():
    """Test function that returns clinVar track as a dictionary when build is 38"""

    # WHEN clinVar track controller is invoked with genome build 38
    track = controllers.clinvar_track(BUILD38, CHROM)

    # THEN it should return a dictionary with the right keys/values
    assert track["name"] == "ClinVar"
    assert track["type"] == "annotation"
    assert track["sourceType"] == "file"
    assert "hg38" in track["url"]


def test_clinvar_cnvs_track_build_37():
    """Test function that returns clinVar CNVs track as a dictionary when build is 37"""

    # WHEN clinVar CNVs track controller is invoked with genome build 37
    track = controllers.clinvar_cnvs_track(BUILD37, CHROM)

    # THEN it should return a dictionary with the right keys/values
    assert track["name"] == "ClinVar CNVs"
    assert track["type"] == "annotation"
    assert track["displayMode"] == "SQUISHED"
    assert track["sourceType"] == "file"
    assert "hg19" in track["url"]


def test_clinvar_cnvs_track_build_38():
    """Test function that returns clinVar CNVs track as a dictionary when build is 38"""

    # WHEN clinVar CNVs track controller is invoked with genome build 38
    track = controllers.clinvar_cnvs_track(BUILD38, CHROM)

    # THEN it should return a dictionary with the right keys/values
    assert track["name"] == "ClinVar CNVs"
    assert track["type"] == "annotation"
    assert track["displayMode"] == "SQUISHED"
    assert track["sourceType"] == "file"
    assert "hg38" in track["url"]


def test_reference_track_build_37():
    """Test function that returns the reference track as a dictionary when build is 37"""

    # WHEN genome reference track controller is invoked with genome build 37
    track = controllers.reference_track(BUILD37, CHROM)

    # THEN it should return a dictionary with the right keys/values
    assert "hg19" in track["fastaURL"]
    assert "hg19" in track["indexURL"]
    assert "hg19" in track["cytobandURL"]


def test_reference_track_build_38():
    """Test function that returns the reference track as a dictionary when build is 38"""

    # WHEN genome reference track controller is invoked with genome build 38
    track = controllers.reference_track(BUILD38, CHROM)

    # THEN it should return a dictionary with the right keys/values
    assert "hg38" in track["fastaURL"]
    assert "hg38" in track["indexURL"]
    assert "hg38" in track["cytobandURL"]


def test_genes_track_build_37():
    """Test function that returns the genes track as a dictionary when build is 37"""

    # WHEN genes track controller is invoked with genome build 37
    track = controllers.genes_track(BUILD37, CHROM)

    # THEN it should return a dictionary with the right keys/values
    assert track["name"] == "Genes"
    assert track["type"] == "annotation"
    assert track["sourceType"] == "file"
    assert "hg19" in track["url"]
    assert "hg19" in track["indexURL"]


def test_genes_track_build_38():
    """Test function that returns the genes track as a dictionary when build is 38"""

    # WHEN genes track controller is invoked with genome build 38
    track = controllers.genes_track(BUILD38, CHROM)

    # THEN it should return a dictionary with the right keys/values
    assert track["name"] == "Genes"
    assert track["type"] == "annotation"
    assert track["sourceType"] == "file"
    assert "hg38" in track["url"]
    assert "hg38" in track["indexURL"]
