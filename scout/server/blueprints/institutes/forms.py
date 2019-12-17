# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import (IntegerField, SelectMultipleField, SubmitField,
    validators)
from scout.constants import COHORT_TAGS

class InstituteForm(FlaskForm):
    """ Instutute-specif settings """

    cohort_tuples = [ (COHORT_TAGS[i], COHORT_TAGS[i]) for i in range(0, len(COHORT_TAGS)) ]

    coverage_cutoff = IntegerField('Coverage cutoff', validators=[validators.Optional(),
        IntegerField], default=10)
    partner_institutes = SelectMultipleField('Institutes to share cases with', choices=[])
    snvs_rank_threshold = IntegerField('SNVs rank threshold',  validators=[validators.Optional(),
        IntegerField], default=0,)
    svs_rank_threshold = IntegerField('SVs rank threshold', validators=[validators.Optional(),
        IntegerField], default=0,)
    pheno_groups = SelectMultipleField('Custom phenotype groups', choices=[])
    cohorts = SelectMultipleField('Patient coorts', choices=cohort_tuples)
    submit = SubmitField('Save settings')
