import logging

import click

logger = logging.getLogger(__name__)

from scout.load import load_institute

@click.command()
@click.option('-i', '--internal_id',
                type=str,
                required=True
)
@click.option('-d', '--display_name',
)
@click.pass_context
def institute(ctx, internal_id, display_name):
    """
    Manage institutes
    
    """
    adapter = ctx.obj['adapter']
    
    if not internal_id:
        logger.warning("A institute has to have an internal id")
        ctx.abort()
    
    if not display_name:
        display_name = internal_id
    
    try:
        load_institute(
            adapter=adapter, 
            internal_id=internal_id, 
            display_name=display_name, 
            sanger_recipients=None
        )
    except Exception as e:
        logger.warning(e.message)
        ctx.abort()
