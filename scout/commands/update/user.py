import logging

import click
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)
USER_ROLES = ["admin", "institute_admin", "mme_submitter", "beacon_submitter"]

@click.command("user", short_help="Update a user")
@click.option("--user-id", "-u", help="A email adress that identifies the user", required=True)
@click.option(
    "--update-role",
    "-r",
    # There will be more roles in the future
    type=click.Choice(USER_ROLES),
    help="Add a role to the user",
)
@click.option("--remove-admin", is_flag=True, help="(Deprecated) Remove admin role from the user")
@click.option("--remove-role", multiple=True, help="Specify one or more roles to remove from the user")
@click.option("--add-institute", "-i", multiple=True, help="Specify one or more institutes to add")
@click.option("--remove-institute", multiple=True, help="Specify one or more institutes to remove")
@with_appcontext
def user(user_id, update_role, add_institute, remove_admin, remove_role, remove_institute):
    """
    Update a user in the database
    """
    adapter = store
    user_obj = adapter.user(user_id)

    if not user_obj:
        LOG.warning("User %s could not be found", user_id)
        raise click.Abort()

    # ----- Handle roles -----
    roles = set(user_obj.get("roles", []))

    # Add role
    if update_role:
        if update_role in roles:
            LOG.warning("User already has role '%s'", update_role)
        else:
            roles.add(update_role)
            LOG.info("Adding role '%s' to user '%s'", update_role, user_id)

    # Support deprecated --remove-admin
    all_roles_to_remove = set(remove_role)
    if remove_admin:
        if "admin" not in all_roles_to_remove:
            click.echo("⚠️ --remove-admin is deprecated. Use --remove-role admin instead.")
            all_roles_to_remove.add("admin")

    # Remove roles
    for role in all_roles_to_remove:
        if role in roles:
            roles.remove(role)
            LOG.info("Removing role '%s' from user '%s'", role, user_id)
        else:
            LOG.info("User does not have role '%s'", role)

    user_obj["roles"] = list(roles)

    # ----- Handle institutes -----
    institutes = set(user_obj.get("institutes", []))

    for inst_id in add_institute:
        if adapter.institute(inst_id):
            institutes.add(inst_id)
            LOG.info("Adding institute '%s' to user '%s'", inst_id, user_id)
        else:
            LOG.warning("Institute '%s' could not be found", inst_id)

    for inst_id in remove_institute:
        if inst_id in institutes:
            institutes.remove(inst_id)
            LOG.info("Removing institute '%s' from user '%s'", inst_id, user_id)
        else:
            LOG.info("User does not have access to institute '%s'", inst_id)

    user_obj["institutes"] = list(institutes)

    # ----- Save updated user -----
    adapter.update_user(user_obj)
