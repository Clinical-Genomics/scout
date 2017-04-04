import logging

import click

from .case import case as case_command

log = logging.getLogger(__name__)

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
@click.option('--add-institute', '-i',
                multiple=True,
                help="Specify the institutes to add",
)
@click.pass_context
def user(context, user_id, update_role, add_institute):
    """
    Update a user in the database
    """
    adapter = context.obj['adapter']
    
    # Chock if the user exists
    if user_id:
        user_obj = adapter.user(user_id)
    else:
        log.warning("Please specify a user id")
        context.abort()
    
    if not user_obj:
        log.warning("User %s could not be found", user_id)
        context.abort()
    
    if update_role:
        if not update_role in user_obj['roles']:
            user_obj['roles'].append(update_role)
            log.info("Adding role %s to user", update_role)
        else:
            log.warning("User already have role %s", update_role)
        
    
    if add_institute:
        for institute in add_institute:
            institute_obj = adapter.institute(institute)
            if not institute_obj:
                log.warning("Institute %s could not be found", institute)
            else:
                if institute in user_obj['institutes']:
                    log.info("User already connected to institute %s", institute)
                else:
                    user_obj['institutes'].append(institute)
                    log.info("Adding institute %s to user", institute)
                    
    
    updated_user = adapter.update_user(user_obj)

@click.group()
@click.pass_context
def update(context):
    """
    Update objects in the database.
    """
    pass

update.add_command(user)
update.add_command(case_command)
