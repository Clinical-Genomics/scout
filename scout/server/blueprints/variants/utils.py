# -*- coding: utf-8 -*-


def update_case_panels(store, case_obj):
    """Refresh case gene panels with info on if a panel was removed.

    Also return these more populated panels for optional storage on the variant_obj.
    If you do not use the returned variants, but rely on the update, please remember
    to call this function before updating the variants.

    store(adapter.MongoAdapter)
    case_obj(dict)

    Returns:
        list(panel_info)
    """

    for panel_info in case_obj.get("panels", []):
        panel_name = panel_info["panel_name"]
        latest_panel = store.gene_panel(panel_name)
        panel_info["removed"] = False if latest_panel is None else latest_panel.get("hidden", False)

    return case_obj.get("panels", [])
