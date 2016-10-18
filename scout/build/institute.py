import logging

from scout.models import Institute

logger = logging.getLogger(__name__)

def build_institute(internal_id, display_name, sanger_recipients=None):
    """Build a institute object
    
        Args:
            internal_id(str)
            display_name(str)
            sanger_recipients(list(str)): List with email adresses
    """
    sanger_recipients = sanger_recipients or None
    
    logger.info("Building institute {0} with display name {1}".format(
                 internal_id, display_name))
    
    institute_obj = Institute(
        internal_id = internal_id,
        display_name = display_name,
        sanger_recipients = sanger_recipients
    )
    
    return institute_obj
    