from typing import List

from scout.server.extensions import store


def institute_mme_cases(institute_id: str) -> List[dict]:
    """Retrieves all cases for a given institute with an active MatchMaker Exchange submission."""
    institute_mme_events = store.institute_events_by_verb(
        category="case", institute_id=institute_id, verb="mme_add"
    )
    unique_case_ids = set([event["case"] for event in institute_mme_events])
    mme_cases = []
    for case_id in unique_case_ids:
        case_obj = store.case(case_id=case_id)
        if not case_obj or not case_obj.get("mme_submission"):
            continue
        mme_cases.append(case_obj)
    return mme_cases
