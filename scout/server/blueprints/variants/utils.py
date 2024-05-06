# -*- coding: utf-8 -*-
from scout.adapter import MongoAdapter


def update_case_panels(store: MongoAdapter, case_obj: dict):
    """Refresh case gene panels with info on if a panel was removed.
    Also sets the key "latest_panels" for a case where the value is the latest version of the case panels

    If you do not use the returned variants, but rely on the update, please remember
    to call this function before updating the variants.
    """
    case_obj["latest_panels"] = []

    for panel_info in case_obj.get("panels", []):
        panel_name = panel_info["panel_name"]
        latest_panel = store.gene_panel(panel_name)
        panel_info["removed"] = False if latest_panel is None else latest_panel.get("hidden", False)
        if latest_panel:
            latest_panel["hgnc_ids"] = [gene["hgnc_id"] for gene in latest_panel.get("genes", [])]
            case_obj["latest_panels"].append(latest_panel)
