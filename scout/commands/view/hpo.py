import logging
import click

from pprint import pprint as pp
from operator import itemgetter

LOG = logging.getLogger(__name__)


@click.command('hpo', short_help='Display all hpo terms')
@click.option('--term', '-t', help='Search for a single hpo term')
@click.option('--description', '-d', help='Search for hpo terms with a description')
@click.pass_context
def hpo(context, term, description):
    """Show all hpo terms in the database"""
    LOG.info("Running scout view hpo")
    adapter = context.obj['adapter']
    if term:
        term = term.upper()
        if not term.startswith('HP:'):
            while len(term) < 7:
                term = '0' + term
            term = 'HP:' + term
        LOG.info("Searching for term %s", term)
        hpo_terms = adapter.hpo_terms(hpo_term=term)
    elif description:
        sorted_terms = sorted(adapter.hpo_terms(query=description), key=itemgetter('hpo_number'))
        for term in sorted_terms:
            term.pop('genes')
            print("name: {} | {} | {}".format(term['_id'], term['description'], term['hpo_number']))
        # pp(hpo_terms)
        context.abort()
    else:
        hpo_terms = adapter.hpo_terms()
    if hpo_terms.count() == 0:
        LOG.warning("No matching terms found")
        return

    click.echo("hpo_id\tdescription\tnr_genes")
    for hpo_obj in hpo_terms:
        click.echo("{0}\t{1}\t{2}".format(
            hpo_obj['hpo_id'],
            hpo_obj['description'],
            len(hpo_obj.get('genes',[]))
        ))
