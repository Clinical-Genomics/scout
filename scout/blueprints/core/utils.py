# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import url_for


def genecov_links(individuals, genes=None):
    """Return links for coverage for all samples in a case."""
    # map internal + external sample ids
    kwargs = {}
    kwargs['sample_id'] = [sample.individual_id for sample in individuals]
    kwargs['link'] = 'core.pileup_range'
    if genes:
        coverage_links = {}
        for gene in genes:
            gene_id = (gene.common.hgnc_symbol if gene.common else
                       "HGNC:{}".format(gene.hgnc_id))
        coverage_links[gene_id] = url_for('report.gene', gene_id=gene.hgnc_id,
                                          **kwargs)
        return coverage_links
    else:
        return kwargs
