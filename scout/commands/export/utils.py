import click

from scout.constants import BUILDS

json_option = click.option("--json", is_flag=True, help="Output result in json format")

build_option = click.option(
    "-b",
    "--build",
    default="37",
    type=click.Choice(BUILDS),
    show_default=True,
    help="Genome build version",
)
