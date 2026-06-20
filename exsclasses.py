# ███████╗██╗  ██╗███████╗ ██████╗██╗      █████╗ ███████╗███████╗███████╗███████╗   ██████╗ ██╗   ██╗
# ██╔════╝╚██╗██╔╝██╔════╝██╔════╝██║     ██╔══██╗██╔════╝██╔════╝██╔════╝██╔════╝   ██╔══██╗╚██╗ ██╔╝
# █████╗   ╚███╔╝ ███████╗██║     ██║     ███████║███████╗███████╗█████╗  ███████╗   ██████╔╝ ╚████╔╝
# ██╔══╝   ██╔██╗ ╚════██║██║     ██║     ██╔══██║╚════██║╚════██║██╔══╝  ╚════██║   ██╔═══╝   ╚██╔╝
# ███████╗██╔╝ ██╗███████║╚██████╗███████╗██║  ██║███████║███████║███████╗███████║██╗██║        ██║
# ╚══════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝╚═╝╚═╝        ╚═╝


import struct
from dataclasses import dataclass, fields, field
import exsparams

def bool_to_byte(bools):
    return sum(1 << (7 - i) for i, bit in enumerate(bools) if bit)


@dataclass
class EXSInstrument():
    data:     str = None
    name:     str = None
    pathname: str = None
    header:   str = None
    zones:   list = field(default_factory=lambda: [])
    groups:  list = field(default_factory=lambda: [])
    samples: list = field(default_factory=lambda: [])
    objects: list = field(default_factory=lambda: [])
    params:  dict = field(default_factory=lambda: {})
    param_data: str = None
    passthrough_blocks: list = field(default_factory=lambda: [])  # raw bytes of aux blocks (0x0A archive etc.) to round-trip
    is_modern: bool = False                                       # 0x40 type-byte flag (modern Sampler editor save)
    has_editor_archive: bool = False                              # a real type-0x0A editor-state archive block is present (independent of is_modern/0x40)
    original_chunk: bytes = None                                  # full original instrument chunk bytes, for byte-faithful round-trip

    # Typed, enumerable access to the auxiliary blocks kept in passthrough_blocks. These
    # are round-tripped byte-identically; the engine reads type-7 chunks as key-switch /
    # per-key "key action" records and type-8 chunks as output-bus labels. Their internal
    # field layout isn't exposed here (it varies and isn't reliably documented), so these
    # return the raw block bytes so callers can find/count/inspect them by type.
    @property
    def keyaction_blocks(self):
        return [b for b in self.passthrough_blocks if len(b) > 3 and (b[3] & 0x3F) == 0x07]

    @property
    def buslabel_blocks(self):
        return [b for b in self.passthrough_blocks if len(b) > 3 and (b[3] & 0x3F) == 0x08]


def parse_instrument(data):
    instrument = EXSInstrument()
    instrument.data = data
    instrument.name = data[12:76].split(b'\x00',maxsplit=1)[0].decode('latin-1')
    return instrument


@dataclass
class EXSZone():
    data:           str = None
    Name:           str = "Zone #"
    id:             int = None # set by parse function
    options:        int = 0
    KeyNote:       int = 60
    TuneFine:       int = 0
    Pan:            int = 0
    Volume:   int = 0
    VolScale:    int = 0
    FirstNote:      int = 0
    LastNote:        int = 127
    LowestVelocity:         int = 0
    HighestVelocity:         int = 127
    StartFrame:    int = 0
    EndFrame:      int = None
    loopoptions:    int = 0 #default
    SustainLoopStart:      int = 0
    SustainLoopEnd:        int = None
    SustainLoopXFade:  int = 0
    SustainLoopDeTune:       int = 0
    SustainLoop:     bool = False
    SustainLoopXFadeEQPwr: bool = False
    SustainLoopMode:  int = 0
    LoopDisableOnRelease: bool = True  # INVERSE of the old loopplaytoendonrelease (default True == old 0)

    OneShot:        bool = False
    Pitched:  bool = True
    Reverse:        bool = False
    velrangeenable: bool = True
    mute:           bool = False

    flexoptions:    int = 0
    FlexSpeed:      int = 0
    Tune:     int = 0
    Output:         int = 0
    Group:          int = -1
    FileName:    int = 0
    NumFadeInFrames:         int = 0
    NumFadeOutFrames:        int = 0
    SyncFrameOffset:         int = 0
    TuneTail:       int = 0
    VolumeTail:     int = 0
    FileNameTail: int = -1
    StartFrameTail:      int = 0
    EndFrameTail:        int = 0
    # Modern Sampler's precise (sub-dB) zone volume float at chunk 0xd0 — the engine
    # writes it alongside the coarse integer `Volume` (within 1.0 of it). None = leave
    # the source bytes untouched on export (so set it too if you change `Volume`).
    VolumePrecise:       float = None
    # Flex pitch offset (signed byte at zone body 0x32), applied by the engine when Flex
    # is enabled; populated in ~181k factory zones. Read/edit + round-trips byte-exact.
    FlexPitchOffset:     int = 0
    # options bit 6 (0x40): route this zone to its own direct Output bus (the Output field).
    ExsOutputFlag:       bool = False
    # flexoptions bit 0 = Flex enabled; bit 1 (engine-INVERTED) = follow project tempo.
    FlexEnabled:         bool = False
    FlexFollowTempo:     bool = True


def parse_zone(data,id=None,endian='<'):
    zone = EXSZone()
    zone.data = data

    # Zone content grew across EXS versions; each longer layout only appends
    # trailing fields. Pick the largest layout that fits, so unusual in-between
    # lengths parse what they can instead of crashing.
    zone_formats = (
        (180, "<8x4s64sBBbbbbBBxBBxIIIIIbBB42xBbbbxB5xiI8x"),
        (184, "<8x4s64sBBbbbbBBxBBxIIIIIbBB42xBbbbxB5xiI8xI"),
        (204, "<8x4s64sBBbbbbBBxBBxIIIIIbBB42xBbbbxB5xiI8xIIiII4x"),
        (208, "<8x4s64sBBbbbbBBxBBxIIIIIbBB42xBbbbxB5xiI8xIIiII8x"),
        (212, "<8x4s64sBBbbbbBBxBBxIIIIIbBB42xBbbbxB5xiI8xIIiII8xf"),
        (216, "<8x4s64sBBbbbbBBxBBxIIIIIbBB42xBbbbxB5xiI8xIIiII8xfI"),
    )
    struct_format = None
    for min_len, fmt in zone_formats:
        if len(zone.data) >= min_len:
            struct_format = fmt
    if struct_format is None:
        raise ValueError(f"EXS zone block too short: {len(zone.data)} bytes")

    struct_format = endian + struct_format[1:]  # honor the block's byte order
    struct_size   = struct.calcsize(struct_format)
    #print (struct_size)
    #print (len(zone.data))
    values = list(struct.unpack(struct_format,data[:struct_size]))
    # clean up name
    values[1] = values[1].split(b'\x00',maxsplit=1)[0].decode('latin-1')
    #print (values)

    if id is not None: zone.id = id
    zone.Name         = values[1]   # Zone: Name
    zone.options      = values[2]   # Pitch, One-Shot, Reverse, VelocityRangeOn, Mute
    zone.KeyNote     = values[3]   # Pitch: Key
    zone.TuneFine     = values[4]   # Pitch: Tune (decimal)
    zone.Pan          = values[5]   # Mixer: Pan
    zone.Volume = values[6]   # Mixer: Volume
    zone.VolScale  = values[7]   # Mixer: Volume
    zone.FirstNote    = values[8]   # Key Range: Low
    zone.LastNote      = values[9]   # Key Range: High
    zone.LowestVelocity       = values[10]  # Velocity Range: Low
    zone.HighestVelocity       = values[11]  # Velocity Range: High
    zone.StartFrame  = values[12]  # Sample: Start
    zone.EndFrame    = values[13]  # Sample: End
    zone.SustainLoopStart    = values[14]  # Loop: Start
    zone.SustainLoopEnd      = values[15]  # Loop: End
    zone.SustainLoopXFade = values[16]  # Loop: XFade
    zone.SustainLoopDeTune     = values[17]  # Loop: Tune
    zone.loopoptions  = values[18]  # LoopOn, LoopEqualPower, PlayToEndOnRelease
    zone.SustainLoopMode= values[19]
    zone.flexoptions  = values[20]  # FlexOn, FollowTempo
    zone.FlexSpeed    = values[21]  # 0=1, 1=2, 2=4, 3=8
    zone.TuneTail     = values[22]  # Audio File Tail: Tune
    zone.Tune   = values[23]  # Pitch: Tune (whole numbers)
    zone.Output       = values[24]  # Zone: Output
    zone.Group        = values[25]  # Group Assignment
    zone.FileName  = values[26]  #
    if len(zone.data) >= 184:
        zone.NumFadeOutFrames      = values[27]  # Fade Out
    if len(zone.data) >= 204:
        zone.SyncFrameOffset       = values[28]  # Offset
        zone.FileNameTail = values[29] # Audio File Tail
        zone.StartFrameTail    = values[30]  # Audio File Tail: Start
        zone.EndFrameTail      = values[31]  # Audio File Tail: End
    if len(zone.data) >= 212:
        zone.VolumeTail   = values[32]  # Audio File Tail: Volume
    if len(zone.data) >= 216:
        zone.NumFadeInFrames       = values[33]  # Fade In

    # Precise volume float (chunk 0xd0 / legacy 200) — sits in the trailing pad of
    # the struct map; read it directly so it's a first-class, editable value.
    if len(zone.data) >= 204:
        zone.VolumePrecise = struct.unpack_from(endian + 'f', data, 200)[0]

    #zone options
    zone.OneShot        = {0:False, 1:True}[zone.options & 1]  # 0 = OFF, 1  = ON
    zone.Pitched  = {2:False, 0:True}[zone.options & 2]  # 0 = ON,  2  = OFF #<<<< !!!!!!!!!!
    zone.Reverse        = {0:False, 4:True}[zone.options & 4]  # 0 = OFF, 4  = ON
    zone.velrangeenable = {0:False, 8:True}[zone.options & 8]  # 0 = OFF, 8  = ON deprecated in new SAMPLER plugin
    zone.mute           = {0:False,16:True}[zone.options & 16] # 0 = OFF, 16 = ON (muted)

    #loop options
    zone.SustainLoop     = {0:False, 1:True}[zone.loopoptions & 1]  # 0 = OFF, 1  = ON
    zone.SustainLoopXFadeEQPwr = {0:False, 2:True}[zone.loopoptions & 2]  # 0 = OFF, 2  = ON
    zone.LoopDisableOnRelease = {0:True, 4:False}[zone.loopoptions & 4]  # loopoptions bit2 set (play-to-end) -> NOT disabled

    # options bit 6 = direct-output routing; flexoptions bits 0/1 = Flex on / follow-tempo (inverted).
    zone.ExsOutputFlag   = bool(zone.options & 64)
    zone.FlexEnabled     = bool(zone.flexoptions & 1)
    zone.FlexFollowTempo = not (zone.flexoptions & 2)
    # Flex pitch offset: signed byte at zone body 0x32 (legacy 126), inside the struct map's pad.
    if len(zone.data) >= 127:
        zone.FlexPitchOffset = struct.unpack_from(endian + 'b', data, 126)[0]

    # for field in fields(group):
    #     field_name = field.name
    #     field_value = getattr(group, field_name)
    #     print(f"{field_name}: {field_value}")

    return zone


import re as _re

def _merge_passthrough(original, rebuilt, struct_format):
    """Reconcile a freshly-rebuilt chunk body with the source chunk so the
    rebuild/edit path preserves every byte it does not model.

    export_zone/group/sample pack a FIXED struct whose 'Nx' pad runs (and the
    region past the modeled struct) are written as zeros. But Logic stores real,
    populated state in some of those gaps -- e.g. a zone's float fine-volume at
    chunk 0xd0, a group's boolean flag at body 0x08 -- so a plain rebuild
    silently drops them. Here we start from the ORIGINAL bytes and overwrite only
    the genuine semantic fields (every non-pad struct token except the leading
    8-byte stream-bookkeeping word) with their current/edited values. Padding,
    the bookkeeping word, and any trailing bytes are kept verbatim. Net effect:
    an UNEDITED parse->export is byte-identical to the source, and unparsed
    fields survive edits to neighbouring fields.

    The output keeps the SOURCE chunk's exact length: legacy/short EXS24 chunks
    (e.g. 212-byte zones without the trailing fade-in field) are preserved at
    their own length rather than expanded to the full modern struct, so an
    unedited rebuild is byte-identical for short and full chunks alike. A field
    that does not fit inside the source length (only possible on a shorter legacy
    layout) is simply not written -- consistent with that layout never carrying
    it. Constructed objects (no source chunk) get the full freshly-built bytes.

    Only merges when the source chunk is little-endian (magic TBOS/JBOS at chunk
    0x10 == data[8:12]), matching the byte order export_* always writes. A
    big-endian source is re-emitted little-endian via the plain rebuild (its
    raw bytes are a different byte order and must NOT be spliced in)."""
    if not original or bytes(original[8:12]) not in (b'TBOS', b'JBOS'):
        return rebuilt
    out = bytearray(original)
    pos = 0
    for i, tok in enumerate(_re.findall(r'\d*[a-zA-Z]', struct_format[1:])):  # skip byte-order char
        size = struct.calcsize('<' + tok)
        # i==0 is the leading 8s stream-bookkeeping word -> keep original; pads -> keep original;
        # genuine fields -> take the (edited) rebuilt value, but only where it fits both buffers.
        if i != 0 and not tok.endswith('x') and pos + size <= len(out) and pos + size <= len(rebuilt):
            out[pos:pos + size] = rebuilt[pos:pos + size]
        pos += size
    return bytes(out)


def export_zone(zone):
    to_pack = [
        b'\x00' * 8,
        b'TBOS',
        zone.Name.encode('latin-1'),
        bool_to_byte([
            {0: False, 128: True}[zone.options & 128],  # pass through the high bits of the existing options
            zone.ExsOutputFlag,                          # bit 6 (0x40) = direct-output routing
            {0: False, 32:  True}[zone.options & 32],
            zone.mute,
            zone.velrangeenable,
            zone.Reverse,
            (not zone.Pitched),
            zone.OneShot,
        ]),
        zone.KeyNote,
        zone.TuneFine,
        zone.Pan,
        zone.Volume,
        zone.VolScale,
        zone.FirstNote,
        zone.LastNote,
        zone.LowestVelocity,
        zone.HighestVelocity,
        zone.StartFrame,
        zone.EndFrame,
        zone.SustainLoopStart,
        zone.SustainLoopEnd,
        zone.SustainLoopXFade,
        zone.SustainLoopDeTune,
        bool_to_byte([
            {0: False, 128: True}[zone.loopoptions & 128],  # pass through the high bits of the existing options
            {0: False, 64:  True}[zone.loopoptions & 64],
            {0: False, 32:  True}[zone.loopoptions & 32],
            {0: False, 16:  True}[zone.loopoptions & 16],
            {0: False, 8:   True}[zone.loopoptions & 8],
            (not zone.LoopDisableOnRelease),  # on-disk play-to-end bit = NOT LoopDisableOnRelease
            zone.SustainLoopXFadeEQPwr,
            zone.SustainLoop
        ]),
        zone.SustainLoopMode,
        # flexoptions: bits 0/1 from FlexEnabled/FlexFollowTempo (inverted), other bits passed through
        (zone.flexoptions & ~0x03) | (1 if zone.FlexEnabled else 0) | (0 if zone.FlexFollowTempo else 2),
        zone.FlexSpeed,
        zone.TuneTail,
        zone.Tune,
        zone.Output,
        zone.Group,
        zone.FileName,
        zone.NumFadeOutFrames,
        # this would be the end of the old version EXS24 stuff
        # new format stuff follows
        zone.SyncFrameOffset,
        zone.FileNameTail,
        zone.StartFrameTail,
        zone.EndFrameTail,
        zone.VolumeTail,
        zone.NumFadeInFrames
    ]

    #old_struct_format = "<8s4s64sBBbbbbBBxBBxIIIIIbBB42xBbbbxB5xII8xI"
    struct_format = "<8s4s64sBBbbbbBBxBBxIIIIIbBB42xBbbbxB5xiI8xIIiII8xfI"

    b = struct.pack(struct_format,*to_pack)
    out = bytearray(_merge_passthrough(zone.data, b, struct_format))
    # Promoted out-of-struct field: write the precise volume float at chunk 0xd0
    # (legacy 200) when set; None leaves whatever the overlay preserved.
    if zone.VolumePrecise is not None and len(out) >= 204:
        struct.pack_into('<f', out, 200, zone.VolumePrecise)
    # Flex pitch offset (signed byte at legacy 126) — written so it survives a
    # rebuild/scratch build; equals the source byte for an unedited parsed zone.
    if zone.FlexPitchOffset is not None and len(out) >= 127:
        struct.pack_into('<b', out, 126, zone.FlexPitchOffset)
    return bytes(out)


@dataclass
class EXSGroup():
    data:                   str = None
    Name:                   str = None
    id:                     int = None # set by parse function
    Volume:                 int = 0
    Pan:                    int = 0
    Voices:              int = 0 # 'Max'
    options:                int = 1
    mute:                   bool = False
    ReleaseTriggerDecay:    bool = False
    fixedsampleselect:      bool = False #https://www.logicprohelp.com/forums/topic/99786-whats-the-fss-on-exs24-edit-solved/
    # Engine flags packed in the same `options` byte (confirmed bit positions):
    IgnorePitchWheelAndBend: bool = False  # options bit 1 (0x02)
    DecayIsDbLinear:         bool = False  # options bit 2 (0x04)
    RoundRobinPerNoteOn:     bool = False  # options bit 5 (0x20)
    ExclusiveClass:              int = 0
    LowestVelocity:                 int = 0
    HighestVelocity:                 int = 127
    SampleSelectRandOffset: int = 0
    ReleaseTriggerDecayTime:     int = 0
    VelocityXFade:     int = 0
    VelocityXFadeType: int = 0
    NoteXFadeType:      int = 0
    NoteXFade:          int = 0
    SelByTempoLow:       int = 80
    SelByTempoHigh:      int = 140
    FilterCutOffOffset:           int = 0
    FilterResonanceOffset:             int = 0
    Env1AttackOffset:       int = 0
    Env1DecayOffset:        int = 0
    Env1SustainOffset:      int = 0
    Env1ReleaseOffset:      int = 0
    ReleaseTrigger:         bool = False
    Output:                 int = 0
    SelByNoteNote:      int = 0
    SelByGroupCycle:     int = -1 #i.e. group ID to play after
    enablebytype:           int = 0
    SelByCtrlCtrl:   int = 0
    SelByCtrlLow:     int = 0
    SelByCtrlHigh:    int = 0
    FirstNote:              int = 0
    LastNote:                int = 127
    SelByChannelChannel:    int = 1
    SelByArticNum:   int = 1
    SelByPitchLow:      int = 0
    SelByPitchHigh:     int = 127
    Env1HoldOffset:         int = 0
    Env2AttackOffset:       int = 0
    Env2DecayOffset:        int = 0
    Env2SustainOffset:      int = 0
    Env2ReleaseOffset:      int = 0
    Env2HoldOffset:         int = 0
    Env1DelayOffset:        int = 0
    Env2DelayOffset:        int = 0
    # Boolean at group-body 0x08 (0/255), set in ~54% of factory groups; its exact
    # meaning is undetermined. None = leave source bytes untouched on export (the
    # overlay preserves it); set 0/255 to override.
    unknown_byte_0x08:      int = None
    # The engine evaluates up to THREE stacked "enable by" conditions; `enablebytype`
    # above is slot 1 (body 84). Slots 2 & 3 live at body 92/93 and use the same
    # selector map (1=Note,2=Group,3=Ctrl,4=Pitch,5=Channel,6=Artic,7=Tempo).
    enablebytype2:          int = 0
    enablebytype3:          int = 0
    # Group body 36/37 (signed bytes): "Live" pre-anchor time (ms) and dynamic-range
    # low-level offset (engine scales x0.5). Both round-trip byte-exact.
    LivePreAnchorTimeMs:    int = 0
    DynaRangeLowLevelOffset: int = 0

    SelByNote:          bool = False  # 1
    SelByGroup:    bool = False  # 2
    SelByCtrl:       bool = False  # 3
    SelByPitch:          bool = False  # 4
    SelByChannel:       bool = False  # 5
    SelByArtic:  bool = False  # 6
    SelByTempo:         bool = False  # 7


def parse_group(data,id=None,endian='<'):
    group = EXSGroup()
    group.data = data
    #print ("len(group.data)",len(group.data))

    # As with zones, group layouts only append trailing fields across versions.
    # Pick the largest layout that fits the block.
    group_formats = (
        (168, "<8x4s64sbbBBBBBb8xH14xBBBB2xBBxbxb12xiiiixBBB4xiBBBBBBBB"),
        (172, "<8x4s64sbbBBBBBb8xH14xBBBB2xBBxbxb12xiiiixBBB4xiBBBBBBBB2xbb"),
        (196, "<8x4s64sbbBBBBBb8xH14xBBBB2xBBxbxb12xiiiixBBB4xiBBBBBBBB2xbbiiiiii"),
        (200, "<8x4s64sbbBBBBBb8xH14xBBBB2xBBxbxb12xiiiixBBB4xiBBBBBBBB2xbbiiiiii4x"),
        (208, "<8x4s64sbbBBBBBb8xH14xBBBB2xBBxbxb12xiiiixBBB4xiBBBBBBBB2xbbiiiiii4xii"),
    )
    struct_format = None
    for min_len, fmt in group_formats:
        if len(group.data) >= min_len:
            struct_format = fmt
    if struct_format is None:
        raise ValueError(f"EXS group block too short: {len(group.data)} bytes")

    struct_format = endian + struct_format[1:]  # honor the block's byte order
    struct_size   = struct.calcsize(struct_format)
    #print (struct_size)

    values = list(struct.unpack(struct_format,data[:struct_size]))
    # clean up name
    values[1] = values[1].split(b'\x00',maxsplit=1)[0].decode('latin-1')
    #print (values)

    if id is not None: group.id = id
    group.Name                   = values[1]   # Group: Name
    group.Volume                 = values[2]   # Mixer: Volume
    group.Pan                    = values[3]   # Mixer: Pan
    group.Voices              = values[4]   # Playback: Voices
    group.options                = values[5]   # Mute, ReleaseTriggerDecay, FixedSampleSelect
    group.ExclusiveClass              = values[6]   # Playback: Exclusive
    group.LowestVelocity                 = values[7]   # Velocity Range: Low
    group.HighestVelocity                 = values[8]   # Velocity Range: High
    group.SampleSelectRandOffset = values[9]
    # Boolean at body 0x08 (legacy 84), inside the struct map's 8x pad; expose it.
    if len(group.data) >= 85:
        group.unknown_byte_0x08 = struct.unpack_from(endian + 'B', data, 84)[0]
    # Release Trigger: Time -- a 32-bit engine field (legacy 92); the struct map reads
    # only its low 16 bits, so read the full width directly (upper bytes are 0 in practice).
    group.ReleaseTriggerDecayTime     = struct.unpack_from(endian + 'I', data, 92)[0]
    group.VelocityXFade     = values[11]-128     # Velocity Range: XFade
    group.VelocityXFadeType = values[12]  # Velocity Range: XFade Type
    group.NoteXFadeType      = values[13]  # Key Range: XFade Type
    group.NoteXFade          = values[14]-128 # Key Range: XFade
    group.SelByTempoLow       = values[15]  # Enable By Tempo: Low
    group.SelByTempoHigh      = values[16]  # Enable By Tempo: High
    group.FilterCutOffOffset           = values[17]  # Filter Offsets: Cutoff
    group.FilterResonanceOffset             = values[18]  # Filter Offsets: Res.
    group.Env1AttackOffset       = values[19]  # Envelope 1 Offsets: A (amp env)
    group.Env1DecayOffset        = values[20]  # Envelope 1 Offsets: D (amp env)
    group.Env1SustainOffset      = values[21]  # Envelope 1 Offsets: S (amp env)
    group.Env1ReleaseOffset      = values[22]  # Envelope 1 Offsets: R (amp env)
    group.ReleaseTrigger         = {0: False, 1:  True}[values[23] & 1]  # Release Trigger: On (0 = OFF, 1  = ON)
    group.Output                 = values[24]  # Mixer: Output
    group.SelByNoteNote      = values[25]  # Enable By Note: Value
    group.SelByGroupCycle     = values[26]  # -1 if no RR; otherwise group ID to play after
    group.enablebytype           = values[27]  # 'On' for first 'Enable by' sets this
    group.SelByCtrlCtrl   = values[28]  # Enable by Control: Value
    group.SelByCtrlLow     = values[29]  # Enable by Control: Low
    group.SelByCtrlHigh    = values[30]  # Enable by Control: High
    group.FirstNote              = values[31]  # Key Range: Low
    group.LastNote                = values[32]  # Key Range: High
    group.SelByChannelChannel    = values[33]+1  # Enable By Channel: Value (originally zero-based)
    group.SelByArticNum   = values[34]  # Enable by Articulation: Value
    if len(group.data) >= 188:
        group.SelByPitchLow      = values[35]  # Enable by Bend: Low
        group.SelByPitchHigh     = values[36]  # Enable by Bend: High
    if len(group.data) >= 196:
        group.Env1HoldOffset         = values[37]  # Envelope 1 Offsets: H (amp env)
        group.Env2AttackOffset       = values[38]  # Envelope 2 Offsets: A (env 2)
        group.Env2DecayOffset        = values[39]  # Envelope 2 Offsets: D (env 2)
        group.Env2SustainOffset      = values[40]  # Envelope 2 Offsets: S (env 2)
        group.Env2ReleaseOffset      = values[41]  # Envelope 2 Offsets: R (env 2)
        group.Env2HoldOffset         = values[42]  # Envelope 2 Offsets: H (env 2)
    if len(group.data) >= 208:
        group.Env1DelayOffset        = values[43]  # Env 1 (Amp) Delay Offset (delayAmpEnvOffset)
        group.Env2DelayOffset        = values[44]  # Env 2 (Filter) Delay Offset (delayFilterEnvOffset)

    #group options
    group.mute                = {0: False, 16:  True}[group.options & 16]  # 0 = OFF, 1  = ON
    group.ReleaseTriggerDecay = {0: False, 64:  True}[group.options & 64]  # 0 = OFF, 1  = ON
    group.fixedsampleselect   = {0: False, 128: True}[group.options & 128]  # 0 = OFF, 1  = ON -- Vel Range XfadeType OFF == 1/ON
    group.IgnorePitchWheelAndBend = bool(group.options & 2)   # bit 1
    group.DecayIsDbLinear         = bool(group.options & 4)   # bit 2
    group.RoundRobinPerNoteOn     = bool(group.options & 32)  # bit 5

    #group enable by
    group.SelByNote         = group.enablebytype == 1
    group.SelByGroup   = group.enablebytype == 2
    group.SelByCtrl      = group.enablebytype == 3
    group.SelByPitch         = group.enablebytype == 4
    group.SelByChannel      = group.enablebytype == 5
    group.SelByArtic = group.enablebytype == 6
    group.SelByTempo        = group.enablebytype == 7

    # "Live" pre-anchor time + dynamic-range offset (body 36/37 = legacy 112/113).
    if len(group.data) >= 114:
        group.LivePreAnchorTimeMs     = struct.unpack_from(endian + 'b', data, 112)[0]
        group.DynaRangeLowLevelOffset = struct.unpack_from(endian + 'b', data, 113)[0]
    # Stacked enable-by slots 2 & 3 (body 92/93 = legacy 168/169), present in longer groups.
    if len(group.data) >= 170:
        group.enablebytype2 = struct.unpack_from(endian + 'b', data, 168)[0]
        group.enablebytype3 = struct.unpack_from(endian + 'b', data, 169)[0]

    #print (group)

    # for field in fields(group):
    #     field_name = field.name
    #     field_value = getattr(group, field_name)
    #     print(f"{field_name}: {field_value}")

    return group


def export_group(group):
    to_pack = [
        b'\x00' * 8,
        b'TBOS',
        group.Name.encode('latin-1'),
        group.Volume,
        group.Pan,
        group.Voices,
        bool_to_byte([
            group.fixedsampleselect,                    # bit 7
            group.ReleaseTriggerDecay,                  # bit 6
            group.RoundRobinPerNoteOn,                  # bit 5
            group.mute,                                 # bit 4
            {0: False, 8:   True}[group.options & 8],   # bit 3 (pass through)
            group.DecayIsDbLinear,                      # bit 2
            group.IgnorePitchWheelAndBend,              # bit 1
            {0: False, 1:   True}[group.options & 1]    # bit 0 (pass through)
        ]),
        group.ExclusiveClass,
        group.LowestVelocity,
        group.HighestVelocity,
        group.SampleSelectRandOffset,
        group.ReleaseTriggerDecayTime & 0xFFFF,   # low 16 bits here; full 32-bit written via pack_into below
        group.VelocityXFade+128,
        group.VelocityXFadeType,
        group.NoteXFadeType,
        group.NoteXFade+128,
        group.SelByTempoLow,
        group.SelByTempoHigh,
        group.FilterCutOffOffset,
        group.FilterResonanceOffset,
        group.Env1AttackOffset,
        group.Env1DecayOffset,
        group.Env1SustainOffset,
        group.Env1ReleaseOffset,
        {False:0,True:1}[group.ReleaseTrigger],
        group.Output,
        group.SelByNoteNote,
        group.SelByGroupCycle,
        group.enablebytype,
        group.SelByCtrlCtrl,
        group.SelByCtrlLow,
        group.SelByCtrlHigh,
        group.FirstNote,
        group.LastNote,
        group.SelByChannelChannel - 1,
        group.SelByArticNum,
        group.SelByPitchLow,
        group.SelByPitchHigh,
        group.Env1HoldOffset,
        group.Env2AttackOffset,
        group.Env2DecayOffset,
        group.Env2SustainOffset,
        group.Env2ReleaseOffset,
        group.Env2HoldOffset,
        group.Env1DelayOffset,
        group.Env2DelayOffset
    ]
    #struct_format ="<8x4s64sbbBBBBBb8xH14xBBBB2xBBxbxb12xiiiixBBB4xiBBBBBBBB2xbbiiiiii4xii"
    struct_format = "<8s4s64sbbBBBBBb8xH14xBBBB2xBBxbxb12xiiiixBBB4xiBBBBBBBB2xbbiiiiii4xii"

    b = struct.pack(struct_format, *to_pack)
    out = bytearray(_merge_passthrough(group.data, b, struct_format))
    # Promoted out-of-struct field: the body-0x08 boolean (legacy 84) when set.
    if group.unknown_byte_0x08 is not None and len(out) >= 85:
        struct.pack_into('<B', out, 84, group.unknown_byte_0x08)
    # Promoted pad fields: Live pre-anchor / dyna-range offset (legacy 112/113) and
    # enable-by slots 2/3 (legacy 168/169). Equal the source bytes for unedited parses.
    if len(out) >= 114:
        struct.pack_into('<b', out, 112, group.LivePreAnchorTimeMs)
        struct.pack_into('<b', out, 113, group.DynaRangeLowLevelOffset)
    if len(out) >= 170:
        struct.pack_into('<b', out, 168, group.enablebytype2)
        struct.pack_into('<b', out, 169, group.enablebytype3)
    # Release-trigger decay time is 32-bit (legacy 92); write the full width.
    if len(out) >= 96:
        struct.pack_into('<I', out, 92, group.ReleaseTriggerDecayTime & 0xFFFFFFFF)
    return bytes(out)



@dataclass
class EXSSample():
    data:               str = None
    Name:               str = None
    id:                 int = None # set by parse function
    dataOffset:      int = None
    frameCount:             int = None  # length of sample IN SAMPLES
    sampleRate:               int = None
    bitdepth:           int = None
    channels:           int = 2
    fileType:      str = None  # default 'EVAW' = WAVE
    # WAVE     = b'EVAW'
    # AIFF     = b'FFIA'
    # CAF AAC  = b'ffac'
    # M4A AAC  = b' A4M'
    # MP3      = b'3GPM'
    # SD2      = b'f2dS'
    fileSize:           int = 0
    isCompressed:       bool = False
    folder:             str = None
    filename:           str = None
    # # Logic sometimes overwrites 'Samples\x00' over some Keymap files...
    # # sometimes there's enough characters left over to figure out the sample file
    # corruptedfilename: str = ""
    # newsamplefileindex: int = 0  # for merging
    # israwaudio: bool = False  # SFZ import uses this
    # embeddedsample: bool = False
    exsfile_pos: int = None  # used for in-place sample relinking
    # Windows volume / drive-reference id (sample body 72) — passed by the engine to
    # its Windows->POSIX path resolver; often the 0xffffff9c (-100) sentinel. 0 = none.
    WindowsVolumeId: int = 0
    merge_pitch_adjust: float = 0.0
    merge_monolith_index: int = 0
    merge_monolith_sample_start: int = 0
    merge_monolith_sample_end:   int = 0


def parse_sample(data,id=None,endian='<'):
    sample = EXSSample()
    sample.data = data
    #print (len(sample.data))

    # The 412-byte layout has only the folder path; the longer layout also
    # carries the file name. Pick the largest that fits.
    sample_formats = (
        (412, "<8x4s64sIIIIII4x4sII40x256s"),
        (668, "<8x4s64sIIIIII4x4sII40x256s256s"),
        (676, "<8x4s64sIIIIII4x4sII40x256s256s8x"),  # explicit long variant (8 trailing bytes)
    )
    struct_format = None
    for min_len, fmt in sample_formats:
        if len(sample.data) >= min_len:
            struct_format = fmt
    if struct_format is None:
        raise ValueError(f"EXS sample block too short: {len(sample.data)} bytes")
    struct_format = endian + struct_format[1:]  # honor the block's byte order
    struct_size   = struct.calcsize(struct_format)
    #print (f'\n{struct_size}')

    values = list(struct.unpack(struct_format,data[:struct_size]))
    # clean up name
    values[1]  = values[1].split(b'\x00',maxsplit=1)[0].decode('latin-1')
    values[11] = values[11].split(b'\x00', maxsplit=1)[0].decode('latin-1')


    if id is not None: sample.id = id
    sample.Name             = values[1]   # Sample Name
    sample.dataOffset    = values[2]   # Wave data start offset in file. In WAV files this is 4 bytes after 'data'
                                                # (the 4 bytes following 'data' is the chunk size in bytes, wave data starts after.)
    sample.frameCount           = values[3]   # length of sample IN SAMPLES
    sample.sampleRate             = values[4]   # sample rate (samples per second, e.g. 44100, 48000)
    sample.bitdepth         = values[5]   # bit depth (16 or 24 bits)
    sample.channels         = values[6]   # 1 = mono, 2 = stereo
    channels_again          = values[7]   # not sure why this is stored twice. they always match.
    sample.fileType    = values[8]   #
    sample.fileSize         = values[9]   # size (in bytes) of the actual sample file, probably used for relinking
    sample.isCompressed     = values[10]==1
    sample.folder           = values[11]
    # Windows volume/drive id at sample body 72 (legacy 148), inside the struct map's pad.
    if len(sample.data) >= 152:
        sample.WindowsVolumeId = struct.unpack_from(endian + 'i', data, 148)[0]
    if len(sample.data) >= 668:
        values[12] = values[12].split(b'\x00', maxsplit=1)[0].decode('latin-1')
        sample.filename         = values[12]

    # for field in fields(sample):
    #     field_name = field.name
    #     field_value = getattr(sample, field_name)
    #     print(f"{field_name}: {field_value}")

    return sample


def export_sample(sample):
    to_pack = [
        b'\x00' * 8,
        b'TBOS',
        sample.Name.encode('latin-1'),
        sample.dataOffset,
        sample.frameCount,
        sample.sampleRate,
        sample.bitdepth,
        sample.channels,
        sample.channels, #yep! again
        sample.fileType,
        sample.fileSize,
        {False: 0, True: 1}[sample.isCompressed],
        {False: b'\x00\x00\x00\x00', True: b'PMOC'}[sample.isCompressed],
        16, #not sure, but always 16! even at 24 bit
        sample.folder.encode('latin-1'),
    ]

    struct_format = "<8s4s64sIIIIII4x4sII4sI32x256s"

    if sample.filename is not None:
        struct_format += '256s8x'
        to_pack.append(sample.filename.encode('latin-1'))

    b = struct.pack(struct_format, *to_pack)
    # parse_sample doesn't read the codec fourcc (sf10) or the constant-16 (sf11);
    # export synthesizes them from isCompressed, which can differ from the source
    # (e.g. 'lpcm'/'mcpl'). Mark them pad for the overlay so a parsed sample keeps
    # its original bytes there; constructed samples (no .data) still get the synth.
    overlay_fmt = struct_format.replace('4sI32x', '4x4x32x')
    out = bytearray(_merge_passthrough(sample.data, b, overlay_fmt))
    # Windows volume/drive id (legacy 148) — equals the source bytes for an unedited parse.
    if len(out) >= 152:
        struct.pack_into('<i', out, 148, sample.WindowsVolumeId)
    return bytes(out)


def parse_params(data,endian='<'):
    chunk_length = len(data)

    # print (chunk_length)
    # print (data[:40])
    # print ("HI!")

    struct_format = endian + "8x4s64sI"
    struct_size = struct.calcsize(struct_format)
    #print (f'\n{struct_size}')

    values = list(struct.unpack(struct_format, data[:struct_size]))
    # clean up name
    values[1] = values[1].split(b'\x00', maxsplit=1)[0].decode('latin-1')
    #assert (values[1] == 'Default Param')

    old_style_param_count = values[2]
    old_style_param_ids   = list(struct.unpack(f'{endian}{old_style_param_count}B', data[80:80+old_style_param_count]))
    old_style_param_data  = list(struct.unpack(f'{endian}{old_style_param_count}h', data[80+old_style_param_count:80+old_style_param_count*3]))
    params = dict(zip(old_style_param_ids, old_style_param_data))

    new_style_param_offset = (80+old_style_param_count*3) + 4
    if len(data) > new_style_param_offset:
        new_style_param_count  = struct.unpack(endian + 'I', data[new_style_param_offset-4:new_style_param_offset])[0]
        # Some converted files store a corrupt/oversized count here; never read
        # past the end of the block.
        max_pairs = (len(data) - new_style_param_offset) // 4
        if new_style_param_count > max_pairs:
            new_style_param_count = max_pairs
        new_style_param_IDs_and_data = struct.unpack(f'{endian}{new_style_param_count*2}h', data[new_style_param_offset: new_style_param_offset+new_style_param_count * 4])

        new_params = dict(zip(new_style_param_IDs_and_data[::2], new_style_param_IDs_and_data[1::2]))
        params.update(new_params)

    if 0 in params: del(params[0])

    # for k, v in params.items():
    #     if k in exsparams.id_to_param:
    #         keyname = exsparams.id_to_param[k]
    #     else:
    #         keyname = hex(k)

    return params


def export_params(params):
    to_pack = [
        b'\x00' * 8,
        b'TBOS',
        b"Default Param",
        100, #old school param count
    ]

    old_school_param_keys, old_school_param_values = [], []
    new_school_param_keys, new_school_param_values = [], []

    # print (params.keys())

    #for k, v in params.items():
        #if k not in exsparams.parameter_order:
        #    print (f"Parameter #{k} found in instrument but not in my master parameter order list! Aborting!")
        #    quit()

    for k in exsparams.parameter_order:
        #get the value for this parameter
        if k in params: # if it exists in our patch
            v = params[k]
        elif k in exsparams.default_params: # if it's a default we haven't included
            v = exsparams.default_params[k]
        else: # if neither, skip it
            continue

        if k not in exsparams.mandatory_parameter_ids and v == 0: continue  # skip optional parameters that == 0

        if k < 255 and len(old_school_param_keys) < 100: # old school parameters
            old_school_param_keys.append(k)
            old_school_param_values.append(v)
        else: # new school parameters (keys > 255 and overflow when old-school parameters are greater than 100 in count)
            new_school_param_keys.append(k)
            new_school_param_values.append(v)

    # Preserve ANY parameter the reader captured that isn't in parameter_order (e.g. the
    # legacy EXS24 mkI control ids the engine still honours on load, or newer ids);
    # otherwise a rebuild-from-fields would silently drop them.
    _emitted = set(old_school_param_keys) | set(new_school_param_keys)
    for k, v in params.items():
        if k == 0 or v == 0 or k in exsparams.parameter_order or k in _emitted:
            continue
        if k < 255 and len(old_school_param_keys) < 100:
            old_school_param_keys.append(k)
            old_school_param_values.append(v)
        elif len(new_school_param_keys) < 200:
            new_school_param_keys.append(k)
            new_school_param_values.append(v)

    while len(old_school_param_keys) < 100:
        old_school_param_keys.append(0)
        old_school_param_values.append(0)

    while len(new_school_param_keys) < 200:
        new_school_param_keys.append(0)
        new_school_param_values.append(0)

    struct_format = "<8s4s64sI100B100hI400h"
    struct_size = struct.calcsize(struct_format)
    #print (f'\n{struct_size}')

    to_pack.extend(old_school_param_keys)
    to_pack.extend(old_school_param_values)
    to_pack.append(200) # number of 'new-school' params & values
    to_pack.extend([val for pair in zip(new_school_param_keys, new_school_param_values) for val in pair])

    #to_pack.extend([*zip(new_school_param_keys,new_school_param_values)])

    b = struct.pack(struct_format, *to_pack)
    return b
