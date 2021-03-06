######################################################################
#
# File: test/v1/test_sync_report.py
#
# Copyright 2019 Backblaze Inc. All Rights Reserved.
#
# License https://www.backblaze.com/using_b2_code.html
#
######################################################################

from __future__ import print_function

from .test_base import TestBase

from .deps import SyncReport

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock


class TestSyncReport(TestBase):
    def test_bad_terminal(self):
        stdout = MagicMock()
        stdout.write = MagicMock(
            side_effect=[
                UnicodeEncodeError('codec', u'foo', 100, 105, 'artificial UnicodeEncodeError')
            ] + list(range(25))
        )
        sync_report = SyncReport(stdout, False)
        sync_report.print_completion('transferred: 123.txt')
