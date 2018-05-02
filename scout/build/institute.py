import logging

from scout.models import Institute

LOG = logging.getLogger(__name__)

def build_institute(internal_id, display_name, sanger_recipients=None,
                    coverage_cutoff=None, frequency_cutoff=None):
    """Build a institute object

    Args:
        internal_id(str)
        display_name(str)
        sanger_recipients(list(str)): List with email addresses

    Returns:
        institute_obj(scout.models.Institute)

    """

    LOG.info("Building institute %s with display name %s", internal_id,display_name)

    institute_obj = Institute(
        internal_id=internal_id, 
        display_name=display_name, 
        sanger_recipients=sanger_recipients,
        coverage_cutoff = coverage_cutoff,
        frequency_cutoff = frequency_cutoff
    )
    
    for key in list(institute_obj):
        if institute_obj[key] is None:
            institute_obj.pop(key)

    return institute_obj
