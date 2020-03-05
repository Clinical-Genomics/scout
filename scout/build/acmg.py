import logging
import datetime

LOG = logging.getLogger(__name__)


def build_evaluation(
    variant_specific,
    variant_id,
    user_id,
    user_name,
    institute_id,
    case_id,
    classification,
    criteria,
):
    """Build a evaluation object ready to be inserted to database

    Args:
        variant_specific(str): md5 string for the specific variant
        variant_id(str): md5 string for the common variant
        user_id(str)
        user_name(str)
        institute_id(str)
        case_id(str)
        classification(str): The ACMG classification
        criteria(list(dict)): A list of dictionaries with ACMG criterias

    Returns:
        evaluation_obj(dict): Correctly formatted evaluation object

    """
    LOG.info("Creating classification: %s for variant %s", classification, variant_id)
    criteria = criteria or []
    evaluation_obj = dict(
        variant_specific=variant_specific,
        variant_id=variant_id,
        institute_id=institute_id,
        case_id=case_id,
        classification=classification,
        user_id=user_id,
        user_name=user_name,
        created_at=datetime.datetime.now(),
    )
    criteria_objs = []
    for info in criteria:
        criteria_obj = {}
        # This allways has to exist
        # We might want to check if the term is valid here...
        criteria_obj["term"] = info["term"]
        if "comment" in info:
            criteria_obj["comment"] = info["comment"]
        if "links" in info:
            criteria_obj["links"] = info["links"]
        criteria_objs.append(criteria_obj)

    evaluation_obj["criteria"] = criteria_objs

    return evaluation_obj
