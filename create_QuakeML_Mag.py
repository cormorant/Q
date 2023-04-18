#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import datetime

import numpy as np

from obspy import UTCDateTime

from obspy.core.event import Catalog, Event, Origin, Magnitude#, Pick
#from obspy.core.event import WaveformStreamID
from obspy.geodetics import FlinnEngdahl

USERID = 'PP'

# current station we do
STATION = "HVG"

filename = "hovsgol.dat"


def make_datetime(date, time=None):
    if time is not None:
        string = "%sT%s" % (str(date), str(time))
        #forPy3
        #string = str(date, "utf-8") +"T"+ str(time, "utf-8")
        #string = "%sT%s" % (date, time)
        
        try:
            dt = datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.%f")
            #dt = datetime.datetime.strptime(string, "%d.%m.%YT%H:%M:%S.%f")
        except ValueError:
            dt = datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%S")
    else:
        dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    return dt


if __name__ == "__main__":
    # load original catalog
    
    # DATE_E TIME_E LAT LON M DEPTH
    data = np.loadtxt(filename,
        skiprows=1, delimiter="\t",
        dtype=[
            ('DATE_E', "|U12"),
            ('TIME_E', "|U12"),
            ('LAT', float),
            ('LON', float),
            ('M', float),
            ('DEPTH', float),
        ])
    
    # for every item in DATA, lets find it start_time and FILENAME!
    catalog = Catalog()
    for DATE_E, TIME_E, LAT, LON, M, DEPTH in data:
        # for this date and time, find GSE2 filename
        dt = make_datetime(DATE_E, TIME_E)
        # should also make Event (Obspy object)
        event_time = UTCDateTime(dt)
        
        # prepare other info: picks, coords etc
        o = Origin()
        o.time = dt
        o.latitude = LAT
        o.longitude = LON
        o.depth = DEPTH * 1000
        o.depth_type = "operator assigned"# added
        o.evaluation_mode = "manual"
        o.evaluation_status = "preliminary"
        
        # add magnitude information
        _mag = M # already Magnitudes calculated
        m = Magnitude()
        m.mag = _mag
        m.magnitude_type = "Ml"
        m.origin_id = o.resource_id
        
        # LAKE BAYKAL REGION, RUSSIA
        o.region = FlinnEngdahl().get_region(o.longitude, o.latitude)
        
        # create Event
        e = Event()
        e.event_type = "earthquake"
        e.origins = [o]
        e.magnitudes = [m]
        
        # append to Catalog
        catalog += e
        
    # write Catalog
    catalog.write('%sevents.xml' % STATION, format="QUAKEML")
