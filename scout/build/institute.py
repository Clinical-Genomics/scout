import logging

from datetime import datetime

logger = logging.getLogger(__name__)

def build_institute(internal_id, display_name, sanger_recipients=None, 
                    coverage_cutoff=None, frequency_cutoff=None):
    """Build a institute object
    
    Args:
        internal_id(str)
        display_name(str)
        sanger_recipients(list(str)): List with email adresses
    
    Return:
     {
        '_id': str, # same as internal_id
        'internal_id': str, # like 'cust000', required
        'display_name': str, # like 'Clinical Genomics', required
        'sanger_recipients': list, # list of email adressess
    
        'created_at': datetime, 
        'updated_at': datetime,

        'coverage_cutoff': int, # Defaults to  10
        'frequency_cutoff': float, # Defaults to 0.01
    }
    
    """
    sanger_recipients = sanger_recipients or None
    
    logger.info("Building institute {0} with display name {1}".format(
                 internal_id, display_name))
    
    now = datetime.now()
    
    institute_obj = dict(
        _id = internal_id,
        internal_id = internal_id,
        display_name = display_name,
        created_at = now,
        updated_at = now,
    )

    if sanger_recipients:
        institute_obj['sanger_recipients'] = sanger_recipients

    institute_obj['coverage_cutoff'] = coverage_cutoff or 10
    institute_obj['frequency_cutoff'] = frequency_cutoff or 0.01
    
    return institute_obj
    