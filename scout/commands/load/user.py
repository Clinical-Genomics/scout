#!/usr/bin/env python
# encoding: utf-8
import logging

import click
from flask.cli import with_appcontext

from scout.build.user import build_user
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("user", short_help="Load a user")
@click.option("-i", "--institute-id", required=True, multiple=True)
@click.option("-u", "--user-name", required=True)
@click.option("-m", "--user-mail", required=True)
@click.option("-id", "--user-id", required=False)
@click.option("--admin", is_flag=True, help="If user should be admin")
@with_appcontext
def user(institute_id, user_name, user_mail, admin, user_id=None):
    """Add a user to the database."""
    adapter = store

    institutes = []
    for institute in institute_id:
        institute_obj = adapter.institute(institute_id=institute)

        if not institute_obj:
            LOG.warning("Institute % does not exist", institute)
            raise click.Abort()

        institutes.append(institute)

    roles = []
    if admin:
        LOG.info("User is admin")
        roles.append("admin")

    user_info = dict(
        email=user_mail.lower(),
        name=user_name,
        roles=roles,
        institutes=institutes,
        id=user_id,
    )

    user_obj = build_user(user_info)

    try:
        adapter.add_user(user_obj)
    except Exception as err:
        LOG.warning(err)
        raise click.Abort()
