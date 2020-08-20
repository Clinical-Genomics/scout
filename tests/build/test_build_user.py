import datetime
import pytest
from scout.build.user import build_user


def test_build_user(parsed_user):
    ## GIVEN some parsed user information

    ## WHEN building a user object
    user_obj = build_user(parsed_user)

    ## THEN assert that the build was correct
    assert user_obj["_id"] == user_obj["email"] == parsed_user["email"]

    assert user_obj["name"] == user_obj["name"]

    assert isinstance(user_obj["created_at"], datetime.datetime)


@pytest.mark.parametrize("key", ['email', 'name'])    
def test_build_user_KeyError(parsed_user, key):
    ## GIVEN a dictionary with hpo information

    ## WHEN deleteing key
    parsed_user.pop(key)
    ## THEN calling build_hgnc_gene() will raise KeyError
    with pytest.raises(KeyError):
        build_user(parsed_user)
