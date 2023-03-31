from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, validators


class PhenoModelForm(FlaskForm):
    """Base Phenopanel form, not including any subpanel"""

    model_name = StringField("Phenotype panel name", validators=[validators.InputRequired()])
    model_desc = StringField("Description", validators=[validators.Optional()])
    create_model = SubmitField("Create")


class PhenoSubPanelForm(FlaskForm):
    """A form corresponfing to a phenopanel sub-panel"""

    title = StringField("Phenotype subpanel title", validators=[validators.InputRequired()])
    subtitle = StringField("Phenotype subpanel subtitle", validators=[validators.Optional()])
    add_subpanel = SubmitField("Save phenotype subpanel")
