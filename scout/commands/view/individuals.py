import logging

import click
from flask.cli import with_appcontext

from scout.constants import PHENOTYPE_MAP, SEX_MAP
from scout.server.extensions import store

LOG = logging.getLogger(__name__)


@click.command("individuals", short_help="Display individuals")
@click.option("-i", "--institute", help="institute id of related cases")
@click.option("--causatives", is_flag=True, help="Has causative variants")
@click.option("-c", "--case-id")
@with_appcontext
def individuals(institute, causatives, case_id):
    """Show all individuals from all cases in the database"""
    LOG.info("Running scout view individuals")
    adapter = store
    individuals = []

    CASE_VIEW_INDIVIDUAL_PROJECTION = {
        "individuals": 1,
    }
    if case_id:
        case = adapter.case(case_id=case_id)
        if case:
            cases = [case]
        else:
            LOG.info("Could not find case %s", case_id)
            return
    else:
        cases = [
            case_obj
            for case_obj in adapter.cases(
                collaborator=institute,
                has_causatives=causatives,
                projection=CASE_VIEW_INDIVIDUAL_PROJECTION,
            )
        ]
        if len(cases) == 0:
            LOG.info("Could not find cases that match criteria")
            return
        individuals = (ind_obj for case_obj in cases for ind_obj in case_obj["individuals"])

    click.echo("#case_id\tind_id\tdisplay_name\tsex\tphenotype\tmother\tfather")

    for case in cases:
        for ind_obj in case["individuals"]:
            ind_info = [
                case["_id"],
                ind_obj["individual_id"],
                ind_obj["display_name"],
                SEX_MAP[int(ind_obj["sex"])],
                PHENOTYPE_MAP[ind_obj["phenotype"]],
                ind_obj["mother"],
                ind_obj["father"],
            ]
            click.echo("\t".join(ind_info))
