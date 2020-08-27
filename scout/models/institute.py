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
    loqusdb_id = str, # points to loqusdb configuration in server.py

    created_at = datetime, # Defaults to now
    updated_at = datetime, # Defaults to now

    collaborators = list, # list of institute _ids to allow sharing with,
    phenotype_groups = list, # list of phenotypes
    cohorts = list, # list of cohort tags

    coverage_cutoff = int, # Defaults to  10
    frequency_cutoff = float, # Defaults to 0.01

    """

    def __init__(
        self,
        internal_id,
        display_name,
        sanger_recipients,
        loqusdb_id,
        created_at=None,
        updated_at=None,
        coverage_cutoff=None,
        collaborators=None,
        phenotype_groups=None,
        cohorts=None,
        frequency_cutoff=None,
    ):
        super(Institute, self).__init__()
        self["internal_id"] = internal_id
        self["_id"] = internal_id
        self["display_name"] = display_name
        self["sanger_recipients"] = sanger_recipients
        self["loqusdb_id"] = loqusdb_id
        self["collaborators"] = collaborators
        self["phenotype_groups"] = phenotype_groups
        self["cohorts"] = cohorts
        self["created_at"] = created_at or datetime.now()
        self["updated_at"] = updated_at or datetime.now()
        self["coverage_cutoff"] = coverage_cutoff or 10
        self["frequency_cutoff"] = frequency_cutoff or 0.01
