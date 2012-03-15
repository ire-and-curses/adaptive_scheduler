#!/usr/bin/env python

'''
pond.py - Facade to the pond_client library.

This module provides the scheduler's interface for constructing POND objects.
It maps objects across domains from 1) -> 2) (described below).

1) A complete scheduled observation in this facade needs the following:
    * A ScheduledBlock made up of
            * A Proposal object
        * One or more Molecules, each made up of
            * A set of Molecule-specific parameters
            * A Target, if applicable


2) A complete scheduled observation in the POND needs the following:
    * A ScheduledBlock made up of
        * One or more Observations, each made up of
            * A set of Observation-specific parameters
            * A Pointing, if applicable

   Meta information about Observations is added by means of Group objects.

Author: Eric Saunders
February 2012
'''

from adaptive_scheduler.model import Proposal, Target
from lcogt.pond import pond_client


class Block(object):

    def __init__(self, location, start, end, group_id, priority=0):
        # TODO: Extend to allow datetimes or epoch times (and convert transparently)
        self.location  = location
        self.start     = start
        self.end       = end
        self.group_id  = group_id
        self.priority  = priority

        self.proposal  = Proposal()
        self.molecules = []
        self.target    = Target()

        # TODO: For now, assume all molecules have the same priority
        self.OBS_PRIORITY = 1

        self.pond_block = None


    def list_missing_fields(self):
        # Find the list of missing proposal fields
        proposal_missing = self.proposal.list_missing_fields()

        # Find the list of missing molecule fields
        molecule_missing = ['[No molecules specified]']
        if len(self.molecules) > 0:
            molecule_missing = []
            for molecule in self.molecules:
                molecule_missing.extend(molecule.list_missing_fields())

        # Find the list of missing target fields
        target_missing = self.target.list_missing_fields()

        # Aggregate the missing fields to return
        missing_fields = {}

        if len(proposal_missing) > 0:
            missing_fields['proposal'] = proposal_missing

        if len(molecule_missing) > 0:
            missing_fields['molecule'] = molecule_missing

        if len(target_missing) > 0:
            missing_fields['target'] = target_missing


        return missing_fields


    def add_proposal(self, proposal):
        self.proposal = proposal

    def add_molecule(self, molecule):
        # TODO: Handle molecule priorities
        self.molecules.append(molecule)

    def add_target(self, target):
        self.target = target

    def create_pond_block(self):
        # Check we have everything we need
        missing_fields = self.list_missing_fields()
        if len(missing_fields) > 0:
            raise IncompleteBlockError(missing_fields)

        # Construct the POND objects...
        # 1) Create a POND ScheduledBlock
        site, observatory, telescope = self.split_location()
        pond_block = pond_client.ScheduledBlock(
                                                 start       = self.start,
                                                 end         = self.end,
                                                 site        = site,
                                                 observatory = observatory,
                                                 telescope   = telescope,
                                                 priority    = self.priority
                                                )

        # 2) Create a Group
        pond_group = pond_client.Group(
                                        tag_id   = self.proposal.tag,
                                        user_id  = self.proposal.user,
                                        prop_id  = self.proposal.proposal_name,
                                        group_id = self.group_id
                                      )

        # 3) Construct the Pointing
        pond_pointing = pond_client.Pointing.sidereal(
                                          source_name  = self.target.name,
                                          ra           = self.target.ra.in_degrees(),
                                          dec          = self.target.dec.in_degrees(),
                                          )

        # 4) Construct the Observations
        observations = []
        for molecule in self.molecules:
            obs = pond_group.add_expose(
                                         cnt    = molecule.count,
                                         len    = molecule.duration,
                                         bin    = molecule.binning,
                                         inst   = molecule.instrument_name,
                                         filter = molecule.filter,
                                         target = pond_pointing,
                                        )
            observations.append(obs)

        # 5) Add the Observations to the Block
        for obs in observations:
            pond_block.add_obs(obs, self.OBS_PRIORITY)

        self.pond_block = pond_block

        return pond_block


    def split_location(self):
        '''
            If the location is of the form telescope.observatory.site, then
            extract those separate components and return them. Otherwise, return
            the full location in the place of each component without splitting.

            Examples:  '0m4a.aqwb.coj' -> (0m4a, aqwb, coj)
                       'Maui'          -> (Maui, Maui, Maui)
        '''
        # Split on full stops (sometimes obscurely also known as periods)
        DELIMITER = '.'

        # Number of sections making up the full location string
        N_COMPONENTS = 3

        separated = tuple(self.location.split(DELIMITER))

        if len(separated) == N_COMPONENTS:
            return separated

        # Separation wasn't possible. Selling a house is all about:
        return (self.location, self.location, self.location)


    def send_to_pond(self):
        if not self.pond_block:
            self.create_pond_block()

        self.pond_block.save()

        return



def make_simple_pond_block(compound_reservation, semester_start):
    '''Create a minimal POND block, with no molecule information. This is not
       useful for realistic requests, but helpful for debugging and simulation.'''

    dt_start, dt_end = get_cr_datetimes(compound_reservation, semester_start)

    pond_block = pond_client.ScheduledBlock(
                                         start       = dt_start,
                                         end         = dt_end,
                                         site        = compound_reservation.resource,
                                         observatory = compound_reservation.resource,
                                         telescope   = compound_reservation.resource,
                                         priority    = compound_reservation.priority
                                        )
    return pond_block


def make_simple_pond_schedule(schedule, semester_start):
    '''Given a set of Reservations, construct simple POND blocks corresponding to
       them. This is helpful for debugging and simulation.'''

    pond_blocks = []

    for resource_reservations in schedule.values():
        for res in resource_reservations:
            pond_block = make_pond_block(res, semester_start)
            pond_blocks.append(pond_block)

    return pond_blocks


def send_blocks_to_pond(pond_blocks):
    '''Commit a set of POND blocks to the POND endpoint.'''

    for block in pond_blocks:
        block.save()

    return



class IncompleteBlockError(Exception):
    '''Raised when a block is missing required parameters.'''

    def __init__(self, value):
        self.value = value

    def __str__(self):
        message = "The following fields are missing in this Block.\n"
        for param_type in self.value:
            message += "%s:\n" % param_type

            for parameter in self.value[param_type]:
                message += "    %s\n" % parameter

        return message