'''
model.py - Data model of the adaptive scheduler.

This module provides the model objects which form the adaptive scheduler's domain.
It includes representations of targets, telescopes and observable time slots.

Author: Eric Saunders
November 2011
'''

# Required for true (non-integer) division
from __future__ import division

from adaptive_scheduler.utils import EqualityMixin
from adaptive_scheduler.exceptions import InvalidRequestError
from adaptive_scheduler.kernel.reservation_v2 import CompoundReservation_v2 as CompoundReservation

from rise_set.sky_coordinates import RightAscension, Declination



class DataContainer(EqualityMixin):
    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])


class Target(DataContainer):

    def list_missing_fields(self):
        req_fields = ('ra', 'dec')
        missing_fields = []

        for field in req_fields:
            try:
                getattr(self, field)
            except:
                missing_fields.append(field)

        return missing_fields

    # Use accessors to ensure we always have valid coordinates
    def get_ra(self):
        return self._ra

    def set_ra(self, ra):
        self._ra = RightAscension(ra)

    def set_dec(self, dec):
        self._dec = Declination(dec)

    def get_dec(self):
        return self._dec

    ra  = property(get_ra, set_ra)
    dec = property(get_dec, set_dec)



class Telescope(DataContainer):
    pass


class Window(DataContainer):
    pass


class Proposal(DataContainer):
    def list_missing_fields(self):
        req_fields = ('proposal_name', 'proposal_id',
                      'user_name', 'user_id',
                      'tag')
        missing_fields = []

        for field in req_fields:
            try:
                getattr(self, field)
            except:
                missing_fields.append(field)

        return missing_fields



class Molecule(DataContainer):
    #TODO: This is really an expose_n molecule, so should be specialised
    #TODO: Specialisation will be necessary once other molecules are scheduled

    def list_missing_fields(self):
        req_fields = ('type', 'exposure_count', 'bin_x', 'bin_y',
                      'instrument_name', 'filter', 'exposure_time')
        missing_fields = []

        for field in req_fields:
            try:
                getattr(self, field)
            except:
                missing_fields.append(field)

        return missing_fields



class Request(EqualityMixin):
    '''
        Represents a single valid configuration where an observation could take
        place. These are combined within a CompoundRequest to allow AND and OR
        semantics ("do this and this and this", "do this or this").

        target    - a Target object (pointing information)
        molecule  - a Molecule object (detailed observing information)
        windows   - a list of start/end datetimes, representing when this observation
                    is eligible to be performed. For user observations with no
                    time constraints, this should be the planning window of the
                    scheduler (e.g. the semester bounds).
        duration  - exposure time of each observation. TODO: Clarify what this means.

        # Optional arguments (normally one of these will be specified):
        telescope_name - the name of a Telescope, or class of Telescope
        telescope      - a Telescope object (lat/long information)
    '''

    def __init__(self, target, molecule, windows, duration,
                 telescope_name=None, telescope=None):

        self.target         = target
        self.molecule       = molecule
        self.windows        = windows
        self.duration       = duration

        if telescope_name:
            self.telescope_name = telescope_name

        # This is expected to be set later, but is provided as a convenience
        if telescope:
            self.telescope      = telescope
            self.telescope_name = telescope.name



class CompoundRequest(EqualityMixin):
    '''
        A user-level request for an observation. This will be translated into the
        Reservation/CompoundReservation of the scheduling kernel.

        operator - the type of compound request (single, and, oneof)
        proposal - proposal meta information associated with this request
        requests - a list of Request objects. There must be at least one.
    '''

    valid_types = CompoundReservation.valid_types

    def __init__(self, operator, requests):
        self.res_type  = self._validate_type(res_type)
        self.requests  = requests


    def _validate_type(self, provided_type):
        '''Check the type being asked for matches a valid type
           of CompoundObservation.'''

        if provided_type not in CompoundRequest.valid_types:

            error_msg = ("You've asked for a type of request that doesn't exist. "
                         "Valid types are:\n")

            for res_type, help_txt in CompoundRequest.valid_types.iteritems():
                error_msg += "    %9s - %s\n" % (res_type, help_txt)

            raise InvalidRequestError(error_msg)

        return provided_type



class UserRequest(CompoundRequest):

    def __init__(self, operator, requests, proposal, expires):
        CompoundRequest.__init__(self, operator, requests)

        self.proposal = proposal
        self.expires  = expires
