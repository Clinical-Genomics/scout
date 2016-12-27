# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_admin.contrib.mongoengine import ModelView
from flask_login import login_required

from scout.admin import UserModelView
from scout.extensions import admin
from scout.models import (User, Institute, Variant, Whitelist, Case, GenePanel,
                          Event, HgncGene)
from scout.utils.helpers import templated

user = Blueprint('profile', __name__, template_folder='templates')


class CaseView(ModelView):
    column_filters = ['display_name', 'owner', 'status']
    column_searchable_list = ('display_name', 'owner')
    column_exclude_list = ['madeline_info', 'dynamic_gene_list', 'synopsis',
                           'vcf_files']
    form_excluded_columns = ['madeline_info', 'dynamic_gene_list', 'vcf_files',
                             'suspects', 'causatives']


class VariantView(ModelView):
    column_exclude_list = ['variant_id', 'compounds']


class PanelView(ModelView):
    column_exclude_list = ['gene_objects']


# register admin views - TODO: move!
admin.add_view(ModelView(Whitelist))
admin.add_view(UserModelView(User))

admin.add_view(ModelView(Institute))
admin.add_view(CaseView(Case))
admin.add_view(VariantView(Variant))
admin.add_view(PanelView(GenePanel))
admin.add_view(ModelView(HgncGene))
admin.add_view(ModelView(Event))


@user.route('/profile/<user_id>')
@templated('profile.html')
@login_required
def profile(user_id):
    """View a user profile."""
    user_model = User.objects.get(id=user_id)

    # fetch cases from the data store
    return dict(user=user_model)
