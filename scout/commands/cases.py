# -*- coding: utf-8 -*-
import logging

import click

log = logging.getLogger(__name__)


@click.command()
@click.option('-i', '--institute')
@click.option('-r', '--reruns', is_flag=True)
@click.pass_context
def cases(context, institute, reruns):
    """Show information about cases."""
    adapter = context.obj['adapter']
    models = adapter.cases(institute, reruns=reruns)
    for model in models:
        click.echo(model.owner_case_id)
