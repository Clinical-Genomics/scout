import logging
from scout.models import Institute

logger = logging.getLogger(__name__)

def load_institute(adapter, internal_id, display_name, sanger_recipients=None):
    """Load a institute into the database
    
        Args:
            adapter(MongoAdapter)
            internal_id(str)
            display_name(str)
            sanger_recipients(list(email))
    """
    sanger_recipients = sanger_recipients or []
    
    logger.info("Loading institute {0} with display name {1}"\
                " into databse".format(internal_id, display_name))
    
    institute_obj = Institute(
        internal_id = internal_id,
        display_name = display_name,
        sanger_recipients = sanger_recipients
    )
    
    adapter.add_institute(institute_obj)