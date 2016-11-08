# -*- coding: utf-8 -*-
import logging

from scout.models import GenePanel

logger = logging.getLogger(__name__)

def build_panel(panel_info):
    """Build a mongoengine GenePanel

        Args:
            panel_info(dict): A dictionary with panel information

        Returns:
            panel_obj(GenePanel)

    """
    logger.info("Building panel with id: {0}".format(panel_info['id']))

    panel_obj = GenePanel(
        institute=panel_info['institute'],
        panel_name=panel_info['id'],
        version=panel_info['version'],
        date=panel_info['date'],
    )
    panel_obj.display_name = panel_info['display_name']

    panel_obj.genes = panel_info['genes']

    return panel_obj
