from __future__ import absolute_import

import os
import logging
from datetime import datetime

from . import STATUS

# from scout.constants import ANALYSIS_TYPES


logger = logging.getLogger(__name__)


class Myy(dict):
    def __keytransform__(self, key):
        return key

    def __init__(self):
        super(Myy, self).__init__()

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, x):
        self.__x = x

    def __getitem(self, key):
        return dict.__getitem__(self, self.__keytransform__(key))

    def __setitem__(self, key, value):
        if key == "y" and isinstance(value, str) is not True:
            raise KeyError
        return dict.__setitem__(self, self.__keytransform__(key), value)


class Individual(dict):
    def __init__(
        self,
        individual_id=None,
        display_name=None,
        sex=None,
        phenotype=None,
        father=None,
        mother=None,
        capture_kits=None,
        bam_file=None,
        rhocall_bed=None,
        rhocall_wig=None,
        tiddit_coverage_wig=None,
        upd_regions_bed=None,
        upd_sites_bed=None,
        vcf2cytosure=None,
        analysis_type=None,
        confirmed_sex=None,
        confirmed_parent=None,
        is_sma=None,
        is_sma_carrier=None,
        smn1_cn=None,
        smn2_cn=None,
        smn2delta78_cn=None,
        smn_27134_cn=None,
        predicted_ancestry=None,
        tumor_type=None,
        tmb=None,
        msi=None,
        tumor_purity=None,
        tissue_type=None,
    ):
        self["individual_id"] = individual_id  # required =str
        self["display_name"] = display_name
        self["sex"] = sex
        self["phenotype"] = phenotype
        self["father"] = father  # Individual id of father
        self["mother"] = mother  # Individual id of mother
        self["capture_kits"] = capture_kits  # List of names of capture kits
        self["bam_file"] = bam_file  # Path to bam file
        self["rhocall_bed"] = rhocall_bed  # Path to bed file
        self["rhocall_wig"] = rhocall_wig  # Path to wig file
        self["tiddit_coverage_wig"] = tiddit_coverage_wig  # Path to wig file
        self["upd_regions_bed"] = upd_regions_bed  # Path to bed file
        self["upd_sites_bed"] = upd_sites_bed  # Path to bed file
        self["vcf2cytosure"] = vcf2cytosure  # Path to CGH file
        self["analysis_type"] = analysis_type  # choices=ANALYSIS_TYPES
        self["confirmed_sex"] = confirmed_sex  # True or False. None if no check has been done
        self["confirmed_parent"] = confirmed_parent
        self["is_sma"] = is_sma  # True / False if SMA status determined - None if not done.
        self[
            "is_sma_carrier"
        ] = is_sma_carrier  # True/False if SMA carriership determined - None if not done.
        self["smn1_cn"] = smn1_cn  # CopyNumber
        self["smn2_cn"] = smn2_cn  # CopyNumber
        self["smn2delta78_cn"] = smn2delta78_cn  # CopyNumber
        self["smn_27134_cn"] = smn_27134_cn  # CopyNumber
        self["predicted_ancestry"] = predicted_ancestry  # one of AFR AMR EAS EUR SAS UNKNOWN
        self["tumor_type"] = tumor_type
        self["tmb"] = tmb
        self["msi"] = msi
        self["tumor_purity"] = tumor_purity
        self["tissue_type"] = tissue_type
        super(Individual, self).__init__()

        def __getitem(self, key):
            return dict.__getitem__(self, self.__keytransform__(key))

        def __setitem__(self, key, value):
            if key == "case_id" and isinstance(value, str) is not True:
                raise KeyError
            if key == "phenotype" and isinstance(value, int) is not True:
                raise KeyError
            if (
                key == "predicted_ancestry"
                and value in ["AFR", "AMR", "EAS", "EUR", "SAS", "UNKNOWN", None] is False
            ):
                raise KeyError
            return dict.__setitem__(self, self.__keytransform__(key), value)
