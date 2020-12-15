# coding=UTF-8
from scout.server.app import create_app
from scout.server.extensions import cloud_tracks


def test_align_handler_public_tracks(igv_test_tracks):
    """Test The class creating cloud tracks with public tracks"""
    # GIVEN app config settings with a custom cloud public track
    config = dict(CLOUD_IGV_TRACKS=igv_test_tracks)
    # THEN the initialized app should create a cloud_tracks extension
    app = create_app(config=config)

    # Contanining the public track
    assert cloud_tracks.public_tracks["37"][0]["name"] == "Test public track"
