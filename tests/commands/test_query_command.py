#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from scout.commands import app_cli
from scout.server.extensions import store

def test_hgnc(adapter, mock_app, parsed_gene):
    """Testing the CLI that queries for hgnc aliases"""

    store = adapter

    runner = mock_app.test_cli_runner()
    assert runner

    #insert mock gene in mock database:
    store.hgnc_collection.insert_one(parsed_gene)
    assert store.hgnc_collection.find().count() == 1

    # test query by hgnc_symbol
    result =  runner.invoke(app_cli, ['query', 'hgnc', '-s' , parsed_gene['hgnc_symbol']])
    assert result.exit_code == 0

    # test query by hgnc id
    result =  runner.invoke(app_cli, ['query', 'hgnc', '--hgnc-id', '1'])
    assert result.exit_code == 0

    # test query by hgnc id and build
    result =  runner.invoke(app_cli, ['query', 'hgnc', '--hgnc-id', '1', '-b', '37'])
    assert result.exit_code == 0
