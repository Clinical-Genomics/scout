# -*- coding: utf-8 -*-
import logging
from io import StringIO
from os.path import exists

import requests
from configobj import ConfigObj

LOG = logging.getLogger(__name__)
TIMEOUT = 20


class RankModelHandler(object):
    def fetch_rank_model(self, rank_model_url: str) -> StringIO:
        """Send HTTP request to retrieve rank model config file

        Args:
            rank_model_url(str): URL to resource containing rank model configuration

        Returns:
            StringIO(response.text): A StringIO containing the content of the config file
        """
        try:
            response = requests.get(rank_model_url, timeout=TIMEOUT)
            return StringIO(response.text)
        except Exception as ex:
            LOG.warning(ex)

    def read_rank_model(self, rank_model_url) -> StringIO:
        """Read rank model file contents into a StringIO to use same parsing as URL"""

        with open(rank_model_url, "r") as rank_model_file:
            rank_model_lines = rank_model_file.read()

        return StringIO(rank_model_lines)

    def parse_rank_model(self, stringio: StringIO):
        """Use configobj lib to extract RankModel key/values from content of a model from a file as a StringIO
        and return them in a dictionary
        """
        try:
            return ConfigObj(stringio).dict()
        except Exception as ex:
            LOG.error(ex)

    def add_rank_model(self, rank_model_url: str) -> dict:
        """Fetch a rank model ini file from remote.
        If the URL does not start with http, assume it is instead a local file.
        """

        if rank_model_url.startswith("http"):
            rank_model_lines = self.fetch_rank_model(rank_model_url)
        elif exists(rank_model_url):
            rank_model_lines = self.read_rank_model(rank_model_url)

        if config := self.parse_rank_model(rank_model_lines):
            config.update({"_id": rank_model_url})
            config_id = self.rank_model_collection.insert_one(config).inserted_id
            return self.rank_model_collection.find_one(config_id)

        return {}

    def get_rank_model_url(self, variant_obj, case_obj) -> str | None:
        rank_model_version = None
        rm_link_prefix = None
        rm_file_extension = None
        rank_model_url = None

        if variant_obj.get("category") == "sv":
            rank_model_url = case_obj.get("sv_rank_model_url")
            if not rank_model_url:
                rank_model_version = case_obj.get("sv_rank_model_version")
                rm_link_prefix = current_app.config.get("SV_RANK_MODEL_LINK_PREFIX")
                rm_file_extension = current_app.config.get("SV_RANK_MODEL_LINK_POSTFIX")
        else:  # snv, cancer
            rank_model_url = case_obj.get("rank_model_url")
            if not rank_model_url:
                rank_model_version = case_obj.get("rank_model_version")
                rm_link_prefix = current_app.config.get("RANK_MODEL_LINK_PREFIX")
                rm_file_extension = current_app.config.get("RANK_MODEL_LINK_POSTFIX")
        if all([rank_model_version, rm_link_prefix, rm_file_extension]):
            rank_model_url = self.rank_model_url_from_version(
                rank_model_link_prefix=rm_link_prefix,
                rank_model_version=rank_model_version,
                rank_model_file_extension=rm_file_extension,
            )
        return rank_model_url

    def rank_model_url_from_version(
        self, rank_model_link_prefix: str, rank_model_version: str, rank_model_file_extension: str
    ) -> str:
        """Make a rank model URL from version and link prefix- and postfix (passed here, specified in app config)."""
        rank_model_url = "".join(
            [rank_model_link_prefix, str(rank_model_version), rank_model_file_extension]
        )

        return rank_model_url

    def rank_model_from_url(self, rank_model_url: str) -> dict:
        """Fetch a rank model configuration for A SNV or SV variant of a case
        Check if rank model document is already present in scout database.
        Otherwise fetch it with HTTP request and save it to database.
        """

        rank_model = self.rank_model_collection.find_one(rank_model_url) or self.add_rank_model(
            rank_model_url
        )

        return rank_model

    def get_ranges_info(self, rank_model, category):
        """Extract Rank model params value ranges from a database model.
        These numbers will be used to describe model scores on variant page.

        Args:
            rank_model(dict)
            category(string) examples: "Variant_call_quality_filter", "Deleteriousness" ..

        Returns:
            info(list): list of dictionaries containing "key", "description" and "score_ranges" key/values
        """
        rank_model_categories = rank_model.get("Categories")

        category_aggregation = None
        if category in rank_model_categories:
            model_category = rank_model_categories.get(category)
            category_aggregation = model_category.get("category_aggregation", None)

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
                "aggregation_mode": item.get("record_rule"),
                "score_ranges": {},
                "category_aggregation": category_aggregation,
            }
            component_scores = []
            for key, value in item.items():
                if isinstance(value, dict) and "score" in value:
                    rank_info["score_ranges"][key] = value
                    component_scores.append(int(value["score"]))

            rank_info["max"] = max(component_scores)
            rank_info["min"] = min(component_scores)

            info.append(rank_info)

        return info

    def range_span(self, info: list) -> tuple:
        """Determine max and min score range for each rank model category.

        Args:
          info(list): list of dictionaries containing "max", "min", "key", "description" and "score_ranges" key/values
                      One item for e.g. each caller or data source in the rank model category.
                      Also has "category_aggregation" set for each info item, but those should be the same for the whole
                      category.
        Returns:
          (range_min, range_max) tuples
        """
        if not info:
            return ("N/A", "N/A")

        category_aggregation = info[0].get("category_aggregation")
        range_max = 0
        range_min = 0

        if category_aggregation == "sum":
            for component in info:
                range_max = range_max + int(component["max"])
                range_min = range_min + int(component["min"])
        if not category_aggregation or category_aggregation in ["max", "min"]:
            range_max = max([component["max"] for component in info])
            range_min = min([component["min"] for component in info])

        return (range_min, range_max)
