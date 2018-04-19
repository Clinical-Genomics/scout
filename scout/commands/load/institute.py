import logging

import click

logger = logging.getLogger(__name__)

from scout.load import load_institute


@click.command('institute', short_help='Load a institute')
@click.option('-i', '--internal-id',
              required=True)
@click.option('-d', '--display-name')
@click.option('-s', '--sanger-recipients', multiple=True)
@click.pass_context
def institute(ctx, internal_id, display_name, sanger_recipients):
    """
    Create a new institute and add it to the database

    """
    adapter = ctx.obj['adapter']

    if not internal_id:
        logger.warning("A institute has to have an internal id")
        ctx.abort()

    if not display_name:
        display_name = internal_id

    if sanger_recipients:
        sanger_recipients = list(sanger_recipients)

    try:
        load_institute(
            adapter=adapter,
            internal_id=internal_id,
            display_name=display_name,
            sanger_recipients=sanger_recipients
        )
    except Exception as e:
        logger.warning(e)
        ctx.abort()
