import re

from scout.constants.variant_tags import SV_TYPES


def validate_chrom(chrom: str, line: str) -> tuple[bool, str | None]:
    if not chrom or not re.fullmatch(r"[\w.-]+", chrom):
        return False, f"Invalid CHROM field: {chrom!r}\n   Line: {line.strip()}"
    return True, None


def validate_pos(pos: str, line: str) -> tuple[bool, str | None]:
    if not pos.isdigit() or int(pos) < 1:
        return False, f"Invalid POS: {pos}\n   Line: {line.strip()}"
    return True, None


def validate_ref(ref: str, line: str) -> tuple[bool, str | None]:
    if not re.fullmatch(r"[ACGTN]+", ref):
        return False, f"Invalid REF: {ref}\n   Line: {line.strip()}"
    return True, None


def validate_alt(var_type: str, alt: str, line: str) -> tuple[bool, str | None]:
    """
    Validate the ALT field of a VCF line.

    Parameters:
        var_type (str): "TYPE" for SNVs, "SVTYPE" for structural variants
        alt (str): ALT field
        line (str): full VCF line for context in error messages

    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message)
    """

    if var_type == "SVTYPE":
        # Extract declared SVTYPE from INFO field
        declared_svtype = None
        info_fields = line.strip().split("\t")[7].split(";")
        for f in info_fields:
            if f.startswith("SVTYPE="):
                declared_svtype = f.split("=", 1)[1].upper()
                break

        # If no SVTYPE declared, fail
        if not declared_svtype:
            return False, f"Missing SVTYPE in INFO field\n   Line: {line.strip()}"

        # BND / breakends
        if declared_svtype == "BND":
            if "[" in alt or "]" in alt:
                return True, None
            else:
                return False, f"ALT does not match SVTYPE=BND: {alt}\n   Line: {line.strip()}"

        # Standard symbolic SVs
        if alt.startswith("<") and alt.endswith(">"):
            svtype_alt = alt[1:-1].split(":", 1)[0].upper()
            if svtype_alt.lower() not in SV_TYPES:
                return (
                    False,
                    f"Invalid SVTYPE in ALT: {svtype_alt} (got {alt})\n   Line: {line.strip()}",
                )
            return True, None

        # Anything else is invalid
        return False, f"Invalid SV ALT for SVTYPE {declared_svtype}: {alt}\n   Line: {line.strip()}"

    # SNVs / small variants
    else:
        if not re.fullmatch(r"[ACGTN,]+", alt):
            return False, f"Invalid SNV ALT: {alt}\n   Line: {line.strip()}"
        return True, None


def validate_qual(qual: str, line: str) -> tuple[bool, str | None]:
    if qual != ".":
        try:
            float(qual)
        except ValueError:
            return False, f"Invalid QUAL: {qual}\n   Line: {line.strip()}"
    return True, False


def validate_filter(flt: str, line: str) -> tuple[bool, str | None]:
    if flt != "." and not re.fullmatch(r"[A-Za-z0-9_;]+", flt):
        return False, f"Invalid FILTER: {flt}\n   Line: {line.strip()}"
    return True, None


def validate_info(var_type: str, info: str, line: str) -> bool:
    if info != ".":
        parts = info.split(";")
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                if not k or not v:
                    return False, f"Invalid INFO key=value pair: {p}\n   Line: {line.strip()}"
            elif not p:
                return False, f"Empty INFO segment: {info}\n   Line: {line.strip()}"

        if var_type == "SVTYPE" and "SVTYPE=" not in info:
            return False, f"SV line missing SVTYPE in INFO.\n   Line: {line.strip()}"

    return True, None


def validate_vcf_line(var_type: str, line: str) -> bool:
    """
    Validate a single VCF line (SNV or SV) by delegating to smaller helper functions.
    """
    fields = line.strip().split("\t")
    if len(fields) < 8:
        return False, f"Less than 8 VCF fields.\n   Line: {line.strip()}"

    chrom, pos, _, ref, alt, qual, flt, info = fields[:8]

    validators = [
        validate_chrom(chrom, line),
        validate_pos(pos, line),
        validate_ref(ref, line),
        validate_alt(var_type, alt, line),
        validate_qual(qual, line),
        validate_filter(flt, line),
        validate_info(var_type, info, line),
    ]

    for ok, msg in validators:
        if not ok:
            # Prefix with the line content for better context
            full_msg = f"❌ {msg}"
            # you can either print or return this message — depending on your use
            print(full_msg)
            return False, msg

    return True, None
