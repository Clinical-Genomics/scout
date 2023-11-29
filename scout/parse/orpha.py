"""Code for parsing ORPHA formatted files"""
import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict, Iterable

LOG = logging.getLogger(__name__)


# TODO:
#  1)Extract relevant info from tree
#  2) Add typing?
def parse_orpha_en_product6(tree):
    phenotypes_found = {}
    for disorder in tree.iter("Disorder"):
        phenotype = {}
        source = "ORPHA"
        orphacode = disorder.find("OrphaCode").text
        phenotype_id = source + ":" + orphacode
        description = disorder.find("Name").text
        phenotype["description"] = description
        # print('start')
        # print(disorder.find('OrphaCode').text)
        # print(disorder.tag, disorder.attrib)
        # print(disorder.find('Name').text)
        # print('end')
        phenotypes_found[phenotype_id] = phenotype
    return phenotypes_found
