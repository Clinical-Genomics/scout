"""Code for flask mongodb extension in scout"""
import os

from scout.adapter.client import get_connection


class MongoDB:
    """Flask interface to mongodb"""

    @staticmethod
    def init_app(app):
        """Initialize from flask"""

        db_name = os.environ.get("MONGO_DBNAME") or app.config.get("MONGO_DBNAME", "scout")

        client = get_connection(
            host=os.environ.get("MONGO_HOST") or app.config.get("MONGO_HOST", "localhost"),
            port=os.environ.get("MONGO_PORT") or app.config.get("MONGO_PORT", 27017),
            username=os.environ.get("MONGO_USERNAME") or app.config.get("MONGO_USERNAME", None),
            password=os.environ.get("MONGO_PASSWORD") or app.config.get("MONGO_PASSWORD", None),
            uri=os.environ.get("MONGO_URI") or app.config.get("MONGO_URI", None),
            mongodb=db_name,
        )

        app.config["MONGO_DATABASE"] = client[db_name]
        app.config["MONGO_CLIENT"] = client

    def __repr__(self):
        return f"{self.__class__.__name__}"
