# coding=UTF-8
import logging
import re
from os.path import abspath, exists, isabs

LOG = logging.getLogger(__name__)

REQUIRED_FIELDS = ["name", "type", "url"]
TRACK_KEYS = ["name", "type", "format", "url", "indexURL"]
URL_PATTERN = re.compile("https?://")

from typing import List


class AlignTrackHandler:
    """Class collecting external IGV tracks stored in the cloud"""

    def init_app(self, app):
        self.tracks = self.set_custom_tracks(
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
        else:
            raise FileNotFoundError(
                f"One or more custom tracks specified in the config file could not be used, Please provide all required keys:{REQUIRED_FIELDS}"
            )

    def set_local_track_path(self, path: str) -> str:
        """Returns the complete path to a local igv track file"""
        if exists(path) and isabs(path):
            return path
        elif exists(path):
            return abspath(path)
        else:
            raise FileNotFoundError(f"Could not verify path to IGV track:{path}")

    def set_custom_tracks(self, track_dictionaries: List[dict]) -> dict:
        """Return a list of IGV tracks collected from the config settings

        Args:
            track_dictionaries: a list of cloud bucket dictionaries containing IGV tracks, can be public or private
        """
        custom_tracks = {"37": [], "38": []}
        # Loop over the bucket list and collect all public tracks
        for track_category in track_dictionaries:
            for track in track_category.get("tracks", []):
                build = track.get("build")
                if build not in ["37", "38"]:
                    LOG.warning(
                        "One or more IGV public tracks could not be used, Please provide a genome build ('37', '38') for it."
                    )
                    continue
                track_obj = self.track_template(track)

                if not URL_PATTERN.search(track_obj["url"]):  # It's a local file
                    track_obj["url"] = self.set_local_track_path(track_obj["url"])

                custom_tracks[build].append(track_obj)
        return custom_tracks
