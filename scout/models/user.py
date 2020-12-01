# -*- coding: utf-8 -*-
"""
"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from datetime import datetime


class User(dict):
    """User dictionary

    _id = str, # required, unique, same as email
    email = str, # required, unique
    name = str, # required=True
    created_at = datetime,
    accessed_at = datetime,
    location = str,
    institutes = list, # List of institute_ids
    roles = list, # List of roles
    """

    def __init__(
        self,
        email,
        name,
        id=None,
        created_at=None,
        accessed_at=None,
        location=None,
        institutes=None,
        roles=None,
        igv_tracks=None,
    ):
        super(User, self).__init__()
        self["email"] = email
        self["_id"] = id or email
        self["name"] = name
        self["created_at"] = created_at or datetime.now()
        self["accessed_at"] = accessed_at
        self["location"] = location
        self["institutes"] = institutes or []
        self["roles"] = roles or []
        self["igv_tracks"] = igv_tracks or []
