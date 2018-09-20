import logging

from pprint import pprint as pp

import click

LOG = logging.getLogger(__name__)


@click.command('institute', short_help='Update institute for a case')
@click.argument('institute-id')
@click.option('-c', '--coverage-cutoff',
    type=int,
    help="Set a new coverage cutoff for a institute", 
)
@click.option('-f', '--frequency-cutoff',
    type=float,
    help="Set a new frequency cutoff for a institute", 
)
@click.option('-s', '--sanger-recipient',
    help="Specify email adress for a existing user that should be added to the institute",
)
@click.option('-d', '--display-name',
    help="Set a new display name for a insitute",
)
@click.option('-r', '--remove-sanger',
    help="Specify email adress for a existing user that should be removed from sanger recipients",
)
@click.option('-p', '--phenotype-group',
    help="Add one or more phenotype groups to institute",
    multiple = True,
)
@click.option('-a', '--group-abbreviation',
    help="Specify a phenotype group abbreviation",
    multiple = True,
)
@click.pass_context
def institute(context, institute_id, sanger_recipient, coverage_cutoff, frequency_cutoff, 
              display_name, remove_sanger, phenotype_group, group_abbreviation):
    """
    Update an institute
    """
    adapter = context.obj['adapter']
    LOG.info("Running scout update institute")
    
    if (phenotype_group and group_abbreviation):
        if not len(phenotype_group) == len(group_abbreviation):
            LOG.warning("Specify same number of groups and abbreviations")
            context.abort()
    context.abort()

    try:
        adapter.update_institute(
            internal_id=institute_id, 
            sanger_recipient=sanger_recipient, 
            coverage_cutoff=coverage_cutoff, 
            frequency_cutoff=frequency_cutoff, 
            display_name=display_name,
            remove_sanger=remove_sanger,
            phenotype_groups=phenotype_group,
            group_abbreviations=group_abbreviation,
            )
    except Exception as err:
        LOG.warning(err)
        context.abort()
