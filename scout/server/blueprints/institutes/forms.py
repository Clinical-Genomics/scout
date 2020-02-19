# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    SelectMultipleField,
    SubmitField,
    DecimalField,
    TextField,
    validators,
)
from scout.constants import PHENOTYPE_GROUPS


class NonValidatingSelectMultipleField(SelectMultipleField):
    """Necessary to skip validation of dynamic multiple selects in form"""

    def pre_validate(self, form):
        pass


class InstituteForm(FlaskForm):
    """ Instutute-specif settings """

    hpo_tuples = []
    for key in PHENOTYPE_GROUPS.keys():
        option_name = " ".join(
            [
                key,
                ",",
                PHENOTYPE_GROUPS[key]["name"],
                "(",
                PHENOTYPE_GROUPS[key]["abbr"],
                ")",
            ]
        )
        hpo_tuples.append((option_name, option_name))

    display_name = TextField(
        "Institute display name",
        validators=[validators.InputRequired(), validators.Length(min=2, max=100)],
    )
    sanger_emails = NonValidatingSelectMultipleField(
        "Sanger recipients", validators=[validators.Optional()]
    )
    coverage_cutoff = IntegerField(
        "Coverage cutoff",
        validators=[validators.Optional(), validators.NumberRange(min=1)],
    )
    frequency_cutoff = DecimalField(
        "Frequency cutoff",
        validators=[
            validators.Optional(),
            validators.NumberRange(min=0, message="Number must be positive"),
        ],
    )

    pheno_group = TextField("New phenotype group", validators=[validators.Optional()])
    pheno_abbrev = TextField("Abbreviation", validators=[validators.Optional()])

    pheno_groups = NonValidatingSelectMultipleField(
        "Custom phenotype groups", choices=hpo_tuples
    )
    cohorts = NonValidatingSelectMultipleField(
        "Available patient cohorts", validators=[validators.Optional()]
    )
    institutes = NonValidatingSelectMultipleField(
        "Institutes to share cases with", choices=[]
    )
    submit_btn = SubmitField("Save settings")
