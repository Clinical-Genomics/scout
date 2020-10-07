# coding=UTF-8
from scout.server.app import create_app
from scout.server.extensions import cloud_tracks

TEST_TRACKS = [
    {
        "name": "custom_public_bucket",
        "access": "public",
        "tracks": [
            {
                "name": "Test public track",
                "type": "variant",
                "format": "vcf",
                "build": "37",
                "url": "url/to/public/track",
                "indexURL": "url/to/public/track.index",
            }
        ],
    },
]


def test_align_handler_public_tracks():
    """Test The class creating cloud tracks with public tracks"""
    # GIVEN app config settings with a custom cloud public track
    config = dict(CLOUD_IGV_TRACKS=TEST_TRACKS)
    # THEN the initialized app should create a cloud_tracks extension
    app = create_app(config=config)

    # Contanining the public track
    assert cloud_tracks.public_tracks["37"][0]["name"] == "Test public track"
