# -*- coding: utf-8 -*-
from flask_login import UserMixin


class LoginUser(UserMixin):

    def __init__(self, user_data):
        """Create a new user object."""
        for key, value in user_data.items():
            setattr(self, key, value)

    def get_id(self):
        return self.email
