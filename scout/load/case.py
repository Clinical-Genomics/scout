# -*- coding: utf-8 -*-
import logging

from scout.exceptions import IntegrityError

logger = logging.getLogger(__name__)


def load_case(adapter, case_obj, update=False, gene_panels=None,
              default_panels=None):
    """Load a case into the database

    If the case already exists the function will exit.
    If the user want to load a case that is already in the database
    'update' has to be 'True'

    Args:
        adapter (MongoAdapter): connection to the database
        case_obj (Case): case object to persist to the database
        update(bool): If existing case should be updated
        gene_panels(list(str)): Name of the gene panels
        default_panels(list(str)): Name of the default panels
    """
    gene_panels = gene_panels or []
    default_panels = default_panels or []
    logger.info('Loading case {} into database'.format(case_obj.display_name))
    owner = case_obj.owner
    institute_obj = adapter.institute(institute_id=owner)
    if not institute_obj:
        message = "Institute {} does not exist in database".format(owner)
        raise ValueError(message)

    panel_objs = []
    default_panels_objs = []
    for panel in gene_panels:
        panel_obj = adapter.gene_panel(panel_id=panel)
        panel_objs.append(panel_obj)
        if panel in default_panels:
            default_panels_objs.append(panel_obj)
    case_obj.gene_panels = panel_objs
    case_obj.default_panels = default_panels_objs

    # Check if case exists in database
    existing_case = adapter.case(institute_id=owner,
                                 case_id=case_obj.display_name)
    if existing_case:
        if update:
            adapter.update_case(case_obj)
        else:
            raise IntegrityError("Case {0} already exists in database".format(
                                 case_obj.case_id))
    else:
        adapter.add_case(case_obj)
