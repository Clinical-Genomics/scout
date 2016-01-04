# -*- coding: utf-8 -*-
from flask import Blueprint
from flask.ext.admin.contrib.mongoengine import ModelView
from flask.ext.login import login_required

from ..admin import UserModelView
from ..extensions import admin
from ..models import User, Institute, Variant, Whitelist, Case
from ..helpers import templated

user = Blueprint('profile', __name__, template_folder='templates')


class CaseView(ModelView):
    column_exclude_list = ['coverage_report', 'madeline_info',
                           'dynamic_gene_list']
    form_columns = ['display_name', 'owner', 'collaborators', 'individuals',
                    'status', 'is_research', 'default_panels',
                    'gender_check', 'clinical_panels', 'phenotype_terms']


class VariantView(ModelView):
    column_exclude_list = ['variant_id', 'compounds']

# register admin views - TODO: move!
admin.add_view(ModelView(Whitelist))
admin.add_view(UserModelView(User))

admin.add_view(ModelView(Institute))
admin.add_view(CaseView(Case))
admin.add_view(VariantView(Variant))


@user.route('/profile/<user_id>')
@templated('profile.html')
@login_required
def profile(user_id):
    """View a user profile."""
    user_model = User.objects.get(id=user_id)

    # fetch cases from the data store
    return dict(user=user_model)
