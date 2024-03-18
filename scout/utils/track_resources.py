# coding=UTF-8
import logging
import re
from os.path import abspath, exists

LOG = logging.getLogger(__name__)

REQUIRED_FIELDS = ["name", "type", "url"]
TRACK_KEYS = ["name", "type", "format", "url", "indexURL"]

from typing import List


class AlignTrackHandler:
    """Class collecting external IGV tracks stored in the cloud"""

    def init_app(self, app):
        self.public_tracks = self.set_custom_tracks(
            app.config.get("CUSTOM_IGV_TRACKS") or app.config.get("CLOUD_IGV_TRACKS")
        )

    def track_template(self, track_info: dict) -> dict:
        """Provides the template for a VCF track object"""
        track = {}

        for key in TRACK_KEYS:
            if key in track_info:
                track[key] = track_info[key]

        # Save track only of it contains the minimal required keys
        if all(track.get(key) for key in REQUIRED_FIELDS):
            return track

    def set_local_track_path(self, path: str) -> str:
        """Returns the complete path to a local igv track file"""
        if exists(path):
            return abspath(path)
        else:
            LOG.error(f"Path to IGV track not found:{path}")

    def set_custom_tracks(self, track_dictionaries: List[dict]) -> dict:
        """Return a list of IGV tracks collected from the config settings

        Args:
            track_dictionaries: a list of cloud bucket dictionaries containing IGV tracks, can be public or private
        """
        custom_tracks = {}
        # Loop over the bucket list and collect all public tracks
        for track_category in track_dictionaries:
            for track in track_category.get("tracks", []):
                build = track.get("build")
                if build not in ["37", "38"]:
                    LOG.warning(
                        f"One or more IGV public tracks could not be used, Please provide a genome build ('37', '38') for it."
                    )
                    continue
                track_obj = self.track_template(track)
                if track_obj is None:
                    LOG.warning(
                        f"One or more IGV cloud public tracks could not be used, Please provide all required keys:{REQUIRED_FIELDS}"
                    )
                    continue

                if bool(re.match("https?://", track_obj["url"])) is False:  # Is a local file
                    track_obj["url"] = self.set_local_track_path(track_obj["url"])

                if build in custom_tracks:
                    custom_tracks[build].append(track_obj)
                else:
                    custom_tracks[build] = [track_obj]

        if custom_tracks != {}:
            return custom_tracks
