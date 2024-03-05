# ███████╗██╗  ██╗███████╗██████╗  █████╗ ██████╗  █████╗ ███╗   ███╗███████╗   ██████╗ ██╗   ██╗
# ██╔════╝╚██╗██╔╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗████╗ ████║██╔════╝   ██╔══██╗╚██╗ ██╔╝
# █████╗   ╚███╔╝ ███████╗██████╔╝███████║██████╔╝███████║██╔████╔██║███████╗   ██████╔╝ ╚████╔╝
# ██╔══╝   ██╔██╗ ╚════██║██╔═══╝ ██╔══██║██╔══██╗██╔══██║██║╚██╔╝██║╚════██║   ██╔═══╝   ╚██╔╝
# ███████╗██╔╝ ██╗███████║██║     ██║  ██║██║  ██║██║  ██║██║ ╚═╝ ██║███████║██╗██║        ██║
# ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚═╝╚═╝        ╚═╝



parameter_order = [65, 66, 7, 8, 3, 4, 10, 5, 51, 50, 45, 14, 15, 47, 20, 70, 71, 72, 73, 44, 28, 48, 53, 52, 243, 170, 30, 29, 75, 46, 90, 89, 60, 61, 62, 64, 63, 76, 77, 78, 79, 80, 92, 91, 82, 83, 84, 81, 85, 95, 164, 163, 98, 97, 165, 171, 167, 166, 172, 173, 174, 175, 176, 177, 233, 178, 244, 179, 180, 181, 182, 183, 234, 184, 245, 185, 186, 187, 188, 189, 235, 190, 246, 191, 192, 193, 194, 195, 236, 196, 247, 197, 198, 199, 200, 201, 237, 202, 248, 203, 204, 205, 206, 207, 238, 208, 249, 209, 210, 211, 212, 213, 239, 214, 250, 215, 216, 217, 218, 219, 240, 371, 378, 372, 375, 376, 377, 389, 390, 220, 251, 221, 222, 223, 224, 225, 241, 226, 252, 227, 228, 229, 230, 231, 242, 232, 352, 363, 405, 56, 500, 362, 402, 88, 381, 501, 353, 354, 355, 357, 358, 359, 502, 503, 505, 506, 509, 511, 512, 515, 516, 518, 519, 522, 524, 525, 528, 332, 333, 335, 334, 336, 391, 337, 341, 340, 342, 343, 344, 347, 349, 492, 491, 493, 496, 498, 535, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 278, 282, 387, 388, 253, 254]
default_params = {7: 0, 8: 0, 3: 2, 4: -1, 5: 16, 20: 0, 73: 0, 243: 0, 30: 1000, 29: 0, 75: 100, 46: 0, 90: -60, 89: 0, 60: 0, 61: 98, 62: 0, 64: 0, 63: 98, 76: 0, 77: 0, 78: 0, 79: 0, 80: 0, 92: 0, 82: 0, 83: 0, 84: 0, 81: 127, 85: 0, 97: 0, 165: 1, 167: 98, 166: -1, 172: 64, 173: 8, 174: -14, 175: -1, 176: 0, 177: 0, 179: 6, 180: -12, 181: 1, 182: 0, 183: 343, 254: 1000, 378: 0, 375: 1000, 376: 0, 377: 100, 389: 3, 390: 3, 363: 2, 500: 0, 362: 2, 501: 0, 353: 2, 354: 0, 355: 0, 357: 0, 358: 0, 359: 0, 502: 0, 503: 2, 505: 0, 506: 0, 509: 0, 511: 0, 512: 0, 515: 0, 516: 2, 518: 0, 519: 0, 522: 0, 524: 0, 525: 0, 528: 0, 335: 0, 334: 0, 336: 0, 337: 0, 341: 0, 340: 0, 342: 0, 343: 0, 344: 0, 347: 0, 349: 0, 492: 0, 491: 98, 493: 0, 496: 0, 498: 0, 535: 1, 282: 48, 387: -10, 388: 1}
mandatory_parameter_ids = [7, 8, 3, 4, 5, 20, 73, 243, 30, 29, 75, 46, 90, 89, 60, 61, 62, 64, 63, 76, 77, 78, 79, 80, 92, 82, 83, 84, 81, 85, 97, 165, 167, 166, 172, 173, 174, 175, 176, 177, 179, 180, 181, 182, 183, 254, 378, 375, 376, 377, 389, 390, 363, 500, 362, 501, 353, 354, 355, 357, 358, 359, 502, 503, 505, 506, 509, 511, 512, 515, 516, 518, 519, 522, 524, 525, 528, 335, 334, 336, 337, 341, 340, 342, 343, 344, 347, 349, 492, 491, 493, 496, 498, 535, 282, 387, 388]


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

PARAM_ENV2_TYPE                 = 0x16a # 0=AD, 1=AR, 2=ADSR, 3=AHDSR, 4=DADSR, 5=DAHDSR
PARAM_ENV2_VEL_SENS             = 0x17d

PARAM_ENV2_DELAY_START          = 0x16c
PARAM_ENV2_ATK_CURVE            = 0x192
PARAM_ENV2_ATK_HI_VEL           = 0x4c
PARAM_ENV2_ATK_LO_VEL           = 0x4d
PARAM_ENV2_HOLD                 = 0x38
PARAM_ENV2_DECAY                = 0x4e
PARAM_ENV2_SUSTAIN              = 0x4f
PARAM_ENV2_RELEASE              = 0x50
PARAM_ENV2_TIME_CURVE           = 0x5b

PARAM_ENV1_TYPE                 = 0x16b # 0=AD, 1=AR, 2=ADSR, 3=AHDSR, 4=DADSR, 5=DAHDSR
PARAM_ENV1_VEL_SENS             = 0x5a
PARAM_ENV1_VOLUME_HIGH          = 0x59 # can't find this anymore in the new SAMPLER
PARAM_ENV1_DELAY_START          = 0x16d
PARAM_ENV1_ATK_CURVE            = 0x195
PARAM_ENV1_ATK_HI_VEL           = 0x52
PARAM_ENV1_ATK_LO_VEL           = 0x53
PARAM_ENV1_HOLD                 = 0x58
PARAM_ENV1_DECAY                = 0x54
PARAM_ENV1_SUSTAIN              = 0x51
PARAM_ENV1_RELEASE              = 0x55
PARAM_ENV1_TIME_CURVE           = None #??

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

MS_LUT = [0,0.003,0.009,0.024,0.049,0.092,0.157,0.252,0.384,0.562,0.797,1.097,1.476,1.946,2.519,3.21,4.035,5.009,6.15,7.475,9.004,10.757,12.753,15.015,17.566,20.428,23.627,27.187,31.136,35.5,40.307,45.586,51.368,57.684,64.564,72.043,80.152,88.929,98.406,108.62,119.61,131.41,144.07,157.62,172.11,187.57,204.05,221.59,240.25,260.05,281.05,303.31,326.85,351.75,378.03,405.77,435,465.79,498.18,532.23,568,605.54,644.91,686.18,729.39,774.61,821.9,871.32,922.94,976.82,1033,1091.6,1152.6,1216.2,1282.4,1351.2,1422.8,1497.2,1574.5,1654.7,1737.9,1824.3,1913.8,2006.5,2102.7,2202.2,2305.2,2411.8,2522,2636,2753.8,2875.5,3001.2,3130.9,3264.9,3403,3545.5,3692.5,3844,4000,4160.8,4326.4,4496.9,4672.4,4852.9,5038.7,5229.7,5426.1,5628,5835.4,6048.6,6267.5,6492.3,6723.2,6960.1,7203.2,7452.6,7708.5,7970.9,8239.9,8515.7,8798.4,9088,9384.8,9688.7,10000]

def ms_to_index(list, K):
    return min(list, key=lambda x: abs(x-K))

params_dict = dict(vars())
for k in list(params_dict.keys()):
    if not k.startswith('PARAM'): del (params_dict[k])

id_to_param = dict((v,k) for k,v in params_dict.items())

if __name__ == '__main__':
    # exs_params_dict = exsparams.__dict__
    # for k in list(exs_params_dict.keys()):
    #     if not k.startswith('PARAM'): del (exs_params_dict[k])
    #
    # print(exs_params_dict)
    print (id_to_param)