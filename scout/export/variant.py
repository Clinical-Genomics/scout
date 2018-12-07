# -*- coding: utf-8 -*-
import logging
import urllib.parse

LOG = logging.getLogger(__name__)

from scout.constants import (CHROMOSOMES, CHROMOSOME_INTEGERS)

def export_variants(adapter, collaborator, document_id=None, case_id=None):
    """Export causative variants for a collaborator

    Args:
        adapter(MongoAdapter)
        collaborator(str)
        document_id(str): Search for a specific variant
        case_id(str): Search causative variants for a case

    Yields:
        variant_obj(scout.Models.Variant): Variants marked as causative ordered by position.
    """

    # Store the variants in a list for sorting
    variants = []
    if document_id:
        yield adapter.variant(document_id)
        return

    variant_ids = adapter.get_causatives(
        institute_id=collaborator,
        case_id=case_id
        )
    ##TODO add check so that same variant is not included more than once
    for document_id in variant_ids:

        variant_obj = adapter.variant(document_id)
        chrom = variant_obj['chromosome']
        # Convert chromosome to integer for sorting
        chrom_int = CHROMOSOME_INTEGERS.get(chrom)
        if not chrom_int:
            LOG.info("Unknown chromosome %s", chrom)
            continue

        # Add chromosome and position to prepare for sorting
        variants.append((chrom_int, variant_obj['position'], variant_obj))

    # Sort varants based on position
    variants.sort(key=lambda x: (x[0], x[1]))

    for variant in variants:
        variant_obj = variant[2]
        yield variant_obj


def export_mt_variants(variants, sample_id):
    """Export mitochondrial variants for a case to create a MT excel report

    Args:
        variants(list): all MT variants for a case, sorted by position
        sample_id(str) : the id of a sample within the case

    Returns:
        document_lines(list): list of lines to include in the document
    """
    document_lines = []
    for variant in variants:
        line = []
        position = variant.get('position')
        change = '>'.join([variant.get('reference'),variant.get('alternative')])
        line.append(position)
        line.append(change)
        line.append(str(position)+change)
        genes = []
        prot_effect = []
        for gene in variant.get('genes'):
            genes.append(gene.get('hgnc_symbol',''))
            for transcript in gene.get('transcripts'):
                if transcript.get('is_canonical') and transcript.get('protein_sequence_name'):
                    prot_effect.append(urllib.parse.unquote(transcript.get('protein_sequence_name')))
        line.append(','.join(genes))
        line.append(','.join(prot_effect))
        ref_ad = ''
        alt_ad = ''
        for sample in variant['samples']:
            if sample.get('sample_id') == sample_id:
                ref_ad = sample['allele_depths'][0]
                alt_ad = sample['allele_depths'][1]
        line.append(ref_ad)
        line.append(alt_ad)
        document_lines.append(line)
    return document_lines
