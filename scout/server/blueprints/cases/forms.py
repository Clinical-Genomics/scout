# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectMultipleField


class NonValidatingSelectMultipleField(SelectMultipleField):
    """Skip strict choice validation for dynamic multi-selects."""

    def pre_validate(self, _form):
        # Choices are populated at runtime from case/institute panels.
        pass


class SmaPanelFilterForm(FlaskForm):
    """Panel filter form used on the SMA/dark regions page."""

    panel_filter_applied = HiddenField()
    gene_panels = NonValidatingSelectMultipleField(choices=[])
