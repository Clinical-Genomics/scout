def parse_genetic_models(models_info, case_id):
    """Parse the genetic models entry of a vcf

    Args:
        models_info(str): The raw vcf information
        case_id(str)

    Returns:
        genetic_models(list)

    """
    genetic_models = []
    if models_info:
        for family_info in models_info.split(","):
            splitted_info = family_info.split(":")
            if splitted_info[0] == case_id:
                genetic_models = splitted_info[1].split("|")

    return genetic_models
