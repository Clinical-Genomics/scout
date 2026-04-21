"""Template filters for Scout Flask application."""

import re
from typing import Dict, List, Optional, Union
from urllib.parse import parse_qsl, unquote, urlsplit

from markdown import markdown as python_markdown
from markupsafe import Markup
from pymongo.cursor import Cursor

from scout.constants import (
    REVEL_SCORE_LABEL_COLOR_MAP,
    SPIDEX_HUMAN,
    SPLICEAI_SCORE_LABEL_COLOR_MAP,
)


def human_longint(value: Union[int, str]) -> str:
    """Convert a long integers int or string representation into a human easily readable number."""
    value = str(value)
    if value.isnumeric():
        return "{:,}".format(int(value)).replace(",", "&thinsp;")
    return value


def spidex_human(spidex: int | float | None) -> str:
    """Translate SPIDEX annotation to human readable string."""
    if spidex is None:
        return "not_reported"
    if abs(spidex) < SPIDEX_HUMAN["low"]["pos"][1]:
        return "low"
    if abs(spidex) < SPIDEX_HUMAN["medium"]["pos"][1]:
        return "medium"
    return "high"


def get_label_or_color_by_score(
    score: float,
    map: str,
    map_key: str,
) -> str:
    """Return a label or color for a given score based on predefined score ranges from the provided items_map."""
    SCORE_ITEM_MAPS = {
        "revel": REVEL_SCORE_LABEL_COLOR_MAP,
        "spliceai": SPLICEAI_SCORE_LABEL_COLOR_MAP,
    }
    for (low, high), info in SCORE_ITEM_MAPS[map].items():
        if low <= score <= high:
            return info[map_key]


def l2fc_2_fc(l2fc: float) -> float:
    """Converts Log2 fold change to fold change."""
    fc = 2 ** abs(l2fc)
    return fc if l2fc >= 0 else -1 / fc


def human_decimal(number: float, ndigits: int = 4) -> str | int:
    """Return a standard representation of a decimal number.

    Inputs number to humanize and a max number of digits to round to
    and outputs a humanized string of the decimal number.

    Returns 0 if value is 0 to avoid confusion over what is rounded and what is actually 0
    """
    min_number = 10**-ndigits
    if isinstance(number, str):
        number = None
    if number is None:
        # NaN
        return "-"
    if number == 0:
        return 0
    if number < min_number:
        return "<{}".format(min_number)

    # round all other numbers
    return round(number, ndigits)


def markdown(text: str) -> Markup:
    """Convert markdown text to HTML markup."""
    return Markup(python_markdown(text))


def tuple_list_to_dict(tuple_list, key_elem, value_elem):
    """Accepts a list of tuples and returns a dictionary with tuple element = key_elem as keys and tuple element = value_elem as values"""
    return {tup[key_elem]: tup[value_elem] for tup in tuple_list}


def url_decode(string: str) -> str:
    """Decode a string with encoded hex values."""
    return unquote(string)


def url_args(url: str) -> Dict[str, str]:
    """Return all arguments and values present in a string URL."""
    return dict(parse_qsl(urlsplit(url).query))


def cosmic_prefix(cosmicId: int | str) -> str:
    """If cosmicId is an integer, add 'COSM' as prefix
    otherwise return unchanged"""
    if isinstance(cosmicId, int):
        return "COSM" + str(cosmicId)
    return cosmicId


def pretty_variant(variant: dict) -> str:
    """Recaps variant info to string which is both visually appealing and informative."""

    def truncate(value: str | None, length: int = 20) -> str:
        if not value:
            return ""
        value = str(value)
        return value[:length]

    category = variant.get("category")

    match category:
        # --- STR ---
        case "str":
            main = (
                variant.get("str_repid")
                or variant.get("str_trid")
                or " ".join(gene.get("symbol", "") for gene in variant.get("genes", []))
            )

            tail = (
                f"STR{variant.get('str_mc')}"
                if variant.get("str_mc")
                else truncate(variant.get("alternative", ""), 20)
            )

            return " ".join(part for part in (main, tail) if part)

        # --- SNV / cancer ---
        case "snv" | "cancer":
            display_genes = []

            for gene in variant.get("genes", []):
                symbol = gene.get("hgnc_symbol")
                hgvs = gene.get("hgvs_identifier")
                hgnc_id = gene.get("hgnc_id")

                if symbol and hgvs:
                    display_genes.append(f"{symbol} {truncate(hgvs, 20)}")
                elif symbol:
                    display_genes.append(symbol)
                elif hgvs and hgnc_id:
                    display_genes.append(f"{hgnc_id} {truncate(hgvs, 20)}")

            if not display_genes:
                display_genes.append(truncate(variant.get("simple_id", ""), 40))

            return ", ".join(display_genes)

        # --- OUTLIER ---
        case "outlier":
            subcat = variant.get("sub_category", "")
            genes = variant.get("genes", [])

            gene_part = (
                " ".join(g.get("hgnc_symbol") or str(g.get("hgnc_id", "")) for g in genes)
                if genes
                else variant.get("gene_name_orig", "")
            )

            match subcat:
                case "splicing":
                    detail = (
                        f"{variant.get('delta_psi', '')}Δψ "
                        f"{variant.get('potential_impact', '')} - fs "
                        f"{variant.get('causes_frameshift', '')}"
                    )
                case "expression":
                    l2fc = variant.get("l2fc", 0)
                    if l2fc > 0:
                        arrow = "↑"
                    elif l2fc < 0:
                        arrow = "↓"
                    else:
                        arrow = ""
                    detail = f"{l2fc}{arrow}"
                case "methylation":
                    cpg = variant.get("cpg_label", "")
                    cpg = cpg.split("_")[0] if cpg else ""
                    detail = f"{variant.get('compare_label', '')} {cpg}"
                case _:
                    detail = ""

            return " - ".join(filter(None, [subcat.upper(), gene_part, detail]))

        # --- SVs, MEIs ---
        case _:
            return "{}({}{}-{}{})".format(
                variant.get("sub_category", "").upper(),
                variant.get("chromosome", ""),
                variant.get("cytoband_start", ""),
                variant.get("end_chrom", ""),
                variant.get("cytoband_end", ""),
            )


def format_variant_canonical_transcripts(variant: dict) -> List[str]:
    """Format canonical transcripts for a variant."""
    lines = set()
    genes = variant.get("genes") or []

    for gene in genes:
        gene_symbol = gene.get("hgnc_symbol", "")
        hgvs = gene.get("hgvs_identifier") or ""
        transcripts = gene.get("transcripts") or []

        canonical_tx = None
        primary_tx = None
        tx_id = None

        protein = None

        for tx in transcripts:
            tx_id = tx.get("transcript_id")
            if not tx.get("is_canonical"):
                if tx.get("is_primary"):
                    primary_tx = tx_id
                continue
            canonical_tx = tx_id
            protein = tx.get("protein_sequence_name") or ""
            break

        line_components = [f"{canonical_tx or primary_tx or tx_id} ({gene_symbol})"]
        if hgvs:
            line_components.append(unquote(hgvs))
        if protein:
            line_components.append(unquote(protein))

        lines.add(" ".join(line_components))

    return list(lines)


def upper_na(string: str) -> str:
    """Uppercase occurrences of "dna" and "rna" for nice display."""
    return re.sub(r"[Dd][Nn][Aa]", r"DNA", re.sub(r"[Rr][Nn][Aa]", r"RNA", string))


def count_cursor(pymongo_cursor: Cursor) -> int:
    """Count number of returned documents (deprecated pymongo.cursor.count())

    Perform operations on a copy of the cursor so original does not move
    """
    cursor_copy = pymongo_cursor.clone()
    return len(list(cursor_copy))


def list_intersect(list1: list, list2: list) -> list:
    """Returns the elements that are common in 2 lists"""
    return list(set(list1) & set(list2))


def list_remove_none(in_list: list) -> list:
    """Returns a list after removing any None values from it."""
    return [item for item in in_list if item is not None]


def spliceai_max(values: list) -> Optional[float]:
    """Returns a list of SpliceAI values, extracting floats only from values like 'score:0.23'."""
    float_values = []
    for value in values:
        if isinstance(value, str):
            if ":" in value:  # Variant hits multiple genes
                value = value.split(":")[1].strip()
        if value in [None, "-", "None"]:
            continue
        float_values.append(float(value))
    if float_values:
        return max(float_values)


def register_template_filters(app):
    """Register all template filters with the Flask app.

    We want to make some filters available also for view/controller function calls.
    In particular, format_variant_canonical_transcripts is made accessible via
    custom_filters, an empty CustomFilters object as namespace
    """
    app.template_filter()(human_longint)
    app.template_filter()(spidex_human)
    app.template_filter()(get_label_or_color_by_score)
    app.template_filter()(l2fc_2_fc)
    app.template_filter()(human_decimal)
    app.template_filter()(markdown)
    app.template_filter()(tuple_list_to_dict)
    app.template_filter()(url_decode)
    app.template_filter()(url_args)
    app.template_filter()(cosmic_prefix)
    app.template_filter()(format_variant_canonical_transcripts)
    app.template_filter()(upper_na)
    app.template_filter()(count_cursor)
    app.template_filter()(list_intersect)
    app.template_filter()(list_remove_none)
    app.template_filter()(spliceai_max)

    app.custom_filters = type("CustomFilters", (), {})()
    app.custom_filters.format_variant_canonical_transcripts = format_variant_canonical_transcripts
