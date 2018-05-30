import logging

import click

LOG = logging.getLogger(__name__)

@click.command('panel', short_help='Delete a gene panel')
@click.option('--panel-id', 
    help="The panel identifier name",
    required=True
)
@click.option('-v', '--version',
    type=float,
)
@click.pass_context
def panel(context, panel_id, version):
    """Delete a version of a gene panel or all versions of a gene panel"""
    LOG.info("Running scout delete panel")
    adapter = context.obj['adapter']

    panel_objs = adapter.gene_panels(panel_id=panel_id, version=version)
    if panel_objs.count() == 0:
        LOG.info("No panels found")
        
    for panel_obj in panel_objs:
        adapter.delete_panel(panel_obj)

# @click.command('users', short_help='Display users')
# @click.pass_context
# def users(context):
#     """Show all users in the database"""
#     LOG.info("Running scout view users")
#     adapter = context.obj['adapter']
#
#     ## TODO add a User interface to the adapter
#     for user_obj in User.objects():
#         click.echo(user_obj['name'])
#
# @click.command('institutes', short_help='Display institutes')
# @click.pass_context
# def institutes(context):
#     """Show all institutes in the database"""
#     LOG.info("Running scout view institutes")
#     adapter = context.obj['adapter']
#
#     for institute_obj in adapter.institutes():
#         click.echo(institute_obj['internal_id'])


@click.command('index', short_help='Delete all indexes')
@click.pass_context
def index(context):
    """Delete all indexes in the database"""
    LOG.info("Running scout delete index")
    adapter = context.obj['adapter']
    
    for collection in adapter.db.collection_names():
        adapter.db[collection].drop_indexes()
    LOG.info("All indexes deleted")


@click.command('user', short_help='Delete a user')
@click.option('-m', '--mail', required=True)
@click.pass_context
def user(context, mail):
    """Delete a user from the database"""
    LOG.info("Running scout delete user")
    adapter = context.obj['adapter']
    user_obj = adapter.user(mail)
    if not user_obj:
        LOG.warning("User {0} could not be found in database".format(mail))
    else:
        adapter.delete_user(mail)


@click.command('genes', short_help='Delete genes')
@click.option('-b', 'build', type=click.Choice(['37', '38']))
@click.pass_context
def genes(context, build):
    """Delete all genes in the database"""
    LOG.info("Running scout delete genes")
    adapter = context.obj['adapter']

    if build:
        LOG.info("Dropping genes collection for build: %s", build)
    else:
        LOG.info("Dropping genes collection")
        adapter.drop_genes()

@click.command('exons', short_help='Delete exons')
@click.option('-b', 'build', type=click.Choice(['37', '38']))
@click.pass_context
def exons(context, build):
    """Delete all exons in the database"""
    LOG.info("Running scout delete exons")
    adapter = context.obj['adapter']

    adapter.drop_exons(build)


@click.command('case', short_help='Delete a case')
@click.option('-i', '--institute', help='institute id of related cases')
@click.option('-c', '--case-id')
@click.option('-d', '--display-name')
@click.pass_context
def case(context, institute, case_id, display_name):
    """Delete a case and it's variants from the database"""
    adapter = context.obj['adapter']
    if not (case_id or display_name):
        click.echo("Please specify what case to delete")
        context.abort()

    if display_name:
        if not institute:
            click.echo("Please specify the owner of the case that should be "
                       "deleted with flag '-i/--institute'.")
            context.abort()
        case_id = "{0}-{1}".format(institute, display_name)

    LOG.info("Running deleting case {0}".format(case_id))
    case = adapter.delete_case(
        case_id=case_id,
        institute_id=institute,
        display_name=display_name
    )

    if case.deleted_count == 1:
        adapter.delete_variants(case_id=case_id, variant_type='clinical')
        adapter.delete_variants(case_id=case_id, variant_type='research')
    else:
        LOG.warning("Case does not exist in database")
        context.abort()

# @click.command('diseases', short_help='Display all diseases')
# @click.pass_context
# def diseases(context):
#     """Show all diseases in the database"""
#     LOG.info("Running scout view diseases")
#     adapter = context.obj['adapter']
#
#     click.echo("Disease")
#     for disease_obj in adapter.disease_terms():
#         click.echo("{0}:{1}".format(
#             disease_obj['source'],
#             disease_obj['disease_id'],
#         ))
#
# @click.command('hpo', short_help='Display all hpo terms')
# @click.pass_context
# def hpo(context):
#     """Show all hpo terms in the database"""
#     LOG.info("Running scout view hpo")
#     adapter = context.obj['adapter']
#
#     click.echo("hpo_id\tdescription")
#     for hpo_obj in adapter.hpo_terms():
#         click.echo("{0}\t{1}".format(
#             hpo_obj.hpo_id,
#             hpo_obj.description,
#         ))


@click.group()
@click.pass_context
def delete(context):
    """
    Delete objects from the database.
    """
    pass


delete.add_command(genes)
delete.add_command(case)
delete.add_command(user)
delete.add_command(index)
delete.add_command(panel)
delete.add_command(exons)
