# -*- coding: utf-8 -*-

from scout.server.blueprints.managed_variants import controllers


def test_upload_managed_variants(adapter, managed_variants_lines):
    # when calling upload_managed_variants for these lines
    test_user = "noone"
    test_institutes = ["cust000"]

    result = controllers.upload_managed_variants(
        adapter, managed_variants_lines, test_institutes, test_user
    )
    # THEN all lines are correctly parsed
    assert result[0] == 3
    assert result[1] == 3
