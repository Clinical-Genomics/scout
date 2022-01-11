from flask_wtf import FlaskForm
from wtforms import HiddenField


class CoverageForm(FlaskForm):
    """Class containing info to be passed to chanjo report (report.report endpoint in Scout)"""

    gene_ids = HiddenField()
    sample_id = HiddenField()
    level = HiddenField()
    panel_name = HiddenField()
