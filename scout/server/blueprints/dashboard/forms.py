# -*- coding: utf-8 -*-
from wtforms import SelectField, StringField, SubmitField, validators

from scout.server.blueprints.institutes.forms import CaseFilterForm


class NonValidatingSelectField(SelectField):
    """Necessary to skip validation of dynamic selects in form"""

    def pre_validate(self, form):
        pass


class DashboardFilterForm(CaseFilterForm):
    """Takes care of cases filtering on dashboard page"""

    search_institute = NonValidatingSelectField("Institute", choices=[])
