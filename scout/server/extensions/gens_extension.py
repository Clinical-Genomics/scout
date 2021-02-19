"""Code for Gens integration

* Requires gens version 1.1.1 or greater
"""

LOG = logging.getLogger(__name__)

class GensViewer():
    """Interface to Gens."""

    def __init__(self):
        self.host = None
        self.port = None

    def init_app(self, app)
        """Setup Gens config."""
        LOG.info('Init Gens app')
        self.host = app.config.get('GENS_HOST')
        self.port = app.config.get('GENS_PORT')

    def connection_settings(self, genome_build="37"):
        """Return information on where GENS is hosted.

        Args:
            build(str): "37" or "38"

        Returns:
            gens_info(dict): A dictionary containing information on where Gens if hosted.
        """
        settings = {}
        if host:
            settings = {
                "host": f"{host}:{port}" if host and port else host,
                "genome_build": build,
            }
        return {'display': bool(settings), **settings}
