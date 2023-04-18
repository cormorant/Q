#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
create StationXML inventory file from scratch, not using NRL.

"""
import os
import sys
import copy

import math
import datetime
import obspy
from obspy.core.inventory import Inventory, Network, Station, Channel, Site

from obspy.core.inventory.response import Response, PolesZerosResponseStage


STATIONS = {
    
    # BR Buryat branch GS RAS
    "HRMR": (51.62806, 106.95528, 620),
    "STDB": (52.16889, 106.36583, 458),
    "MXMB": (53.26333, 108.74528, 510),
    "UUDB": (51.86889, 107.66333, 600),
    "ZRHB": (52.54479, 107.15950, 480),
    # UZR
    "UZR":  (53.32382, 107.74089, 480),
    # KEL
    "KELR": (52.763, 108.078, 460),
    # FFN
    "FFNB": (52.04722, 106.76472, 564),
    # TRT
    "TRTB": (52.22333, 107.64944, 600),
    # No data for BTM, VBR instead
    "VBR":  (51.79832, 106.01503, 500),
    # add BTM
    "BTM": (51.69972, 105.8325, 550),
    # GORB since 24.07.2011
    "GORB":  (52.98559, 108.28516, 480),
    
    # BY Baykal filial
    #"OGRR": (53.6397, 107.59398, 495),
    "OGRR": (53.64634, 107.59444, 495),
    "BGT": (52.04526, 105.40658, 466),
    "IVK": (51.80084, 104.4137, 470),
    "LSTR": (51.86783, 104.83263, 450),
    "TRG":  (52.76123, 106.34483, 718),
    "ARS": (51.920, 102.423, 970),
    "LSTR": (51.86782, 104.83263, 510),
    "TLY": (51.681, 103.644, 579),
}

ALL_COEFFS = {
    # BY
    #"OGRR": (0.00032, 0.00033, 0.00033),
    # old 2009 0.000401, 0.000433, 0.000404
    #"OGRR": (0.000401, 0.000433, 0.000404),
    "OGRR": (0.000317, 0.000341, 0.000315),
    #"BGT":  (0.0028,  0.0031,  0.00320),
    "BGT":  (0.00195,  0.0022,  0.00247),
    "IVK":  (0.00384, 0.00399, 0.00387),
    # trg since 2006, has
    #"TRG":  (0.00038, 0.00034, 0.00036),
    # old 2009
    "TRG":  (0.000229, 0.000213, 0.000231),
    #"TRG":  (0.00023, 0.00021, 0.00023),
    #
    "ARS": (0.0027, 0.0029, 0.0028),
    #"LSTR": (0.00031, 0.00031, 0.00031),
    # LSTR since 01.01.2011
    "LSTR": (0.000527, 0.000359, 0.00036),
    # talaya CM-3KB???
    "TLY": (0.0003, 0.0003, 0.0003),
    #===
    #
    # BR
    # old Baikal-10 coeffs
    "HRMR": (0.0004, 0.00036, 0.00028),
    # irkut STDB
    #"STDB": (0.00006, 0.00006, 0.00006),
    # stdb Geon
    #"STDB": (0.00000074, 0.00000072, 0.00000058),
    # stdb B-7HR
    ###"STDB": (0.0166, 0.0166, 0.0178),
    # STDB A7b + CMG-40T
    "STDB": (0.00009, 0.000096, 0.000094),
    # baikal CM-3 ZRH
    #"ZRHB": (0.0025, 0.0025, 0.0025),
    # ZRHB old A-7b CM-3
    "ZRHB": (0.004, 0.004, 0.004),
    # ZRHB A-7b CM-3KB
    #"ZRHB": (0.0005, 0.0007, 0.0006),
    # UZR CM-3
    #"UZR":  (0.0046, 0.0049, 0.0046),
    
    # UZR CM-3KB + A7b 2021
    "UZR":  (0.0005308, 0.0005629, 0.0005518),
    # UZR CM-3KB 2019
    #"UZR":  (0.000674, 0.000591, 0.001063),
    
    # KELR irkut
    "KELR": (0.00006, 0.00006, 0.00006),
    # FFN (A-7b)
    "FFNB": (0.0042, 0.00498, 0.004267),
    # FFN unknow baikal
    #"FFNB": (0.0027, 0.0026, 0.0026),
    # TRT b-7hr + CM-3KB
    "TRTB": (0.0025, 0.0024, 0.0025),
    # UUD Baikal-11
    "UUDB": (0.0025, 0.0025, 0.0025),
    # MXM Baikal CM-3KB, CM-3, Guralp
    "MXMB": [
        (0.00042, 0.00033, 0.00032),   # CM-3KB
        (0.0025, 0.0025, 0.0025),      # CM-3
        (0.000415, 0.000415, 0.000415),# B-7HR + Guralp
    ],
    #===
    # VBR (B-7hr +CM-3 )
    "VBR":  (0.02, 0.02, 0.02),
    # add BTM geon
    # 0.0000001
    "BTM": (0.0000001, 0.0000001, 0.0000001),
    # GORB 2019
    "GORB":  (0.002, 0.0021, 0.00215),
}


def make_response():
    
    nrl = NRL()
    
    sensor_keys = ['Guralp', 'CMG-40T', '30s - 50 Hz', "800"]
    
    datalogger_keys = ['Nanometrics', 'Centaur', '40 Vpp (1)', 'Off', 'Linear phase', '100']
    
    response = nrl.get_response(sensor_keys=sensor_keys,
        datalogger_keys=datalogger_keys)
    # remove unused stages 4-6 ???
    #_ = response.response_stages.pop(5)
    #_ = response.response_stages.pop(4)
    #_ = response.response_stages.pop(3)
    return response


def create_station(STA):
    
    latitude, longitude, elevation = STATIONS[STA]
    COEFFS = ALL_COEFFS[STA]
    
    # Station
    sta = Station(code=STA,
        latitude=latitude, longitude=longitude, elevation=elevation,
        creation_date=obspy.UTCDateTime(1996, 2, 1),
        site=Site(name="%s district" % STA)
    )
    
    # make response file
    response = make_response()
    
    # info for every channel 
    for CHA, COEF in zip(CHANNELS, COEFFS):
        channel_response = copy.deepcopy(response)
        cha = Channel(code="HH%s" % CHA,
            location_code="00",
            latitude=latitude,
            longitude=longitude,
            elevation=elevation,
            depth=0.0,
            azimuth=90.0 if CHA=="E" else 0, # North 0, 90 East
            dip=-90. if CHA=="Z" else 0.,#-90.0 for Z else 0
            sample_rate=100)
        
        # modify response!
        # overall sensitivity
        ###channel_response.instrument_sensitivity.value = 1e6/COEF
        # sensor sensitivity
        '''
        sensor_sensitivity = #
        DATALOGGER_AMPLIFIER = channel_response.instrument_sensitivity.value / sensor_sensitivity
        channel_response.response_stages[2].stage_gain = DATALOGGER_AMPLIFIER
        print("DATALOGGER_AMPLIFIER = %.0f" % DATALOGGER_AMPLIFIER)
        
        # sensitivity of sensor (unknown)
        #sensor_sensitivity = channel_response.instrument_sensitivity.value / DATALOGGER_AMPLIFIER
        channel_response.response_stages[0].stage_gain = sensor_sensitivity
        print("Sensor sensitivity = %.0f" % sensor_sensitivity)

        # finally, recalculate (modify overall sensitivity)
        channel_response.recalculate_overall_sensitivity()
        '''
        
        # attach response
        cha.response = channel_response
        
        # append station
        sta.channels.append(cha)
    
    # done
    return sta


def main(args):
    
    STATION = args[1]
    # create Inventory obj
    inv = Inventory(networks=[], source="io.xseed version 1.1.0")
    
    # Network
    net = Network(code="BR", description="B", stations=[],
        start_date=obspy.UTCDateTime(1996, 2, 1)
    )
    
    # which station
    sta = create_station(STATION)
    
    # station with channels done! Append it
    net.stations.append(sta)
    
    inv.networks.append(net)
    
    # save inventory
    # Supported types: STATIONXML, SHAPEFILE, KML, SACPZ, CSS, STATIONTXT
    inv.write("BR.%s.BH.xml" % STATION, format="STATIONXML", validate=True)
    
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))

