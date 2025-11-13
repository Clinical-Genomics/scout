import logging
import re

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
            REF=A, ALT=A → invalid unless N
            REF=GGTT, ALT=TT → 3-prime-trimmable deletion
            REF=TTAA, ALT=TT → 5-prime-trimmable variant
    """

    if alt == ref and ref != "N":
        return False, f"Invalid (identical) ref and alt: {alt}"

    if len(ref) > 1 and len(alt) > 1 and ref.endswith(alt):
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
