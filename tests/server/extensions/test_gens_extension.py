from scout.server.extensions import gens


def test_gens_app_extension(gens_app):
    """Test that invoking the Gens extension connection settings in the app works"""

    # GIVEN an app initialized with Gens settings
    # These settings should have the expected values
    assert gens.host == "127.0.0.1"
    assert gens.port == 5000
