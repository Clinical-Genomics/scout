# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import url_for


def genecov_links(individuals, genes=None):
    """Return links for coverage for all samples in a case."""
    # map internal + external sample ids
    kwargs = {"alt_{}".format(sample.individual_id): sample.display_name
              for sample in individuals}
    kwargs['sample_id'] = [sample.individual_id for sample in individuals]
    kwargs['link'] = 'core.pileup_range'
    if genes:
        gene_ids = (gene.common.hgnc_symbol for gene in genes)
        coverage_links = {gene_id: url_for('report.gene', gene_id=gene_id,
                                           **kwargs)
                          for gene_id in gene_ids}
        return coverage_links
    else:
        return kwargs
