#!/usr/bin/env python

'''
test_fullscheduler_v5.py

Author: Sotiria Lampoudi
August 2012
'''

from nose.tools import assert_equal
from adaptive_scheduler.kernel.timepoint import *
from adaptive_scheduler.kernel.intervals import *
from adaptive_scheduler.kernel.fullscheduler_v5 import *
import copy

class TestFullScheduler_v3(object):

    def setup(self):
        s1 = Intervals([Timepoint(1, 'start'),
                        Timepoint(2, 'end')]) # 1-2
        s2 = Intervals([Timepoint(2, 'start'),
                        Timepoint(4, 'end')]) # --2--4
        s3 = copy.copy(s1)
        s4 = copy.copy(s1)
        s5 = copy.copy(s2)
        s6 = copy.copy(s1)
        s7 = copy.copy(s1)

        self.r1 = Reservation_v3(1, 1, {'foo': s1})
        self.r2 = Reservation_v3(2, 2, {'bar': s2})
        self.r3 = Reservation_v3(1, 1, {'foo': s3})
        self.r4 = Reservation_v3(1, 1, {'foo': s4})
        self.r5 = Reservation_v3(2, 2, {'bar': s5})
        self.r6 = Reservation_v3(1, 2, {'bar': s5})
        self.r7 = Reservation_v3(1, 1, {'bar': s6, 'foo' : s5})
        self.r8 = Reservation_v3(1, 1, {'foo': s6, 'bar' : s7})

        self.cr1 = CompoundReservation_v2([self.r1])
        self.cr2 = CompoundReservation_v2([self.r3, self.r2], 'and')
        self.cr3 = CompoundReservation_v2([self.r4])
        self.cr4 = CompoundReservation_v2([self.r5])
        self.cr5 = CompoundReservation_v2([self.r4, self.r5], 'oneof')
        self.cr6 = CompoundReservation_v2([self.r3])
        self.cr7 = CompoundReservation_v2([self.r2])
        self.cr8 = CompoundReservation_v2([self.r4, self.r6], 'oneof')
        self.cr9 = CompoundReservation_v2([self.r4, self.r1, self.r3], 'oneof')
        self.cr10 = CompoundReservation_v2([self.r7])
        self.cr11 = CompoundReservation_v2([self.r8])

        self.gpw = {}
        self.gpw['foo'] = [Timepoint(1, 'start'), Timepoint(5, 'end')]
        
        self.gpw2 = {}
        self.gpw2['foo'] = Intervals([Timepoint(1, 'start'), Timepoint(5, 'end')], 'free')
        self.gpw2['bar'] = Intervals([Timepoint(1, 'start'), Timepoint(5, 'end')], 'free')

        slice_dict = {}
        slice_dict['foo'] = [0,1]
        slice_dict['bar'] = [0,1]
        self.fs1 = FullScheduler_v5([self.cr1, self.cr2, self.cr3], 
                                    self.gpw2, [], slice_dict)
        self.fs2 = FullScheduler_v5([self.cr1, self.cr4],
                                    self.gpw2, [], slice_dict)
        self.fs3 = FullScheduler_v5([self.cr5],
                                    self.gpw2, [], slice_dict)
        self.fs4 = FullScheduler_v5([self.cr8, self.cr6, self.cr7],
                                    self.gpw2, [], slice_dict)
        self.fs5 = FullScheduler_v5([self.cr10, self.cr2, self.cr3], 
                                    self.gpw2, [], slice_dict)
        self.fs6 = FullScheduler_v5([self.cr11, self.cr2, self.cr3], 
                                    self.gpw2, [], slice_dict)
        

    def test_create(self):
        assert_equal(self.fs1.compound_reservation_list, [self.cr1, self.cr2, self.cr3])
        assert_equal(self.fs1.globally_possible_windows_dict, self.gpw2)
        assert_equal(self.fs1.contractual_obligation_list, [])
        assert_equal(self.fs1.schedule_dict_free['foo'].timepoints[0].time, 1)
        assert_equal(self.fs1.schedule_dict_free['foo'].timepoints[0].type, 
                     'start')
        assert_equal(self.fs1.schedule_dict_free['foo'].timepoints[1].time, 5)
        assert_equal(self.fs1.schedule_dict_free['foo'].timepoints[1].type, 
                     'end')
        

    def test_create_2(self):
        assert_equal(self.fs2.resource_list, ['foo', 'bar'])
        assert_equal(self.fs2.schedule_dict['foo'], [])
        assert_equal(self.fs2.schedule_dict['bar'], [])


    def test_convert_compound_to_simple_1(self):
        assert_equal(self.fs1.reservation_list[0], self.r1)
        assert_equal(self.fs1.reservation_list[1], self.r3)
        assert_equal(self.fs1.reservation_list[2], self.r2)
        assert_equal(self.fs1.reservation_list[3], self.r4)
        assert_equal(self.fs1.and_constraints[0][0], self.r3)
        assert_equal(self.fs1.and_constraints[0][1], self.r2)


    def test_convert_compound_to_simple_2(self):
        assert_equal(self.fs3.reservation_list[0], self.r4)
        assert_equal(self.fs3.reservation_list[1], self.r5)
        assert_equal(self.fs3.oneof_constraints[0][0], self.r4)
        assert_equal(self.fs3.oneof_constraints[0][1], self.r5)


    def test_schedule_all_1(self):
        d = self.fs1.schedule_all()
        assert_equal(self.r1.scheduled, False)
        assert_equal(self.r2.scheduled, True)
        assert_equal(self.r3.scheduled, True)
        assert_equal(self.r4.scheduled, False)


    def test_schedule_all_multi_resource(self):
        d = self.fs5.schedule_all()
        assert_equal(self.r7.scheduled, True)
        assert_equal(self.r2.scheduled, True)
        assert_equal(self.r3.scheduled, True)
        assert_equal(self.r4.scheduled, False)


    def test_schedule_all_multi_resource_2(self):
        d = self.fs6.schedule_all()
        assert_equal(self.r8.scheduled, True)
        assert_equal(self.r2.scheduled, True)
        assert_equal(self.r3.scheduled, True)
        assert_equal(self.r4.scheduled, False)


    def test_schedule_all_2(self):
        d = self.fs2.schedule_all()
        assert_equal(self.r1.scheduled, True)
        assert_equal(self.r5.scheduled, True)
        
    def test_schedule_all_3(self):
        d = self.fs3.schedule_all()
        assert_equal(self.r4.scheduled, False)
        assert_equal(self.r5.scheduled, True)

    def test_schedule_all_4(self):
        d = self.fs4.schedule_all()
        assert_equal(self.r2.scheduled, True)
        assert_equal(self.r6.scheduled, False)
        # either r3 or r4 should be scheduled, not both
        if self.r3.scheduled:
            assert_equal(self.r4.scheduled, False)
        else:
            assert_equal(self.r4.scheduled, True)


    def test_schedule_triple_oneof(self):
        slice_dict = {}
        slice_dict['foo'] = [0,1]
        slice_dict['bar'] = [0,1]
        fs = FullScheduler_v5([self.cr9],
                              self.gpw2, [], slice_dict)
        s = fs.schedule_all()
        # only one should be scheduled

    def test_schedule_5_7_2012(self):
        s1 = Intervals([Timepoint(93710, 'start'), 
                        Timepoint(114484, 'end'),
                        Timepoint(180058, 'start'), 
                        Timepoint(200648, 'end')])
        r1 = Reservation_v3(1, 30, {'foo': s1})
        s2 = copy.copy(s1)
        r2 = Reservation_v3(1, 30, {'goo': s2})

        cr = CompoundReservation_v2([r1,r2], 'oneof')
        gpw = {}
        gpw['foo'] = Intervals([Timepoint(90000, 'start'), 
                                Timepoint(201000, 'end')])
        gpw['goo'] = Intervals([Timepoint(90000, 'start'), 
                                Timepoint(201000, 'end')])
        slice_dict = {}
        slice_dict['foo'] = [90000,60]
        slice_dict['goo'] = [90000,60]
        fs = FullScheduler_v5([cr], gpw, [], slice_dict)
        schedule = fs.schedule_all()
