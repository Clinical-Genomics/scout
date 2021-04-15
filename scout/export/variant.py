# -*- coding: utf-8 -*-
import logging
import urllib.parse

LOG = logging.getLogger(__name__)

from scout.constants import CALLERS, CHROMOSOME_INTEGERS, CHROMOSOMES


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

    variant_ids = adapter.get_causatives(institute_id=collaborator, case_id=case_id)
    ##TODO add check so that same variant is not included more than once
    for document_id in variant_ids:

        variant_obj = adapter.variant(document_id)
        chrom = variant_obj["chromosome"]
        # Convert chromosome to integer for sorting
        chrom_int = CHROMOSOME_INTEGERS.get(chrom)
        if not chrom_int:
            LOG.info("Unknown chromosome %s", chrom)
            continue

        # Add chromosome and position to prepare for sorting
        variants.append((chrom_int, variant_obj["position"], variant_obj))

    # Sort varants based on position
    variants.sort(key=lambda x: (x[0], x[1]))

    for variant in variants:
        variant_obj = variant[2]
        yield variant_obj


def export_verified_variants(aggregate_variants, unique_callers):
    """Create the lines for an excel file with verified variants for
    an institute

    Args:
        aggregate_variants(list): a list of variants with aggregates case data
        unique_callers(set): a unique list of available callers

    Returns:
        document_lines(list): list of lines to include in the document
    """
    document_lines = []
    for variant in aggregate_variants:
        # get genotype and allele depth for each sample
        samples = []
        for sample in variant["samples"]:
            line = (
                []
            )  # line elements corespond to contants.variants_export.VERIFIED_VARIANTS_HEADER
            line.append(variant["institute"])
            line.append(variant["_id"])  # variant database ID
            line.append(variant["category"])
            line.append(variant["variant_type"])
            line.append(variant["display_name"][:30])  # variant display name
            # Build local link to variant:
            case_name = variant["case_obj"]["display_name"]  # case display name
            local_link = "/".join(["", variant["institute"], case_name, variant["_id"]])
            line.append(local_link)
            line.append(variant.get("validation"))
            line.append(case_name)
            case_individual = next(
                ind
                for ind in variant["case_obj"]["individuals"]
                if ind["individual_id"] == sample["sample_id"]
            )
            if case_individual["phenotype"] == 2:
                line.append(
                    " ".join([sample.get("display_name"), "(A)"])
                )  # label sample as affected
            else:
                line.append(sample.get("display_name"))
            line.append(
                "".join(["chr", variant["chromosome"], ":", str(variant["position"])])
            )  # position
            line.append(
                ">".join([variant.get("reference")[:10], variant.get("alternative")[:10]])
            )  # change
            genes = []
            prot_effect = []
            funct_anno = []
            for gene in variant.get("genes"):  # this will be a unique long field in the document
                genes.append(gene.get("hgnc_symbol", ""))
                funct_anno.append(gene.get("functional_annotation"))
                for transcript in gene.get("transcripts"):
                    if transcript.get("is_canonical") and transcript.get("protein_sequence_name"):
                        prot_effect.append(
                            urllib.parse.unquote(transcript.get("protein_sequence_name"))
                        )
            line.append(",".join(prot_effect))
            line.append(",".join(funct_anno))
            line.append(",".join(genes))
            line.append(variant.get("rank_score"))
            line.append(variant.get("cadd_score"))
            line.append(sample.get("genotype_call"))
            line.append(sample["allele_depths"][0])
            line.append(sample["allele_depths"][1])
            line.append(sample["genotype_quality"])

            # Set callers values. One cell per caller, leave blank if not applicable
            for caller in unique_callers:
                if variant.get(caller):
                    line.append(variant.get(caller))
                else:
                    line.append("-")
            document_lines.append(line)
    return document_lines


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
        position = variant.get("position")
        change = ">".join([variant.get("reference"), variant.get("alternative")])
        line.append(position)
        line.append(change)
        line.append(str(position) + change)
        genes = []
        prot_effect = []
        for gene in variant.get("genes", []):
            genes.append(gene.get("hgnc_symbol", ""))
            for transcript in gene.get("transcripts"):
                if transcript.get("is_canonical") and transcript.get("protein_sequence_name"):
                    prot_effect.append(
                        urllib.parse.unquote(transcript.get("protein_sequence_name"))
                    )
        line.append(",".join(genes))
        line.append(",".join(prot_effect))
        ref_ad = ""
        alt_ad = ""
        for sample in variant["samples"]:
            if sample.get("sample_id") == sample_id:
                ref_ad = sample["allele_depths"][0]
                alt_ad = sample["allele_depths"][1]
        line.append(ref_ad)
        line.append(alt_ad)
        if not alt_ad == 0:
            document_lines.append(line)
    return document_lines
