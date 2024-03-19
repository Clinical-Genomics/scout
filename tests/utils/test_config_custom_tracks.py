# coding=UTF-8
from scout.server.app import create_app
from scout.server.extensions import config_igv_tracks


def test_align_handler_custom_tracks(igv_test_tracks):
    """Test The class creating custom tracks from the app config settings."""

    # GIVEN app config settings with a custom track
    config = dict(CUSTOM_IGV_TRACKS=igv_test_tracks)
    # THEN the initialized app should create a cloud_tracks extension
    create_app(config=config)

    # Contanining the public track
    assert config_igv_tracks.tracks["37"][0]["name"] == "Test public track"
