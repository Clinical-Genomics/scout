# -*- coding: utf-8 -*-
"""
"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from datetime import datetime


user = dict(
    email = str, # required, unique
    name = str, # required=True
    created_at = datetime,
    accessed_at = datetime,
    location = str,
    institutes = list, # List of institute_ids
    roles = list, # List of roles
)

