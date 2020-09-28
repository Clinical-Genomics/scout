import logging

LOG = logging.getLogger(__name__)


def export_transcripts(adapter, build="37"):
    """Export all transcripts from the database

    Args:
        adapter(scout.adapter.MongoAdapter)
        build(str)

    Yields:
        transcript(scout.models.Transcript)
    """
    LOG.info("Exporting all transcripts")

    for tx_obj in adapter.transcripts(build=build):
        yield tx_obj
