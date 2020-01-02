# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import (IntegerField, SelectMultipleField, SubmitField, DecimalField,
    validators)
from scout.constants import COHORT_TAGS, PHENOTYPE_GROUPS

class InstituteForm(FlaskForm):
    """ Instutute-specif settings """

    cohort_tuples = [ (COHORT_TAGS[i], COHORT_TAGS[i]) for i in range(0, len(COHORT_TAGS)) ]
    hpo_tuples = []
    for key in PHENOTYPE_GROUPS.keys():
        hpo_tuples.append((PHENOTYPE_GROUPS[key], ' '.join([ PHENOTYPE_GROUPS[key]['name'], '(', PHENOTYPE_GROUPS[key]['abbr'] ,')'])))

    coverage_cutoff = IntegerField('Coverage cutoff', validators=[validators.Optional(),
        validators.NumberRange(min=1)], default=10)
    frequency_cutoff = DecimalField('Frequency cutoff', validators=[validators.Optional(),
        validators.NumberRange(min=0, message="Number must be positive")], default=0.01)
    snvs_rank_threshold = IntegerField('SNVs rank threshold',  validators=[validators.Optional(),
        IntegerField], default=0,)
    svs_rank_threshold = IntegerField('SVs rank threshold', validators=[validators.Optional(),
        IntegerField], default=0,)
    pheno_groups = SelectMultipleField('Custom phenotype groups', choices=hpo_tuples)
    cohorts = SelectMultipleField('Patient coorts', choices=cohort_tuples)
    institutes = SelectMultipleField('Institutes to share cases with', choices=[])
    submit = SubmitField('Save settings')
