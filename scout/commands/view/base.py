import logging

import click

from .panels import panels
from .users import users
from .institutes import institutes
from .diseases import diseases
from .hpo import hpo
from .whitelist import whitelist
from .aliases import aliases
from .individuals import individuals
from .index import index
from .intervals import intervals
from .collections import collections
from .transcripts import transcripts
from .case import cases


LOG = logging.getLogger(__name__)


@click.group()
@click.pass_context
def view(context):
    """
    View objects from the database. This command is used to get a overview of objects in the 
    database. To get serialisable things use `scout export`
    """
    pass


view.add_command(panels)
view.add_command(users)
view.add_command(institutes)
view.add_command(diseases)
view.add_command(hpo)
view.add_command(whitelist)
view.add_command(aliases)
view.add_command(individuals)
view.add_command(index)
view.add_command(intervals)
view.add_command(collections)
view.add_command(transcripts)
view.add_command(cases)
