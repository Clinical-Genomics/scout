from typing import Dict, Iterable, List


def parse_omics_tsv(lines: Iterable[str]) -> List[Dict[str, str]]:
    """Parse a DROP Outrider or Fraser TSV file."""
    omics_infos = []
    header = []

    for i, line in enumerate(lines):
        line = line.rstrip()
        if i == 0:
            # Header line
            header = line.split("\t")
            continue

        info = dict(zip(header, line.split("\t")))
        omics_infos.append(info)

    return omics_infos
