import logging

import click

from scout.commands.case import cases

from scout.models.user import User

logger = logging.getLogger(__name__)

@click.command('panels', short_help='Display gene panels')
@click.pass_context
def panels(context):
    """Show all gene panels in the database"""
    logger.info("Running scout view panels")
    adapter = context.obj['adapter']
    
    for panel_obj in adapter.gene_panel():
        click.echo('\t'.join([panel_obj.panel_name, str(panel_obj.version)]))

@click.command('users', short_help='Display users')
@click.pass_context
def users(context):
    """Show all users in the database"""
    logger.info("Running scout view users")
    adapter = context.obj['adapter']
    
    ## TODO add a User interface to the adapter
    for user_obj in User.objects():
        click.echo(user_obj.name)

@click.command('institutes', short_help='Display institutes')
@click.pass_context
def institutes(context):
    """Show all institutes in the database"""
    logger.info("Running scout view institutes")
    adapter = context.obj['adapter']
    
    for institute_obj in adapter.institutes():
        click.echo(institute_obj.internal_id)


@click.group()
@click.pass_context
def view(context):
    """
    View objects from the database.
    """
    pass

view.add_command(cases)
view.add_command(panels)
view.add_command(users)
view.add_command(institutes)
