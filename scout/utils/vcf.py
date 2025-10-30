import re

from scout.constants.variant_tags import SV_TYPES


def validate_chrom(chrom: str, line: str) -> bool:
    if not chrom or not re.fullmatch(r"[\w.-]+", chrom):
        print(f"❌ Invalid CHROM field: {chrom!r}\n   Line: {line.strip()}")
        return False
    return True


def validate_pos(pos: str, line: str) -> bool:
    if not pos.isdigit() or int(pos) < 1:
        print(f"❌ Invalid POS: {pos}\n   Line: {line.strip()}")
        return False
    return True


def validate_ref(ref: str, line: str) -> bool:
    if not re.fullmatch(r"[ACGTN]+", ref):
        print(f"❌ Invalid REF: {ref}\n   Line: {line.strip()}")
        return False
    return True


def validate_alt(var_type: str, alt: str, line: str) -> bool:
    if var_type == "SVTYPE":
        if not alt.startswith("<") or not alt.endswith(">"):
            print(f"❌ Invalid SV ALT format: {alt}\n   Line: {line.strip()}")
            return False
        svtype = alt[1:-1].split(":", 1)[0]  # handle extended forms like INS:ME
        if svtype.lower() not in SV_TYPES:
            print(f"❌ Invalid SVTYPE in ALT: {svtype} (got {alt})\n   Line: {line.strip()}")
            return False
    else:
        if not re.fullmatch(r"[ACGTN,]+", alt):
            print(f"❌ Invalid SNV ALT: {alt}\n   Line: {line.strip()}")
            return False
    return True


def validate_qual(qual: str, line: str) -> bool:
    if qual != ".":
        try:
            float(qual)
        except ValueError:
            print(f"❌ Invalid QUAL: {qual}\n   Line: {line.strip()}")
            return False
    return True


def validate_filter(flt: str, line: str) -> bool:
    if flt != "." and not re.fullmatch(r"[A-Za-z0-9_;]+", flt):
        print(f"❌ Invalid FILTER: {flt}\n   Line: {line.strip()}")
        return False
    return True


def validate_info(info: str, line: str) -> bool:
    if info != ".":
        parts = info.split(";")
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                if not k or not v:
                    print(f"❌ Invalid INFO key=value pair: {p}\n   Line: {line.strip()}")
                    return False
            elif not p:
                print(f"❌ Empty INFO segment: {info}\n   Line: {line.strip()}")
                return False
    return True


def validate_vcf_line(var_type: str, line: str) -> bool:
    """
    Validate a single VCF line (SNV or SV) by delegating to smaller helper functions.
    """
    fields = line.strip().split("\t")
    if len(fields) < 8:
        print(f"❌ Less than 8 VCF fields.\n   Line: {line.strip()}")
        return False

    chrom, pos, _, ref, alt, qual, flt, info = fields[:8]

    return (
        validate_chrom(chrom, line)
        and validate_pos(pos, line)
        and validate_ref(ref, line)
        and validate_alt(var_type, alt, line)
        and validate_qual(qual, line)
        and validate_filter(flt, line)
        and validate_info(info, line)
    )
