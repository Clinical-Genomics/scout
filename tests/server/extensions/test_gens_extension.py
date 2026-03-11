import responses

from scout.server.extensions import gens


def test_gens_app_extension(gens_app):
    """Test that invoking the Gens extension connection settings in the app works"""

    # GIVEN an app initialized with Gens settings
    # These settings should have the expected values
    assert gens.host == "127.0.0.1"
    assert gens.port == 5000


@responses.activate
def test_get_version(gens_app):
    """Test that the gens extension correctly gets a version from API"""

    gens_api_url = f"https://{gens.host}:{gens.port}/api/"
    responses.add(
        responses.GET,
        gens_api_url,
        json={"message": "Welcome to Gens API", "version": "5.6.7"},
        status=200,
    )

    assert gens.get_version() == 5


def test_gens_app_extension_v3(gens_app_v3):
    """Test that invoking the Gens extension connection settings in the app works and sets version correctly"""

    # GIVEN an app initialized with Gens settings
    # These settings should have the expected values
    assert gens.host == "127.0.0.1"
    assert gens.port == 5000
    assert gens.version == 3

    # When checking for connection settings
    settings = gens.connection_settings("38")
    # THEN the version is properly set from app config
    assert settings.get("version") == 3
