from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, validators

from scout.constants.user import USER_ROLES


class NonValidatingSelectMultipleField(SelectMultipleField):
    """Necessary to skip validation of dynamic multiple selects in form"""

    def pre_validate(self, _form):
        """Just skip the validation."""
        pass


class UserForm(FlaskForm):
    """Provides the form fields required to create a new user via the web interface."""

    institute = NonValidatingSelectMultipleField("Institute(s)", choices=[])
    name = StringField("Full name")
    email = StringField("Email")
    user_id = StringField("ID (LDAP authentication only)", [validators.Optional()])
    role = NonValidatingSelectMultipleField(
        "Role(s)",
        [validators.Optional()],
        choices=USER_ROLES,
    )
