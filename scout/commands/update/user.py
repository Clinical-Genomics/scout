import logging
from typing import List, Optional, Tuple

import click
from flask.cli import with_appcontext

from scout.adapter import MongoAdapter
from scout.constants.user import USER_ROLES
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("user", short_help="Update a user")
@click.option("--user-id", "-u", required=True, help="An email address that identifies the user")
@click.option("--update-role", "-r", type=click.Choice(USER_ROLES), help="Add a role to the user")
@click.option("--remove-admin", is_flag=True, help="(Deprecated) Remove admin role from the user")
@click.option("--remove-role", multiple=True, help="Specify roles to remove from the user")
@click.option("--add-institute", "-i", multiple=True, help="Specify institutes to add")
@click.option("--remove-institute", multiple=True, help="Specify institutes to remove")
@with_appcontext
def user(
    user_id: str,
    update_role: Optional[str],
    remove_admin: bool,
    remove_role: Tuple[str, ...],
    add_institute: Tuple[str, ...],
    remove_institute: Tuple[str, ...],
) -> None:
    """Update roles and institutes for a user in the database."""
    adapter = store
    user_obj = adapter.user(user_id)
    if not user_obj:
        LOG.warning("User %s could not be found", user_id)
        raise click.Abort()

    user_obj["roles"] = process_roles(
        current_roles=user_obj.get("roles", []),
        add_role=update_role,
        remove_roles=remove_role,
        remove_admin=remove_admin,
        user_id=user_id,
    )
    user_obj["institutes"] = process_institutes(
        current_institutes=user_obj.get("institutes", []),
        add_institutes=add_institute,
        remove_institutes=remove_institute,
        adapter=adapter,
        user_id=user_id,
    )
    adapter.update_user(user_obj)


def process_roles(
    current_roles: List[str],
    add_role: Optional[str],
    remove_roles: Tuple[str, ...],
    remove_admin: bool,
    user_id: str,
) -> List[str]:
    """Define the list of roles for a user in the database."""
    roles = set(current_roles)

    if add_role:
        if add_role in roles:
            LOG.warning("User already has role '%s'", add_role)
        else:
            roles.add(add_role)
            LOG.info("Adding role '%s' to user '%s'", add_role, user_id)

    all_remove = set(remove_roles)
    if remove_admin and "admin" not in all_remove:
        click.echo("⚠️ --remove-admin is deprecated. Use --remove-role admin instead.")
        all_remove.add("admin")

    for role in all_remove:
        if role in roles:
            roles.remove(role)
            LOG.info("Removing role '%s' from user '%s'", role, user_id)
        else:
            LOG.info("User does not have role '%s'", role)

    return list(roles)


def process_institutes(
    current_institutes: List[str],
    add_institutes: Tuple[str, ...],
    remove_institutes: Tuple[str, ...],
    adapter: MongoAdapter,
    user_id: str,
) -> List[str]:
    """Define the list of institutes for a user in the database."""
    institutes = set(current_institutes)

    for inst in add_institutes:
        if adapter.institute(inst):
            institutes.add(inst)
            LOG.info("Adding institute '%s' to user '%s'", inst, user_id)
        else:
            LOG.warning("Institute '%s' could not be found", inst)

    for inst in remove_institutes:
        if inst in institutes:
            institutes.remove(inst)
            LOG.info("Removing institute '%s' from user '%s'", inst, user_id)
        else:
            LOG.info("User does not have access to institute '%s'", inst)

    return list(institutes)
