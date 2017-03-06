import logging

import click

from scout.commands.case import cases

logger = logging.getLogger(__name__)

@click.command('panels', short_help='Display gene panels')
@click.pass_context
def panels(context):
    """Show all gene panels in the database"""
    logger.info("Running scout view panels")
    adapter = context.obj['adapter']
    
    panel_objs = adapter.gene_panels()
    if panel_objs.count() == 0:
        logger.info("No panels found")
    else:
        click.echo("panel_name\tversion\tnr_genes")
        
        for panel_obj in panel_objs:
            click.echo("{0}\t{1}\t{2}".format(
                panel_obj['panel_name'], 
                str(panel_obj['version']),
                len(panel_obj['genes'])
            ))

@click.command('users', short_help='Display users')
@click.pass_context
def users(context):
    """Show all users in the database"""
    logger.info("Running scout view users")
    adapter = context.obj['adapter']
    
    ## TODO add a User interface to the adapter
    for user_obj in adapter.users():
        click.echo(user_obj['name'])

@click.command('whitelist', short_help='Display whitelist')
@click.pass_context
def whitelist(context):
    """Show all objects in the whitelist collection"""
    logger.info("Running scout view users")
    adapter = context.obj['adapter']
    
    ## TODO add a User interface to the adapter
    for whitelist_obj in adapter.whitelist_collection.find():
        click.echo(whitelist_obj['_id'])


@click.command('institutes', short_help='Display institutes')
@click.pass_context
def institutes(context):
    """Show all institutes in the database"""
    logger.info("Running scout view institutes")
    adapter = context.obj['adapter']
    
    for institute_obj in adapter.institutes():
        click.echo(institute_obj['internal_id'])

@click.command('genes', short_help='Display genes')
@click.option('-b', '--build', default='37', type=click.Choice(['37','38']))
@click.pass_context
def genes(context, build):
    """Show all genes in the database"""
    logger.info("Running scout view genes")
    adapter = context.obj['adapter']
    
    click.echo("Chromosom\tstart\tend\thgnc_id\thgnc_symbol")
    for gene_obj in adapter.all_genes(build=build):
        click.echo("{0}\t{1}\t{2}\t{3}\t{4}".format(
            gene_obj['chromosome'],
            gene_obj['start'],
            gene_obj['end'],
            gene_obj['hgnc_id'],
            gene_obj['hgnc_symbol'],
        ))

@click.command('diseases', short_help='Display all diseases')
@click.pass_context
def diseases(context):
    """Show all diseases in the database"""
    logger.info("Running scout view diseases")
    adapter = context.obj['adapter']
    
    click.echo("Disease")
    for disease_obj in adapter.disease_terms():
        click.echo("{0}:{1}".format(
            disease_obj['source'],
            disease_obj['disease_id'],
        ))

@click.command('hpo', short_help='Display all hpo terms')
@click.pass_context
def hpo(context):
    """Show all hpo terms in the database"""
    logger.info("Running scout view hpo")
    adapter = context.obj['adapter']
    
    click.echo("hpo_id\tdescription")
    for hpo_obj in adapter.hpo_terms():
        click.echo("{0}\t{1}".format(
            hpo_obj.hpo_id,
            hpo_obj.description,
        ))


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
view.add_command(genes)
view.add_command(diseases)
view.add_command(hpo)
view.add_command(whitelist)
