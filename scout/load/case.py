import logging

from scout.parse import parse_case
from scout.build import (build_case)
from scout.exceptions import IntegrityError
from . import load_panel

logger = logging.getLogger(__name__)


def load_case(adapter, case_lines, owner, case_type='mip',
              analysis_type='unknown', scout_configs=None, update=False):
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

        Returns:
            case_obj(Case)
    """
    institute_obj = adapter.institute(institute_id=owner)
    if not institute_obj:
        message = "Institute {} does not exist in database".format(owner)
        raise SyntaxError(message)

    # Parse the case lines with the extra information
    parsed_case = parse_case(
        case_lines=case_lines,
        owner=owner,
        case_type=case_type,
        analysis_type=analysis_type,
        scout_configs=scout_configs
    )

    logger.info("Create the gene panels if they do not exist")

    #Build the mongoenginge case object
    case_obj = build_case(parsed_case)

    panel_objs = []
    for panel_obj in case_obj['clinical_panels']:
        #Replace with stored gene panels
        load_panel(adapter, panel_obj)
        panel_objs.append(adapter.gene_panel(panel_obj['panel_name'], panel_obj['version']))

    case_obj['clinical_panels'] = panel_objs

    panel_objs = []
    for panel_info in parsed_case['research_panels']:
        #Replace with stored gene panels
        load_panel(adapter, panel_obj)
        panel_objs.append(adapter.gene_panel(panel_obj['panel_name'], panel_obj['version']))

    case_obj['research_panels'] = panel_objs

    # Check if case exists in database
    existing_case = adapter.case(institute_id=owner,case_id=case_obj.display_name)
    if existing_case:
        if update:
            adapter.update_case(case_obj)
        else:
            raise IntegrityError("Case {0} already exists in database".format(
                                 case_obj.case_id))
    else:
        adapter.add_case(case_obj)

    return case_obj
