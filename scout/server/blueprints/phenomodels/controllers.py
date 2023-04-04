import datetime
import logging

from anytree import Node, RenderTree
from anytree.exporter import DictExporter
from flask import flash

from scout.server.extensions import store
from scout.utils.md5 import generate_md5_key

LOG = logging.getLogger(__name__)


def _subpanel_omim_checkbox_add(model_dict, user_form):
    """Add an OMIM checkbox to a phenotype subpanel
    Args:
        model_dict(dict): a dictionary coresponding to a phenotype model
        user_form(request.form): a POST request form object

    Returns:
        model_dict(dict): an updated phenotype model dictionary to be saved to database
    """
    subpanel_id = user_form.get("omim_subpanel_id")
    omim_id = user_form.get("omim_term").split(" | ")[0]
    omim_obj = store.disease_term(omim_id)
    if omim_obj is None:
        flash("Please specify a valid OMIM term", "warning")
        return
    checkboxes = model_dict["subpanels"][subpanel_id].get("checkboxes", {})
    if omim_id in checkboxes:
        flash(f"Omim term '{omim_id}' already exists in this panel", "warning")
        return

    checkbox_obj = dict(name=omim_id, description=omim_obj.get("description"), checkbox_type="omim")
    if user_form.get("omimTermTitle"):
        checkbox_obj["term_title"] = user_form.get("omimTermTitle")
    if user_form.get("omim_custom_name"):
        checkbox_obj["custom_name"] = user_form.get("omim_custom_name")
    checkboxes[omim_id] = checkbox_obj
    model_dict["subpanels"][subpanel_id]["checkboxes"] = checkboxes
    model_dict["subpanels"][subpanel_id]["updated"] = datetime.datetime.now()
    return model_dict


def _subpanel_hpo_checkgroup_add(model_dict, user_form):
    """Add an HPO term (and eventually his children) to a phenotype subpanel

    Args:
        model_dict(dict): a dictionary coresponding to a phenotype model
        user_form(request.form): a POST request form object

    Returns:
        model_dict(dict): an updated phenotype model dictionary to be saved to database
    """
    hpo_id = user_form.get("hpo_term").split(" ")[0]
    hpo_obj = store.hpo_term(hpo_id)
    if hpo_obj is None:  # user didn't provide a valid HPO term
        flash("Please specify a valid HPO term", "warning")
        return
    subpanel_id = user_form.get("hpo_subpanel_id")
    tree_dict = {}
    checkboxes = model_dict["subpanels"][subpanel_id].get("checkboxes", {})

    if hpo_id in checkboxes:  # Do not include duplicated HPO terms in checkbox items
        flash(f"Subpanel contains already HPO term '{hpo_id}'", "warning")
        return
    if user_form.get("includeChildren"):  # include HPO terms children in the checkboxes
        tree_dict = store.build_phenotype_tree(hpo_id)
        if tree_dict is None:
            flash(f"An error occurred while creating HPO tree from '{hpo_id}'", "danger")
            return
    else:  # include just HPO term as a standalone checkbox:
        tree_dict = dict(name=hpo_obj["_id"], description=hpo_obj["description"])
    tree_dict["checkbox_type"] = "hpo"
    if user_form.get("hpoTermTitle"):
        tree_dict["term_title"] = user_form.get("hpoTermTitle")
    if user_form.get("hpo_custom_name"):
        tree_dict["custom_name"] = user_form.get("hpo_custom_name")
    checkboxes[hpo_id] = tree_dict
    model_dict["subpanels"][subpanel_id]["checkboxes"] = checkboxes
    model_dict["subpanels"][subpanel_id]["updated"] = datetime.datetime.now()
    return model_dict


def _subpanel_checkgroup_remove_one(model_dict, user_form):
    """Remove a checkbox group from a phenotype subpanel

    Args:
        model_dict(dict): a dictionary coresponding to a phenotype model
        user_form(request.form): a POST request form object

    Returns:
        model_dict(dict): an updated phenotype model dictionary to be saved to database
    """
    subpanel_id = user_form.get("checkgroup_remove").split("#")[1]
    remove_field = user_form.get("checkgroup_remove").split("#")[0]

    try:
        model_dict["subpanels"][subpanel_id]["checkboxes"].pop(remove_field, None)
        model_dict["subpanels"][subpanel_id]["updated"] = datetime.datetime.now()
    except Exception as ex:
        flash(ex, "danger")

    return model_dict


def _update_subpanel(subpanel_obj, supb_changes):
    """Update the checkboxes of a subpanel according to checkboxes checked in the model preview.

    Args:
        subpanel_obj(dict): a subpanel object
        supb_changes(dict): terms to keep under a parent term. example: {"HP:0001250": [(HP:0020207, HP:0020215, HP:0001327]}

    Returns:
        subpanel_obj(dict): an updated subpanel object
    """
    checkboxes = subpanel_obj.get("checkboxes", {})
    new_checkboxes = {}
    for parent, children_list in supb_changes.items():
        # create mini tree obj from terms in changes dict. Add all nodes at the top level initially
        root = Node(id="root", name="root", parent=None)
        all_terms = {}
        # loop over the terms to keep into the checboxes dict
        for child in children_list:
            if child.startswith("OMIM"):
                new_checkboxes[child] = checkboxes[child]
                continue

            term_obj = store.hpo_term(child)  # else it's an HPO term, and might have nested term:
            node = None
            try:
                node = Node(child, parent=root, description=term_obj["description"])
            except Exception:
                flash(f"Term {child} could not be find in database")
                continue

            all_terms[child] = term_obj

            if child not in checkboxes:
                continue
            node.custom_name = checkboxes[child].get("custom_name")
            node.term_title = checkboxes[child].get("term_title")

        # Rearrange tree nodes according the HPO ontology
        root = store.organize_tree(all_terms, root)
        LOG.info(f"Updated HPO tree:{root}:\n{RenderTree(root)}")
        exporter = DictExporter()
        for child_node in root.children:
            # export node to dict
            node_dict = exporter.export(child_node)
            new_checkboxes[child_node.name] = node_dict

    subpanel_obj["checkboxes"] = new_checkboxes
    subpanel_obj["updated"] = datetime.datetime.now()
    return subpanel_obj


def phenomodel_checkgroups_filter(model_dict, user_form):
    """Filter the checboxes of one or more subpanels according to preferences specified in the model preview

    Args:
        model_dict(dict): a dictionary coresponding to a phenotype model
        user_form(request.form): a POST request form object

    Returns:
        model_dict(dict): an updated phenotype model dictionary to be saved to database
    """
    subpanels = model_dict.get("subpanels") or {}
    check_list = (
        user_form.getlist("cheked_terms") or []
    )  # a list like this: ["subpanelID.rootTerm_checkedTerm", .. ]
    updates_dict = {}
    # From form values, create a dictionary like this: { "subpanel_id1":{"parent_term1":[children_terms], parent_term2:[children_terms2]}, .. }
    for checked_value in check_list:
        panel_key = checked_value.split(".")[0]
        parent_term = checked_value.split(".")[1]
        child_term = checked_value.split(".")[2]
        if panel_key in updates_dict:
            if parent_term in updates_dict[panel_key]:
                updates_dict[panel_key][parent_term].append(child_term)
            else:
                updates_dict[panel_key][parent_term] = [child_term]
        else:
            updates_dict[panel_key] = {parent_term: [child_term]}

    # loop over the subpanels of the model, and check they need to be updated
    for key, subp in subpanels.items():
        if key in updates_dict:  # if subpanel requires changes
            model_dict["subpanels"][key] = _update_subpanel(subp, updates_dict[key])  # update it

    return model_dict


def _add_subpanel(model_id, model_dict, user_form):
    """Add an empty subpanel to a phenotype model

    Args:
        model_id(str): string of the ID of a phenotype model
        model_dict(dict): a dictionary coresponding to a phenotype model
        user_form(request.form): a POST request form object

    """
    subpanel_key = generate_md5_key([model_id, user_form.get("title")])
    phenomodel_subpanels = model_dict.get("subpanels") or {}

    if subpanel_key in phenomodel_subpanels:
        flash("A model panel with that title already exists", "warning")
        return
    subpanel_obj = {
        "title": user_form.get("title"),
        "subtitle": user_form.get("subtitle"),
        "created": datetime.datetime.now(),
        "updated": datetime.datetime.now(),
    }
    phenomodel_subpanels[subpanel_key] = subpanel_obj
    model_dict["subpanels"] = phenomodel_subpanels
    return model_dict


def edit_subpanel_checkbox(model_id, user_form):
    """Update checkboxes from one or more panels according to the user form
    Args:
        model_id(ObjectId): document ID of the model to be updated
        user_form(request.form): a POST request form object
    """
    model_dict = store.phenomodel(model_id)
    update_model = False
    if model_dict is None:
        return
    if "add_hpo" in user_form:  # add an HPO checkbox to subpanel
        update_model = _subpanel_hpo_checkgroup_add(model_dict, user_form)
    if "add_omim" in user_form:  # add an OMIM checkbox to subpanel
        update_model = _subpanel_omim_checkbox_add(model_dict, user_form)
    if user_form.get("checkgroup_remove"):  # remove a checkbox of any type from subpanel
        update_model = _subpanel_checkgroup_remove_one(model_dict, user_form)

    if update_model:
        store.update_phenomodel(model_id=model_id, model_obj=model_dict)


def update_phenomodel(model_id, user_form):
    """Update a phenotype model according to the user form

    Args:
        model_id(ObjectId): document ID of the model to be updated
        user_form(request.form): a POST request form object
    """
    model_dict = store.phenomodel(model_id)
    update_model = False
    if model_dict is None:
        return
    if user_form.get("update_model"):  # update either model name of description
        update_model = True
        model_dict["name"] = user_form.get("model_name")
        model_dict["description"] = user_form.get("model_desc")
    if user_form.get("subpanel_delete"):  # Remove a phenotype submodel from phenomodel
        subpanels = model_dict["subpanels"]
        # remove panel from subpanels dictionary
        subpanels.pop(user_form.get("subpanel_delete"), None)
        model_dict["subpanels"] = subpanels
        update_model = True
    if user_form.get("add_subpanel"):  # Add a new phenotype submodel
        update_model = _add_subpanel(model_id, model_dict, user_form)
    if user_form.get("model_save"):  # Save model according user preferences in the preview
        update_model = phenomodel_checkgroups_filter(model_dict, user_form)

    if update_model:
        store.update_phenomodel(model_id=model_id, model_obj=model_dict)
