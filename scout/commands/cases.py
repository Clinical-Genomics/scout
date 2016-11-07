# -*- coding: utf-8 -*-
import logging

import click

log = logging.getLogger(__name__)


@click.command()
@click.option('-i', '--institute')
@click.option('-r', '--reruns', is_flag=True)
@click.option('-f', '--finished', is_flag=True, help="archived or solved")
@click.pass_context
def cases(context, institute, reruns, finished):
    """Show information about cases."""
    adapter = context.obj['adapter']
    models = adapter.cases(institute, reruns=reruns, finished=finished)
    for model in models:
        click.echo(model.owner_case_id)
