# -*- coding: utf-8 -*-
from functools import wraps

from flask import render_template, request


def templated(template=None):
    """Template decorator.

    Ref: http://flask.pocoo.org/docs/patterns/viewdecorators/
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint.replace('.', '/') + '.html'
            context = f(*args, **kwargs)
            if context is None:
                context = {}
            elif not isinstance(context, dict):
                return context
            return render_template(template_name, **context)
        return decorated_function
    return decorator


def public_endpoint(function):
    function.is_public = True
    return function


def institute_and_case(store, institute_id, case_name):
    """Fetch insitiute and case objects."""
    institute_obj = store.institute(institute_id)
    case_obj = store.case(institute_id=institute_id, display_name=case_name)
    return institute_obj, case_obj
