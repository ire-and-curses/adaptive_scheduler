#!/usr/bin/env python

'''
test_orchestrator.py - Tests for the orchestrator module.

description

Author: Eric Saunders
August 2013
'''

from adaptive_scheduler.orchestrator import update_telescope_events, report_scheduling_outcome
from adaptive_scheduler.model2       import Telescope
from adaptive_scheduler.kernel.reservation_v3 import CompoundReservation_v2 as CompoundReservation

from nose.tools import assert_equal
import mock


class TestOrchestrator(object):

    def setup(self):
        pass


    def test_update_telescope_events_no_events(self):
        events = {}
        tels = {
                 '1m0a.doma.lsc' : Telescope(),
                 '1m0a.doma.coj' : Telescope(),
               }

        update_telescope_events(tels, events)

        assert_equal(tels['1m0a.doma.lsc'].events, [])
        assert_equal(tels['1m0a.doma.coj'].events, [])


    def test_update_telescope_events_one_event(self):
        events = {
                   '1m0a.doma.lsc' : ['event1', 'event2'],
                 }
        tels = {
                 '1m0a.doma.lsc' : Telescope(),
                 '1m0a.doma.coj' : Telescope(),
               }

        update_telescope_events(tels, events)

        assert_equal(tels['1m0a.doma.lsc'].events, ['event1', 'event2'])
        assert_equal(tels['1m0a.doma.coj'].events, [])



    def test_report_scheduling_outcome(self):

        class Request(object):
            def __init__(self, request_number):
                self.request_number = request_number

        class Reservation(object):
            def __init__(self, request, mock_cr):
                self.request = request
                self.compound_request = mock_cr


        mock_cr1 = mock.Mock()
        mock_cr2 = mock.Mock()

        res1 = Reservation(Request('0000000001'), mock_cr1)
        res2 = Reservation(Request('0000000002'), mock_cr2)
        reservation_list1 = [res1, res2]
        compound_reservation1 = CompoundReservation(reservation_list1, type='and')
        to_schedule = [compound_reservation1]

        scheduled_reservations = [res2]

        report_scheduling_outcome(to_schedule, scheduled_reservations)

        mock_cr1.emit_user_feedback.assert_called_with('This Request (request number=0000000001) was not scheduled (it clashed)', 'WasNotScheduled')
        mock_cr2.emit_user_feedback.assert_called_with('This Request (request number=0000000002) was scheduled', 'WasScheduled')

