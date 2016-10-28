# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


def load_panel(adapter, panel_obj):
    """Load a gene panel into the databse"""
    # Check if the panel exists in database
    panel = adapter.gene_panel(panel_obj['panel_name'], panel_obj['version'])

    if not panel:
        adapter.add_gene_panel(panel_obj)
    else:
        logger.info("Panel {0} version {1} already exists".format(
            panel.panel_name, panel.version))
