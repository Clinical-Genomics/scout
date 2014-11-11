#!/usr/bin/env python
# coding: utf-8

import sys
import configparser
from collections import defaultdict

# Import third party library
# https://github.com/mitsuhiko/logbook
from logbook import Logger, StderrHandler
log = Logger('Logbook')
log_handler = StderrHandler()


def read_config(config_file):
    """Reads the config file

    Args:
        config_file (file) : plugin config file

    Returns:
        object: config object
    """
    config = configparser.ConfigParser()

    config.read(config_file)

    return config


def collectKeys(config_file):
    """Collects database keys determined by plug-in and saves them in dict

    Args:
        config_file (file) : plugin config file

    Returns:
        dict: dict[collection][list_of_keys]
    """
    # Create config object
    config = read_config(config_file)

    database_keys = defaultdict(list)

    # Collect keys for plug-in
    for section in config.items():

        # Alias
        key = section[0]
        # Only vcf records
        if 'vcf_record' in config[key]:

            # Only sections that are present as database key
            if key == config[key]["database_field"]:

                # Keys in collection variable
                if config[key]["database_collection"] == "variable":

                    database_keys['variable'].append(key)

                # Keys in collection constant
                if config[key]["database_collection"] == "constant":

                    database_keys['constant'].append(key)
    # Return dict with collection as key and database keys as items in list
    return database_keys


def core(vcf_reader, config_file):
    """Evaluate keys in vcf for core plug-in

    Args:
        vcf_reader  (object) : VCF reader object
        config_file (file) : plugin config file

    Returns:
        int:    1=Not compatible
    """

    # Create config object
    config = read_config(config_file)

    keys = []
    call = []

    # Collect keys for plug-in
    for key in config.items():

        # Save keys to list
        keys.append(key[0])

        # key attributes
        for info in config[key[0]]:

            # Key is a vcf format key
            if info == "vcf_field":

            ## Evaluate keys in config and vcf ##
                if config[key[0]][info] == "INFO":

                    # Key exists in supplied vcf
                    if key[0] not in vcf_reader.infos:

                        log.notice('Plug-in.' +
                                   config['Plug-in']['name'] +
                                   ': Could not find key="' + key[0] +
                                   '" in INFO fields of variant file!'
                                   + '\n'
                                   )
                        return 1

                if config[key[0]][info] == "FILTER":

                    # Key exists in supplied vcf
                    if key[0] not in vcf_reader.filters:

                        log.notice('Plug-in.' +
                                   config['Plug-in']['name'] +
                                   ': Could not find key="' + key[0] +
                                   '" in FILTER of variant file!'
                                   + '\n'
                                   )
                        return 1

                if config[key[0]][info] == "FORMAT":

                    # Key exists in supplied vcf
                    if key[0] in vcf_reader.formats:

                        # Save to call list
                        call.append(key[0])

                    else:
                        log.notice('Plug-in.' +
                                   config['Plug-in']['name'] +
                                   ': Could not find key="' + key[0] +
                                   '" in FORMAT fields of variant file!'
                                   + '\n'
                                   )
                        return 1

                if config[key[0]][info] == "header_line":

                    if config[key[0]]['vcf_record'] == "samples":

                        if len(vcf_reader.samples) == 0:

                            log.warning('Plug-in.' +
                                        config['Plug-in']['name'] +
                                        ': Could not find any samples' +
                                        '" in header line of ' +
                                        'variant file!'
                                        + '\n'
                                        )
