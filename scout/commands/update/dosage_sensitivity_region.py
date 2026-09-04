import logging

import click
from flask.cli import with_appcontext

from scout.commands.download.clingen import CLINGEN_FILES
from scout.load.clingen import load_clingen_dosage_sensitivity
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("regions", short_help="Update dosage sensitivity regions")
@click.option(
    "-f",
    "--downloads-folder",
    type=click.Path(exists=True, dir_okay=True, readable=True),
    help="specify path to folder where files necessary to update dosage sensitivity regions are pre-downloaded",
)
@with_appcontext
def dosage_sensitivity_regions(downloads_folder):
    """Update dosage sensitivity regions in the database.

    This command updates the dosage sensitivity regions in the database using the ClinGen dosage sensitivity information.
    It also loads the ISCA regions information, as ClinGen is the primary source of ISCA regions.

    The ClinGen dosage sensitivity information is fetched from the ClinGen website if not pre-downloaded.

    The command will drop all existing regions in the database before loading the new regions.
    """

    dosage_lines = None
    if downloads_folder:
        dosage_file_path = f"{downloads_folder}/{CLINGEN_FILES['dosage']['file_name']}"
        try:
            with open(dosage_file_path, "r") as dosage_file:
                dosage_lines = dosage_file.readlines()
        except FileNotFoundError:
            LOG.warning("File %s not found. Fetching from ClinGen website.", dosage_file_path)
            dosage_lines = None

    load_clingen_dosage_sensitivity(store, dosage_lines)
