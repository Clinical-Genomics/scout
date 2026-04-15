import click

from scout.constants import BUILDS
from scout.constants.variant_tags import DNA_VARIANT_CATEGORIES

json_option = click.option("--json", is_flag=True, help="Output result in json format")

category_option = click.option(
    "--category",
    type=click.Choice(DNA_VARIANT_CATEGORIES, case_sensitive=False),
    multiple=True,
    default=DNA_VARIANT_CATEGORIES,
    show_default=True,
    help="One or more categories to include.",
)

collaborator_option = click.option(
    "-c",
    "--collaborator",
    help="Specify which collaborator to export variants from. Defaults to all variants",
)

build_option = click.option(
    "-b",
    "--build",
    default="37",
    type=click.Choice(BUILDS),
    show_default=True,
    help="Genome build version",
)
