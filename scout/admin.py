# -*- coding: utf-8 -*-
from flask_login import current_user
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.mongoengine import ModelView


class AuthMixin(object):
    """All admin views should subclass AuthMixin."""
    def is_accessible(self):
        """Check if the current user should have access to the view."""
        return current_user.has_role('admin')


class AdminView(AuthMixin, AdminIndexView):
    @expose('/')
    def index(self):
        """Expose the index view of the admin section of the site."""
        return self.render('admin/index.html')


# customized admin views
class UserModelView(ModelView):
    """Slightly customized admin view for the user model."""
    column_filters = ['name', 'email', 'created_at', 'location']
    column_searchable_list = ('name', 'email')
