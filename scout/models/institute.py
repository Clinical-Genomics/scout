# -*- coding= utf-8 -*-
"""

"main concept of MongoDB is embed whenever possible"
Ref= http=//stackoverflow.com/questions/4655610#comment5129510_4656431
"""
from datetime import datetime

class Institute(dict):
    """Represents a institute
    
    _id = str, # same as internal_id
    internal_id = str, # like 'cust000', required
    display_name = str, # like 'Clinical Genomics', required
    sanger_recipients = list, # list of email adressess

    created_at = datetime, # Defaults to now
    updated_at = datetime, # Defaults to now

    coverage_cutoff = int, # Defaults to  10
    frequency_cutoff = float, # Defaults to 0.01
    
    """
    def __init__(self, internal_id, display_name, sanger_recipients, created_at=None, 
                 updated_at=None, coverage_cutoff=None, frequency_cutoff=None):
        super(Institute, self).__init__()
        self['internal_id'] = internal_id
        self['_id'] = internal_id
        self['display_name'] = display_name
        self['sanger_recipients'] = sanger_recipients
        self['created_at'] = created_at or datetime.now()
        self['updated_at'] = updated_at or datetime.now()
        self['coverage_cutoff'] = coverage_cutoff or 10
        self['frequency_cutoff'] = frequency_cutoff or 0.01

