import logging

import click

from scout.utils.date import get_date

from .case import case as case_command
from .omim import omim as omim_command

LOG = logging.getLogger(__name__)

@click.command('user', short_help='Update a user')
@click.option('--user-id', '-u',
                help="A email adress that identifies the user",
                required=True
)
@click.option('--update-role', '-r',
                # There will be more roles in the future
                type=click.Choice(['admin']),
                help="Add a role to the user",
)
@click.option('--remove-admin',
                is_flag=True,
                help="Remove admin rights from user",
)
@click.option('--add-institute', '-i',
                multiple=True,
                help="Specify the institutes to add",
)
@click.option('--remove-institute',
                multiple=True,
                help="Specify the institutes to remove",
)
@click.pass_context
def user(context, user_id, update_role, add_institute, remove_admin, remove_institute):
    """
    Update a user in the database
    """
    adapter = context.obj['adapter']
    
    user_obj = adapter.user(user_id)

    if not user_obj:
        LOG.warning("User %s could not be found", user_id)
        context.abort()
    
    existing_roles = set(user_obj['roles'])
    if update_role:
        if not update_role in user_obj['roles']:
            existing_roles = set(user_obj['roles'])
            existing_roles.add(update_role)
            LOG.info("Adding role %s to user", update_role)
        else:
            LOG.warning("User already have role %s", update_role)
    
    if remove_admin:
        try:
            existing_roles.remove('admin')
            LOG.info("Removing admin rights from user %s", user_id)
        except KeyError as err:
            LOG.info("User %s does not have admin rights", user_id)
    
    user_obj['roles'] = list(existing_roles)
        
    
    existing_institutes = set(user_obj['institutes'])
    for institute_id in add_institute:
        institute_obj = adapter.institute(institute_id)
        if not institute_obj:
            LOG.warning("Institute %s could not be found", institute_id)
        else:
            existing_institutes.add(institute_id)
            LOG.info("Adding institute %s to user", institute_id)

    for institute_id in remove_institute:
        try:
            existing_institutes.remove(institute_id)
            LOG.info("Removing institute %s from user", institute_id)
        except KeyError as err:
            LOG.info("User does not have access to institute %s", institute_id)

    user_obj['institutes'] = list(existing_institutes)

    updated_user = adapter.update_user(user_obj)

@click.command('panel', short_help='Update a panel')
@click.option('--panel', '-p',
                help="Specify what panel to update",
                required=True
)
@click.option('--version',
                help="Specify the version of a panel. If no version the latest panel is chosen.",
)
@click.option('--update-date', '-d',
                # There will be more roles in the future
                help="Update the date for a panel",
)
@click.option('--update-version',
                type=float,
                help="Change the version of a panel",
)
@click.pass_context
def panel(context, panel, version, update_date, update_version):
    """
    Update a panel in the database
    """
    adapter = context.obj['adapter']
    
    panel_obj = adapter.gene_panel(panel, version=version)

    if not panel_obj:
        LOG.warning("Panel %s (version %s) could not be found" % (panel, version))
        context.abort()
    
    date_obj = None
    if update_date:
        try:
            date_obj = get_date(update_date)
        except Exception as err:
            LOG.warning(err)
            context.abort()
    
    if update_version:
        panel_obj['version'] = update_version
    updated_panel = adapter.update_panel(panel_obj, date_obj)




@click.group()
@click.pass_context
def update(context):
    """
    Update objects in the database.
    """
    pass

update.add_command(user)
update.add_command(panel)
update.add_command(case_command)
update.add_command(omim_command)
