import logging

import click

logger = logging.getLogger(__name__)

@click.command()
@click.option('-i', '--internal_id',
                type=str,
                required=True
)
@click.option('-d', '--display_name',
                type=str,
                required=True
)
@click.pass_context
def institute(ctx, internal_id, display_name):
    """
    Manage institutes
    
    """
    adapter = ctx.obj['adapter']
    
    if adapter.institute(institute_id=internal_id):
        logger.warning('Institute already exists in database')
        ctx.abort()
    
    adapter.add_institute(
        internal_id=internal_id, 
        display_name=display_name
    )
