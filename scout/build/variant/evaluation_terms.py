"""Build object containing variant evaluation terms."""
import logging

LOG = logging.getLogger(__name__)


def build_evaluation_term(term):
    term_obj = dict(
            internal_id=term['internal_id'],
            name=term['name'],
            rank=term['rank'],
            last_modified=term['last_modified'].isoformat(),
    )
    # add optional terms
    if term.get('label_class'):  # css class name to control display property
        term_obj['label_class'] = term['label_class']

    for key in ('description', 'label_class', 'institute', 'evidence', 'track', 'term_category'):
        if key in term:
            term_obj[key] = term[key]

    # add optional terms
    if term.get('label'):
        term_obj['label'] = term['label']
    else:
        term_obj['label'] = term['name']

    return term_obj


def build_variant_evaluation_terms(evaluation_terms):
    """Build variant dismiss term object.

    These represent the terms used to dismiss variants and are local to a given institute.

        Args:
            institute_id(str): unique identifier of an institute

        Returns:
            dissmiss_terms_obj(dict)
    """
    if evaluation_terms.count() == 0:
        LOG.warning('No evaluation terms in query')
        terms = []
    else:
        terms = [build_evaluation_term(term) for term in evaluation_terms]
    return terms
