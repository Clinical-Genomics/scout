# -*- coding: utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref: http://stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import, unicode_literals
from datetime import datetime

whitelist = dict(
    email = str, # required, unique
    created_at = datetime, 
    institutes = list, # list of institute_ids
)
