#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import datetime
#sys.path.insert(0, "e:/miniconda2/Scripts")
from obspy import Stream, read as read_mseed


EXT = "seed"


def main(args, network="BR", location="00", channel="H"):
    
    STATION, PATH = args[1], args[2] # check STATION name?
    
    if not os.path.exists(PATH):
        print("Error: Path '%s' not found! Exiting..." % PATH)
        return
    
    # list of miniseed-files
    files = sorted([os.path.join(PATH, s) for s in os.listdir(PATH) 
        if s.lower().endswith(EXT)])
    
    stream = Stream()
    for filename in files:
        
        traces = read_mseed(filename)
        # fix channels location etc
        for tr in traces:
            tr.stats.network = network
            tr.stats.location = location
            tr.stats.station = STATION
            tr.stats.channel = channel + tr.stats.channel[1:]
        
        # append
        stream += traces
    
    # write result
    outfname = os.path.join(PATH, '%s.mseed' % STATION)
    stream.write(outfname, format='MSEED', encoding='STEIM2')#, dataquality='D')


if __name__ == "__main__":
    sys.exit(main(sys.argv))
