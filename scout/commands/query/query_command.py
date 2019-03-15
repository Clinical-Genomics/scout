


@click.group()
@click.pass_context
def query(context):
    """
    View objects from the database.
    """
    pass

query.add_command(hgnc)
