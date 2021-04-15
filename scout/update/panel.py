import logging
from pprint import pprint as pp

from scout.exceptions import IntegrityError

LOG = logging.getLogger(__name__)


def update_panel(
    adapter,
    panel_name,
    panel_version,
    new_version=None,
    new_date=None,
    new_maintainer=None,
):
    """Update a gene panel in the database

    We need to update the actual gene panel and then all cases that refers to the panel.

    Args:
        adapter(scout.adapter.MongoAdapter)
        panel_name(str): Unique name for a gene panel
        panel_version(float)
        new_version(float)
        new_date(datetime.datetime)
        new_maintainer(list(user_id))

    Returns:
        updated_panel(scout.models.GenePanel): The updated gene panel object
    """
    panel_obj = adapter.gene_panel(panel_name, panel_version)

    if not panel_obj:
        raise IntegrityError("Panel %s version %s does not exist" % (panel_name, panel_version))

    updated_panel = adapter.update_panel(panel_obj, new_version, new_date, new_maintainer)

    panel_id = updated_panel["_id"]

    # We need to alter the embedded panels in all affected cases
    update = {"$set": {}}
    if new_version:
        update["$set"]["panels.$.version"] = updated_panel["version"]
    if new_date:
        update["$set"]["panels.$.updated_at"] = updated_panel["date"]

    # there is however no need to update maintainer for the embedded versions

    if update["$set"] != {}:
        LOG.info("Updating affected cases with {0}".format(update))

        query = {"panels": {"$elemMatch": {"panel_name": panel_name}}}
        adapter.case_collection.update_many(query, update)

    return updated_panel
