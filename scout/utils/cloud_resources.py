# coding=UTF-8
import logging

LOG = logging.getLogger(__name__)

REQUIRED_FIELDS = ["name", "type", "url"]
TRACK_KEYS = ["name", "type", "format", "url", "indexURL"]


class AlignTrackHandler:
    """Class collecting external IGV tracks stored in the cloud"""

    def init_app(self, app):
        self.public_tracks = self.set_public_tracks(app.config["CLOUD_IGV_TRACKS"])

    def track_template(self, track_info):
        """Provides the template for a VCF track object"""
        track = {}

        for key in TRACK_KEYS:
            if key in track_info:
                track[key] = track_info[key]

        # Save track only of it contains the minimal required keys
        if all(track.get(key) for key in REQUIRED_FIELDS):
            return track

    def set_public_tracks(self, bucket_list):
        """Return a list of public IGV tracks stored on the cloud

        Args:
            bucket_list(list): a list of cloud bucket dictionaries containing IGV tracks, can be public or private

        Returns:
            public_tracks(dict): a list of public access tracks stored on the cloud, where key is genome build
        """
        public_tracks = {}
        # Loop over the bucket list and collect all public tracks
        for bucket_obj in bucket_list:
            if bucket_obj.get("access") == "private" or None:
                continue
            for track in bucket_obj.get("tracks", []):
                build = track.get("build")
                if build not in ["37", "38"]:
                    LOG.warning(
                        f"One or more IGV cloud public tracks could not be used, Please provide a genome build ('37', '38') for it."
                    )
                    continue
                track_obj = self.track_template(track)
                if track_obj is None:
                    LOG.warning(
                        f"One or more IGV cloud public tracks could not be used, Please provide all required keys:{REQUIRED_FIELDS}"
                    )
                    continue
                if build in public_tracks:
                    public_tracks[build].append(track_obj)
                else:
                    public_tracks[build] = [track_obj]

        if public_tracks != {}:
            return public_tracks
