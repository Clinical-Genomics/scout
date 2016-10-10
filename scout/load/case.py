import logging

from scout.parse import parse_case
from scout.build import build_case

logger = logging.getLogger(__name__)

def load_case(adapter, case_lines, owner, case_type='mip', analysis_type='unknown',
               scout_configs=None, update=False):
    """Load a case into the database
    
        If the case already exists the function will exit.
        If the user want to load a case that is already in the database 
        'update' has to be 'True'
    
        Args:
            adapter(MongoAdapter)
            case_lines(Iterable): An iterable with ped like lines
            owner(str): Id of institute that owns the case   
            case_type(str): Describe the format of the ped lines
            analysis_type(str): 'WES', 'WGS', 'unknown' or 'mixed'
            scout_configs(dict): A dictionary with meta information
            update(bool): If existing case should be updated
    """
    # Parse the case lines with the extra information
    parsed_case = parse_case(
        case_lines=case_lines, 
        owner=owner, 
        case_type=case_type, 
        analysis_type=analysis_type,
        scout_configs=scout_configs
    )
    #Build the mongoenginge case object
    case_obj = build_case(parsed_case)

    # Check if case exists in database
    if adapter.case(institute_id=owner,case_id=case_obj.display_name):
        logger.warning("Case %s exists in database" % case_obj.display_name)
        if not update:
            raise SyntaxError()
    
    adapter.add_case(case_obj)
