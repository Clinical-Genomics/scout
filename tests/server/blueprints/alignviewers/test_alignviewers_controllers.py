from scout.server.blueprints.alignviewers import controllers

BUILD37 = "37"
BUILD38 = "38"

CHROM = "22"

MOCK_CLOUD_CREDENTIALS = {
    "region": "eu-north-1",
    "key": "mock_key",
    "secret_key": "mock_secret_access_key",
    "bucket": "mock_bucket_name",
    "folder": "mock_folder",
}

TEST_IGV_TRACKS = {
    "cosmic_coding_v90": {
        "37": {
            "description": "Cosmic coding mutations v90 hg19",
            "file_name": "CosmicCodingMuts_v90_hg19.vcf.gz",
            "type": "variant",
            "format": "vcf",
            "displayMode": "squished",
            "genome_build": "37",
            "access_type": "credentials",
            "index_format": "tbi",
        },
        "38": {
            "description": "Cosmic coding mutations v90 hg38",
            "file_name": "CosmicCodingMuts_v90_hg38.vcf.gz",
            "type": "variant",
            "format": "vcf",
            "displayMode": "squished",
            "genome_build": "37",
            "access_type": "credentials",
            "index_format": "tbi",
        },
    }
}


def app_cloud_credentials(app):
    """MOCK cloud credentials in the app config"""

    # Add params to app config settings
    app.config["REGION_NAME"] = MOCK_CLOUD_CREDENTIALS["region"]
    app.config["ACCESS_KEY"] = MOCK_CLOUD_CREDENTIALS["key"]
    app.config["SECRET_ACCESS_KEY"] = MOCK_CLOUD_CREDENTIALS["secret_key"]
    app.config["BUCKET_NAME"] = MOCK_CLOUD_CREDENTIALS["bucket"]
    app.config["BUCKET_FOLDER"] = MOCK_CLOUD_CREDENTIALS["folder"]


def test_get_cloud_credentials(app):
    """Test function that retrieves cloud credentials from app config settings"""

    # GIVEN an app with config settings containing cloud settings
    app_cloud_credentials(app)

    # WHEN get_cloud_credentials function is invoked
    cloud_credentials = controllers.get_cloud_credentials()

    # THEN it should return the expected parameters
    for key in cloud_credentials.keys():
        assert cloud_credentials[key] == MOCK_CLOUD_CREDENTIALS[key]


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


def test_cloud_tracks_chr_non_MT(app):
    """Test alignviewers controllers function that prepares the custom cloud tracks for a non-MT variant"""

    # GIVEN an app with config settings containing cloud settings
    app_cloud_credentials(app)

    # AND custom cloud tracks
    app.config["CUSTOM_IGV_TRACKS"] = TEST_IGV_TRACKS

    display_obj = {}

    # WHEN the function that prespares cloud tracks is invoked for a MT variant (build37)
    controllers.cloud_tracks("37", "22", ["cosmic_coding_v90"], display_obj)

    # THEN the display object should have a track with expected key/values in build 38
    assert (
        display_obj["custom_tracks"][0]["name"]
        == TEST_IGV_TRACKS["cosmic_coding_v90"]["37"]["description"]
    )
    assert (
        display_obj["custom_tracks"][0]["type"]
        == TEST_IGV_TRACKS["cosmic_coding_v90"]["37"]["type"]
    )
    assert (
        display_obj["custom_tracks"][0]["format"]
        == TEST_IGV_TRACKS["cosmic_coding_v90"]["37"]["format"]
    )
    assert (
        display_obj["custom_tracks"][0]["displayMode"]
        == TEST_IGV_TRACKS["cosmic_coding_v90"]["37"]["displayMode"]
    )
    assert (
        display_obj["custom_tracks"][0]["url"]
        == TEST_IGV_TRACKS["cosmic_coding_v90"]["37"]["file_name"]
    )

    track_url = TEST_IGV_TRACKS["cosmic_coding_v90"]["37"]["file_name"]
    track_index_format = TEST_IGV_TRACKS["cosmic_coding_v90"]["37"]["index_format"]
    assert display_obj["custom_tracks"][0]["indexURL"] == ".".join([track_url, track_index_format])


def test_cloud_tracks_chr_MT(app):
    """Test alignviewers controllers function that prepares the custom cloud tracks for a MT variant"""

    # GIVEN an app with config settings containing cloud settings
    app_cloud_credentials(app)

    # AND custom cloud tracks
    app.config["CUSTOM_IGV_TRACKS"] = TEST_IGV_TRACKS

    display_obj = {}

    # WHEN the function that prespares cloud tracks is invoked for a MT variant (build37)
    controllers.cloud_tracks("37", "M", ["cosmic_coding_v90"], display_obj)

    # THEN the display object should have a track with expected key/values in build 38
    assert (
        display_obj["custom_tracks"][0]["name"]
        == TEST_IGV_TRACKS["cosmic_coding_v90"]["38"]["description"]
    )
    assert (
        display_obj["custom_tracks"][0]["type"]
        == TEST_IGV_TRACKS["cosmic_coding_v90"]["38"]["type"]
    )
    assert (
        display_obj["custom_tracks"][0]["format"]
        == TEST_IGV_TRACKS["cosmic_coding_v90"]["38"]["format"]
    )
    assert (
        display_obj["custom_tracks"][0]["displayMode"]
        == TEST_IGV_TRACKS["cosmic_coding_v90"]["38"]["displayMode"]
    )
    assert (
        display_obj["custom_tracks"][0]["url"]
        == TEST_IGV_TRACKS["cosmic_coding_v90"]["38"]["file_name"]
    )

    track_url = TEST_IGV_TRACKS["cosmic_coding_v90"]["38"]["file_name"]
    track_index_format = TEST_IGV_TRACKS["cosmic_coding_v90"]["38"]["index_format"]
    assert display_obj["custom_tracks"][0]["indexURL"] == ".".join([track_url, track_index_format])


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
