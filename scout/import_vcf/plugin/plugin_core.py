#!/usr/bin/env python
# coding: utf-8

import configparser

config = configparser.ConfigParser()

config['Plug-in'] = {'name': 'core'}

config['samples'] = {'vcf_field': 'header_line',
                     'vcf_record': 'samples',
                     'vcf_reader': 'samples',
                     'database_collection': 'variable',
                     'database_field': 'samples'
                     }
config['GT'] = {'vcf_field': 'FORMAT',
                'vcf_record': 'genotype',
                'database_collection': 'variable',
                'database_field': 'samples'
                }
config['AD'] = {'vcf_field': 'FORMAT',
                'vcf_record': 'genotype',
                'database_collection': 'variable',
                'database_field': 'samples'
                }
config['DP'] = {'vcf_field': 'FORMAT',
                'vcf_record': 'genotype',
                'database_collection': 'variable',
                'database_field': 'samples'
                }
config['GQ'] = {'vcf_field': 'FORMAT',
                'vcf_record': 'genotype',
                'database_collection': 'variable',
                'database_field': 'samples'
                }
config['PL'] = {'vcf_field': 'FORMAT',
                'vcf_record': 'genotype',
                'database_collection': 'variable',
                'database_field': 'samples'
                }
config['CHROM'] = {'vcf_field': 'header_line',
                   'vcf_record': 'CHROM',
                   'database_collection': 'variable',
                   'database_field': 'CHROM'
                   }
config['POS'] = {'vcf_field': 'header_line',
                 'vcf_record': 'POS',
                 'database_collection': 'variable',
                 'database_field': 'POS'
                 }
config['ID'] = {'vcf_field': 'header_line',
                'vcf_record': 'ID',
                'database_collection': 'constant',
                'database_field': 'ID'
                }
config['REF'] = {'vcf_field': 'header_line',
                 'vcf_record': 'REF',
                 'database_collection': 'variable',
                 'database_field': 'REF'
                 }
config['ALT'] = {'vcf_field': 'header_line',
                 'vcf_record': 'ALT',
                 'database_collection': 'variable',
                 'database_field': 'ALT'
                 }
config['QUAL'] = {'vcf_field': 'header_line',
                  'vcf_record': 'QUAL',
                  'database_collection': 'variable',
                  'database_field': 'QUAL'
                  }
config['FILTER'] = {'vcf_field': 'header_line',
                    'vcf_record': 'FILTER',
                    'database_collection': 'variable',
                    'database_field': 'FILTER'
                    }
config['INFO'] = {'vcf_field': 'header_line',
                  'vcf_record': 'INFO',
                  'database_collection': 'variable',
                  'database_field': 'INFO'
                  }
config['_id'] = {'database_field': '_id',
                 'database_collection': 'variable',
                 }

with open('get_core.ini', 'w') as configfile:
    config.write(configfile)
