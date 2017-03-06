# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_login import current_user

from scout.server.extensions import store
from scout.server.utils import templated
from . import controllers

cases_bp = Blueprint('cases', __name__, template_folder='templates')


@cases_bp.route('/institutes')
@templated('cases/index.html')
def index():
    """Display a list of all user institutes."""
    user_institutes = controllers.user_institutes(store, current_user)
    return dict(institutes=user_institutes)


@cases_bp.route('/<institute_id>')
@templated('cases/cases.html')
def cases(institute_id):
    """Display a list of cases for an institute."""
    return dict()
