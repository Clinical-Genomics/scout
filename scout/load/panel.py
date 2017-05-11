# -*- coding: utf-8 -*-
import logging

from scout.parse.panel import parse_gene_panel
from scout.build import build_panel

logger = logging.getLogger(__name__)


def load_panel(adapter, panel_info):
    """Load a gene panel into the databse

    Args:
        adapter(MongoAdapter)
        panel_info(dict)
    """
    panel_data = parse_gene_panel(panel_info)

    panel_obj = build_panel(panel_data, adapter)

    # Check if the panel exists in database
    panel = adapter.gene_panel(panel_obj['panel_name'], panel_obj['version'])

    if not panel:
        adapter.add_gene_panel(panel_obj)
    else:
        logger.info("Panel {} version {} already exists".format(panel_obj['panel_name'],
                                                                panel_obj['version']))
