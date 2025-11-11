import logging
import re

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
    Returns (is_valid, error_message)
    """
    if var_type != "SVTYPE":
        return validate_snv_alt(alt)

    svtype = extract_svtype(info)
    if svtype is None:
        return False, "Missing SVTYPE in INFO"

    if svtype == "BND":
        return validate_bnd_alt(alt)

    if is_symbolic_alt(alt):
        return validate_symbolic_alt(alt)

    if svtype in {"DEL", "INS", "DUP", "INV"}:
        return validate_ref_alt(alt, ref)

    return False, f"Invalid SV ALT for SVTYPE {svtype}: {alt}"


def validate_snv_alt(alt: str) -> tuple[bool, str | None]:
    if re.fullmatch(r"[ACGTN,]+", alt):
        return True, None
    return False, f"Invalid SNV ALT: {alt}"


def extract_svtype(info: str) -> str | None:
    match = re.search(r"SVTYPE=([^;]+)", info)
    return match.group(1).upper() if match else None


def validate_bnd_alt(alt: str) -> tuple[bool, str | None]:
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
    if alt == ref or (len(ref) > 1 and ref.startswith(alt)):
        return True, None
    return False, f"Invalid SV ALT for REF-based SV: {alt}"


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
