# -*- coding: utf-8 -*-
import logging
import urllib.parse
from typing import List, Optional

from scout.adapter.mongo.base import MongoAdapter
from scout.constants import CHROMOSOME_INTEGERS
from scout.constants.managed_variant import MANAGED_CATEGORIES, MANAGED_VARIANTS_INFILE_HEADER
from scout.models.managed_variant import ManagedVariant
from scout.utils.ensembl_rest_clients import EnsemblRestApiClient

LOG = logging.getLogger(__name__)


def export_causative_variants(
    adapter: MongoAdapter,
    collaborator: Optional[str] = None,
    document_id: Optional[str] = None,
    case_id: str = None,
    build: Optional[str] = None,
    category: Optional[str] = None,
) -> dict:
    """Export causative variants for a collaborator.

    A collaborator institute is required to narrow the export.
    Given a document_id, yields that particular document.

    Given a case id, narrows causatives search to that collaborator and case.

    Yields dict variant objects (scout.Models.Variant) sorted by chromosome and position.
    """

    # Store the variants in a list for sorting
    variants = []
    if document_id:
        yield adapter.variant(document_id)
        return

    variant_ids = adapter.get_causatives(institute_id=collaborator, case_id=case_id, build=build)

    for doc_id in variant_ids:
        variant_obj = adapter.variant(doc_id)
        if variant_obj is None:
            continue
        if category and variant_obj.get("category") not in category:
            continue
        variants.append(variant_obj)

    sorted_variants = _sort_variants_by_chromosome(variants)

    for variant in sorted_variants:
        yield variant


def _sort_variants_by_chromosome(variants: List[dict]) -> List[dict]:
    """Return a new list of managed variants sorted like Mongo sort(chromosome, position)."""

    def sort_key(var: dict):
        chrom = var.get("chromosome")
        chrom_int = CHROMOSOME_INTEGERS.get(chrom, float("inf"))
        pos = var.get("position", 0)
        return (chrom_int, pos)

    return sorted(variants, key=sort_key)

def liftover_managed_variants(managed_variants, liftover_from) -> List[str]:
    """Perform liftover over a list of managed variants and return a list of lines formatted as a managed variants upload infile."""

    valid_lines = [MANAGED_VARIANTS_INFILE_HEADER]
    ensembl_client = EnsemblRestApiClient()
    for variant_obj in managed_variants:
        if variant_obj["category"] not in ["snv", "cancer_snv"]:
            continue
        liftover_result = ensembl_client.liftover(build=liftover_from, chrom=variant_obj["chromosome"],
                                                  start=variant_obj["position"], end=variant_obj.get("end", ""))
        if not liftover_result:
            continue
        chrom = liftover_result[0]["mapped"]["seq_region_name"]
        pos = liftover_result[0]["mapped"]["start"]
        end = liftover_result[0]["mapped"]["end"]
        ref = variant_obj.get("reference", "")
        alt = variant_obj.get("alternative", "")
        category = variant_obj.get("category", "snv")
        sub_category = variant_obj.get("sub_category", "snv")
        build = "38" if liftover_from == "37" else "37"
        description = variant_obj.get("description")
        institutes = ",".join(variant_obj.get("institute"))

        valid_lines.append(
            f"{chrom};{pos};{end};{ref};{alt};"
            f"{category};{sub_category};{build};{description};;{institutes}"
        )
        return valid_lines


def export_managed_variants(
    adapter: MongoAdapter,
    institute: str = None,
    build: str = None,
    category: list = MANAGED_CATEGORIES,
) -> ManagedVariant:
    """Export managed variants, optionally for a given institute or variant category (["snv", "cancer_sv", ...])"""

    raw_managed = adapter.managed_variants(category=category, build=build, institute=institute)

    managed_variants = []
    for managed in raw_managed:
        managed_variants.append(
            ManagedVariant(
                chromosome=managed["chromosome"],
                position=managed["position"],
                end=managed["end"],
                reference=managed["reference"],
                alternative=managed["alternative"],
                institute=managed.get("institute"),
                maintainer=managed.get("maintainer", []),
                build=managed.get("build", "37"),
                date=managed.get("date"),
                category=managed.get("category", "snv"),
                sub_category=managed.get("sub_category", "snv"),
                description=managed.get("description"),
            )
        )

    yield from _sort_variants_by_chromosome(managed_variants)


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
            for gene in variant.get(
                "genes", []
            ):  # this will be a unique long field in the document
                genes.append(gene.get("hgnc_symbol", ""))
                if gene.get("functional_annotation"):
                    funct_anno.append(gene.get("functional_annotation"))
                for transcript in gene.get("transcripts", []):
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
        if alt_ad != 0:
            document_lines.append(line)
    return document_lines
