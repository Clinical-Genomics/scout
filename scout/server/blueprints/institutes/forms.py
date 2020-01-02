# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import (IntegerField, SelectMultipleField, SubmitField, DecimalField,
    TextField, validators, TextAreaField)
from wtforms.fields.html5 import EmailField
from scout.constants import COHORT_TAGS, PHENOTYPE_GROUPS

class InstituteForm(FlaskForm):
    """ Instutute-specif settings """

    cohort_tuples = [ (COHORT_TAGS[i], COHORT_TAGS[i]) for i in range(0, len(COHORT_TAGS)) ]
    hpo_tuples = []
    for key in PHENOTYPE_GROUPS.keys():
        option_name = ' '.join([ PHENOTYPE_GROUPS[key]['name'], '(', PHENOTYPE_GROUPS[key]['abbr'] ,')'])
        hpo_tuples.append((option_name,option_name))

    display_name = TextField('Institute display name', validators=[validators.InputRequired(),
        validators.Length(min=2, max=100)])
    sanger_recipients = TextAreaField('Sanger recipients, comma separated', validators=[validators.Optional()],
        render_kw={"rows": 2, "cols": 12})
    coverage_cutoff = IntegerField('Coverage cutoff', validators=[validators.Optional(),
        validators.NumberRange(min=1)])
    frequency_cutoff = DecimalField('Frequency cutoff', validators=[validators.Optional(),
        validators.NumberRange(min=0, message="Number must be positive")])
    snvs_rank_threshold = IntegerField('SNVs rank threshold',  validators=[validators.Optional(),
        IntegerField])
    svs_rank_threshold = IntegerField('SVs rank threshold', validators=[validators.Optional(),
        IntegerField])
    pheno_groups = SelectMultipleField('Custom phenotype groups', choices=hpo_tuples)
    cohorts = SelectMultipleField('Patient coorts', choices=cohort_tuples)
    institutes = SelectMultipleField('Institutes to share cases with', choices=[])
    submit = SubmitField('Save settings')
