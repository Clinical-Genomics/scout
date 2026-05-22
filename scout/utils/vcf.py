import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import click
from flask import current_app

from scout.constants.variants_export import CONTIG_LENGTHS, VCF_HEADER

nucleotide_re = re.compile(r"[ACGTN,]+")

from scout.constants.variant_tags import SV_TYPES

LOG = logging.getLogger(__name__)


def validate_chrom(chrom: str) -> tuple[bool, str | None]:
    if not chrom or not re.fullmatch(r"[\w.-]+", chrom):
        return False, f"Invalid CHROM field: {chrom!r}"
    return True, None


def validate_pos(pos: str) -> tuple[bool, str | None]:
    if not pos.isdigit() or int(pos) < 1:
        return False, f"Invalid POS: {pos}"
    return True, None


def validate_ref(ref: str) -> tuple[bool, str | None]:
    if not re.fullmatch(r"[ACGTN]+", ref):
        return False, f"Invalid REF: {ref}"
    return True, None


def validate_alt(var_type: str, alt: str, ref: str, info: str) -> tuple[bool, str | None]:
    """
    Validate the ALT field for a VCF line.
     For SNVs and INDELS, this is mostly a matter of having valid nucleotides.

    Returns (is_valid, error_message)
    """
    status, msg = validate_ref_alt(alt, ref)
    if not status:
        return status, msg

    if var_type != "SVTYPE":
        return validate_snv_alt(alt)

    svtype = extract_svtype(info)
    if svtype is None:
        return False, "Missing SVTYPE in INFO"

    return validate_sv_alt(svtype, alt)


def validate_sv_alt(svtype: str, alt: str) -> tuple[bool, str | None]:
    """

    For BNDs, the format shall match the VCF standard.
    For other SVs,
        the ALT can either be symbolic, in which case a bracket notation "<DEL>" is required,
        or completely described with nucleotides, so same criteria as for SNVs. This is the default here.
    """
    if svtype == "BND":
        return validate_bnd_alt(alt)

    if svtype in {"CNV", "DEL", "DUP", "INS", "INV"} and is_symbolic_alt(alt):
        return validate_symbolic_alt(alt)

    return validate_snv_alt(alt)


def validate_snv_alt(alt: str) -> tuple[bool, str | None]:
    if re.fullmatch(nucleotide_re, alt):
        return True, None
    return False, f"Invalid ALT: {alt}"


def extract_svtype(info: str) -> str | None:
    match = re.search(r"SVTYPE=([^;]+)", info)
    return match.group(1).upper() if match else None


def validate_bnd_alt(alt: str) -> tuple[bool, str | None]:
    """BND fields shall have either [ or ] chars, in addition to contig coordinates and the ref char replacement, and
    any extra nucleotides."""
    if not re.fullmatch(r"[\w\[\]:.-]+", alt):
        return False, f"Invalid char in BND ALT: {alt}"
    if "[" in alt or "]" in alt:
        return True, None
    return False, f"Invalid BND ALT: {alt}"


def is_symbolic_alt(alt: str) -> bool:
    return alt.startswith("<") and alt.endswith(">")


def validate_symbolic_alt(alt: str) -> tuple[bool, str | None]:
    base_type = alt[1:-1].split(":", 1)[0].lower()
    if base_type in SV_TYPES:
        return True, None
    return False, f"Invalid SVTYPE in ALT: {base_type} (got {alt})"


def validate_ref_alt(alt: str, ref: str) -> tuple[bool, str | None]:
    """
    Validate the REF and ALT fields of a VCF record for basic consistency and normalization.

      - Flags identical REF and ALT alleles (except when REF == 'N')
      - Flags variants that appear non-normalized, i.e. containing redundant nucleotides on the 3' (right) or 5' (left) side
        Examples:
            REF=A, ALT=A           → invalid unless REF is 'N'
            REF=GGTT, ALT=TT       → 3-prime-trimmable deletion
            REF=TTAA, ALT=TT       → 5-prime-trimmable variant
            REF=TT, ALT=TTAAGG     → 3-prime-trimmable insertion

        Reference: https://genome.sph.umich.edu/wiki/Variant_Normalization
    """

    if alt == ref and ref != "N":
        return False, f"Invalid (identical) ref and alt: {alt}"

    if len(ref) > 1 and len(alt) > 1 and (ref.endswith(alt) or alt.endswith(ref)):
        return (
            False,
            "The variant is not normalised - it has extra nucleotides on the right (3-prime) side",
        )

    if len(ref) > 1 and len(alt) > 1 and (ref.startswith(alt) or alt.startswith(ref)):
        return (
            False,
            "The variant is not normalised - it has extra nucleotides on the left (5-prime) side",
        )

    return True, None


def validate_qual(qual: str) -> tuple[bool, str | None]:
    if qual != ".":
        try:
            float(qual)
        except ValueError:
            return False, f"Invalid QUAL: {qual}"
    return True, False


def validate_filter(flt: str) -> tuple[bool, str | None]:
    if flt != "." and not re.fullmatch(r"[A-Za-z0-9_;]+", flt):
        return False, f"Invalid FILTER: {flt}"
    return True, None


def validate_info(var_type: str, info: str) -> tuple[bool, str | None]:
    if info != ".":
        parts = info.split(";")
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                if not k or not v:
                    return False, f"Invalid INFO key=value pair: {p}"
            elif not p:
                return False, f"Empty INFO segment: {info}"

        if var_type == "SVTYPE" and "SVTYPE=" not in info:
            return False, "SV line missing SVTYPE in INFO."

    return True, None


def validate_vcf_line(var_type: str, line: str) -> tuple[bool, str | None]:
    """
    Validate a single VCF line (SNV or SV) by delegating to smaller helper functions.
    """
    fields = line.strip().split("\t")
    if len(fields) < 8:
        return False, f"❌ Less than 8 VCF fields.\n   Line: {line.strip()}"

    chrom, pos, _, ref, alt, qual, flt, info = fields[:8]

    validators = [
        validate_chrom(chrom),
        validate_pos(pos),
        validate_ref(ref),
        validate_alt(var_type, alt, ref, info),
        validate_qual(qual),
        validate_filter(flt),
        validate_info(var_type, info),
    ]

    for ok, msg in validators:
        if not ok:
            full_msg = f"❌ {msg}\n   Line: {line.strip()}"
            LOG.error(full_msg)
            return False, msg

    return True, None


def normalize_chrom(chrom: str, build: str) -> str:
    """
    Normalize chromosome names depending on genome build.

    Rules:
      - build "37":
            no 'chr' prefix
            mitochondrial chromosome = MT

      - build "38":
            no 'chr' prefix
            mitochondrial chromosome = M

      - build "GRCh38":
            'chr' prefix
            mitochondrial chromosome = chrM
    """
    if chrom in {"M", "MT"}:
        if build == "37":
            return "MT"
        elif build == "38":
            return "M"
        elif build == "GRCh38":
            return "chrM"

    if build == "GRCh38":
        return f"chr{chrom}"

    return chrom


def build_vcf_header(
    build: str,
    contains_date: bool = False,
    argv: Optional[List[str]] = None,
    source: Optional[str] = None,
) -> List[str]:
    """Create the VCF header used when exporting variants from the CLI."""

    lengths_build = "37" if build == "37" else "38"
    vcf_header = VCF_HEADER

    add_line = 2
    if contains_date:
        vcf_header.insert(add_line, "##fileDate={}".format(datetime.now()))
        add_line += 1

    if argv:
        vcf_header.insert(add_line, "##commandline={}".format(" ".join(argv)))
        add_line += 1

    if source:
        vcf_header.insert(add_line, "##source={}".format(source))

    for chrom, length in CONTIG_LENGTHS[lengths_build].items():
        chrom_name = normalize_chrom(chrom, build)

        vcf_header.append(f"##contig=<ID={chrom_name},length={length}>")

    vcf_header.append("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO")

    return vcf_header


def print_vcf(
    variants: Iterable[Dict[str, Any]],
    build: str,
    export_category: str,
    case_obj: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Print variants in VCF format.

    If a case_id is provided, the VCF header is extended with FORMAT
    and per-individual genotype columns.
    """

    argv = [Path(sys.argv[0]).name] + sys.argv[1:]
    header = build_vcf_header(
        build=build, contains_date=True, argv=argv, source=current_app.config["MONGO_DBNAME"]
    )

    if case_obj:
        header[-1] += "\tFORMAT"
        for ind in case_obj["individuals"]:
            header[-1] += "\t" + ind["individual_id"]

    for line in header:
        click.echo(line)

    for variant_obj in variants:
        if variant_string := get_vcf_entry(
            variant_obj,
            case_id=case_obj["_id"] if case_obj else None,
            build=build,
            info_tags={"EXPORT_CATEGORY": export_category},
        ):
            click.echo(variant_string)


def get_vcf_entry(
    variant_obj: dict, case_id: str = None, build: str = "37", info_tags: Optional[dict] = None
) -> str | None:
    """
    Get vcf entry from variant object

    Add any additional INFO tags in a dict info_tags.
    """

    pos = variant_obj["position"]
    end = variant_obj.get("end") or pos
    category = variant_obj["category"]
    subcat = variant_obj["sub_category"].upper()
    var_type = "TYPE" if category in ["snv", "cancer"] else "SVTYPE"

    # Build INFO field
    if category in ["snv", "cancer"] and not variant_obj.get("end"):
        info_field = f"{var_type}={subcat}"
    else:
        info_field = f"END={end};{var_type}={subcat}"

    for key, value in info_tags.items() if info_tags else {}:
        info_field += f";{key}={value}"

    ref = variant_obj.get("reference") or "N"
    if ref == ".":
        ref = "N"

    alt = variant_obj.get("alternative") or "N"
    if alt in [".", "-", variant_obj["sub_category"]]:
        alt = f"<{subcat}>" if category == "sv" else "N"

    chrom = variant_obj["chromosome"]
    if build == "GRCh38":
        chrom = variant_obj["chromosome"]
        if chrom == "MT":
            chrom = "M"
        chrom = "".join(["chr", chrom])

    filters = ";".join(variant_obj.get("filters", [])) or "."
    vcf_fields = [
        chrom,
        str(pos),
        variant_obj.get("dbsnp_id", ".") or ".",
        ref,
        alt,
        str(variant_obj.get("quality", ".") or "."),
        filters,
        info_field,
    ]

    if case_id and variant_obj.get("samples"):
        vcf_fields.append("GT")
        vcf_fields.extend(sample["genotype_call"] for sample in variant_obj["samples"])

    variant_string = "\t".join(vcf_fields)

    if validate_vcf_line(var_type=var_type, line=variant_string)[0]:
        return variant_string
