import logging

import click
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("user", short_help="Update a user")
@click.option("--user-id", "-u", help="A email adress that identifies the user", required=True)
@click.option(
    "--update-role",
    "-r",
    # There will be more roles in the future
    type=click.Choice(["admin", "mme_submitter", "beacon_submitter"]),
    help="Add a role to the user",
)
@click.option("--remove-admin", is_flag=True, help="Remove admin rights from user")
@click.option("--add-institute", "-i", multiple=True, help="Specify the institutes to add")
@click.option("--remove-institute", multiple=True, help="Specify the institutes to remove")
@with_appcontext
def user(user_id, update_role, add_institute, remove_admin, remove_institute):
    """
    Update a user in the database
    """
    adapter = store

    user_obj = adapter.user(user_id)

    if not user_obj:
        LOG.warning("User %s could not be found", user_id)
        raise click.Abort()

    existing_roles = set(user_obj.get("roles", []))
    if update_role:
        if not update_role in user_obj["roles"]:
            existing_roles = set(user_obj["roles"])
            existing_roles.add(update_role)
            LOG.info("Adding role %s to user", update_role)
        else:
            LOG.warning("User already have role %s", update_role)

    if remove_admin:
        try:
            existing_roles.remove("admin")
            LOG.info("Removing admin rights from user %s", user_id)
        except KeyError as err:
            LOG.info("User %s does not have admin rights", user_id)

    user_obj["roles"] = list(existing_roles)

    existing_institutes = set(user_obj.get("institutes", []))
    for institute_id in add_institute:
        institute_obj = adapter.institute(institute_id)
        if not institute_obj:
            LOG.warning("Institute %s could not be found", institute_id)
        else:
            existing_institutes.add(institute_id)
            LOG.info("Adding institute %s to user", institute_id)

    for institute_id in remove_institute:
        try:
            existing_institutes.remove(institute_id)
            LOG.info("Removing institute %s from user", institute_id)
        except KeyError as err:
            LOG.info("User does not have access to institute %s", institute_id)

    user_obj["institutes"] = list(existing_institutes)

    adapter.update_user(user_obj)
