import logging

import click

log = logging.getLogger(__name__)

@click.command('case', short_help='Update a case')
@click.option('--case-name', '-n',
                help="A email adress that identifies the user",
                required=True
)
@click.option('--institute', '-i',
                help="Specify the institutes of the case",
                required=True
)
@click.option('--add-collaborator', '-c',
                help="Add a collaborator to the case",
)
@click.pass_context
def case(context, case_name, institute, add_collaborator):
    """
    Update a case in the database
    """
    adapter = context.obj['adapter']
    
    case_id = "{0}-{1}".format(institute, case_name)
    # Chock if the case exists
    case_obj = adapter.case(case_id)
    
    if not case_obj:
        log.warning("Case %s could not be found", case_id)
        context.abort()
    
    if add_collaborator:
        if not adapter.institute(add_collaborator):
            log.warning("Institute %s could not be found", add_collaborator)
            context.abort()
        if not add_collaborator in case_obj['collaborators']:
            case_obj['collaborators'].append(add_collaborator)
            log.info("Adding collaborator %s", add_collaborator)

    adapter.update_case(case_obj)
