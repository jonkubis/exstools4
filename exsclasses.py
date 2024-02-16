# started 2/12/2024

import struct
from dataclasses import dataclass, fields, field
import exsparams


def bool_to_byte(bools):
    return sum(1 << (7 - i) for i, bit in enumerate(bools) if bit)


@dataclass
class EXSInstrument():
    data:     str = None
    name:     str = None
    header:   str = None
    zones:   list = field(default_factory=lambda: [])
    groups:  list = field(default_factory=lambda: [])
    samples: list = field(default_factory=lambda: [])
    objects: list = field(default_factory=lambda: [])
    params:  dict = field(default_factory=lambda: {})
    param_data: str = None


def parse_instrument(data):
    instrument = EXSInstrument()
    instrument.data = data
    instrument.name = data[12:76].split(b'\x00',maxsplit=1)[0].decode()
    return instrument


@dataclass
class EXSZone():
    data:           str = None
    name:           str = "Zone #"
    id:             int = None # set by parse function
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


def parse_zone(data,id=None):
    zone = EXSZone()
    zone.data = data

    if len(zone.data) == 184:
        struct_format = "<8x4s64sBBbbbbBBxBBxIIIIIbBB42xBbbbxB5xII8xI"
    else:
        struct_format = "<8x4s64sBBbbbbBBxBBxIIIIIbBB42xBbbbxB5xII8xIIiII8xfI"

    struct_size   = struct.calcsize(struct_format)
    #print (struct_size)
    #print (len(zone.data))
    values = list(struct.unpack(struct_format,data[:struct_size]))
    assert (values[0] == b'TBOS')
    # clean up name
    values[1] = values[1].split(b'\x00',maxsplit=1)[0].decode()
    #print (values)

    if id is not None: zone.id = id
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
    if len(zone.data) == 216:
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

    # for field in fields(group):
    #     field_name = field.name
    #     field_value = getattr(group, field_name)
    #     print(f"{field_name}: {field_value}")

    return zone


def export_zone(zone):
    to_pack = [
        b'\x00' * 8,
        b'TBOS',
        zone.name.encode(),
        bool_to_byte([
            {0: False, 128: True}[zone.options & 128],  # pass through the high bits of the existing options
            {0: False, 64:  True}[zone.options & 64],
            {0: False, 32:  True}[zone.options & 32],
            zone.mute,
            zone.velrangeenable,
            zone.reverse,
            (not zone.pitchtracking),
            zone.oneshot,
        ]),
        zone.rootnote,
        zone.finetune,
        zone.pan,
        zone.volumeadjust,
        zone.volumescale,
        zone.startnote,
        zone.endnote,
        zone.minvel,
        zone.maxvel,
        zone.samplestart,
        zone.sampleend,
        zone.loopstart,
        zone.loopend,
        zone.loopcrossfade,
        zone.looptune,
        bool_to_byte([
            {0: False, 128: True}[zone.loopoptions & 128],  # pass through the high bits of the existing options
            {0: False, 64:  True}[zone.loopoptions & 64],
            {0: False, 32:  True}[zone.loopoptions & 32],
            {0: False, 16:  True}[zone.loopoptions & 16],
            {0: False, 8:   True}[zone.loopoptions & 8],
            zone.loopplaytoendonrelease,
            zone.loopequalpower,
            zone.loopenable
        ]),
        zone.loopdirection,
        zone.flexoptions, # need to unpack/repack this
        zone.flexspeed,
        zone.tailtune,
        zone.coarsetune,
        zone.output,
        zone.group,
        zone.sampleindex,
        zone.fadeout,
        # this would be the end of the old version EXS24 stuff
        # new format stuff follows
        zone.anchor,
        zone.tailsampleindex,
        zone.tailstart,
        zone.tailend,
        zone.tailvolume,
        zone.fadein
    ]
    #old_struct_format = "<8s4s64sBBbbbbBBxBBxIIIIIbBB42xBbbbxB5xII8xI"
    struct_format = "<8s4s64sBBbbbbBBxBBxIIIIIbBB42xBbbbxB5xII8xIIiII8xfI"

    b = struct.pack(struct_format,*to_pack)
    return b


@dataclass
class EXSGroup():
    data:                   str = None
    name:                   str = None
    id:                     int = None # set by parse function
    volume:                 int = 0
    pan:                    int = 0
    polyphony:              int = 0 # 'Max'
    options:                int = 1
    mute:                   bool = False
    releasetriggerdecay:    bool = False
    fixedsampleselect:      bool = False #https://www.logicprohelp.com/forums/topic/99786-whats-the-fss-on-exs24-edit-solved/
    exclusive:              int = 0
    minvel:                 int = 0
    maxvel:                 int = 127
    sampleselectrandomoffset: int = 0
    releasetriggertime:     int = 0
    velocityrangexfade:     int = 0
    velocityrangexfadetype: int = 0
    keyrangexfadetype:      int = 0
    keyrangexfade:          int = 0
    enablebytempolow:       int = 80
    enabletempohigh:        int = 140
    cutoffoffset:           int = 0
    resooffset:             int = 0
    env1attackoffset:       int = 0
    env1decayoffset:        int = 0
    env1sustainoffset:      int = 0
    env1releaseoffset:      int = 0
    releasetrigger:         bool = False
    output:                 int = 0
    enablebynotevalue:      int = 0
    roundrobingrouppos:     int = -1 #i.e. group ID to play after
    enablebytype:           int = 0
    enablebycontrolvalue:   int = 0
    enablebycontrollow:     int = 0
    enablebycontrolhigh:    int = 0
    startnote:              int = 0
    endnote:                int = 127
    enablebymidichannel:    int = 0
    enablebyarticulation:   int = 1
    enablebybenderlow:      int = 0
    enablebybenderhigh:     int = 127
    env1holdoffset:         int = 0
    env2attackoffset:       int = 0
    env2decayoffset:        int = 0
    env2sustainoffset:      int = 0
    env2releaseoffset:      int = 0
    env2holdoffset:         int = 0
    env1delayoffset:        int = 0
    env2delayoffset:        int = 0

    enableby_note:          bool = False  # 1
    enableby_roundrobin:    bool = False  # 2
    enableby_control:       bool = False  # 3
    enableby_bend:          bool = False  # 4
    enableby_channel:       bool = False  # 5
    enableby_articulation:  bool = False  # 6
    enableby_tempo:         bool = False  # 7


def parse_group(data,id=None):
    group = EXSGroup()
    group.data = data
    #print (len(group.data))

    if len(group.data) == 196:
        struct_format = "<8x4s64sbbBBBBBb8xH14xBBBB2xBBxbxb12xiiiixBBB4xiBBBBBBBB2xbbiiiiii"
    else:
        struct_format = "<8x4s64sbbBBBBBb8xH14xBBBB2xBBxbxb12xiiiixBBB4xiBBBBBBBB2xbbiiiiii4xii"
    struct_size   = struct.calcsize(struct_format)
    #print (struct_size)

    values = list(struct.unpack(struct_format,data[:struct_size]))
    assert (values[0] == b'TBOS')
    # clean up name
    values[1] = values[1].split(b'\x00',maxsplit=1)[0].decode()
    #print (values)

    if id is not None: group.id = id
    group.name                   = values[1]   # Group: Name
    group.volume                 = values[2]   # Mixer: Volume
    group.pan                    = values[3]   # Mixer: Pan
    group.polyphony              = values[4]   # Playback: Voices
    group.options                = values[5]   # Mute, ReleaseTriggerDecay, FixedSampleSelect
    group.exclusive              = values[6]   # Playback: Exclusive
    group.minvel                 = values[7]   # Velocity Range: Low
    group.maxvel                 = values[8]   # Velocity Range: High
    group.sampleselectrandomoffset = values[9]
    group.releasetriggertime     = values[10]   # Release Trigger: Time
    group.velocityrangexfade     = values[11]-128     # Velocity Range: XFade
    group.velocityrangexfadetype = values[12]  # Velocity Range: XFade Type
    group.keyrangexfadetype      = values[13]  # Key Range: XFade Type
    group.keyrangexfade          = values[14]-128 # Key Range: XFade
    group.enablebytempolow       = values[15]  # Enable By Tempo: Low
    group.enablebytempohigh      = values[16]  # Enable By Tempo: High
    group.cutoffoffset           = values[17]  # Filter Offsets: Cutoff
    group.resooffset             = values[18]  # Filter Offsets: Res.
    group.env1attackoffset       = values[19]  # Envelope 1 Offsets: A (amp env)
    group.env1decayoffset        = values[20]  # Envelope 1 Offsets: D (amp env)
    group.env1sustainoffset      = values[21]  # Envelope 1 Offsets: S (amp env)
    group.env1releaseoffset      = values[22]  # Envelope 1 Offsets: R (amp env)
    group.releasetrigger         = {0: False, 1:  True}[values[23] & 1]  # Release Trigger: On (0 = OFF, 1  = ON)
    group.output                 = values[24]  # Mixer: Output
    group.enablebynotevalue      = values[25]  # Enable By Note: Value
    group.roundrobingrouppos     = values[26]  # -1 if no RR; otherwise group ID to play after
    group.enablebytype           = values[27]  # 'On' for first 'Enable by' sets this
    group.enablebycontrolvalue   = values[28]  # Enable by Control: Value
    group.enablebycontrollow     = values[29]  # Enable by Control: Low
    group.enablebycontrolhigh    = values[30]  # Enable by Control: High
    group.startnote              = values[31]  # Key Range: Low
    group.endnote                = values[32]  # Key Range: High
    group.enablebymidichannel    = values[33]+1  # Enable By Channel: Value (originally zero-based)
    group.enablebyarticulation   = values[34]  # Enable by Articulation: Value
    group.enablebybenderlow      = values[35]  # Enable by Bend: Low
    group.enablebybenderhigh     = values[36]  # Enable by Bend: High
    group.env1holdoffset         = values[37]  # Envelope 1 Offsets: H (amp env)
    group.env2attackoffset       = values[38]  # Envelope 2 Offsets: A (env 2)
    group.env2decayoffset        = values[39]  # Envelope 2 Offsets: D (env 2)
    group.env2sustainoffset      = values[40]  # Envelope 2 Offsets: S (env 2)
    group.env2releaseoffset      = values[41]  # Envelope 2 Offsets: R (env 2)
    group.env2holdoffset         = values[42]  # Envelope 2 Offsets: H (env 2)
    if len(group.data) == 208:
        group.env1delayoffset        = values[43]  # Envelope 2 Delay Offset (amp env)
        group.env2delayoffset        = values[44]  # Envelope 1 Delay Offset (env 2)

    #group options
    group.mute                = {0: False, 16:  True}[group.options & 16]  # 0 = OFF, 1  = ON
    group.releasetriggerdecay = {0: False, 64:  True}[group.options & 64]  # 0 = OFF, 1  = ON
    group.fixedsampleselect   = {0: False, 128: True}[group.options & 128]  # 0 = OFF, 1  = ON -- Vel Range XfadeType OFF == 1/ON

    #group enable by
    group.enableby_note         = group.enablebytype == 1
    group.enableby_roundrobin   = group.enablebytype == 2
    group.enableby_control      = group.enablebytype == 3
    group.enableby_bend         = group.enablebytype == 4
    group.enableby_channel      = group.enablebytype == 5
    group.enableby_articulation = group.enablebytype == 6
    group.enableby_tempo        = group.enablebytype == 7

    # for field in fields(group):
    #     field_name = field.name
    #     field_value = getattr(group, field_name)
    #     print(f"{field_name}: {field_value}")

    return group


@dataclass
class EXSSample():
    data:               str = None
    name:               str = None
    id:                 int = None # set by parse function
    wavedatastart:      int = None
    length:             int = None  # length of sample IN SAMPLES
    rate:               int = None
    bitdepth:           int = None
    channels:           int = 2
    fourdigitcode:      str = None  # default 'EVAW' = WAVE
    filesize:           int = 0
    iscompressed:       bool = False
    folder:             str = None
    filename:           str = None
    # # Logic sometimes overwrites 'Samples\x00' over some Keymap files...
    # # sometimes there's enough characters left over to figure out the sample file
    # corruptedfilename: str = ""
    # newsamplefileindex: int = 0  # for merging
    # israwaudio: bool = False  # SFZ import uses this
    # embeddedsample: bool = False


def parse_sample(data,id=None):
    sample = EXSSample()
    sample.data = data

    if len(sample.data) == 668:
        struct_format = "<8x4s64sIIIIII4x4sII40x256s256s"
    else:
        struct_format = "<8x4s64sIIIIII4x4sII40x256s"
    struct_size   = struct.calcsize(struct_format)
    #print (f'\n{struct_size}')

    values = list(struct.unpack(struct_format,data[:struct_size]))
    assert (values[0] == b'TBOS')
    # clean up name
    values[1]  = values[1].split(b'\x00',maxsplit=1)[0].decode()
    values[11] = values[11].split(b'\x00', maxsplit=1)[0].decode()


    if id is not None: sample.id = id
    sample.name             = values[1]   # Sample Name
    sample.wavedatastart    = values[2]   # Wave data start offset in file. In WAV files this is 4 bytes after 'data'
                                                # (the 4 bytes following 'data' is the chunk size in bytes, wave data starts after.)
    sample.length           = values[3]   # length of sample IN SAMPLES
    sample.rate             = values[4]   # sample rate (samples per second, e.g. 44100, 48000)
    sample.bitdepth         = values[5]   # bit depth (16 or 24 bits)
    sample.channels         = values[6]   # 1 = mono, 2 = stereo
    channels_again          = values[7]   # not sure why this is stored twice. they always match.
    sample.fourdigitcode    = values[8]   #
    sample.filesize         = values[9]   # size (in bytes) of the actual sample file, probably used for relinking
    sample.iscompressed     = values[10]==1
    sample.folder           = values[11]
    if len(sample.data) == 668:
        values[12] = values[12].split(b'\x00', maxsplit=1)[0].decode()
        sample.filename         = values[12]

    # for field in fields(sample):
    #     field_name = field.name
    #     field_value = getattr(sample, field_name)
    #     print(f"{field_name}: {field_value}")

    return sample


def parse_params(data):
    chunk_length = len(data)

    # print (chunk_length)
    # print (data[:40])
    # print ("HI!")

    struct_format = "<8x4s64sI"
    struct_size = struct.calcsize(struct_format)
    #print (f'\n{struct_size}')

    values = list(struct.unpack(struct_format, data[:struct_size]))
    # clean up name
    values[1] = values[1].split(b'\x00', maxsplit=1)[0].decode()
    assert (values[0] == b'TBOS')
    #assert (values[1] == 'Default Param')

    old_style_param_count = values[2]
    old_style_param_ids   = list(struct.unpack(f'<{old_style_param_count}B', data[80:80+old_style_param_count]))
    old_style_param_data  = list(struct.unpack(f'<{old_style_param_count}h', data[80+old_style_param_count:80+old_style_param_count*3]))
    params = dict(zip(old_style_param_ids, old_style_param_data))

    new_style_param_offset = (80+old_style_param_count*3) + 4
    if len(data) > new_style_param_offset:
        new_style_param_count  = struct.unpack('<I', data[new_style_param_offset-4:new_style_param_offset])[0]
        new_style_param_IDs_and_data = struct.unpack(f'<{new_style_param_count*2}h', data[new_style_param_offset: new_style_param_offset+new_style_param_count * 4])

        new_params = dict(zip(new_style_param_IDs_and_data[::2], new_style_param_IDs_and_data[1::2]))
        params.update(new_params)

    if 0 in params: del(params[0])

    # for k, v in params.items():
    #     if k in exsparams.id_to_param:
    #         keyname = exsparams.id_to_param[k]
    #     else:
    #         keyname = hex(k)

    return params