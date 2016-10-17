# -*- coding: utf-8 -*-
from functools import wraps

from flask import abort, render_template, request, flash
from mongoengine import DoesNotExist

from scout.extensions import store


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


def validate_user(current_user, institute_id):
    # abort with 404 error if case/institute doesn't exist
    try:
        institute = store.institute(institute_id)
    except DoesNotExist:
        return abort(404)

    if institute not in current_user.institutes:
        flash('You do not have access to this institute.')
        return abort(403)

    return institute
