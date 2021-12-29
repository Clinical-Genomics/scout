# -*- coding: utf-8 -*-
import logging
import urllib.request

from configobj import ConfigObj

LOG = logging.getLogger(__name__)


class RankModelHandler(object):
    def add_rank_model(self, rank_model_url):
        """Fetch a rank model from remote.

        Args:
            rank_model_url(string): A string with the url to the rank model ini file to fetch.

        Returns:
            rank_model(dict): a copy of what was inserted
        """
        LOG.info("Adding rank model to the database")

        response = urllib.request.urlopen(rank_model_url, timeout=20)
        config = ConfigObj(response).dict()
        config.update({"_id": rank_model_url})
        config_id = self.rank_model_collection.insert_one(config).inserted_id
        rank_model = self.rank_model_collection.find_one(config_id)

        return rank_model

    def rank_model(self, rank_model_version=None):
        """Fetch a rank model from the database or fetch it from remote.

        Args:
            rank_model_version(string)

        Returns:
            rank_model(dict)
        """
        if not (rank_model_version):
            LOG.warning("No key provided for rank_model")
            return None

        rank_model_url = f"https://raw.githubusercontent.com/Clinical-Genomics/reference-files/master/rare-disease/rank_model/rank_model_-v{rank_model_version}-.ini"
        rank_model = self.rank_model_collection.find_one(rank_model_url)

        if not rank_model:
            rank_model = self.add_rank_model(rank_model_url)

        return rank_model
