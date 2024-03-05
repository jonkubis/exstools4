# █████╗ ██╗  ██╗ █████╗ ██╗███████╗ █████╗ ██╗  ██╗██╗  ██╗   ██████╗ ██╗   ██╗
#██╔══██╗██║ ██╔╝██╔══██╗██║██╔════╝██╔══██╗╚██╗██╔╝╚██╗██╔╝   ██╔══██╗╚██╗ ██╔╝
#███████║█████╔╝ ███████║██║███████╗╚██████║ ╚███╔╝  ╚███╔╝    ██████╔╝ ╚████╔╝
#██╔══██║██╔═██╗ ██╔══██║██║╚════██║ ╚═══██║ ██╔██╗  ██╔██╗    ██╔═══╝   ╚██╔╝
#██║  ██║██║  ██╗██║  ██║██║███████║ █████╔╝██╔╝ ██╗██╔╝ ██╗██╗██║        ██║
#╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝ ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝        ╚═╝

from dataclasses import dataclass, fields, field
import struct
import soundfile as sf
import numpy as np
import os


# S900/S950 disk format

# Track 1, side 1 starts with 64 entries of 24 bytes as follows:
# Length    Format      Description -----------------------------------------------------------
# 10        ASCII       Filename
# 6                     0
# 1         ASCII       File type: 'S'=sample, 'P'=program, etc.
# 3         unsigned    File length in bytes
# 2         unsigned    Starting block on disk
# 2                     S900 ID = {0,0}
import exsparams
from exsclasses import EXSInstrument, EXSZone
from exsfile import write_exsfile
from samplesearch import get_sample_info


def parse_s9xx_fat_entry(data,id=None):
    struct_format = "<10s6x1sHBHH"

    struct_size   = struct.calcsize(struct_format)

    values = list(struct.unpack(struct_format,data[:struct_size]))

    values[2] = values[2] + (values[3] << 16)

    #values[1] = values[1].split(b'\x00',maxsplit=1)[0].decode()
    del values[3]


    if values == [b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', b'\x00', 0, 0, 0]: return None
    #print(values)

    entry = s9xx_fat_entry()
    #entry.data = data

    entry.id                = id
    entry.name              = values[0].decode().strip()
    entry.entry_type        = values[1].decode()
    entry.size              = values[2]
    entry.starting_block    = values[3]
    entry.s9xx_id           = values[4]

    return entry

@dataclass
class s9xx_fat_entry():
    data:           str = None
    id:             int = None
    name:           str = None
    entry_type:     str = None
    size:           int = None
    starting_block: int = None
    block_table:    list = field(default_factory=lambda: [])
    s9xx_id:        int = None
    block_data:     str = b"" #list = field(default_factory=lambda: [])


def parse_s9xx_block_table(data):
    data_as_ints = struct.unpack('<800H',data)
    block_table = {}

    block_id = 0
    block_start = 0
    #inner_pos = 0

    current_block = []
    for pos, i in enumerate(data_as_ints):
        if i == 0: # empty block
            block_table[block_start] = None
            current_block = []
            block_id += 1
            block_start = pos + 1
            #continue
        elif i == 32768: # end of this block
            block_table[block_start] = current_block
            current_block = []
            block_id += 1
            block_start = pos + 1

            #continue
        else:
            current_block.append(i)
            #continue

    return block_table


@dataclass
class s9xx_sample():
    name:           str = None
    length:         int = 0 # in samples
    rate:           int = 0 # hz
    tuning:         int = 0 # in 16ths of a semitone, C3 = 960
    midi_note:      int = 0
    loudness_offset: int = 0
    loop_mode:      str = ''
    end:            int = 0
    start:          int = 0
    loop_start:     int = 0
    dma_desc_addr:  int = 0
    sample_type:    int = 0   # norm = 0x00, vel_xfade = 0xFF
    direction:      str = ''  # norm = 'N', reverse = 'R'
    absolute_addr:  int = 0

    sample_data:    list = field(default_factory=lambda: [])


def parse_s9xx_sample(data):
    struct_format = "<10s6xIHHh1sxIIIHB1s10xI2x"
    struct_size = struct.calcsize(struct_format)
    values = list(struct.unpack(struct_format, data[:struct_size]))
    #if values == [b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', b'\x00', 0, 0, 0]: return None
    #print(len(data))
    #print(values)

    sample = s9xx_sample()
    sample.name             = values[0].decode().strip()
    sample.length           = values[1]
    sample.rate             = values[2]
    sample.tuning           = values[3]
    sample.midi_note        = sample.tuning // 16
    sample.loudness_offset  = values[4]
    sample.loop_mode        = values[5].decode()
    sample.end              = values[6]
    sample.start            = values[7]
    sample.loop_start       = values[8]
    sample.dma_desc_addr    = values[9]   # /* address of DMA descriptor list (updated by sampler) */
    sample.sample_type      = values[10]  # 0x00 = Normal, 0xFF velocity crossfade
    sample.direction        = values[11]  # 'N' = normal, 'R' = reverse
    sample.absolute_addr    = values[12]  # updated by sampler

    sample.sample_data = decode_akai_s900_sample_data(data[60:], sample.length)

    # data = np.array(sample.sample_data, dtype=np.int16)
    # pathname = os.path.join('/Users/jonkubis/Desktop/OUT_TEST',sample.name+".wav")
    # sf.write(pathname, data, sample.rate)

    return sample


# Helper function to convert two bytes to a signed 16-bit integer
def bytes_to_int16(upper_byte, lower_byte):
    # Combine upper and lower bytes
    value = (upper_byte << 8) | lower_byte
    # Convert from unsigned to signed
    if value >= 32768:
        value -= 65536
    return value


def decode_akai_s900_sample_data(sbuf, length):
    samplecountpart = int(length/2)
    wav_samples = []

    # First part
    for i in range(samplecountpart):
        upper_byte = sbuf[i * 2 + 1]
        lower_byte = 0xf0 & sbuf[i * 2 + 0]
        wav_samples.append(bytes_to_int16(upper_byte, lower_byte))

    # Second part
    for i in range(samplecountpart):
        upper_byte = sbuf[samplecountpart * 2 + i]
        lower_byte = 0xf0 & (sbuf[i * 2 + 0] << 4)
        wav_samples.append(bytes_to_int16(upper_byte, lower_byte))

    return wav_samples


@dataclass
class s9xx_program():
    name:           str = None
    keygroup1_addr: int = None
    keygroup_xfade: bool = None
    keygroup_count: int = None
    keygroups:      list = field(default_factory=lambda: [])


def parse_s9xx_program(data):
    struct_format = "<10s8xHxBxB14x"
    struct_size = struct.calcsize(struct_format)
    values = list(struct.unpack(struct_format, data[:struct_size]))

    program = s9xx_program()
    program.name            = values[0].decode().strip()
    program.keygroup1_addr  = values[1]
    program.keygroup_xfade  = values[2] != 0
    program.keygroup_count  = values[3]

    offset = 0x26

    for i in range(program.keygroup_count):
        keygroup = parse_s9xx_keygroup(data[offset:offset+0x46])
        program.keygroups.append(keygroup)
        offset += 0x46

    return program


@dataclass
class s9xx_keygroup():
    key_hi:                     int = 127
    key_lo:                     int = 24
    vel_switch_thresh:          int = 128 # =0 if no soft sample, =128 if no loud sample
    attack:                     int = 0
    decay:                      int = 80
    sustain:                    int = 99
    release:                    int = 30
    velocity_to_filter:         int = 10
    keytrack_to_filter:         int = 50
    velocity_to_attack:         int = 0
    velocity_to_release:        int = 0
    velocity_sensitivity:       int = 30
    velocity_to_pitch_warp:     int = 0
    pitch_warp_initial_offset:  int = 0
    pitch_warp_recovery_time:   int = 99
    lfo_delay:                  int = 64
    lfo_rate:                   int = 42
    lfo_depth:                  int = 0
    flags:                      int = None
    # 0x01 = constant pitch enable, 0x02 = vel xfade enable, 0x04 = vibrato desync, 0x08 = one-shot trigger enable
    # 0x10 = vel release from note off or note on, 0x20 = vel xfade modification
    output_channel:             int = 0
    midi_channel_offset:        int = 0
    aftertouch_lfo_depth:       int = 0
    modwheel_lfo_depth:         int = 0
    adsr_to_filter_cutoff:      int = 0
    sample_1_name:              str = None
    filter_attack:              int = 20
    filter_decay:               int = 20
    filter_sustain:             int = 20
    filter_release:             int = 20
    vel_xfade_50_percent:       int = 64
    sample_1_header_addr:       int = 0
    sample_1_tuning_offset:     int = 0
    sample_1_filter:            int = 99
    sample_1_loudness_offset:   int = 0
    sample_2_name:              str = None
    sample_2_header_addr:       int = 0
    sample_2_tuning_offset:     int = 0
    sample_2_filter:            int = 99
    sample_2_loudness_offset:   int = 0
    next_keygroup_address:      int = 0


def parse_s9xx_keygroup(data):
    struct_format = "<BBBBBBBBBBBBBBBBBBBBBBBb10sBBBBBxHhBb10s6xHhBbH"
    struct_size = struct.calcsize(struct_format)
    values = list(struct.unpack(struct_format, data[:struct_size]))

    keygroup = s9xx_keygroup()

    keygroup.key_hi                 = values[0]
    keygroup.key_lo                 = values[1]
    keygroup.vel_switch_thresh      = values[2]
    keygroup.attack                 = values[3]
    keygroup.decay                  = values[4]
    keygroup.sustain                = values[5]
    keygroup.release                = values[6]
    keygroup.velocity_to_filter     = values[7]
    keygroup.keytrack_to_filter     = values[8]
    keygroup.velocity_to_attack     = values[9]
    keygroup.velocity_to_release    = values[10]
    keygroup.velocity_sensitivity   = values[11]
    keygroup.velocity_to_pitch_warp = values[12]
    keygroup.pitch_warp_initial_offset = values[13]
    keygroup.pitch_warp_recovery_time  = values[14]
    keygroup.lfo_delay              = values[15]
    keygroup.lfo_rate               = values[16]
    keygroup.lfo_depth              = values[17]
    keygroup.flags                  = values[18]
    keygroup.output_channel         = values[19]
    keygroup.midi_channel_offset    = values[20]
    keygroup.aftertouch_lfo_depth   = values[21]
    keygroup.modwheel_lfo_depth     = values[22]
    keygroup.adsr_to_filter_cutoff  = values[23]
    keygroup.sample_1_name          = values[24].decode().strip()
    keygroup.filter_attack          = values[25]
    keygroup.filter_decay           = values[26]
    keygroup.filter_sustain         = values[27]
    keygroup.filter_release         = values[28]
    keygroup.vel_xfade_50_percent   = values[29]
    keygroup.sample_1_header_addr   = values[30]
    keygroup.sample_1_tuning_offset = values[31]
    keygroup.sample_1_filter        = values[32]
    keygroup.sample_1_loudness_offset = values[33] # signed, +/- 50, units of 0.375db
    keygroup.sample_2_name          = values[34].decode().strip()
    keygroup.sample_2_header_addr   = values[35]
    keygroup.sample_2_tuning_offset = values[36]
    keygroup.sample_2_filter        = values[37]
    keygroup.sample_2_loudness_offset = values[38]
    keygroup.next_keygroup_address  = values[39]

    return keygroup


@dataclass
class s9xx_disk():
    programs:   list = field(default_factory=lambda: [])
    samples:    list = field(default_factory=lambda: [])


def read_akai_s9xx_imgfile(pathname):
    data = open(pathname,'rb').read()

    disk = s9xx_disk()

    fat_entries = []

    offset = 0
    for ctr in range(64):
        entry_data = data[offset:offset+24]
        entry = parse_s9xx_fat_entry(entry_data,id=ctr)
        if entry is not None: fat_entries.append(entry)
        offset += 24

    block_table = parse_s9xx_block_table(data[offset:offset+1600])
    offset += 1600

    #print (block_table)
    #The first 4 blocks are needed for the file entries and map.

    for e in fat_entries:
        e.block_table = [e.starting_block]
        e.block_table.extend(block_table[e.starting_block])

        for ctr, block_id in enumerate(e.block_table):
            e.block_data += data[block_id*1024:(block_id+1)*1024]

        #print (e.name, len(e.block_data))

        if e.entry_type == 'S':
            sample = parse_s9xx_sample(e.block_data)
            disk.samples.append(sample)

        elif e.entry_type == 'P':
            program = parse_s9xx_program(e.block_data)
            disk.programs.append(program)

    return disk


def akai_s9xx_imgfile_to_exs(pathname,output_path):
    disk = read_akai_s9xx_imgfile(pathname)

    samples = {}

    for sample in disk.samples:
        samples[sample.name] = sample
        data = np.array(sample.sample_data, dtype=np.int16)
        pathname = os.path.join(output_path, sample.name + ".wav")
        sf.write(pathname, data, sample.rate)
        samples[sample.name].sample_data = None

        print (sample,'\n')


    for p in disk.programs:
        inst = EXSInstrument()
        inst.name = p.name

        print('\n'+"-"*80,"\nPROGRAM:",p.name, '\n'+"-"*80+'\n')

        # check for unanimous ADSR
        a, d, s, r, v_sens = {}, {}, {}, {}, {}
        for k in p.keygroups:
            if k.attack  not in a.keys(): a[k.attack] = 0
            if k.decay   not in d.keys(): d[k.decay] = 0
            if k.sustain not in s.keys(): s[k.sustain] = 0
            if k.release not in r.keys(): r[k.release] = 0
            if k.velocity_sensitivity not in v_sens.keys(): v_sens[k.velocity_sensitivity] = 0
            a[k.attack]  += 1
            d[k.decay]   += 1
            s[k.sustain] += 1
            r[k.release] += 1
            v_sens[k.velocity_sensitivity] += 1

        a = dict(sorted(a.items(), key=lambda item: item[1], reverse=True))
        d = dict(sorted(d.items(), key=lambda item: item[1], reverse=True))
        s = dict(sorted(s.items(), key=lambda item: item[1], reverse=True))
        r = dict(sorted(r.items(), key=lambda item: item[1], reverse=True))
        v_sens = dict(sorted(v_sens.items(), key=lambda item: item[1], reverse=True))

        adsr_attack, adsr_decay, adsr_sustain, adsr_release = list(a.keys())[0], list(d.keys())[0], list(s.keys())[0], list(r.keys())[0]
        vel_sens = list(v_sens.keys())[0]

        sample_ctr = -1
        for ctr, k in enumerate(p.keygroups):
            print (k,'\n')
            two_layers = k.sample_2_header_addr != 0

            for s_ctr in range(0,2):
                sample_ctr += 1
                sample_name = k.sample_1_name if s_ctr == 0 else k.sample_2_name

                pathname = os.path.join(output_path, sample_name + ".wav")
                s = get_sample_info(pathname)
                inst.samples.append(s)
                z = EXSZone()
                z.name = s.name
                z.id, z.sampleindex = sample_ctr, sample_ctr
                z.rootnote = samples[sample_name].midi_note
                z.startnote = k.key_lo
                z.endnote = k.key_hi
                z.samplestart = samples[sample_name].start
                z.sampleend = samples[sample_name].end
                z.loopstart = samples[sample_name].end - samples[sample_name].loop_start
                z.loopend = z.sampleend
                z.loopenable = samples[sample_name].loop_mode == 'L'

                if s_ctr == 0:
                    z.volumeadjust = int(k.sample_1_loudness_offset * 0.375)
                    zonetune = k.sample_1_tuning_offset / 16  # tuning is in 16ths of a semitone
                    if two_layers:
                        z.maxvel = k.vel_switch_thresh - 1

                elif s_ctr == 1: # we automatically know it's two layers
                    z.volumeadjust = int(k.sample_2_loudness_offset * 0.375)
                    zonetune = k.sample_2_tuning_offset / 16  # tuning is in 16ths of a semitone
                    z.minvel = k.vel_switch_thresh

                zonetunesemi = int(round(zonetune))
                zonetunecents = int(round(100 * (zonetune + (-1 * zonetunesemi))))
                z.coarsetune = zonetunesemi
                z.finetune = zonetunecents
                z.loopcrossfade = 2

                inst.zones.append(z)

                if not two_layers: break


        inst.params = exsparams.default_params
        inst.params[exsparams.PARAM_ENV1_ATK_HI_VEL] = adsr_attack
        inst.params[exsparams.PARAM_ENV1_ATK_LO_VEL] = adsr_attack
        inst.params[exsparams.PARAM_ENV1_DECAY]      = adsr_decay
        inst.params[exsparams.PARAM_ENV1_SUSTAIN]    = int((127/99) * adsr_sustain)
        inst.params[exsparams.PARAM_ENV1_RELEASE]    = adsr_release
        inst.params[exsparams.PARAM_ENV1_VEL_SENS]   = 0 - int((96/99) * vel_sens)


        write_exsfile(
            inst,
            os.path.join(output_path, inst.name  + ".exs")
        )


if __name__ == '__main__':
    #disk = read_akai_s9xx_imgfile('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL503_Drums1.img')
    #for p in disk.programs:
    #    print (p.name)

    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL501 - GrandPiano1.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL501 - GrandPiano1.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL502 - ChopperBass.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL504_Voices_Flute_Vocal.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL505_Orchestra1.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL506_Strings1.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL507_Brass1.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL508_HarpGliss_CelloViolin_PanPipes.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL509_PizzStrings_Easterin_Kalimba.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL510_TheStick.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL511_Bell_Strings_StringBell.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL512_Guitar1.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL513_Effects1.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL514_Clarinet_Brook_HarpPluck_GlockHarp.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL515_GlassBell_Choir_VoiceStrings.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL516_Ooohs.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL536_PanFlute.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL542_Basses_Fretless.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL543_BrazilianGuitars.img','/Users/jonkubis/Desktop/OUT_TEST')
    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai S900 - SL5xx Library (v1, incomplete)/SL554_LatinPercussion_Conga.img','/Users/jonkubis/Desktop/OUT_TEST')

    # akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai SL5000 Library (S900) [IMG & HFE]/DD (S900 and S950)/IMG/SL5001 - Off Mic Piano.IMG','/Users/jonkubis/Desktop/OUT_TEST')
    akai_s9xx_imgfile_to_exs('/Users/jonkubis/Downloads/Akai SL5000 Library (S900) [IMG & HFE]/DD (S900 and S950)/IMG/SL5002 - Electric Piano.IMG','/Users/jonkubis/Desktop/OUT_TEST')
