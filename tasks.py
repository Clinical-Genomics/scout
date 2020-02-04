# -*- coding: utf-8 -*-
from invoke import task
from invoke.util import log


@task
def docs(context):
    """Publish docs to the GitHub pages branch."""
    context.run("mkdocs gh-deploy")


@task
def deploy(context):
    """Deploy recent updated to AWS demo instance."""
    context.run("./scripts/deploy")
