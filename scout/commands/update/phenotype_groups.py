import logging
from pprint import pprint as pp

import click
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("groups", short_help="Update phenotype groups for an institute")
@click.argument("institute-id")
@click.option(
    "-p",
    "--phenotype-group",
    help="Add one or more phenotype groups to institute",
    multiple=True,
)
@click.option(
    "-a",
    "--group-abbreviation",
    help="Specify a phenotype group abbreviation",
    multiple=True,
)
@click.option("-f", "--group-file", help="CSV file with phenotype groups", type=click.File("r"))
@click.option(
    "-add",
    "--add",
    help="If groups should be added instead of replacing existing groups",
    is_flag=True,
)
@with_appcontext
def groups(institute_id, phenotype_group, group_abbreviation, group_file, add):
    """
    Update the phenotype for a institute.
    If --add the groups will be added to the default groups. Else the groups will be replaced.
    """
    adapter = store
    LOG.info("Running scout update institute")
    if group_file:
        phenotype_group = []
        group_abbreviation = []
        for line in group_file:
            if line.startswith("#"):
                continue
            if len(line) < 7:
                continue
            line = line.rstrip().split("\t")
            phenotype_group.append(line[0])
            if line[1]:
                group_abbreviation.append(line[1])

    if not phenotype_group:
        LOG.info("Please provide some groups")
        return

    if phenotype_group and group_abbreviation:
        if not len(phenotype_group) == len(group_abbreviation):
            LOG.warning("Specify same number of groups and abbreviations")
            return

    # try:
    adapter.update_institute(
        internal_id=institute_id,
        phenotype_groups=phenotype_group,
        group_abbreviations=group_abbreviation,
        add_groups=add,
    )
