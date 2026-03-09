import click

from scout.commands.delete.case import case as case_cmd
from scout.commands.delete.genes import exons as exons_cmd
from scout.commands.delete.genes import genes as genes_cmd
from scout.commands.delete.index import index as index_cmd
from scout.commands.delete.panel import panel as panel_cmd
from scout.commands.delete.rna import rna as rna_cmd
from scout.commands.delete.user import user as user_cmd
from scout.commands.delete.variants import variants as variants_cmd


@click.group()
def delete():
    """
    Delete objects from the database.
    """


delete.add_command(panel_cmd)
delete.add_command(genes_cmd)
delete.add_command(case_cmd)
delete.add_command(user_cmd)
delete.add_command(index_cmd)
delete.add_command(exons_cmd)
delete.add_command(rna_cmd)
delete.add_command(variants_cmd)
