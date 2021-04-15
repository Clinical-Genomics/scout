# -*- coding: utf-8 -*-
from scout.server.blueprints.login.models import LdapUser, LoginUser


def test_login_user(user_obj):
    """Test the Flask login class used for general user login"""

    user_dict = LoginUser(user_obj)
    assert user_dict.get_id() == user_obj["email"]
