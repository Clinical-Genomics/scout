from flask_wtf import FlaskForm
from wtforms import SelectMultipleField, StringField, validators

from scout.commands.update.user import USER_ROLES


class UserForm(FlaskForm):
    """Provides the form fields required to create a new user via the web interface."""

    institute = SelectMultipleField("Institute(s)", choices=[])
    name = StringField("Full name")
    email = StringField("Email")
    user_id = StringField("ID (LDAP)", [validators.Optional()])
    role = SelectMultipleField(
        "Role(s)",
        [validators.Optional()],
        choices=USER_ROLES,
    )
