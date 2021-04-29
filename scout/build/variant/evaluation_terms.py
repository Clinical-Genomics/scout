"""Build object containing variant evaluation terms."""
import logging

LOG = logging.getLogger(__name__)


def build_variant_evaluation_terms(evaluation_terms):
    """Build variant dismiss term object.

    These represent the terms used to dismiss variants and are local to a given institute.

        Args:
            institute_id(str): unique identifier of an institute

        Returns:
            dissmiss_terms_obj(dict)
    """
    eval_terms_obj = []
    for term in evaluation_terms:
        term_obj = dict(
                internal_id=term['internal_id'],
                rank=term['rank'],  # label to be displayed
                last_modified=term['last_modified'].isoformat(),
        )
        # add optional terms
        if term.get('label_class'):  # css class name to control display property
            term_obj['label_class'] = term['label_class']

        # add optional terms
        if term.get('name'):  # css class name to control display property
            term_obj['name'] = term['name']

        if term.get('label'):
            term_obj['label'] = term['label']

        if term.get('description'):
            term_obj['description'] = term['description']

        if term.get('institute'):
            term_obj['institute'] = term['institute']

        if term.get('evidence'):
            term_obj['evidence'] = term['evidence']

        if term.get('analysis_type'):
            term_obj['analysis_type'] = term['analysis_type']

        if term.get('term_category'):
            term_obj['term_category'] = term['term_category']
        # store processed term
        eval_terms_obj.append(term_obj)
    return eval_terms_obj
