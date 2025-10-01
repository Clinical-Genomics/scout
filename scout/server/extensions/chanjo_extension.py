"""
Generate coverage reports using chanjo and chanjo-report. Documentation under -> `docs/admin-guide/chanjo_coverage_integration.md`
"""

import json
import logging

import requests
from flask import current_app, request, url_for
from flask_babel import Babel
from markupsafe import Markup

LOG = logging.getLogger(__name__)
REF_CHROM_MT_STATS = "14"


class ChanjoReport:
    """Interfaces with chanjo-report. Creates the /reports endpoints in scout domain. Use Babel to set report language."""

    def init_app(self, app):
        try:
            from chanjo_report.server.app import configure_template_filters
            from chanjo_report.server.blueprints import report_bp
            from chanjo_report.server.extensions import api as chanjo_api
        except ImportError as error:
            chanjo_api = None
            report_bp = None
            configure_template_filters = None
            LOG.error(error)

        if not chanjo_api:
            raise ImportError(
                "An SQL db path was given, but chanjo-report could not be registered."
            )

        def get_locale():
            """Determine locale to use for translations."""
            accept_languages = current_app.config.get("ACCEPT_LANGUAGES", ["en"])

            # first check request args
            session_language = Markup.escape(request.args.get("lang"))
            if session_language in accept_languages:
                current_app.logger.info("using session language: %s", session_language)
                return session_language

            # language can be forced in config
            user_language = current_app.config.get("REPORT_LANGUAGE")
            if user_language:
                return user_language

            # try to guess the language from the user accept header that
            # the browser transmits.  We support de/fr/en in this example.
            # The best match wins.
            return request.accept_languages.best_match(accept_languages)

        babel = Babel(app)
        babel.init_app(app, locale_selector=get_locale)
        chanjo_api.init_app(app)
        configure_template_filters(app)
        app.register_blueprint(report_bp, url_prefix="/reports")
        app.config["chanjo_report"] = True
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True if app.debug else False

    def mt_coverage_stats(self, individuals: dict) -> dict:
        """Send a request to chanjo endpoint to retrieve MT vs autosome coverage stats

        Args:
            individuals(dict): case_obj["individuals"] object

        Returns:
            coverage_stats(dict): a dictionary with mean MT and autosome transcript coverage stats
        """
        coverage_stats = {}
        ind_ids = [ind["individual_id"] for ind in individuals]

        cov_calc_url = url_for("report.json_chrom_coverage", _external=True)

        try:
            # Calculate MT coverage
            mt_data = {"sample_ids": ",".join(ind_ids), "chrom": "MT"}

            resp = requests.post(cov_calc_url, json=mt_data)
            mt_cov_data = resp.json()

            # Calculate autosomal coverage
            ref_data = {"sample_ids": ",".join(ind_ids), "chrom": REF_CHROM_MT_STATS}
            resp = requests.post(cov_calc_url, json=ref_data)
            ref_cov_data = resp.json()

            for ind in ind_ids:
                if not (mt_cov_data.get(ind) and ref_cov_data.get(ind)):
                    continue
                coverage_info = dict(
                    mt_coverage=round(mt_cov_data[ind], 2),
                    autosome_cov=round(ref_cov_data[ind], 2),
                    mt_copy_number=round((mt_cov_data[ind] / ref_cov_data[ind]) * 2, 2),
                )
                coverage_stats[ind] = coverage_info

        except Exception as e:
            # Generic catch-all for network issues, invalid JSON, etc.
            LOG.warning(f"Failed to fetch chanjo MT coverage stats: {e}")
            return {}

        return coverage_stats
