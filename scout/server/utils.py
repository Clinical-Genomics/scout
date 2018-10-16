# -*- coding: utf-8 -*-
from functools import wraps

from flask import render_template, request, abort, flash
from flask_login import current_user


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


def institute_and_case(store, institute_id, case_name=None):
    """Fetch insitiute and case objects."""
    institute_obj = store.institute(institute_id)
    if institute_obj is None and institute_id != 'favicon.ico':
        flash("Can't find institute: {}".format(institute_id), 'warning')
        return abort(404)

    if case_name:
        if case_name:
            case_obj = store.case(institute_id=institute_id, display_name=case_name)
            if case_obj is None:
                return abort(404)

    # validate that user has access to the institute
    if not current_user.is_admin:
        if institute_id not in current_user.institutes:
            if not case_name or not any(inst_id in case_obj['collaborators'] for inst_id in
                                        current_user.institutes):
                # you don't have access!!
                flash("You don't have acccess to: {}".format(institute_id),'danger')
                return abort(403)

    # you have access!
    if case_name:
        return institute_obj, case_obj
    else:
        return institute_obj


def user_institutes(store, login_user):
    """Preprocess institute objects."""
    if login_user.is_admin:
        institutes = store.institutes()
    else:
        institutes = [store.institute(inst_id) for inst_id in login_user.institutes]

    return institutes
