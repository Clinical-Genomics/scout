# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import Blueprint
from flask.ext.admin.contrib.mongoengine import ModelView
from flask.ext.login import login_required

from ..admin import UserView
from ..extensions import admin
from ..models import User, Institute, Variant, Whitelist, Case
from ..helpers import templated

user = Blueprint('user', __name__, template_folder='templates')

# register admin views - TODO: move!
admin.add_view(ModelView(Whitelist))
admin.add_view(UserView(User))

admin.add_view(ModelView(Institute))
admin.add_view(ModelView(Case))
admin.add_view(ModelView(Variant))


@user.route('/profile/<user_id>')
@templated('profile.html')
@login_required
def profile(user_id):
  """View a user profile."""
  user = User.objects.get_or_404(id=user_id)

  # fetch cases from the data store
  return dict(user=user)
