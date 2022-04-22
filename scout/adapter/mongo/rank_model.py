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

    def get_rank_score_ranges(self, variant, rank_model):
        """Calculate rank ranges for the variant and its corresponding rank model."""

        def get_scores(field):
            return [
                int(v.get("score"))
                for v in field.values()
                if isinstance(v, dict) and isinstance(int(v.get("score")), (int))
            ]

        def get_category_abbr(category_name):
            category_names = category_name.split(" ")

            return (
                "".join([x[0].upper() for x in category_names])
                if len(category_names) > 1
                else category_name
            )

        def get_rank(model, info_fields, variant, category):
            fields = [f for f in info_fields if f.get("category") == category]
            scores = [get_scores(field) for field in fields]
            flattend_scores = [n for v in scores for n in v]

            # finds the already pre-calculated score
            rank_score = next(
                (r for r in variant.get("rank_score_results") if r.get("category") == category), {}
            )
            category_name = category.replace("_", " ").title()
            return {
                "category": category_name,
                "category_abbreviation": get_category_abbr(category_name),
                "score": rank_score.get("score"),
                "min": min(flattend_scores) if flattend_scores else "n.a",
                "max": max(flattend_scores) if flattend_scores else "n.a",
            }

        def get_rank_score_results(rank_model):
            info_fields = [
                v for v in rank_model.values() if isinstance(v, dict) and v.get("field") == "INFO"
            ]

            return [
                get_rank(rank_model, info_fields, variant, category)
                for category in rank_model["Categories"].keys()
            ]

        try:
            appo = get_rank_score_results(rank_model)
            return sorted(appo, key=lambda k: k["category"].casefold())
        except Exception as ex:
            return []
