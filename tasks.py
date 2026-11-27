# -*- coding: utf-8 -*-
from invoke import task
from invoke.util import log


@task
def docs(context):
    """Build the documentation site."""
    context.run("zensical build")


@task
def deploy(context):
    """Deploy recent updated to AWS demo instance."""
    context.run("./scripts/deploy")
