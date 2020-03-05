import datetime

from scout.build.user import build_user


def test_build_user(parsed_user):
    ## GIVEN some parsed user information

    ## WHEN building a user object
    user_obj = build_user(parsed_user)

    ## THEN assert that the build was correct
    assert user_obj["_id"] == user_obj["email"] == parsed_user["email"]

    assert user_obj["name"] == user_obj["name"]

    assert isinstance(user_obj["created_at"], datetime.datetime)
