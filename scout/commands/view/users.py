import logging
import click

LOG = logging.getLogger(__name__)


@click.command('users', short_help='Display users')
@click.pass_context
def users(context):
    """Show all users in the database"""
    LOG.info("Running scout view users")
    adapter = context.obj['adapter']

    user_objs = [user for user in adapter.users()]
    if len(user_objs) == 0:
        LOG.info("No users found")
        return

    click.echo("#name\temail\troles\tinstitutes")
    for user_obj in user_objs:
        click.echo("{0}\t{1}\t{2}\t{3}\t".format(
            user_obj['name'],
            user_obj.get('mail', user_obj['_id']),
            ', '.join(user_obj.get('roles', [])),
            ', '.join(user_obj.get('institutes', [])),
        )
        )
