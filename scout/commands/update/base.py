import logging

import click

from .case import case as case_command
from .compounds import compounds as compound_command
from .disease import diseases as disease_command
from .genes import genes as gene_command
from .hpo import hpo as hpo_command
from .individual import individual as individual_command
from .institute import institute as institute_command
from .omim import omim as omim_command
from .panel import panel as panel_command
from .panelapp import panelapp_green as panelapp_green_command
from .phenotype_groups import groups as groups_command
from .user import user as user_command

LOG = logging.getLogger(__name__)


@click.group()
@click.pass_context
def update(context):
    """
    Update objects in the database.
    """
    pass


update.add_command(institute_command)
update.add_command(user_command)
update.add_command(panel_command)
update.add_command(case_command)
update.add_command(omim_command)
update.add_command(panelapp_green_command)
update.add_command(compound_command)
update.add_command(hpo_command)
update.add_command(gene_command)
update.add_command(disease_command)
update.add_command(groups_command)
update.add_command(individual_command)
