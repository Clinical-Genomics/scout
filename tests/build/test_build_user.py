import datetime
import pytest
from scout.build.user import build_user
from scout.constants import USER_DEFAULT_TRACKS


def test_build_user(parsed_user):
    ## GIVEN some parsed user information

    ## WHEN building a user object
    user_obj = build_user(parsed_user)

    ## THEN assert that the build was correct
    assert user_obj["_id"] == user_obj["email"] == parsed_user["email"]

    assert user_obj["name"] == user_obj["name"]

    assert user_obj["igv_tracks"] == USER_DEFAULT_TRACKS

    assert isinstance(user_obj["created_at"], datetime.datetime)


@pytest.mark.parametrize("key", ["email", "name"])
def test_build_user_missing_key(parsed_user, key):
    ## GIVEN a parsed_user (dict) containing user information

    ## WHEN deleting key
    parsed_user.pop(key)
    ## THEN calling build_user() will raise KeyError
    with pytest.raises(KeyError):
        build_user(parsed_user)
