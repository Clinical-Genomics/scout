import logging
import click

from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("institutes", short_help="Display institutes")
@click.option("-i", "--institute-id", help="What institute to show")
@click.option("--json", help="Show json format", is_flag=True)
@with_appcontext
def institutes(institute_id, json):
    """Show all institutes in the database"""
    LOG.info("Running scout view institutes")
    adapter = store

    if institute_id:
        institute_objs = []
        institute_obj = adapter.institute(institute_id)
        if not institute_obj:
            LOG.info("Institute %s does not exist", institute_id)
            return
        institute_objs.append(institute_obj)
    else:
        institute_objs = [ins_obj for ins_obj in adapter.institutes()]

    if len(institute_objs) == 0:
        click.echo("No institutes found")
        raise click.Abort()

    header = ""
    if not json:
        for key in institute_objs[0].keys():
            header = header + "{0}\t".format(key)

        click.echo(header)

    for institute_obj in institute_objs:
        if json:
            click.echo(institute_obj)
            continue

        row = ""
        for value in institute_obj.values():
            row = row + "{0}\t".format(value)

        click.echo(row)
