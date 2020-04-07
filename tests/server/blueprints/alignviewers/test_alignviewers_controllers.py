from scout.server.blueprints.alignviewers import controllers

BUILD37 = "37"
BUILD38 = "38"

CHROM = "22"

MOCK_CLOUD_CREDENTIALS = {
    "region" : "eu-north-1",
    "key": "mock_key",
    "secret_key" : "mock_secret_access_key",
    "bucket": "mock_bucket_name",
    "folder": "mock_folder"
}

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


def test_cosmic_coding_track_build37(monkeypatch):
    """Test function that returns cosmic coding track as a dictionary when build is 37"""

    def mock_credentials():
        return MOCK_CLOUD_CREDENTIALS

    monkeypatch.setattr(controllers, "get_cloud_credentials", mock_credentials)

    # WHEN cosmic coding track controller is invoked with genome build 37
    track = controllers.cosmic_track(BUILD37, CHROM, True)

    # THEN it should return a dictionary with the right keys/values
    assert track["name"] == "Cosmic coding"
    assert track["type"] == "variant"
    assert track["format"] == "vcf"
    assert "hg19" in track["url"]
    assert "CosmicCoding" in track["url"]
    assert "hg19" in track["indexURL"]


def cosmic_coding_track_build38(monkeypatch):
    """Test function that returns cosmic coding track as a dictionary when build is 38"""

    def mock_credentials():
        return MOCK_CLOUD_CREDENTIALS

    monkeypatch.setattr(controllers, "get_cloud_credentials", mock_credentials)

    # WHEN cosmic coding track controller is invoked with genome build 38
    track = controllers.cosmic_track(BUILD38, CHROM, True)

    # THEN it should return a dictionary with the right keys/values
    assert track["name"] == "Cosmic coding"
    assert "hg38" in track["url"]
    assert "CosmicCoding" in track["url"]
    assert "hg38" in track["indexURL"]


def test_cosmic_non_coding_track_build37(monkeypatch):
    """Test function that returns cosmic non-coding track as a dictionary when build is 37"""

    def mock_credentials():
        return MOCK_CLOUD_CREDENTIALS

    monkeypatch.setattr(controllers, "get_cloud_credentials", mock_credentials)

    # WHEN cosmic non-coding track controller is invoked with genome build 37
    track = controllers.cosmic_track(BUILD37, CHROM, False)

    # THEN it should return a dictionary with the right keys/values
    assert track["name"] == "Cosmic non coding"
    assert track["type"] == "variant"
    assert track["format"] == "vcf"
    assert "hg19" in track["url"]
    assert "CosmicNonCoding" in track["url"]
    assert "hg19" in track["indexURL"]


def test_cosmic_non_coding_track_build38(monkeypatch):
    """Test function that returns cosmic non-coding track as a dictionary when build is 38"""

    def mock_credentials():
        return MOCK_CLOUD_CREDENTIALS

    monkeypatch.setattr(controllers, "get_cloud_credentials", mock_credentials)

    # WHEN cosmic non-coding track controller is invoked with genome build 38
    track = controllers.cosmic_track(BUILD38, CHROM, False)

    # THEN it should return a dictionary with the right keys/values
    assert track["name"] == "Cosmic non coding"
    assert track["type"] == "variant"
    assert track["format"] == "vcf"
    assert "hg38" in track["url"]
    assert "CosmicNonCoding" in track["url"]
    assert "hg38" in track["indexURL"]


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
