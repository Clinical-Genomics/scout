from typing import Dict, Iterable, List

from .drop import parse_omics_tsv

OMICS_CATEGORY_PARSER = {"tsv": parse_omics_tsv}


def parse_omics_file(omics_lines: Iterable[str], omics_file_type: dict) -> List[Dict[str, str]]:
    """Call appropriate parser for omics variants file, depending on the file format anticipated."""
    parser = OMICS_CATEGORY_PARSER[omics_file_type.get("format")]
    return parser(omics_lines)
