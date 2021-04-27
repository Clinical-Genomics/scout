"""CLI command for loading new variant evaluation options."""

import logging

import click
from flask.cli import with_appcontext

LOG = logging.getLogger(__name__)

from scout.load import load_variant_evalutation
from scout.server.extensions import store
