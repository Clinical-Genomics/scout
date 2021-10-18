import logging
from pprint import pprint as pp

import click
from flask.cli import with_appcontext

from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("cases", short_help="Display cases")
@click.option("-i", "--institute", help="Which institute to show cases from")
@click.option("-d", "--display-name", help="Search with display name")
@click.option("-c", "--case-id", help="Search for a specific case")
@click.option("--nr-variants", is_flag=True, help="Show number of clinical and research variants")
@click.option(
    "--similar",
    is_flag=True,
    help="Show the cases that are phenotypic similar to a given case",
)
@click.option(
    "--variants-treshold",
    default=0,
    help="Only show cases with more variants than treshold",
)
@with_appcontext
def cases(institute, display_name, case_id, nr_variants, variants_treshold, similar):
    """Display cases from the database"""
    LOG.info("Running scout view institutes")
    adapter = store
    name_query = None

    models = []
    if case_id:
        case_obj = adapter.case(case_id=case_id)
        if case_obj:
            models.append(case_obj)
        if similar:
            hpo_terms = []
            for term in case_obj.get("phenotype_terms", []):
                hpo_terms.append(term.get("phenotype_id"))

            similar = adapter.cases_by_phenotype(hpo_terms, case_obj["owner"], case_obj["_id"])
            if not similar:
                LOG.info("No more cases with phenotypes found")
                return
            click.echo("#case_id\tscore")
            for i in similar:
                click.echo("\t".join([i[0], str(i[1])]))
            return

    else:
        if display_name:
            name_query = f"case:{display_name}"
        models = adapter.cases(collaborator=institute, name_query=name_query)
        models = [case_obj for case_obj in models]

    if not models:
        LOG.info("No cases could be found")
        return

    header = ["case_id", "display_name", "institute"]

    if variants_treshold:
        LOG.info("Only show cases with more than %s variants", variants_treshold)
        nr_variants = True

    if nr_variants:
        LOG.info("Displaying number of variants for each case")
        header.append("clinical")
        header.append("research")

    click.echo("#" + "\t".join(header))
    for model in models:
        output_str = "{:<12}\t{:<12}\t{:<12}"
        output_values = [model["_id"], model["display_name"], model["owner"]]
        if nr_variants:
            output_str += "\t{:<12}\t{:<12}"
            nr_clinical = 0
            nr_research = 0
            variants = adapter.variant_collection.find({"case_id": model["_id"]})
            i = 0
            for i, var in enumerate(variants, 1):
                if var["variant_type"] == "clinical":
                    nr_clinical += 1
                else:
                    nr_research += 1
            output_values.extend([nr_clinical, nr_research])

            if variants_treshold and i < variants_treshold:
                LOG.debug("Case %s had to few variants, skipping", model["_id"])
                continue

        click.echo(output_str.format(*output_values))
