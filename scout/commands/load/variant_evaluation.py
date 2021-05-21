"""CLI command for loading new variant evaluation options."""

import logging

import click
from flask.cli import with_appcontext

from scout.load import load_variant_evaluation
from scout.server.extensions import store

LOG = logging.getLogger(__name__)
