from flask import Response
from pymongo.cursor import CursorType
from werkzeug.datastructures import Headers

from scout.adapter import MongoAdapter
from scout.constants import EXPORTED_VARIANTS_LIMIT
from scout.server.blueprints.variant.utils import update_variant_case_panels
from scout.server.blueprints.variants.utils import update_case_panels
from scout.server.utils import case_has_alignments, case_has_mt_alignments, case_has_rna_tracks


def outliers(
    store: MongoAdapter,
    institute_obj: dict,
    case_obj: dict,
    omics_variants_query: CursorType,
    variant_count: int,
    page: int = 1,
    per_page: int = 50,
):
    """Pre-process list of outlier omics variants."""
    skip_count = per_page * max(page - 1, 0)

    more_variants = variant_count > (skip_count + per_page)
    variants = []

    update_case_panels(store, case_obj)

    case_has_alignments(case_obj)
    case_has_mt_alignments(case_obj)
    case_has_rna_tracks(case_obj)

    for variant_obj in omics_variants_query.skip(skip_count).limit(per_page):
        parsed_variant = decorate_omics_variant(
            store,
            institute_obj,
            case_obj,
            variant_obj,
        )

        variants.append(parsed_variant)

    return {"variants": variants, "more_variants": more_variants}


def decorate_omics_variant(
    store: MongoAdapter, institute_obj: dict, case_obj: dict, omics_variant_obj: dict
):
    """Decorate each variant with a limited selection of variant obj level information for display on variantS page."""

    omics_variant_obj["comments"] = store.events(
        institute_obj,
        case=case_obj,
        variant_id=omics_variant_obj["omics_variant_id"],
        comments=True,
    )

    update_variant_case_panels(case_obj, omics_variant_obj)

    return omics_variant_obj


def download_omics_variants(case_obj: dict, variant_objs: CursorType):
    """Download omics variants in a csv file."""

    def generate(header, lines):
        yield header + "\n"
        for line in lines:
            yield line + "\n"

    DOCUMENT_HEADER = [
        "Gene",
        "Gene annotation",
        "Category",
        "Sub-category",
        "Potential impact",
        "Delta PSI",
        "L2FC",
        "P-value",
        "Fold-change",
        "Samples/Individuals",
        "Position",
    ]

    export_lines = []
    for variant in variant_objs.limit(EXPORTED_VARIANTS_LIMIT):
        variant_genes: str = (
            f'"{", ".join(variant.get("hgnc_symbols", variant.get("hgnc_ids", variant.get("gene_name_orig"))))}"'
        )
        gene_anno = variant["gene_type"]
        category = variant["category"]
        sub_category = variant["sub_category"]

        if sub_category == "splicing":
            delta_psi = variant["delta_psi"]
            l2fc = "N/A"
            potential_impact = f"{variant['potential_impact']} - fs {variant['causes_frameshift']}"
            fold_change = "N/A"
        else:
            delta_psi = "N/A"
            l2fc = variant["l2fc"]
            potential_impact = "N/A"
            fold_change = variant["fold_change"]
        p_value = "%.3e" % variant["p_value"]
        samples = f'"{", ".join([sample["display_name"] for sample in variant.get("samples")])}"'
        position = f"{variant['chromosome']}:{variant['position']}-{variant['end']}"

        variant_line = f"{variant_genes},{gene_anno},{category},{sub_category},{potential_impact},{delta_psi},{l2fc},{p_value},{fold_change},{samples},{position}"
        export_lines.append(variant_line)

    headers = Headers()
    headers.add(
        "Content-Disposition",
        "attachment",
        filename=str(case_obj["display_name"]) + "-filtered-omics_variants.csv",
    )
    # return a csv with the exported variants
    return Response(
        generate(",".join(DOCUMENT_HEADER), export_lines),
        mimetype="text/csv",
        headers=headers,
    )
