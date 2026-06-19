# ███████╗██╗  ██╗███████╗██████╗  █████╗ ██████╗  █████╗ ███╗   ███╗███████╗   ██████╗ ██╗   ██╗
# ██╔════╝╚██╗██╔╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗████╗ ████║██╔════╝   ██╔══██╗╚██╗ ██╔╝
# █████╗   ╚███╔╝ ███████╗██████╔╝███████║██████╔╝███████║██╔████╔██║███████╗   ██████╔╝ ╚████╔╝
# ██╔══╝   ██╔██╗ ╚════██║██╔═══╝ ██╔══██║██╔══██╗██╔══██║██║╚██╔╝██║╚════██║   ██╔═══╝   ╚██╔╝
# ███████╗██╔╝ ██╗███████║██║     ██║  ██║██║  ██║██║  ██║██║ ╚═╝ ██║███████║██╗██║        ██║
# ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝╚═╝        ╚═╝



parameter_order = [65, 66, 7, 8, 3, 4, 10, 5, 51, 50, 45, 14, 15, 47, 20, 70, 71, 72, 73, 44, 28, 48, 53, 52, 243, 170, 30, 29, 75, 46, 90, 89, 60, 61, 62, 64, 63, 76, 77, 78, 79, 80, 92, 91, 82, 83, 84, 81, 85, 95, 164, 163, 98, 97, 165, 171, 167, 166, 172, 173, 174, 175, 176, 177, 233, 178, 244, 179, 180, 181, 182, 183, 234, 184, 245, 185, 186, 187, 188, 189, 235, 190, 246, 191, 192, 193, 194, 195, 236, 196, 247, 197, 198, 199, 200, 201, 237, 202, 248, 203, 204, 205, 206, 207, 238, 208, 249, 209, 210, 211, 212, 213, 239, 214, 250, 215, 216, 217, 218, 219, 240, 371, 378, 372, 375, 376, 377, 389, 390, 220, 251, 221, 222, 223, 224, 225, 241, 226, 252, 227, 228, 229, 230, 231, 242, 232, 352, 363, 405, 56, 500, 362, 402, 88, 381, 501, 353, 354, 355, 357, 358, 359, 502, 503, 505, 506, 509, 511, 512, 515, 516, 518, 519, 522, 524, 525, 528, 332, 333, 335, 334, 336, 391, 337, 341, 340, 342, 343, 344, 347, 349, 492, 491, 493, 496, 498, 535, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 278, 282, 387, 388, 253, 254]
default_params = {7: 0, 8: 0, 3: 2, 4: -1, 5: 16, 20: 0, 73: 0, 243: 0, 30: 1000, 29: 0, 75: 100, 46: 0, 90: -60, 89: 0, 60: 0, 61: 98, 62: 0, 64: 0, 63: 98, 76: 0, 77: 0, 78: 0, 79: 0, 80: 0, 92: 0, 82: 0, 83: 0, 84: 0, 81: 127, 85: 0, 97: 0, 165: 1, 167: 98, 166: -1, 172: 64, 173: 2, 174: -14, 175: -1, 176: 0, 177: 0, 179: 6, 180: -12, 181: 1, 182: 0, 183: 343, 254: 1000, 378: 0, 375: 1000, 376: 0, 377: 100, 389: 3, 390: 3, 363: 2, 500: 0, 362: 2, 501: 0, 353: 2, 354: 0, 355: 0, 357: 0, 358: 0, 359: 0, 502: 0, 503: 2, 505: 0, 506: 0, 509: 0, 511: 0, 512: 0, 515: 0, 516: 2, 518: 0, 519: 0, 522: 0, 524: 0, 525: 0, 528: 0, 335: 0, 334: 0, 336: 0, 337: 0, 341: 0, 340: 0, 342: 0, 343: 0, 344: 0, 347: 0, 349: 0, 492: 0, 491: 98, 493: 0, 496: 0, 498: 0, 535: 1, 282: 48, 387: -10, 388: 1}
mandatory_parameter_ids = [7, 8, 3, 4, 5, 20, 73, 243, 30, 29, 75, 46, 90, 89, 60, 61, 62, 64, 63, 76, 77, 78, 79, 80, 92, 82, 83, 84, 81, 85, 97, 165, 167, 166, 172, 173, 174, 175, 176, 177, 179, 180, 181, 182, 183, 254, 378, 375, 376, 377, 389, 390, 363, 500, 362, 501, 353, 354, 355, 357, 358, 359, 502, 503, 505, 506, 509, 511, 512, 515, 516, 518, 519, 522, 524, 525, 528, 335, 334, 336, 337, 341, 340, 342, 343, 344, 347, 349, 492, 491, 493, 496, 498, 535, 282, 387, 388]

# ── Mirror Logic's fresh-save defaults EXACTLY (verified param-for-param against
#    /Users/jonkubis/Music/temp/default_patch.exs, a real empty Sampler save). ──
default_params.update({
    7:   -6,    # Output Volume default is -6 dB (not 0)
    63:  34,    # LFO 2 Rate
    174: -3,    # MOD1 Source = Velocity (with dest 173=2 Sample Select, amounts below = the
    176: 1000,  #   engine's default "Velocity -> Sample Select @ 100%" routing)
    177: 1000,  # MOD1 Amount Via
    390: 4,     # Filter 2 Type
})
default_params.pop(342, None)   # 0x156 LFO 2 Rate Mode: Logic OMITS it at default; do the same
mandatory_parameter_ids = [pid for pid in mandatory_parameter_ids if pid != 342]


PARAM_MASTER_VOLUME             = 0x07
PARAM_MASTER_PAN                = 0x160

PARAM_VOLUME_KEYSCALE           = 0x08
PARAM_PITCH_BEND_UP             = 0x03
PARAM_PITCH_BEND_DOWN           = 0x04
PARAM_MONO_LEGATO               = 0x0a
PARAM_MIDI_MONO_MODE            = 0x116
PARAM_MIDI_MONO_MODE_PITCH_RANGE = 0x11a

PARAM_POLYPHONY_VOICES          = 0x05
PARAM_TRANSPOSE                 = 0x2d
PARAM_COARSE_TUNE               = 0x0e
PARAM_FINE_TUNE                 = 0x0f
PARAM_GLIDE                     = 0x14
PARAM_PORTA_DOWN                = 0x48
PARAM_PORTA_UP                  = 0x49

PARAM_FILTER1_TOGGLE            = 0x2c
PARAM_FILTER1_TYPE              = 0xf3
PARAM_FILTER1_FAT               = 0xaa
PARAM_FILTER1_CUTOFF            = 0x1e
PARAM_FILTER1_RESO              = 0x1d
PARAM_FILTER1_DRIVE             = 0x4b
PARAM_FILTER1_KEYTRACK          = 0x2e

PARAM_FILTER2_TOGGLE            = 0x174
PARAM_FILTER2_TYPE              = 0x186
PARAM_FILTER2_CUTOFF            = 0x177
PARAM_FILTER2_RESO              = 0x178
PARAM_FILTER2_DRIVE             = 0x179

PARAM_FILTERS_SERIAL_PARALLEL   = 0x173
PARAM_FILTERS_BLEND             = 0x17a

PARAM_LFO_1_FADE                = 0x3c
PARAM_LFO_1_RATE                = 0x3d
PARAM_LFO_1_WAVE_SHAPE          = 0x3e
PARAM_LFO_1_KEY_TRIGGER         = 0x14c
PARAM_LFO_1_MONO_POLY           = 0x14d
PARAM_LFO_1_PHASE               = 0x14e
PARAM_LFO_1_POSITIVE_OR_MIDPOINT = 0x14f
PARAM_LFO_1_TEMPO_SYNC          = 0x150
PARAM_LFO_1_FADE_IN_OR_OUT      = 0x187

PARAM_LFO_2_RATE                = 0x3f
PARAM_LFO_2_WAVE_SHAPE          = 0x40
PARAM_LFO_2_FADE                = 0x151
PARAM_LFO_2_KEY_TRIGGER         = 0x152
PARAM_LFO_2_MONO_POLY           = 0x153
PARAM_LFO_2_PHASE               = 0x154
PARAM_LFO_2_POSITIVE_OR_MIDPOINT = 0x155
PARAM_LFO_2_TEMPO_SYNC          = 0x156
PARAM_LFO_2_FADE_IN_OR_OUT      = 0x188

PARAM_LFO_3_RATE                = 0xa7
PARAM_LFO_3_WAVE_SHAPE          = 0x158
PARAM_LFO_3_FADE                = 0x157
PARAM_LFO_3_KEY_TRIGGER         = 0x159
PARAM_LFO_3_MONO_POLY           = 0x15a
PARAM_LFO_3_PHASE               = 0x15b
PARAM_LFO_3_POSITIVE_OR_MIDPOINT = 0x15c
PARAM_LFO_3_TEMPO_SYNC          = 0x15d
PARAM_LFO_3_FADE_IN_OR_OUT      = 0x189

# ENV1 = amplitude envelope, ENV2 = filter envelope. The Attack/Decay/Release time
# params below are byte values 0-127; convert to/from milliseconds with MS_LUT /
# env_value_to_ms() / env_ms_to_value() (defined near the bottom of this file).
PARAM_ENV2_TYPE                 = 0x16a # 0=AD, 1=AR, 2=ADSR, 3=AHDSR, 4=DADSR, 5=DAHDSR
PARAM_ENV2_VEL_SENS             = 0x17d

PARAM_ENV2_DELAY_START          = 0x16c
PARAM_ENV2_ATK_CURVE            = 0x192
PARAM_ENV2_ATK_HI_VEL           = 0x4c
PARAM_ENV2_ATK_LO_VEL           = 0x4d
PARAM_ENV2_HOLD                 = 0x58  # RE: 0x58 = "Env 2 Hold" (was 0x38 -- swapped with ENV1)
PARAM_ENV2_DECAY                = 0x4e
PARAM_ENV2_SUSTAIN              = 0x4f
PARAM_ENV2_RELEASE              = 0x50
PARAM_ENV2_TIME_CURVE           = 0x5b # NOTE: legacy id; AutoSampler writes amp-env(ENV1) attackShape here -- env# unconfirmed

PARAM_ENV1_TYPE                 = 0x16b # 0=AD, 1=AR, 2=ADSR, 3=AHDSR, 4=DADSR, 5=DAHDSR
PARAM_ENV1_VEL_SENS             = 0x5a
PARAM_ENV1_VOLUME_HIGH          = 0x59 # legacy ENV1(Amp) dynamic-range high (AutoSampler writes dynRangeHigh*2 here); absent from modern Sampler table
PARAM_ENV1_DELAY_START          = 0x16d
PARAM_ENV1_ATK_CURVE            = 0x195
PARAM_ENV1_ATK_HI_VEL           = 0x52
PARAM_ENV1_ATK_LO_VEL           = 0x53
PARAM_ENV1_HOLD                 = 0x38  # RE: 0x38 = "Env 1 (Amp) Hold" (was 0x58 -- swapped with ENV2)
PARAM_ENV1_DECAY                = 0x54
PARAM_ENV1_SUSTAIN              = 0x51
PARAM_ENV1_RELEASE              = 0x55
# (PARAM_ENV1_TIME_CURVE removed - no such engine id: 0x5b is "Attack Curve All Env";
#  per-env attack curves are ids 405/402/408/507/520, time modes 500/501/502/515/528.)
PARAM_ENV_TIME_VIA_KEY          = 0x5c # "Time via Key" (envelope time keyscale) -- from Sampler descriptor table

PARAM_AMP_VELOCITY_CURVE        = 0x183
PARAM_VELOCITY_OFFSET           = 0x5f
PARAM_RANDOM_VELOCITY           = 0xa4
PARAM_RANDOM_SAMPLE_SEL         = 0xa3
PARAM_RANDOM_PITCH              = 0x62
PARAM_XFADE_AMOUNT              = 0x61
PARAM_XFADE_TYPE                = 0xa5
PARAM_UNISON_TOGGLE             = 0xab
PARAM_COARSE_TUNE_REMOTE        = 0xa6
PARAM_HOLD_VIA_CONTROL          = 0xac


# ── Modulation-matrix VALUE codes (decoded from the Sampler engine via RE) ──
# These are values STORED IN the PARAM_MODn_DESTINATION / _SOURCE params, not ids.
# The getter applies
# no transform, so these are the literal on-disk values. The full 0..90 destination
# enum is engine-generated -- confirm the rest by differential testing in Logic.
MOD_DEST_NONE          = 0
MOD_DEST_SAMPLE_SELECT = 2      # NB: this repo's export doc once said 8 -- WRONG, it is 2
MOD_DEST_PITCH         = 6
MOD_SRC_NONE           = -1     # also used for "no Via"
MOD_SRC_LFO1           = -12
# a positive source value is a MIDI CC number (1 = Mod Wheel, 11 = Expression)
MOD_AMOUNT_FULL        = 1000   # 1000 = 100%
MOD_SLOT_ABSENT        = -1234567  # 0xFFED2979 sentinel: param/slot not present

# Full modulation DESTINATION enum (value stored in PARAM_MODn_DESTINATION -> target),
# validated against Logic and
# every destination code in the 2,236-file factory corpus. Grouped LFO/Env targets are
# indexed ascending (LFO1..4 / Env1..5; Env1 = Amp); singular + Env2 targets are
# corpus-confirmed.
MOD_DESTINATIONS = {
    -1: "(none / off)", 0: "(none)", 2: "Sample Select", 4: "Sample Start Later", 5: "Glide Time",
    6: "Pitch", 7: "Filter 1 Drive", 8: "Filter 1 Cutoff", 9: "Filter 1 Resonance",
    10: "Volume", 11: "Pan", 12: "Relative Volume", 13: "Relative Volume (auto adjust)",
    15: "LFO 1 Fade", 43: "LFO 2 Fade", 44: "LFO 3 Fade", 70: "LFO 4 Fade",
    16: "LFO 1 Rate", 17: "LFO 2 Rate", 18: "LFO 3 Rate", 71: "LFO 4 Rate",
    45: "LFO 1 Phase", 46: "LFO 2 Phase", 47: "LFO 3 Phase", 72: "LFO 4 Phase",
    20: "Env 1 Attack", 24: "Env 2 Attack", 52: "Env 3 Attack", 75: "Env 4 Attack", 83: "Env 5 Attack",
    21: "Env 1 Decay", 25: "Env 2 Decay", 54: "Env 3 Decay", 77: "Env 4 Decay", 85: "Env 5 Decay",
    22: "Env 1 Release", 26: "Env 2 Release", 55: "Env 3 Release", 78: "Env 4 Release", 86: "Env 5 Release",
    32: "Env 1 Delay", 33: "Env 2 Delay", 51: "Env 3 Delay", 74: "Env 4 Delay", 82: "Env 5 Delay",
    49: "Env 1 Hold", 50: "Env 2 Hold", 53: "Env 3 Hold", 76: "Env 4 Hold", 84: "Env 5 Hold",
    63: "Env 1 Atk Curve", 64: "Env 2 Atk Curve", 65: "Env 3 Atk Curve", 79: "Env 4 Atk Curve", 87: "Env 5 Atk Curve",
    66: "Env 1 Time", 67: "Env 2 Time", 68: "Env 3 Time", 80: "Env 4 Time", 88: "Env 5 Time",
    23: "All Env Time Stages", 28: "Hold", 30: "Articulation ID", 34: "Bit Resolution",
    36: "Loop Position", 37: "Loop Start", 38: "Loop End", 40: "Sample Start", 41: "Sample End",
    57: "Filter 2 Drive", 58: "Filter 2 Cutoff", 59: "Filter 2 Resonance", 60: "Filter Blend",
    61: "Filter 1+2 Cutoff", 90: "Flex Speed", 91: 'Trigger "Definable Ctrl" Group',
}

# Full modulation SOURCE enum (value stored in PARAM_MODn_SOURCE -> source name).
# Positive = MIDI CC number (only common CCs named here; others render as "Ctrl #N").
# Negative = internal modulator. Corpus-validated.
MOD_SOURCES = {
    1: "Mod Wheel", 7: "CC7 (Volume)", 10: "CC10 (Pan)", 11: "CC11 (Expression)",
    0: "(none)", -1: "(constant 'on'/max)", -3: "Velocity", -4: "Key (Note Number)",
    -5: "Pitch Bend", -7: "Aftertouch", -8: "Release Velocity",
    -10: "LFO 3", -11: "LFO 2", -12: "LFO 1", -13: "Env 1 (Amp)", -14: "Env 2",
    -16: "Maximum", -17: "Side Chain", -18: "Random",
    -20: "LFO 4", -21: "Env 3", -22: "Env 4", -23: "Env 5",
}


def mod_dest_name(value):
    """Name of a modulation DESTINATION code, or None if reserved/unmapped."""
    return MOD_DESTINATIONS.get(value)


def mod_src_name(value):
    """Name of a modulation SOURCE code; unnamed positive -> 'Ctrl #N' (MIDI CC)."""
    if value in MOD_SOURCES:
        return MOD_SOURCES[value]
    return f"Ctrl #{value}" if value > 0 else None


# ── Enumerated parameter VALUE tables (value stored in the param -> UI name),
#    corpus-validated against Logic. ──
# Legacy EXS24 filter type (PARAM_FILTER1_TYPE 0xf3 / PARAM_FILTER2_TYPE 0x186).
# NOTE: corrects the older doc order -- the engine's actual value->name is:
FILTER_TYPES = {0: "LP 12 dB", 1: "LP 18 dB", 2: "LP 24 dB", 3: "LP 6 dB", 4: "BP", 5: "HP"}
# LFO waveform (PARAM_LFO_n_WAVE_SHAPE). 0 = Triangle is the factory default ("Saw" = Saw Down).
LFO_WAVEFORMS = {0: "Triangle", 1: "Saw", 2: "Saw Up", 3: "Square", 4: "Square Down",
                 5: "Random", 6: "Random Smooth", 7: "Sine"}
# Envelope type (PARAM_ENVn_TYPE). 2 = ADSR is universal in the factory library.
ENV_TYPES = {0: "AD", 1: "AR", 2: "ADSR", 3: "AHDSR", 4: "DADSR", 5: "DAHDSR"}
# Mono mode (PARAM_MONO_LEGATO 0x0a).
MONO_MODES = {0: "Poly", 1: "Mono", 2: "Legato"}


PARAM_MOD1_DESTINATION          = 0xad
PARAM_MOD1_SOURCE               = 0xae
PARAM_MOD1_VIA                  = 0xaf
PARAM_MOD1_AMOUNT_LOW           = 0xb0
PARAM_MOD1_AMOUNT_HIGH          = 0xb1
PARAM_MOD1_SRC_INVERT           = 0xe9
PARAM_MOD1_VIA_INVERT           = 0xb2
PARAM_MOD1_BYPASS               = 0xf4

PARAM_MOD2_DESTINATION          = 0xb3
PARAM_MOD2_SOURCE               = 0xb4
PARAM_MOD2_VIA                  = 0xb5
PARAM_MOD2_AMOUNT_LOW           = 0xb6
PARAM_MOD2_AMOUNT_HIGH          = 0xb7
PARAM_MOD2_SRC_INVERT           = 0xea
PARAM_MOD2_VIA_INVERT           = 0xb8
PARAM_MOD2_BYPASS               = 0xf5

PARAM_MOD3_DESTINATION          = 0xb9
PARAM_MOD3_SOURCE               = 0xba
PARAM_MOD3_VIA                  = 0xbb
PARAM_MOD3_AMOUNT_LOW           = 0xbc
PARAM_MOD3_AMOUNT_HIGH          = 0xbd
PARAM_MOD3_SRC_INVERT           = 0xeb
PARAM_MOD3_VIA_INVERT           = 0xbe
PARAM_MOD3_BYPASS               = 0xf6

PARAM_MOD4_DESTINATION          = 0xbf
PARAM_MOD4_SOURCE               = 0xc0
PARAM_MOD4_VIA                  = 0xc1
PARAM_MOD4_AMOUNT_LOW           = 0xc2
PARAM_MOD4_AMOUNT_HIGH          = 0xc3
PARAM_MOD4_SRC_INVERT           = 0xec
PARAM_MOD4_VIA_INVERT           = 0xc4
PARAM_MOD4_BYPASS               = 0xf7

PARAM_MOD5_DESTINATION          = 0xc5
PARAM_MOD5_SOURCE               = 0xc6
PARAM_MOD5_VIA                  = 0xc7
PARAM_MOD5_AMOUNT_LOW           = 0xc8
PARAM_MOD5_AMOUNT_HIGH          = 0xc9
PARAM_MOD5_SRC_INVERT           = 0xed
PARAM_MOD5_VIA_INVERT           = 0xca
PARAM_MOD5_BYPASS               = 0xf8

PARAM_MOD6_DESTINATION          = 0xcb
PARAM_MOD6_SOURCE               = 0xcc
PARAM_MOD6_VIA                  = 0xcd
PARAM_MOD6_AMOUNT_LOW           = 0xce
PARAM_MOD6_AMOUNT_HIGH          = 0xcf
PARAM_MOD6_SRC_INVERT           = 0xee
PARAM_MOD6_VIA_INVERT           = 0xd0
PARAM_MOD6_BYPASS               = 0xf9

PARAM_MOD7_DESTINATION          = 0xd1
PARAM_MOD7_SOURCE               = 0xd2
PARAM_MOD7_VIA                  = 0xd3
PARAM_MOD7_AMOUNT_LOW           = 0xd4
PARAM_MOD7_AMOUNT_HIGH          = 0xd5
PARAM_MOD7_SRC_INVERT           = 0xef
PARAM_MOD7_VIA_INVERT           = 0xd6
PARAM_MOD7_BYPASS               = 0xfa

PARAM_MOD8_DESTINATION          = 0xd7
PARAM_MOD8_SOURCE               = 0xd8
PARAM_MOD8_VIA                  = 0xd9
PARAM_MOD8_AMOUNT_LOW           = 0xda
PARAM_MOD8_AMOUNT_HIGH          = 0xdb
PARAM_MOD8_SRC_INVERT           = 0xf0
PARAM_MOD8_VIA_INVERT           = 0xdc
PARAM_MOD8_BYPASS               = 0xfb

PARAM_MOD9_DESTINATION          = 0xdd
PARAM_MOD9_SOURCE               = 0xde
PARAM_MOD9_VIA                  = 0xdf
PARAM_MOD9_AMOUNT_LOW           = 0xe0
PARAM_MOD9_AMOUNT_HIGH          = 0xe1
PARAM_MOD9_SRC_INVERT           = 0xf1
PARAM_MOD9_VIA_INVERT           = 0xe2
PARAM_MOD9_BYPASS               = 0xfc

PARAM_MOD10_DESTINATION         = 0xe3
PARAM_MOD10_SOURCE              = 0xe4
PARAM_MOD10_VIA                 = 0xe5
PARAM_MOD10_AMOUNT_LOW          = 0xe6
PARAM_MOD10_AMOUNT_HIGH         = 0xe7
PARAM_MOD10_SRC_INVERT          = 0xf2
PARAM_MOD10_VIA_INVERT          = 0xe8
PARAM_MOD10_BYPASS              = 0xfd

PARAM_MOD11_DESTINATION         = 0x19b
PARAM_MOD11_SOURCE              = 0x19c
PARAM_MOD11_VIA                 = 0x19d
PARAM_MOD11_AMOUNT_LOW          = 0x19e
PARAM_MOD11_AMOUNT_HIGH         = 0x19f
PARAM_MOD11_SRC_INVERT          = 0x1a0
PARAM_MOD11_VIA_INVERT          = 0x1a1
PARAM_MOD11_BYPASS              = 0x1a2

# ── Extended modulation slots 11-20 (the modern Sampler's full 20-slot mod matrix) ──
# Slots 11-20 occupy a contiguous 8-id-per-slot region 0x19b..0x1ea; each slot's
# sub-fields are, in order: DESTINATION, SOURCE, VIA, AMOUNT_LOW, AMOUNT_HIGH,
# SRC_INVERT, VIA_INVERT, BYPASS. Slot 11 (0x19b..0x1a2) is declared explicitly above;
# slots 12-20 are generated here (PARAM_MOD12_* .. PARAM_MOD20_*). Decoded from the
# engine descriptor table and verified against a real 20-slot instrument.
_MOD_SUBFIELDS = ('DESTINATION', 'SOURCE', 'VIA', 'AMOUNT_LOW', 'AMOUNT_HIGH',
                  'SRC_INVERT', 'VIA_INVERT', 'BYPASS')
extended_mod_parameter_ids = []
for _slot in range(11, 21):
    _base = 0x19b + (_slot - 11) * 8
    for _i, _sub in enumerate(_MOD_SUBFIELDS):
        _pid = _base + _i
        globals().setdefault('PARAM_MOD%d_%s' % (_slot, _sub), _pid)  # keep existing MOD11_* names
        extended_mod_parameter_ids.append(_pid)
# The writer only emits ids present in parameter_order; without this, mod slots 11-20
# are silently dropped on write. Append any not already covered.
parameter_order += [pid for pid in extended_mod_parameter_ids if pid not in parameter_order]

# ── Newly-cataloged Logic Sampler params ──
# Per-output Gain bus. Engine 'group' = "Gain", unit dB. NB: descriptor max=12 is a
# one-sided bound; real factory values reach ~ -68 dB -> these are SIGNED, never clamp.
PARAM_GAIN_OUTPUT_MAIN  = 0x11b
PARAM_GAIN_OUTPUT_3_4   = 0x11c
PARAM_GAIN_OUTPUT_5_6   = 0x11d
PARAM_GAIN_OUTPUT_7_8   = 0x11e
PARAM_GAIN_OUTPUT_9_10  = 0x11f
PARAM_GAIN_OUTPUT_11    = 0x120
PARAM_GAIN_OUTPUT_12    = 0x121
PARAM_GAIN_OUTPUT_13    = 0x122
PARAM_GAIN_OUTPUT_14    = 0x123
PARAM_GAIN_OUTPUT_15    = 0x124
PARAM_GAIN_OUTPUT_16    = 0x125
PARAM_GAIN_OUTPUT_17_18 = 0x126
PARAM_GAIN_OUTPUT_19_20 = 0x127
PARAM_GAIN_OUTPUT_21_22 = 0x128
PARAM_GAIN_OUTPUT_23_24 = 0x129
PARAM_GAIN_OUTPUT_25_26 = 0x12a
# LFO 4 (mirrors LFO 1-3)
PARAM_LFO_4_RATE        = 0x1eb
PARAM_LFO_4_FADE        = 0x1ec
PARAM_LFO_4_WAVE_SHAPE  = 0x1ed
PARAM_LFO_4_PHASE       = 0x1f0
PARAM_LFO_4_RATE_MODE   = 0x1f2   # engine "LFO 4 Rate Mode" (tempo-sync/free, max=2)
# Env 5 (mirrors Env 4)
PARAM_ENV5_TYPE         = 0x204
PARAM_ENV5_ATTACK       = 0x206   # engine "Env 5 Attack" (base attack)
PARAM_ENV5_ATTACK_VIA_VEL = 0x207 # engine "Env 5 Att. via Vel"
PARAM_ENV5_DECAY        = 0x20a
PARAM_ENV5_SUSTAIN      = 0x20c
PARAM_ENV5_RELEASE      = 0x20d
PARAM_ENV5_TIME_MODE    = 0x210
# Singles
PARAM_CUTOFF_ON_OFF           = 0xfe    # engine "Cutoff (On/Off)"
PARAM_IGNORE_RELEASE_VELOCITY = 0x184   # engine "Ignore Release Velocity"
PARAM_USE_TRANSIENTS          = 0x217   # engine "Use Transients (INTERNAL)" (Flex)
PARAM_FILTER1_TYPE_MODERN     = 0x185   # modern "Filter 1 Type" (max=28); 0xf3 is the LEGACY 6-mode Filter Type

# ─────────────────────────────────────────────────────────────────────────────
# LEGACY EXS24-ONLY PARAMETERS
# These IDs appear in factory .exs files but are ABSENT from the modern Logic
# Logic Sampler's parameter table;
# see sampler_param_table.py. They are EXS24-era fields the
# current engine dropped -- there is no modern UI control or name for them. Correct
# handling is to PRESERVE them on round-trip and NOT interpret. The comment on each
# is the value pattern observed across the factory library.
# ─────────────────────────────────────────────────────────────────────────────
PARAM_UNKNOWN_0x01 = 0x01   # varied values
PARAM_UNKNOWN_0x16 = 0x16   # usually 0 (sits near GLIDE 0x14)
PARAM_UNKNOWN_0x18 = 0x18   # constant 48
PARAM_UNKNOWN_0x19 = 0x19   # constant 2
PARAM_UNKNOWN_0x31 = 0x31   # constant 1 (default-on toggle?)
PARAM_UNKNOWN_0x36 = 0x36   # level-like: 100/50/70
PARAM_UNKNOWN_0x37 = 0x37   # level-like: 48/10/50
PARAM_UNKNOWN_0x3a = 0x3a   # usually 0
PARAM_UNKNOWN_0x3b = 0x3b   # usually 0
PARAM_UNKNOWN_0x56 = 0x56   # time/rate-like: 420/500
PARAM_UNKNOWN_0x5d = 0x5d   # usually 0 (pairs with 0x5e)
PARAM_UNKNOWN_0x5e = 0x5e   # usually 0 (pairs with 0x5d)

# Handle for the identification pass; iterate this to report/relabel them.
undocumented_parameter_ids = [
    PARAM_UNKNOWN_0x01, PARAM_UNKNOWN_0x16, PARAM_UNKNOWN_0x18, PARAM_UNKNOWN_0x19,
    PARAM_UNKNOWN_0x31, PARAM_UNKNOWN_0x36, PARAM_UNKNOWN_0x37, PARAM_UNKNOWN_0x3a,
    PARAM_UNKNOWN_0x3b, PARAM_UNKNOWN_0x56, PARAM_UNKNOWN_0x5d, PARAM_UNKNOWN_0x5e,
]

# Preserve them on export. Appended last so the well-known params claim the 100
# old-style slots first (real files write at most ~90, so there is headroom).
parameter_order += undocumented_parameter_ids

# EXS24 envelope time encoding. The Attack/Decay/Release BYTE VALUE (0-127, stored in
# the ENV*_* time params) maps to MILLISECONDS by an EXACT 4th-power curve recovered
# ms = 10000 * (byte/127)**4 .
# MS_LUT below is the original measured table (kept for reference); it agrees with the
# formula to 3+ sig figs across the usable range. env_value_to_ms()/env_ms_to_value()
# are now formula-based. Sustain is a 0-127 LEVEL, not a time.
ENV_TIME_MAX_MS = 10000.0
MS_LUT = [0,0.001,0.002,0.003,0.009,0.024,0.049,0.092,0.157,0.252,0.384,0.562,0.797,1.097,1.476,1.946,2.519,3.21,4.035,5.009,6.15,7.475,9.004,10.757,12.753,15.015,17.566,20.428,23.627,27.187,31.136,35.5,40.307,45.586,51.368,57.684,64.564,72.043,80.152,88.929,98.406,108.62,119.61,131.41,144.07,157.62,172.11,187.57,204.05,221.59,240.25,260.05,281.05,303.31,326.85,351.75,378.03,405.77,435,465.79,498.18,532.23,568,605.54,644.91,686.18,729.39,774.61,821.9,871.32,922.94,976.82,1033,1091.6,1152.6,1216.2,1282.4,1351.2,1422.8,1497.2,1574.5,1654.7,1737.9,1824.3,1913.8,2006.5,2102.7,2202.2,2305.2,2411.8,2522,2636,2753.8,2875.5,3001.2,3130.9,3264.9,3403,3545.5,3692.5,3844,4000,4160.8,4326.4,4496.9,4672.4,4852.9,5038.7,5229.7,5426.1,5628,5835.4,6048.6,6267.5,6492.3,6723.2,6960.1,7203.2,7452.6,7708.5,7970.9,8239.9,8515.7,8798.4,9088,9384.8,9688.7,10000]


def env_value_to_ms(value):
    """EXS envelope Attack/Decay/Release byte value (0-127) -> milliseconds.

    Exact closed form used by Logic's Sampler: the engine
    encodes ms = 10000 * (byte/127)**4. Reproduces the measured MS_LUT to 3+ sig figs
    (byte 64 -> 645 ms, 100 -> 3844 ms, 127 -> 10000 ms).
    """
    value = max(0, min(127, int(value)))
    return ENV_TIME_MAX_MS * (value / 127.0) ** 4


def ms_to_index(table, ms):
    """Return the index in `table` whose value is closest to `ms` (i.e. the byte
    value for a milliseconds target). Returns the index, matching its name."""
    return min(range(len(table)), key=lambda i: abs(table[i] - ms))


def env_ms_to_value(ms):
    """Milliseconds -> EXS envelope Attack/Decay/Release byte value (0-127).

    Inverse of the engine's closed form: byte = 127 * (ms/10000)**0.25.
    """
    if ms <= 0:
        return 0
    return max(0, min(127, int(round(127 * (ms / ENV_TIME_MAX_MS) ** 0.25))))

# ── Canonical Logic Sampler names for mislabeled constants (verified against the parameter
#    descriptor table). The original PARAM_* names above stay as back-compat ALIASES;
#    these are defined last so id_to_param resolves the engine name for display. ──
PARAM_PITCHER             = 0x48   # was PARAM_PORTA_DOWN  (engine "Pitcher": bipolar +/-12, NOT portamento)
PARAM_PITCHER_VIA_VEL     = 0x49   # was PARAM_PORTA_UP    (engine "Pitcher via Vel")
PARAM_LEVEL_VIA_VEL       = 0x59   # was PARAM_ENV1_VOLUME_HIGH (engine "Level via Vel", Amp dB)
PARAM_LEVEL_FIXED         = 0x5a   # was PARAM_ENV1_VEL_SENS    (engine "Level Fixed", Amp dB)
PARAM_ATTACK_CURVE_ALL_ENV = 0x5b  # was PARAM_ENV2_TIME_CURVE  (engine "Attack Curve All Env")
PARAM_ENV1_ATTACK         = 0x52   # was PARAM_ENV1_ATK_HI_VEL (engine base "Env 1 (Amp) Attack")
PARAM_ENV1_ATTACK_VIA_VEL = 0x53   # was PARAM_ENV1_ATK_LO_VEL (engine "Env 1 (Amp) Att. via Vel")
PARAM_ENV2_ATTACK         = 0x4c   # was PARAM_ENV2_ATK_HI_VEL
PARAM_ENV2_ATTACK_VIA_VEL = 0x4d   # was PARAM_ENV2_ATK_LO_VEL
PARAM_LFO_1_POLY = 0x14d; PARAM_LFO_2_POLY = 0x153; PARAM_LFO_3_POLY = 0x15a          # were *_MONO_POLY
PARAM_LFO_1_UNIPOLAR = 0x14f; PARAM_LFO_2_UNIPOLAR = 0x155; PARAM_LFO_3_UNIPOLAR = 0x15c  # were *_POSITIVE_OR_MIDPOINT
PARAM_LFO_1_RATE_MODE = 0x150; PARAM_LFO_2_RATE_MODE = 0x156; PARAM_LFO_3_RATE_MODE = 0x15d  # were *_TEMPO_SYNC (3-value mode)
PARAM_FILTER_PARALLEL_PROCESSING = 0x173  # was PARAM_FILTERS_SERIAL_PARALLEL
PARAM_OUTPUT_VOLUME = 0x07   # engine name for PARAM_MASTER_VOLUME
PARAM_OUTPUT_PAN    = 0x160  # engine name for PARAM_MASTER_PAN


# ── Completeness pass (2026-06 Logic Sampler parameter audit) ───────────────────
# PARAM_* constants for every serializable engine id that lacked one (Env3/4/5 +
# LFO4 delay/hold/curve/velocity/time-mode, Flex, Quick Sampler), plus the legacy
# legacy EXS24 mkI control ids.
PARAM_LFO_TRIANGLE_SHAPE                 = 67
PARAM_VOICES                             = 299
PARAM_SAMPLEMODESELECT                   = 300
PARAM_PLAYMODESELECT                     = 301
PARAM_MODSELECT                          = 302
PARAM_REC_OPTIONS                        = 303
PARAM_WAVE_ENV_MODE                      = 304
PARAM_EXPAND_VIEW                        = 305
PARAM_LOOP_MODE                          = 306
PARAM_ONE_SHOT_REVERSE                   = 307
PARAM_ROOT_KEY                           = 308
PARAM_FINE_TUNE_QUICK_SAMPLER            = 309
PARAM_PITCH_KEY                          = 310
PARAM_SLICE_MODE                         = 311
PARAM_TRANS_SENS                         = 312
PARAM_BEAT_SENS                          = 313
PARAM_EQUAL_SENS                         = 314
PARAM_SLICE_FILL_KEY                     = 315
PARAM_FILL_KEY_MODE                      = 316
PARAM_SLICE_GATE                         = 317
PARAM_SLICE_PLAY_TO_END                  = 318
PARAM_ENV3_TYPE                          = 353
PARAM_ENV3_ATTACK                        = 354
PARAM_ENV3_ATT_VIA_VEL                   = 355
PARAM_ENV3_DECAY                         = 357
PARAM_ENV3_SUSTAIN                       = 358
PARAM_ENV3_RELEASE                       = 359
PARAM_STEREO_MODE                        = 360
PARAM_FLEX_MODE                          = 361
PARAM_ENV3_DELAY                         = 366
PARAM_THRESHOLD                          = 367
PARAM_THRESHOLD_RECORDING                = 368
PARAM_FLEX                               = 369
PARAM_ENV3_HOLD                          = 370
PARAM_ENV3_VELOCITY                      = 382
PARAM_SNAP_MODE                          = 383
PARAM_RULER_UNITS                        = 386
PARAM_SAMPLE_S_E_QUANTIZE                = 394
PARAM_LOOP_S_E_QUANTIZE                  = 395
PARAM_LOOP_POSITION_QUANTIZE             = 396
PARAM_LOOP_S_E_MODULATION                = 397
PARAM_PLAY_TO_END_ON_RELEASE             = 398
PARAM_LOOP_POSITION_MODULATION           = 399
PARAM_SAMPLE_S_E_MODULATION              = 400
PARAM_SHOW_BELOW_EDITOR                  = 401
PARAM_ENV2_DECAY_CURVE                   = 403
PARAM_ENV2_RELEASE_CURVE                 = 404
PARAM_ENV1_AMP_DECAY_CURVE               = 406
PARAM_ENV1_AMP_RELEASE_CURVE             = 407
PARAM_ENV3_ATTACK_CURVE                  = 408
PARAM_ENV3_DECAY_CURVE                   = 409
PARAM_ENV3_RELEASE_CURVE                 = 410
PARAM_LFO4_KEY_TRIGGER                   = 494
PARAM_LFO4_POLY                          = 495
PARAM_LFO4_UNIPOLAR                      = 497
PARAM_LFO4_FADE_MODE                     = 499
PARAM_ENV1_AMP_TIME_MODE                 = 500
PARAM_ENV2_TIME_MODE                     = 501
PARAM_ENV3_TIME_MODE                     = 502
PARAM_ENV4_TYPE                          = 503
PARAM_ENV4_DELAY                         = 504
PARAM_ENV4_ATTACK                        = 505
PARAM_ENV4_ATT_VIA_VEL                   = 506
PARAM_ENV4_ATTACK_CURVE                  = 507
PARAM_ENV4_HOLD                          = 508
PARAM_ENV4_DECAY                         = 509
PARAM_ENV4_DECAY_CURVE                   = 510
PARAM_ENV4_SUSTAIN                       = 511
PARAM_ENV4_RELEASE                       = 512
PARAM_ENV4_RELEASE_CURVE                 = 513
PARAM_ENV4_VELOCITY                      = 514
PARAM_ENV4_TIME_MODE                     = 515
PARAM_ENV5_DELAY                         = 517
PARAM_ENV5_ATTACK_CURVE                  = 520
PARAM_ENV5_HOLD                          = 521
PARAM_ENV5_DECAY_CURVE                   = 523
PARAM_ENV5_RELEASE_CURVE                 = 526
PARAM_ENV5_VELOCITY                      = 527
PARAM_FLEX_FOLLOW_TEMPO                  = 529
PARAM_FLEX_SPEED                         = 530
PARAM_INPUT_CHANNEL_TYPE                 = 532
PARAM_INPUT_CHANNEL_INDEX                = 533
PARAM_INPUT_CHANNEL_STEREO               = 534
PARAM_FLEX_FORMANT_TRACK                 = 536
PARAM_FLEX_FORMANT_BEND                  = 537
PARAM_QUICK_SAMPLER_CTRL_538_UNNAMED     = 538
PARAM_LEGACY_FILTER_TYPE                 = 28
PARAM_LEGACY_MODROW_A_SOURCE             = 47
PARAM_LEGACY_MODROW_A_VIA                = 70
PARAM_LEGACY_MODROW_A_AMOUNT             = 71
PARAM_LEGACY_MODROW_B_SOURCE             = 48
PARAM_LEGACY_MODROW_B_VIA                = 53
PARAM_LEGACY_MODROW_B_AMOUNT             = 52

# Ensure parameter_order is a SUPERSET of the engine's serializable id universe so
# the normalized writer can never silently drop a param. (None of these appear in
# the factory corpus or the modern test patch, but Logic can serialize them.)
parameter_order += [pid for pid in [67, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 338, 339, 345, 346, 348, 360, 361, 364, 365, 366, 367, 368, 369, 370, 382, 383, 386, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 403, 404, 406, 407, 408, 409, 410, 494, 495, 497, 499, 504, 507, 508, 510, 513, 514, 517, 520, 521, 523, 526, 527, 529, 530, 532, 533, 534, 536, 537, 538]
                    if pid not in parameter_order]

params_dict = dict(vars())
for k in list(params_dict.keys()):
    if not k.startswith('PARAM'): del (params_dict[k])

id_to_param = dict((v,k) for k,v in params_dict.items())


# ── Official Sampler parameter metadata (111 params: name/short/group/max/default),
#    from Logic Sampler's parameter table. See sampler_param_table.py.
#    Look up Logic's own name/range/default for any param id. ──
try:
    from sampler_param_table import SAMPLER_PARAMS
except Exception:
    SAMPLER_PARAMS = {}

# (Engine name-table completion now lives in sampler_param_table.py — the single
#  source of truth for SAMPLER_PARAMS; imported above.)


def sampler_param_name(param_id):
    """Official Sampler long name for an EXS param id, or None if legacy/unknown."""
    d = SAMPLER_PARAMS.get(param_id)
    return d[0] if d else None


if __name__ == '__main__':
    # exs_params_dict = exsparams.__dict__
    # for k in list(exs_params_dict.keys()):
    #     if not k.startswith('PARAM'): del (exs_params_dict[k])
    #
    # print(exs_params_dict)
    print (id_to_param)