# -*- coding: utf-8 -*-
import csv


def parse_panel(csv_stream):
    """Parse user submitted panel."""
    reader = csv.DictReader(csv_stream, delimiter=';', quoting=csv.QUOTE_NONE)
    genes = []
    for gene_row in reader:
        if not gene_row['HGNC_IDnumber'].strip().isdigit():
            continue
        transcripts_raw = gene_row.get('Disease_associated_transcript')
        if transcripts_raw:
            transcripts_list = [tx.split(':', 1)[-1].strip() for tx in transcripts_raw.split(',')]
        else:
            transcripts_list = []

        models_raw = gene_row.get('Genetic_disease_model')
        models_list = [model.strip() for model in models_raw.split(',')] if models_raw else []
        panel_gene = dict(
            symbol=gene_row['HGNC_symbol'].strip() if gene_row.get('HGNC_symbol') else None,
            hgnc_id=int(gene_row['HGNC_IDnumber'].strip()),
            disease_associated_transcripts=transcripts_list,
            reduced_penetrance=True if gene_row.get('Reduced_penetrance') else None,
            mosaicism=True if gene_row.get('Mosaicism') else None,
            inheritance_models=models_list,
            database_entry_version=gene_row.get('Database_entry_version'),
        )
        genes.append(panel_gene)

    return genes
