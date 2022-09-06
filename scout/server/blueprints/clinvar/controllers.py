from scout.server.extensions import store


def set_clinvar_form(var_list, data):
    """Creates and sets values to the form used in ClinVar create submission page

    Args:
        var_list(list): list of variant _ids
    """
