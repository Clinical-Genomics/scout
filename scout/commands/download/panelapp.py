import json
import logging
import os

import click

from scout.constants.panels import PANELAPP_OUTFILE_NAME
from scout.server.extensions import panelapp as panelapp_extension

LOG = logging.getLogger(__name__)


@click.command("panelapp-all", help="Download all panels from PanelApp to a file")
@click.option("-o", "--out-dir", default="./", show_default=True)
def panelapp_all(out_dir: str):
    """Download all PanelApp panels to a file."""

    LOG.info("Fetching all Panel IDs")
    panel_ids = panelapp_extension.get_panel_ids(
        signed_off=False
    )  # Collect al Panel IDs, page by page

    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, PANELAPP_OUTFILE_NAME)

    with open(out_file, "w") as f:
        with click.progressbar(panel_ids[:10], label="Downloading panels") as bar:
            for panel_id in bar:
                panel_obj = panelapp_extension.get_panel(panel_id)
                f.write(json.dumps(panel_obj) + "\n")

    LOG.info(f"Saved panels to {out_file}")
