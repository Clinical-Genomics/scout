def parse_genetic_models(models_info: str, case_id: str) -> list:
    """Parse the genetic models entry of a vcf

    Return inheritance patterns.
    """
    genetic_models = []
    if models_info:
        for family_info in models_info.split(","):
            split_info = family_info.split(":")
            if split_info[0] == case_id:
                genetic_models = split_info[1].split("|")

    return genetic_models
