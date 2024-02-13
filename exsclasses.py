# started 2/12/2024

import struct
from dataclasses import dataclass, fields

@dataclass
class EXSInstrument():
    data:     str = None,
    name:     str = None,
    header:   str = None,
    zones:   list = [],
    groups:  list = [],
    samples: list = [],
    objects: list = [],
    params:  list = None

def parse_instrument(data):
    instrument = EXSInstrument()
    instrument.data = data
    instrument.name = data[12:76].split(b'\x00',maxsplit=1)[0].decode()
    return instrument

@dataclass
class EXSZone():
    data:           str = None
    name:           str = "Zone #"
    id:             int = 0
    options:        int = 0
    rootnote:       int = 60
    finetune:       int = 0
    pan:            int = 0
    volumeadjust:   int = 0
    volumescale:    int = 0
    startnote:      int = 0
    endnote:        int = 127
    minvel:         int = 0
    maxvel:         int = 127
    samplestart:    int = 0
    sampleend:      int = None
    loopstart:      int = 0
    loopend:        int = None
    loopcrossfade:  int = 0
    looptune:       int = 0
    loopenable:     bool = False
    loopequalpower: bool = False
    loopdirection:  int = 0
    loopplaytoendonrelease: int = 0

    oneshot:        bool = False
    pitchtracking:  bool = True
    reverse:        bool = False
    velrangeenable: bool = False
    mute:           bool = False

    flexoptions:    int = 0
    flexspeed:      int = 0
    coarsetune:     int = 0
    output:         int = 0
    group:          int = -1
    sampleindex:    int = 0
    fadein:         int = 0
    fadeout:        int = 0
    anchor:         int = 0
    tailtune:       int = 0
    tailvolume:     int = 0
    tailsampleindex: int = -1
    tailstart:      int = 0
    tailend:        int = 0

def parse_zone(data):
    zone = EXSZone()
    zone.data = data

    struct_format = "<8x4s64sBBbbbbBBxBBxIIIIIbBB42xBbbbxB5xII8xIIiII8xfI"
    struct_size   = struct.calcsize(struct_format)
    print (struct_size)

    values = list(struct.unpack(struct_format,data[:struct_size]))
    # clean up name
    values[1] = values[1].split(b'\x00',maxsplit=1)[0].decode()
    print (values)

    zone.name         = values[1]   # Zone: Name
    zone.options      = values[2]   # Pitch, One-Shot, Reverse, VelocityRangeOn, Mute
    zone.rootnote     = values[3]   # Pitch: Key
    zone.finetune     = values[4]   # Pitch: Tune (decimal)
    zone.pan          = values[5]   # Mixer: Pan
    zone.volumeadjust = values[6]   # Mixer: Volume
    zone.volumescale  = values[7]   # Mixer: Volume
    zone.startnote    = values[8]   # Key Range: Low
    zone.endnote      = values[9]   # Key Range: High
    zone.minvel       = values[10]  # Velocity Range: Low
    zone.maxvel       = values[11]  # Velocity Range: High
    zone.samplestart  = values[12]  # Sample: Start
    zone.sampleend    = values[13]  # Sample: End
    zone.loopstart    = values[14]  # Loop: Start
    zone.loopend      = values[15]  # Loop: End
    zone.loopcrossfade = values[16]  # Loop: XFade
    zone.looptune     = values[17]  # Loop: Tune
    zone.loopoptions  = values[18]  # LoopOn, LoopEqualPower, PlayToEndOnRelease
    zone.loopdirection= values[19]
    zone.flexoptions  = values[20]  # FlexOn, FollowTempo
    zone.flexspeed    = values[21]  # 0=1, 1=2, 2=4, 3=8
    zone.tailtune     = values[22]  # Audio File Tail: Tune
    zone.coarsetune   = values[23]  # Pitch: Tune (whole numbers)
    zone.output       = values[24]  # Zone: Output
    zone.group        = values[25]  # Group Assignment
    zone.sampleindex  = values[26]  #
    zone.fadeout      = values[27]  # Fade Out
    zone.anchor       = values[28]  # Offset
    zone.tailsampleindex = values[29] # Audio File Tail
    zone.tailstart    = values[30]  # Audio File Tail: Start
    zone.tailend      = values[31]  # Audio File Tail: End
    zone.tailvolume   = values[32]  # Audio File Tail: Volume
    zone.fadein       = values[33]  # Fade In

    #zone options
    zone.oneshot        = {0:False, 1:True}[zone.options & 1]  # 0 = OFF, 1  = ON
    zone.pitchtracking  = {2:False, 0:True}[zone.options & 2]  # 0 = ON,  2  = OFF #<<<< !!!!!!!!!!
    zone.reverse        = {0:False, 4:True}[zone.options & 4]  # 0 = OFF, 4  = ON
    zone.velrangeenable = {0:False, 8:True}[zone.options & 8]  # 0 = OFF, 8  = ON deprecated in new SAMPLER plugin
    zone.mute           = {0:False,16:True}[zone.options & 16] # 0 = OFF, 16 = ON (muted)

    #loop options
    zone.loopenable     = {0:False, 1:True}[zone.loopoptions & 1]  # 0 = OFF, 1  = ON
    zone.loopequalpower = {0:False, 2:True}[zone.loopoptions & 2]  # 0 = OFF, 2  = ON
    zone.loopplaytoendonrelease = {0:False, 4:True}[zone.loopoptions & 4]  # 0 = OFF, 4  = ON

    print(zone.loopoptions & 4)


    print (zone.loopplaytoendonrelease)

    # for field in fields(zone):
    #     field_name = field.name
    #     field_value = getattr(zone, field_name)
    #     print(f"{field_name}: {field_value}")



    #print (zone.name)
    return zone