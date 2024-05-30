"""
    Generate coverage reports using chanjo and chanjo-report. Documentation under -> `docs/admin-guide/chanjo_coverage_integration.md`
"""

try:
    from chanjo_report.server.app import configure_template_filters
    from chanjo_report.server.blueprints import report_bp
    from chanjo_report.server.extensions import api as chanjo_api
except ImportError as error:
    chanjo_api = None
    report_bp = None
    configure_template_filters = None
    LOG.warning("chanjo-report is not properly installed! %s.", error)

from flask import request


class ChanjoReport:
    """Interfaces with chanjo-report. Creates the /reports endpoints in scout domain. Use Babel to set report language."""

    def get_locale(self, app):
        """Determine the language used in the app."""
        accept_languages = app.config.get("ACCEPT_LANGUAGES", ["en"])
        session_language = Markup.escape(request.args.get("lang"))
        if session_language in accept_languages:
            app.logger.info("using session language: %s", session_language)
            return session_language

        # language can be forced in config
        user_language = current_app.config.get("REPORT_LANGUAGE")
        if user_language:
            return user_language

        # try to guess the language from the user accept header that
        # the browser transmits.  We support de/fr/en in this example.
        # The best match wins.
        return request.accept_languages.best_match(accept_languages)

    def init_app(self, app):

        if not chanjo_api:
            raise ImportError(
                "An SQL db path was given, but chanjo-report could not be registered."
            )
        chanjo_api.init_app(app)
        app.register_blueprint(report_bp, url_prefix="/reports")
        app.config["chanjo_report"] = True
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True if app.debug else False

        babel = Babel()
        babel.init_app(app, locale_selector=self.get_locale(app=app))
