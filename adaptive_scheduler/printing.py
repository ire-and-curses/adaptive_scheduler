'''
printing.py - Functions to pretty-print objects.

TODO: These should be folded into the __str__ or __repr__ methods of the actual
objects, but are here for now to preserve those object's APIs.

Author: Eric Saunders
December 2011
'''

from adaptive_scheduler.utils import datetime_to_normalised_epoch
from adaptive_scheduler.log   import RequestGroupLogger
from datetime import timedelta

INDENT = "    "

# Set up and configure a module scope logger
import logging
log = logging.getLogger(__name__)


multi_rg_log = logging.getLogger('rg_logger')
rg_log = RequestGroupLogger(multi_rg_log)


def summarise_rgs(request_groups, log_msg):
    log.debug("Request Group breakdown:")
    for rg in request_groups:
        r_nums  = [r.id for r in rg.requests]
        w_total = sum([r.n_windows() for r in rg.requests])
        _, w_str = pluralise(w_total, 'Window')
        r_total, r_str = pluralise(len(rg.requests), 'Request')
        r_states = [r.state for r in rg.requests]

        sum_str = ' %d: %s (%d %s, %d %s) %s'
        log.debug(sum_str, rg.id, r_nums,
                  r_total, r_str, w_total, w_str, r_states)
        msg = log_msg + sum_str
        rg_log.info(msg % (rg.id, r_nums,
                           r_total, r_str, w_total, w_str, r_states), rg.id)

    return


def log_windows(rg, log_msg):
    for r in rg.requests:
        for w in r.windows:
            rg_log.info("%s %s" % (log_msg, w), rg.id)


def log_full_rg(rg, now):
    rg_log.info("Expires = %s" % rg.expires, rg.id)
    rg_log.info("IPP Value = %s" % rg.ipp_value, rg.id)
    rg_log.info("Base Priority = %s" % rg.get_base_priority(), rg.id)
    rg_log.info("Effective Priority = %s" % rg.priority, rg.id)
    rg_log.info("Operator = %s" % rg.operator, rg.id)

    for r in rg.requests:
        rg_log.info("Request %d: duration = %ss" % (r.id, r.duration),
                    rg.id)
        rg_log.info("Request %d: target = %s" % (r.id, r.target),
                    rg.id)
        rg_log.info("Request %d: constraints = %s" % (r.id, r.constraints),
                    rg.id)


def print_reservation(res):
    log.debug(res)
    for resource, interval in res.possible_windows_dict.iteritems():
        log.debug("Possible windows: %s -> %s" % ( resource, interval ))

    return


def plural_str(n, string):
    n, string = pluralise(n, string)
    return "%d %s" % (n, string)


def pluralise(n, string):
    if n != 1:
        string += 's'

    return n, string


def print_compound_reservation(compound_res):
    log.debug("CompoundReservation (%s):", compound_res.type)

    log.debug(INDENT + "made of %d %s:", *pluralise(compound_res.size, 'Reservation'))
    for res in compound_res.reservation_list:
        print_reservation(res)

    return


def print_request(req, resource_name):
    target_name = getattr(req.target, 'name', 'no name')
    log.debug("Request %s: Target %s, observed from %s",req.id,
                                                        target_name,
                                                        resource_name)



def print_req_summary(req, resource_name, user_intervals, rs_dark_intervals,
                      rs_up_intervals, intersection):
    print_request(req, resource_name)
    # Pull out the timepoint list for printing
    intervals = user_intervals.toTupleList()
    if not intervals:
        log.debug("No user intervals found")
        return
    else:
        earliest_tp = latest_tp = intervals[0][0]

    for (start, end) in intervals:
        log.debug("    User window:          %s to %s", start, end)
        if start < earliest_tp:
            earliest_tp = start
        if end > latest_tp:
            latest_tp = end

    for dark_int in rs_dark_intervals:
        if dark_int[0] < latest_tp+timedelta(days=1) and dark_int[1] > earliest_tp - timedelta(days=1):
            log.debug("    Darkness:             %s to %s", dark_int[0], dark_int[1])

    for up_int in rs_up_intervals:
        if up_int[0] < latest_tp+timedelta(days=1) and up_int[1] > earliest_tp - timedelta(days=1):
            log.debug("    Target above horizon: %s to %s", up_int[0], up_int[1])

    log.debug("    Dark/rise intersections:")
    if not intersection.toDictList():
        log.debug("        <none>")
    else:
        for i in intersection.toDictList():
            log.debug("        %s (%s)", i['time'], i['type'])

    return


def print_resource_windows(resource_windows):
    for resource in resource_windows:
        print resource
        for i in resource_windows[resource].toDictList():
            print i['time'], i['type']

    return


def print_compound_reservations(to_schedule):
    log.info("Finished constructing compound reservations...")
    log.info("There are %d %s to schedule.", *pluralise(len(to_schedule), 'CompoundReservation'))
    for compound_res in to_schedule:
        print_compound_reservation(compound_res)

    return


def print_schedule(schedule, semester_start=None, semester_end=None):

    if semester_start and semester_end:
        epoch_start = datetime_to_normalised_epoch(semester_start, semester_start)
        epoch_end   = datetime_to_normalised_epoch(semester_end, semester_start)

        log.info("Scheduling for semester %s to %s" % (semester_start, semester_end))
        log.info("Scheduling for normalised epoch %s to %s" % (epoch_start, epoch_end))

    for resource_reservations in schedule.values():
        for res in resource_reservations:
            print_reservation(res)

    return


def iprint(string, indent_level=0):
    print (indent_level * INDENT) + string
