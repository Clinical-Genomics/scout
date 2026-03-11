from scout.server.extensions import gens


def test_gens_app_extension(gens_app):
    """Test that invoking the Gens extension connection settings in the app works"""

    # GIVEN an app initialized with Gens settings
    # These settings should have the expected values
    assert gens.host == "127.0.0.1"
    assert gens.port == 5000


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
