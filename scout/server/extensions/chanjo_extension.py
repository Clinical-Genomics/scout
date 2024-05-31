"""
    Generate coverage reports using chanjo and chanjo-report. Documentation under -> `docs/admin-guide/chanjo_coverage_integration.md`
"""

import logging

LOG = logging.getLogger(__name__)
try:
    from chanjo_report.server.app import configure_template_filters
    from chanjo_report.server.blueprints import report_bp
    from chanjo_report.server.extensions import api as chanjo_api
except ImportError as error:
    chanjo_api = None
    report_bp = None
    configure_template_filters = None
    LOG.warning("chanjo-report is not properly installed! %s.", error)


class ChanjoReport:
    """Interfaces with chanjo-report. Creates the /reports endpoints in scout domain. Use Babel to set report language."""

    def init_app(self, app):

        if not chanjo_api:
            raise ImportError(
                "An SQL db path was given, but chanjo-report could not be registered."
            )
        chanjo_api.init_app(app)
        app.register_blueprint(report_bp, url_prefix="/reports")
        app.config["chanjo_report"] = True
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True if app.debug else False
