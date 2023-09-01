"""
Test Phenopacket API extension
"""
import responses

from scout.server.extensions import bionano_access


@responses.activate
def test_bionano_access_extension(bionano_app, bionano_config, bionano_response):
    """Check that bionano extension app is created config options are set."""
    # GIVEN a bionano access extension app

    # THEN the given username and url should be set.
    assert bionano_access.url == bionano_config["BIONANO_ACCESS"]
    assert bionano_access.bionano_username == bionano_config["BIONANO_USERNAME"]
    assert bionano_access.bionano_token == bionano_response["TOKEN"]
    assert (
        bionano_access.bionano_user_dict.get("full_name") == bionano_response["user"]["full_name"]
    )


@responses.activate
def test_bionano_cookie_setup(bionano_app, bionano_response):
    """Test bionano app setup: login and retrieve session token and cookie values"""

    # GIVEN a bionano extension app and mocked response to a login query

    # WHEN attempting to get the access cookies
    cookies = bionano_access._get_auth_cookies()

    # THEN the appropriate cookies should be set on the app
    assert cookies.get("token") == bionano_response["TOKEN"]
    assert cookies.get("fullname") == bionano_response["user"]["full_name"]
