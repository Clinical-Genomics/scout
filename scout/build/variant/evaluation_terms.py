"""Build object containing variant evaluation terms."""
import logging

LOG = logging.getLogger(__name__)


def build_variant_dismiss_terms(evaluation_terms):
    """Build variant dismiss term object.

    These represent the terms used to dismiss variants and are local to a given institute.

        Args:
            institute_id(str): unique identifier of an institute

        Returns:
            dissmiss_terms_obj(dict)
    """
    dissmiss_terms_obj = []
    for term in evaluation_terms:
        term_obj = dict(
                internal_id=term['internal_id'],
                label=term['label'],
                last_modified=term['last_modified'].isoformat(),
        )
        # load optional terms
        if term.get('institute'):
            term_obj['institute'] = term['institute']
        if term.get('description'):
            term_obj['description'] = term['description']
        if term.get('evidence'):
            term_obj['evidence'] = term['evidence']
        dissmiss_terms_obj.append(term_obj)
    return dissmiss_terms_obj

