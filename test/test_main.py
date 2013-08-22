#!/usr/bin/env python

from __future__ import division

from nose import SkipTest
from nose.tools import assert_equal

import shlex
adaptive_scheduler = __import__('as')


class TestMain(object):

    def setup(self):
        pass


    def test_main(self):
        raise SkipTest
        args = shlex.split("--run-once -r http://localhost:8001/ -s 1 --dry-run --now '2013-10-01 00:00:00' --telescopes=telescopes.dat")
        adaptive_scheduler.main(args)


    def test_request_db_dirty_flag_is_invalid(self):
        dirty_response = 'lalalala'

        assert_equal(adaptive_scheduler.request_db_dirty_flag_is_invalid(dirty_response), True)