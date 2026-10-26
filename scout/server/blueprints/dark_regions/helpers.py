from typing import List, Set

from scout.constants import PHENOTYPE_MAP
from scout.constants.case_tags import PARAPHRASE_STATUS
from scout.server.extensions import store

SMN_HGNC_IDS = {11117, 11118}


def _parse_phase_region(region: List[str]) -> dict:
    """Parse a list like ['chr6:32013300-32046200'] into chrom/start/end."""
    region_str = region[0]
    chrom_str, coords_str = region_str.split(":")
    start_str, end_str = coords_str.split("-")
    return {
        "chrom": chrom_str.lstrip("chr"),
        "start": int(start_str),
        "end": int(end_str),
    }


def _populate_hgnc_genes_in_region(ind_region: str) -> List[dict]:
    """Turn region genes_in_region string into a list of HGNC gene objects."""
    genes = []
    for symbol in ind_region.split(","):
        symbol = symbol.strip()
        if not symbol:
            continue
        if gene := store.hgnc_gene(symbol):
            genes.append(gene)
    return genes


def _individual_is_affected(individual: dict) -> bool:
    return PHENOTYPE_MAP[individual.get("phenotype", 0)] == "affected"


def _update_region_status(
    case_region: dict, individual_is_affected: bool, ind_status: str, status_matches: list | None
):
    """Update aggregate region status based on an affected individual's region status."""
    if not individual_is_affected:
        return

    if (
        "status" not in case_region
        or PARAPHRASE_STATUS[ind_status] > PARAPHRASE_STATUS[case_region["status"]]
    ):
        case_region["status"] = ind_status
        if status_matches:
            case_region["status_matches"] = status_matches


def _update_case_region(case_region: dict, region: dict, individual_is_affected: bool):
    """Update case-level region data from one individual's paraphrase region entry."""
    for region_key, ind_region in region.items():
        match region_key:
            case "genes_in_region":
                if "genes_in_region" in case_region:
                    continue
                case_region["genes_in_region"] = _populate_hgnc_genes_in_region(ind_region)
            case "phase_region":
                if "phase_region" in case_region:
                    continue
                case_region["phase_region"] = _parse_phase_region(ind_region)
            case "status":
                _update_region_status(
                    case_region,
                    individual_is_affected,
                    ind_status=ind_region,
                    status_matches=region.get("status_matches"),
                )


def _get_paraphrase_regions(case_obj: dict, panel_hgnc_ids: Set[int] | None = None) -> dict:
    """Collect case-level paraphrase regions and optionally filter by HGNC IDs."""
    case_regions = {}

    for individual in case_obj["individuals"]:
        paraphrase = individual.get("paraphrase")
        individual_is_affected = _individual_is_affected(individual)

        if not paraphrase:
            continue
        for region_name, region in paraphrase.items():
            case_region = case_regions.setdefault(region_name, {})
            _update_case_region(case_region, region, individual_is_affected)

    if not panel_hgnc_ids:
        return case_regions

    filtered_regions = {}
    for region_name, region in case_regions.items():
        region_genes = region.get("genes_in_region", [])
        if not region_genes:
            continue

        matched_genes = [
            gene
            for gene in region_genes
            if gene.get("hgnc_id") is not None and gene["hgnc_id"] in panel_hgnc_ids
        ]
        if not matched_genes:
            continue

        region["genes_in_region"] = matched_genes
        filtered_regions[region_name] = region

    return filtered_regions
