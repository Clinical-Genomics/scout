# coding=UTF-8
from scout.resources import mane_igv_track_path
from scout.server.app import create_app
from scout.server.extensions import config_igv_tracks


def test_align_handler_custom_remote_tracks():
    """Test The class creating custom tracks from the app config settings. Remote IGV track"""

    # GIVEN app config settings with a custom remote track
    TRACK_NAME = "A custom remote track"
    TRACK_URL = "https://track.bb"
    TRACK_BUILD = "37"
    track = {
        "name": TRACK_NAME,
        "type": "annotation",
        "format": "bigbed",
        "build": TRACK_BUILD,
        "url": TRACK_URL,
    }

    config = dict(CUSTOM_IGV_TRACKS=[{"tracks": [track]}])

    # THEN the initialized app should create a config_igv_tracks extension
    create_app(config=config)

    # With the provided track
    assert config_igv_tracks.tracks[TRACK_BUILD][0]["name"] == TRACK_NAME
    assert config_igv_tracks.tracks[TRACK_BUILD][0]["url"] == TRACK_URL


def test_align_handler_custom_local_tracks():
    """Test The class creating custom tracks from the app config settings. Local IGV track."""

    # GIVEN app config settings with a custom local track
    TRACK_NAME = "A custom local track"
    TRACK_PATH = mane_igv_track_path
    TRACK_BUILD = "37"
    track = {
        "name": TRACK_NAME,
        "type": "annotation",
        "format": "bigbed",
        "build": TRACK_BUILD,
        "url": TRACK_PATH,
    }

    # GIVEN app config settings with a custom track
    config = dict(CUSTOM_IGV_TRACKS=[{"tracks": [track]}])

    # THEN the initialized app should create a config_igv_tracks extension
    create_app(config=config)

    # With the provided track
    assert config_igv_tracks.tracks[TRACK_BUILD][0]["name"] == TRACK_NAME
    assert config_igv_tracks.tracks[TRACK_BUILD][0]["url"] == TRACK_PATH
