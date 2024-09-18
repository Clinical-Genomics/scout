import logging

import coloredlogs
from flask.app import Flask

USERS_LOGGER_PATH_PARAM = "USERS_ACTIVITY_LOG_PATH"
ACTIVITY_LOG_IGNORE_TRIGGERS = [
    "static",
    "ideograms",
    "custom_images",
    "autozygous_images",
    "coverage_images",
    "upd_regions_images",
    "favicon",
    "GET /",
    "Closing",
    "Enable",
    "enabled",
    "Collecting IGV tracks",
]  # Substrings used when filtering messages to show if users activity log is on


class ActivityLogFilter(logging.Filter):
    """When monitoring users activity, log only navigation on main pages.
    - Do not log messages that contain the substrings specified in ACTIVITY_LOG_IGNORE_TRIGGERS"""

    def filter(self, record):
        return (
            any(sub_url in record.getMessage() for sub_url in ACTIVITY_LOG_IGNORE_TRIGGERS) is False
        )


def set_activity_log(log: logging.Logger, app: Flask):
    """Log users' activity to a file, if specified in the scout config."""
    app.logger.setLevel("INFO")
    app.logger.addFilter(ActivityLogFilter())
    file_handler = logging.FileHandler(app.config[USERS_LOGGER_PATH_PARAM])
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    log.addHandler(file_handler)


def init_log(log: logging.Logger, app: Flask):
    """Initializes the log file in the proper format."""

    current_log_level = log.getEffectiveLevel()
    coloredlogs.install(level="DEBUG" if app.debug else current_log_level)

    if USERS_LOGGER_PATH_PARAM in app.config:
        set_activity_log(log=log, app=app)
