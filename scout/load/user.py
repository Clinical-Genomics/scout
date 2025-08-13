import logging
from typing import Optional

import click

from scout.build.user import build_user
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


def save_user(user_info: dict) -> Optional[dict]:
    """Saves a new user document to the database, or raises an error if the operation fails."""

    user_obj: dict = build_user(user_info)
    try:
        new_user: dict = store.add_user(user_obj)
        return new_user
    except Exception as err:
        LOG.warning(f"An error occurred while saving user:{err})")
        raise click.Abort()
