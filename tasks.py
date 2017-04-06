# -*- coding: utf-8 -*-
from invoke import task
from invoke.util import log


@task
def docs(context):
    """Publish docs to the GitHub pages branch."""
    context.run("gitbook build docs/")
    context.run("git checkout gh-pages")
    context.run("cp -R docs/_book/* .")
    context.run("git add .")
    context.run("git commit -a -m 'Update docs'")
    context.run("git push origin gh-pages")
    context.run("git checkout master")
