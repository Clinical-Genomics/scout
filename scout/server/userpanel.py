# -*- coding: utf-8 -*-
import csv
import datetime


def parse_panel(csv_stream):
    """Parse user submitted panel."""
    reader = csv.DictReader(csv_stream, delimiter=';', quoting=csv.QUOTE_NONE)
    genes = []
    for gene_row in reader:
        transcripts_raw = gene_row.get('Disease_associated_transcript')
        if transcripts_raw:
            transcripts_list = [tx.split(':', 1)[-1].strip() for tx in transcripts_raw.split(',')]
        else:
            transcripts_list = []

        models_raw = gene_row.get('Genetic_disease_model')
        models_list = [model.strip() for model in models_raw.split(',')] if models_raw else []

        panel_gene = dict(
            symbol=gene_row['HGNC_symbol'].strip() if gene_row.get('HGNC_symbol') else None,
            hgnc_id=(int(gene_row['HGNC_IDnumber'].strip()) if gene_row.get('HGNC_IDnumber')
                     else None),
            disease_associated_transcripts=transcripts_list,
            reduced_penetrance=True if gene_row.get('Reduced_penetrance') else None,
            mosaicism=True if gene_row.get('Mosaicism') else None,
            inheritance_models=models_list,
        )
        genes.append(panel_gene)

    return genes


def build_panel(adapter, institute_id, panel_name, display_name, version, panel_genes):
    """Build a new (updated) gene panel."""
    for panel_gene in panel_genes:
        gene_id = panel_gene['hgnc_id'] or panel_gene['symbol']
        hgnc_gene = adapter.hgnc_gene(gene_id)
        if hgnc_gene is None:
            raise ValueError("can't find gene: {}".format(gene_id))
        if panel_gene['symbol'] and (panel_gene['symbol'] != hgnc_gene['hgnc_symbol']):
            raise ValueError("HGNC symbol not matching: {} vs. {}"
                             .format(panel_gene['symbol'], hgnc_gene['hgnc_symbol']))
        panel_gene['symbol'] = hgnc_gene['hgnc_symbol']
        panel_gene['hgnc_id'] = hgnc_gene['hgnc_id']

    gene_panel = dict(
        institute=institute_id,
        panel_name=panel_name,
        display_name=display_name,
        version=version,
        genes=panel_genes,
        date=datetime.datetime.now(),
    )
    return gene_panel
