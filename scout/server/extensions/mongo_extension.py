"""Code for flask mongodb extension in scout"""
from scout.adapter.client import get_connection


class MongoDB:
    """Flask interface to mongodb"""

    @staticmethod
    def init_app(app):
        """Initialize from flask"""

        db_name = app.config.get("MONGO_DBNAME", "scout")

        client = get_connection(
            host=app.config.get("MONGO_HOST", "localhost"),
            port=app.config.get("MONGO_PORT", 27017),
            username=app.config.get("MONGO_USERNAME", None),
            password=app.config.get("MONGO_PASSWORD", None),
            uri=app.config.get("MONGO_URI", None),
            mongodb=db_name,
        )

        app.config["MONGO_DATABASE"] = client[db_name]
        app.config["MONGO_CLIENT"] = client

    def __repr__(self):
        return f"{self.__class__.__name__}"
