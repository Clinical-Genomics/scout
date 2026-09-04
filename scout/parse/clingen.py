import logging
import re
from typing import Dict, Iterable, List, Tuple

LOG = logging.getLogger(__name__)

CLINGEN_DOSAGE_HEADER_HGNC_MAP = [
    "symbol",
    "hgnc_id",
    "build_37_coordinates",
    "build_38_coordinates",
    "haploinsufficiency",
    "triplosensitivity",
    "online_report",
    "date",
]

CLINGEN_DOSAGE_HEADER_ISCA_MAP = [
    "display_name",
    "isca_id",
    "build_37_coordinates",
    "build_38_coordinates",
    "haploinsufficiency",
    "triplosensitivity",
    "online_report",
    "date",
]

FIELD_RE = re.compile(r"""\s*("(?:""|[^"])*"|(?!$)[^,]*)\s*(?:,|$)""")


def parse_clingen_dosage_line(line: str, data_line: List[str]):
    """Parse a line from the ClinGen dosage sensitivity file into individual cells.
    Note that cells can have commas inside quotes, so we need to handle that."""
    for match in FIELD_RE.finditer(line):
        cell = match.group(1)

        if not cell:
            data_line.append(cell)
            continue

        if (cell.startswith('"') and not cell.endswith('"')) or (
            cell.endswith('"') and not cell.startswith('"')
        ):
            LOG.warning(f"Cell '{cell}' does not both start and end with a quote")
            data_line.append(cell)
            continue

        cell = cell[1:-1].replace('""', '"')
        data_line.append(cell)


def parse_clingen_dosage_csv(
    lines: Iterable[str],
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """Parse a ClinGen dosage sensitivity file.

    "CLINGEN DOSAGE SENSITIVITY CURATIONS (FULL)","","","","","","",""
    "FILE CREATED: 2026-08-25","","","","","","",""
    "WEBPAGE: https://search.clinicalgenome.org/kb/gene-dosage","","","","","","",""
    "+++++++++++","+++++++++","++++++","++++++","++++++++++++++++++","+++++++++++++++++","+++++++++++++","++++"
    "GENE/REGION","HGNC/ISCA","GRCh37","GRCh38","HAPLOINSUFFICIENCY","TRIPLOSENSITIVITY","ONLINE REPORT","DATE"
    "+++++++++++","+++++++++","++++++","++++++","++++++++++++++++++","+++++++++++++++++","+++++++++++++","++++"
    "A4GALT","HGNC:18149","chr22:43088127-43117307","chr22:42692121-42721301","Gene Associated with Autosomal Recessive Phenotype","No Evidence for Triplosensitivity","https://search.clinicalgenome.org/kb/gene-dosage/HGNC:18149","2014-12-11T15:51:23+00:00"
    ...
    "SOX9 upstream enhancer region","ISCA-46303","chr17:67892996-69792434","chr17:69896855 -71796293","Sufficient Evidence for Haploinsufficiency","Little Evidence for Triplosensitivity","https://search.clinicalgenome.org/kb/gene-dosage/region/ISCA-46303","2021-06-07T12:53:51-04:00"
    ...

    Line 7 and above contain data. The id in the second column determines if the line is a gene or a region.
    """
    gene_dosage_infos = []
    isca_region_infos = []

    for i, line in enumerate(lines):
        if i > 6:
            line = line.rstrip()
            data_line = []

            if not line:
                continue

            parse_clingen_dosage_line(line, data_line)

            if data_line[1].startswith("HGNC:"):
                info = dict(zip(CLINGEN_DOSAGE_HEADER_HGNC_MAP, data_line))
                gene_dosage_infos.append(info)

            if data_line[1].startswith("ISCA-"):
                info = dict(zip(CLINGEN_DOSAGE_HEADER_ISCA_MAP, data_line))
                isca_region_infos.append(info)

    return gene_dosage_infos, isca_region_infos
