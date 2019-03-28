import logging
import click

from flask.cli import with_appcontext

from scout.server.extensions import store

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger(__name__)


@click.command('users', short_help='Display users')
@with_appcontext
def users():
    """Show all users in the database"""
    LOG.info("Running scout view users")
    adapter = store

    user_objs = adapter.users()
    if user_objs.count() == 0:
        LOG.info("No users found")
        raise click.Abort()

    click.echo("#name\temail\troles\tinstitutes")
    for user_obj in user_objs:
        click.echo("{0}\t{1}\t{2}\t{3}\t".format(
            user_obj['name'],
            user_obj.get('mail', user_obj['_id']),
            ', '.join(user_obj.get('roles', [])),
            ', '.join(user_obj.get('institutes', [])),
        )
        )
