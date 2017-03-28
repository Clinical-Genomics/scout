# -*- coding= utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref= http=//stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from __future__ import absolute_import
from datetime import datetime

institute = dict(
    _id = str, # same as internal_id
    internal_id = str, # like 'cust000', required
    display_name = str, # like 'Clinical Genomics', required
    sanger_recipients = list, # list of email adressess

    created_at = datetime,
    updated_at = datetime,

    coverage_cutoff = int, # Defaults to  10
    frequency_cutoff = float, # Defaults to 0.01
)
