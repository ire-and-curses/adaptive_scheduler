#!/usr/bin/env python

'''
Bipartite scheduler.

Author: Sotiria Lampoudi (slampoud@cs.ucsb.edu)
November 2011
'''

from reservation_v2 import *

class BipartiteScheduler(object):

    def __init__(self, reservation_list, resource_list):
        self.reservation_list       = reservation_list
        self.scheduled_reservations = []
        self.resource_list          = resource_list
        self.reservations_by_resource_dict = {}
        for resource in resource_list:
            self.reservations_by_resource_dict[resource] = []
        for reservation in reservation_list:
            if reservation.resource in resource_list:
                self.reservations_by_resource_dict[reservation.resource].append(reservation)
            else: 
                print "what's this reservation doing here?"


    def schedule(self):
        constraint_graph = {}
        # calculate quantum as max of all request lengths, per resource
        for resource in self.resource_list:
            quantum = self.max_duration(self.reservations_by_resource_dict[resource])
            for r in self.reservations_by_resource_dict[resource]:
                # quantize free windows of opportunity for each reservation 
                # (first checks which windows of opportunity are still free)
                quantum_starts = self.quantize_windows(r, quantum)
                # add to graph
                constraint_graph[r.get_ID()] = quantum_starts
        # run bipartitematch on graph
        output = bipartiteMatch(constraint_graph)
        matching = output[0]
        for quantum_start, reservation_ID in matching.iteritems():
            r = self.get_reservation_by_ID(reservation_ID)
            [resource, start, quantum] = self.unhash_quantum_start(quantum_start)
            r.schedule(start, quantum, 'bipartite scheduler')
            self.scheduled_reservations.append(r)
        return self.scheduled_reservations


    def max_duration(self, reservation_list):
        duration = -1
        for r in reservation_list:
            if r.duration > duration:
                duration = r.duration
        return duration


    def quantize_windows(self, reservation, quantum):
        quantum_starts = []
        resource = reservation.resource
        qss = reservation.free_windows.get_quantum_starts(quantum)
        for qs in qss:
            quantum_starts.append(self.hash_quantum_start(resource, qs, quantum))
        return quantum_starts


    def hash_quantum_start(self, resource, start, quantum):
        return "resource_"+resource+"_start_"+repr(start)+"_quantum_"+repr(quantum)


    def unhash_quantum_start(self, mystr):
        l = mystr.split("_")
        return [l[1], int(l[3]), int(l[5])]



    def get_reservation_by_ID(self, ID):
        for r in self.reservation_list:
            if r.get_ID() == ID:
                return r
        return None


# Hopcroft-Karp bipartite max-cardinality matching and max independent set
# David Eppstein, UC Irvine, 27 Apr 2002
def bipartiteMatch(graph):
    '''Find maximum cardinality matching of a bipartite graph (U,V,E).
    The input format is a dictionary mapping members of U to a list
    of their neighbors in V.  The output is a triple (M,A,B) where M is a
    dictionary mapping members of V to their matches in U, A is the part
    of the maximum independent set in U, and B is the part of the MIS in V.
    The same object may occur in both U and V, and is treated as two
    distinct vertices if this happens.'''
    
    # initialize greedy matching (redundant, but faster than full search)
    matching = {}
    for u in graph:
        for v in graph[u]:
            if v not in matching:
                matching[v] = u
                break

    while 1:
        # structure residual graph into layers
        # pred[u] gives the neighbor in the previous layer for u in U
        # preds[v] gives a list of neighbors in the previous layer for v in V
        # unmatched gives a list of unmatched vertices in final layer of V,
        # and is also used as a flag value for pred[u] when u is in the first layer
        preds = {}
        unmatched = []
        pred = dict([(u,unmatched) for u in graph])
        for v in matching:
            del pred[matching[v]]
        layer = list(pred)

        # repeatedly extend layering structure by another pair of layers
        while layer and not unmatched:
            newLayer = {}
            for u in layer:
                for v in graph[u]:
                    if v not in preds:
                        newLayer.setdefault(v,[]).append(u)
            layer = []
            for v in newLayer:
                preds[v] = newLayer[v]
                if v in matching:
                    layer.append(matching[v])
                    pred[matching[v]] = v
                else:
                    unmatched.append(v)

        # did we finish layering without finding any alternating paths?
        if not unmatched:
            unlayered = {}
            for u in graph:
                for v in graph[u]:
                    if v not in preds:
                        unlayered[v] = None
            return (matching,list(pred),list(unlayered))

        # recursively search backward through layers to find alternating paths
        # recursion returns true if found path, false otherwise
        def recurse(v):
            if v in preds:
                L = preds[v]
                del preds[v]
                for u in L:
                    if u in pred:
                        pu = pred[u]
                        del pred[u]
                        if pu is unmatched or recurse(pu):
                            matching[v] = u
                            return 1
            return 0

        for v in unmatched: recurse(v)