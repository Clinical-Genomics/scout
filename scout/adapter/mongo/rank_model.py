# -*- coding: utf-8 -*-
import logging
from io import StringIO

import requests
from configobj import ConfigObj

LOG = logging.getLogger(__name__)
TIMEUT = 20


class RankModelHandler(object):
    def fetch_rank_model(self, rank_model_url):
        """Send HTTP request to retrieve rank model config file

        Args:
            rank_model_url(str): URL to resource containing rank model configuration

        Returns:
            StringIO(response.text): A StringIO containing the content of the config file
        """
        try:
            response = requests.get(rank_model_url, timeout=TIMEUT)
            return StringIO(response.text)
        except Exception as ex:
            LOG.warning(ex)

    def parse_rank_model(self, stringio):
        """Use configobj lib to extract RankModel key/values and return them in a dictionary

        Args:
            stringio(StringIO): Content of model from a file as a StringIO

        Returns:
            ConfigObj.dict(dictionary): dictionary with variant rank model key/values
        """
        try:
            return ConfigObj(stringio).dict()
        except Exception as ex:
            LOG.error(ex)

    def add_rank_model(self, rank_model_url):
        """Fetch a rank model from remote.

        Args:
            rank_model_url(string): A string with the url to the rank model ini file to fetch.

        Returns:
            rank_model(dict): a copy of what was inserted, or None if failed
        """
        response = self.fetch_rank_model(rank_model_url)

        config = self.parse_rank_model(response)

        if config:
            config.update({"_id": rank_model_url})
            config_id = self.rank_model_collection.insert_one(config).inserted_id
            return self.rank_model_collection.find_one(config_id)

        return {}

    def rank_model_from_url(
        self, rank_model_link_prefix, rank_model_version, rank_model_file_extension
    ):
        """Fetch a rank model configuration for A SNV or SV variant of a case

        Args:
            rank_model_link_prefix(str): specified in app config file
            rank_model_version(string)
            rank_model_file_extension(str): specified in app config file

        Returns:
            rank_model(dict)
        """
        rank_model_url = "".join(
            [rank_model_link_prefix, str(rank_model_version), rank_model_file_extension]
        )

        # Check if rank model document is already present in scout database
        rank_model = self.rank_model_collection.find_one(rank_model_url)

        if not rank_model:  # Otherwise fetch it with HTTP request and save it to database
            rank_model = self.add_rank_model(rank_model_url)

        return rank_model

    def get_ranges_info(self, rank_model, category):
        """Extract Rank model params value ranges from a database model.
        These numbers will be used to describe model scores on variant page.

        Args:
            rank_model(dict)
            category(string) examples: "Variant_call_quality_filter", "Deleteriousness" ..

        Returns:
            info(list) example:
        """
        info = []
        for _, item in rank_model.items():
            if (
                isinstance(item, dict) is False
                or not item.get("category")
                or item.get("category").casefold() != category.casefold()
            ):
                continue
            rank_info = {
                "key": item.get("info_key"),
                "description": item.get("description"),
                "score_ranges": {},
            }
            for key, value in item.items():
                if isinstance(value, dict) and "score" in value:
                    rank_info["score_ranges"][key] = value
            info.append(rank_info)

        return info
