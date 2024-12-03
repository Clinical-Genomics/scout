import logging
import datetime

LOG = logging.getLogger(__name__)


def build_ccv_evaluation(
    variant_specific,
    variant_id,
    user_id,
    user_name,
    institute_id,
    case_id,
    ccv_classification,
    ccv_criteria,
):
    """Build a ClinGen-CGC-VIGG evaluation object ready to be inserted to database

    Args:
        variant_specific(str): md5 string for the specific variant
        variant_id(str): md5 string for the common variant
        user_id(str)
        user_name(str)
        institute_id(str)
        case_id(str)
        ccv_classification(str): The ClinGen-CGC-VIGG classification
        ccv_criteria(list(dict)): A list of dictionaries with ClinGen-CGC-VIGG criteria

    Returns:
        evaluation_obj(dict): Correctly formatted evaluation object

    """
    LOG.info(
        "Creating ClinGen-CGC-VIGG classification: %s for variant %s",
        ccv_classification,
        variant_id,
    )
    ccv_criteria = ccv_criteria or []
    evaluation_obj = dict(
        variant_specific=variant_specific,
        variant_id=variant_id,
        institute_id=institute_id,
        case_id=case_id,
        ccv_classification=ccv_classification,
        user_id=user_id,
        user_name=user_name,
        created_at=datetime.datetime.now(),
    )
    criteria_objs = []
    for info in ccv_criteria:
        criteria_obj = {}
        for criterion_key in ["term", "comment", "links", "modifier"]:
            if criterion_key in info:
                criteria_obj[criterion_key] = info[criterion_key]
        criteria_objs.append(criteria_obj)

    evaluation_obj["ccv_criteria"] = criteria_objs

    return evaluation_obj
