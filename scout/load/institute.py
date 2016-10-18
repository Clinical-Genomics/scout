import logging
from scout.build import build_institute

logger = logging.getLogger(__name__)

def load_institute(adapter, internal_id, display_name, sanger_recipients=None):
    """Load a institute into the database
    
        Args:
            adapter(MongoAdapter)
            internal_id(str)
            display_name(str)
            sanger_recipients(list(email))
    """

    institute_obj = build_institute(
        internal_id = internal_id,
        display_name = display_name,
        sanger_recipients = sanger_recipients
    )
    logger.info("Loading institute {0} with display name {1}"\
                " into databse".format(internal_id, display_name))
    
    
    adapter.add_institute(institute_obj)