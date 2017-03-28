import click

@click.command('cases', short_help='Fetch cases')
@click.option('-i', '--institute',
              help='institute id of related cases'
)
@click.option('-r', '--reruns',
              is_flag=True,
              help='requested to be rerun'
)
@click.option('-f', '--finished',
              is_flag=True,
              help='archived or solved'
)
@click.option('--causatives',
              is_flag=True,
              help='Has causative variants'
)
@click.option('--research-requested',
              is_flag=True,
              help='If research is requested'
)
@click.option('--is-research',
              is_flag=True,
              help='If case is in research mode'
)
@click.pass_context
def cases(context, institute, reruns, finished, causatives, research_requested,
          is_research):
    """Interact with cases existing in the database."""
    adapter = context.obj['adapter']

    models = adapter.cases(collaborator=institute, reruns=reruns,
                           finished=finished, has_causatives=causatives,
                           research_requested=research_requested,
                           is_research=is_research)
    if models.count() == 0:
        click.echo("No cases could be found")
    
    for model in models:
        click.echo(model['_id'])
