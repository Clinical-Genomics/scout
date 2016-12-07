# -*- coding: utf-8 -*-
"""
"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from datetime import datetime

from flask_login import AnonymousUserMixin
from flask import current_app
from mongoengine import (DateTimeField, Document, EmailField, ListField,
                         ReferenceField, StringField)

from .institute import Institute


class LoginUserMixin(object):
    def has_role(self, query_role):
        """Check if user has been assigned a specific role."""
        return query_role in self.roles

    @property
    def first_name(self):
        """Return the first name of the user."""
        return self.name.split(' ')[0]

    @property
    def display_name(self):
        """Return the name of the user."""
        return self.name

    # required for Flask-Admin interface
    def __unicode__(self):
        return self.name


class User(Document, LoginUserMixin):
    """Represent a Scout user that can belong to multiple instututes."""
    email = EmailField(required=True, unique=True)
    name = StringField(max_length=40, required=True)
    created_at = DateTimeField(default=datetime.now)
    accessed_at = DateTimeField()
    location = StringField()
    institutes = ListField(ReferenceField('Institute'))
    roles = ListField(StringField())

    # Flask-Login integration
    @property
    def is_authenticated(self):
        """Perform a faux check that the user if properly authenticated."""
        return True

    def is_active(self):
        """Perform a faux check that the user is active."""
        return True

    def is_anonymous(self):
        """Perform a faux check whether the user is anonymous."""
        return False

    def get_id(self):
        # the id property is assigned each model automatically
        return str(self.id)


class AnonymousUser(AnonymousUserMixin, LoginUserMixin):

    def __init__(self):
        self.name = 'Paul T. Anderson'
        self.email = 'pt@anderson.com'

        if current_app.config.get('LOGIN_DISABLED'):
            self.roles = ['admin']
            self.institutes = Institute.objects()

        else:
            self.roles = []
            self.institutes = []
