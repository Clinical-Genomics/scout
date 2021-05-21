#!/usr/bin/env python
# encoding: utf-8
import logging

import click

from .case import case as case_command
from .cytoband import cytoband as cytoband_command
from .exons import exons as exons_command
from .institute import institute as institute_command
from .panel import panel as panel_command
from .region import region as region_command
from .report import cnv_report as cnv_report_command
from .report import coverage_qc_report as coverage_qc_report_command
from .report import delivery_report as delivery_report_command
from .report import gene_fusion_report as gene_fusion_report_command
from .research import research as research_command
from .user import user as user_command
from .variants import variants as variants_command

LOG = logging.getLogger(__name__)


@click.group()
def load():
    """Load items into the scout database."""
    pass


load.add_command(case_command)
load.add_command(cytoband_command)
load.add_command(institute_command)
load.add_command(region_command)
load.add_command(panel_command)
load.add_command(user_command)
load.add_command(research_command)
load.add_command(variants_command)
load.add_command(delivery_report_command)
load.add_command(cnv_report_command)
load.add_command(coverage_qc_report_command)
load.add_command(gene_fusion_report_command)
load.add_command(exons_command)
