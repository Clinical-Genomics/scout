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


def validate_user(current_user, institute_id, family_id=None):
    # abort with 404 error if case/institute doesn't exist
    try:
        institute = store.institute(institute_id)
    except DoesNotExist:
        return abort(404)

    is_admin = current_user.has_role('admin')
    if family_id:
        case_model = store.case(institute_id, family_id)
        if case_model is None:
            return abort(404, "Can't find a case '{}' for institute {}"
                              .format(family_id, institute_id))
        inst_ids = set(inst.internal_id for inst in current_user.institutes)
        if not is_admin and len(inst_ids.intersection(case_model.collaborators)) == 0:
            flash('You do not have access to this case.', 'danger')
            return abort(403)
    elif not is_admin and institute not in current_user.institutes:
        flash('You do not have access to this institute.', 'danger')
        return abort(403)

    if family_id:
        return institute, case_model
    else:
        return institute
