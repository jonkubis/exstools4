# ███████╗ █████╗ ███╗   ███╗██████╗ ██╗     ███████╗███╗   ███╗███████╗██████╗  ██████╗ ███████╗   ██████╗ ██╗   ██╗
# ██╔════╝██╔══██╗████╗ ████║██╔══██╗██║     ██╔════╝████╗ ████║██╔════╝██╔══██╗██╔════╝ ██╔════╝   ██╔══██╗╚██╗ ██╔╝
# ███████╗███████║██╔████╔██║██████╔╝██║     █████╗  ██╔████╔██║█████╗  ██████╔╝██║  ███╗█████╗     ██████╔╝ ╚████╔╝
# ╚════██║██╔══██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝  ██║╚██╔╝██║██╔══╝  ██╔══██╗██║   ██║██╔══╝     ██╔═══╝   ╚██╔╝
# ███████║██║  ██║██║ ╚═╝ ██║██║     ███████╗███████╗██║ ╚═╝ ██║███████╗██║  ██║╚██████╔╝███████╗██╗██║        ██║
# ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝╚═╝        ╚═╝
import os
import math
import random
import datetime
import numpy as np
from pydub import AudioSegment
import soundfile

from exsclasses import EXSSample
from exsfile import read_exsfile, write_exsfile
from samplesearch import resolve_sample_locations


def samplemerge(instrument, output_path):
    # first, verify all samples are present and accounted for
    for s in instrument.samples:
        pathname = os.path.join(s.folder, s.filename)
        if not os.path.exists(pathname):
            print (pathname,"not found! Aborting!")
            raise FileNotFoundError

    # second, tally the sample rates of the files FROM THE INSTRUMENT!
    # once imported, EXS24 could care less about the sample rate stored in the actual sample file
    # if all the sample files are the same rate, killer. but if not--
    # find the most common sample rate that they all can coexist at and adjust the playback pitches accordingly
    # e.g. a 22050hz file will need its playback speed adjusted down an octave if concatenated with a 44100hz file
    prevailing_sample_rate, sample_rates, all_samples_are_same_rate = find_prevailing_sample_rate(inst)

    for s in instrument.samples:
        s.merge_pitch_adjust = sr_pitch_offset(s.rate, prevailing_sample_rate)
        #print (s.name,s.rate,prevailing_sample_rate,s.merge_pitch_adjust)

    # next write out our monoliths.
    # let's generate some names
    monolith_filenames = get_monolith_filenames(instrument.name)
    monolith_lengths = {}
    monoliths_as_samples = []

    create_new_monolith = True  # start first sample by creating our first (and probably only) big sample file
    monolith_index = -1

    channel_count = 0
    for s in instrument.samples:
        if s.channels > channel_count: channel_count = s.channels

    one_sample_silence = np.zeros((1, channel_count), dtype=np.int16)

    for sample_ctr, s in enumerate(instrument.samples):
        if create_new_monolith:
            create_new_monolith = False
            monolith_index += 1
            print("Creating monolith: " + monolith_filenames[monolith_index])

            caf_pathname = os.path.join(output_path, monolith_filenames[monolith_index]) + ".caf"
            wav_pathname = os.path.splitext(caf_pathname)[0] + ".wav"

            outfile = soundfile.SoundFile(wav_pathname, 'w', prevailing_sample_rate, channel_count, 'PCM_16')

        source_pathname = os.path.join(s.folder, s.filename)
        data, samplerate = soundfile.read(source_pathname)  # always_2d doesn't work, WTF pyAudioFile peeps?

        if len(data.shape) == 1 and channel_count == 2: data = np.stack((data, data), axis=-1) # if we read a mono file, make it stereo

        s.merge_monolith_index = monolith_index
        s.merge_monolith_sample_start = outfile.tell() # note where this sample starts in the monolith
        outfile.write(data)
        s.merge_monolith_sample_end = outfile.tell() - 1 # note where this sample end in the monolith
        outfile.write(one_sample_silence) # stuff a sample of silence in between

        if (outfile.tell() > 200_000_000):  # 200 million samples -- getting big! best to start a new monolith
            monolith_lengths[monolith_filenames[monolith_index]] = outfile.tell()
            outfile.close()
            print(os.path.basename(wav_pathname) + "->" + os.path.basename(caf_pathname))
            AudioSegment.from_file(wav_pathname).export(caf_pathname, format='caf', codec='alac')
            os.remove(wav_pathname)

            caf_sample = EXSSample()
            caf_sample.name = os.path.basename(caf_pathname)
            caf_sample.filename = caf_pathname
            caf_sample.folder = output_path
            caf_sample.rate = prevailing_sample_rate
            caf_sample.channels = channel_count
            caf_sample.iscompressed = True
            caf_sample.fourdigitcode = b'ffac'
            caf_sample.length = monolith_lengths[monolith_filenames[monolith_index]]
            caf_sample.wavedatastart = 0  # 0 for compressed
            caf_sample.bitdepth = 16
            caf_sample.filesize = os.path.getsize(caf_pathname)
            monoliths_as_samples.append(caf_sample)

            outfile = None
            create_new_monolith = True

    monolith_lengths[monolith_filenames[monolith_index]] = outfile.tell()
    outfile.close()
    print(os.path.basename(wav_pathname) + "->" + os.path.basename(caf_pathname))
    AudioSegment.from_file(wav_pathname).export(caf_pathname, format='caf', codec='alac')
    os.remove(wav_pathname)

    caf_sample = EXSSample()
    caf_sample.name = os.path.basename(caf_pathname)
    caf_sample.filename = caf_pathname
    caf_sample.folder = output_path
    caf_sample.rate = prevailing_sample_rate
    caf_sample.channels = channel_count
    caf_sample.iscompressed = True
    caf_sample.fourdigitcode = b'ffac'
    caf_sample.length = monolith_lengths[monolith_filenames[monolith_index]]
    caf_sample.wavedatastart = 0  # 0 for compressed
    caf_sample.bitdepth = 16
    caf_sample.filesize = os.path.getsize(caf_pathname)
    monoliths_as_samples.append(caf_sample)

    # all the audio is written to the consolidated CAF(s)
    # now we need to repoint the zones to the new samples
    original_samples   = instrument.samples
    instrument.samples = monoliths_as_samples

    for z in instrument.zones:
        zone_pitch_adjust = original_samples[z.sampleindex].merge_pitch_adjust
        z.samplestart += original_samples[z.sampleindex].merge_monolith_sample_start
        z.sampleend   += original_samples[z.sampleindex].merge_monolith_sample_start
        z.loopstart   += original_samples[z.sampleindex].merge_monolith_sample_start
        z.loopend     += original_samples[z.sampleindex].merge_monolith_sample_start
        z.sampleindex = original_samples[z.sampleindex].merge_monolith_index

        #print ("orig coarse",z.coarsetune,"fine",z.finetune)

        zonetune = z.coarsetune + (z.finetune / 100)
        zonetune -= zone_pitch_adjust
        zonetunesemi = int(round(zonetune))
        zonetunecents = int(round(100 * (zonetune + (-1 * zonetunesemi))))
        z.coarsetune = zonetunesemi
        z.finetune = zonetunecents
        #print(" new coarse", z.coarsetune, "fine", z.finetune)

    exs_out_name = instrument.name
    if not exs_out_name.endswith(".exs"): exs_out_name += ".exs"
    write_exsfile(instrument,os.path.join(output_path,exs_out_name),original_group_data=True,original_param_data=True)


def get_monolith_filenames(instrument_name):
    if instrument_name.lower().endswith('.exs'): instrument_name = instrument_name[:-4]

    samplenameprefix = ''.join(e for e in instrument_name if e.isalnum())
    if len(samplenameprefix) > 12: samplenameprefix = samplenameprefix[0:11] + samplenameprefix[-1:]

    monolith_filenames = []
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    timestamp = str(datetime.datetime.now())[0:19].replace('-', '').replace(' ', '-').replace(':', '')
    while len(monolith_filenames) < 16:  # create more names than we need
        thisfilename = samplenameprefix + "-" + timestamp + ''.join(random.choice(letters) for i in range(4))
        if thisfilename not in monolith_filenames: monolith_filenames.append(thisfilename)

    return monolith_filenames


def find_prevailing_sample_rate(instrument):
    sample_rates = {}
    for s in instrument.samples:
        if s.rate in sample_rates:
            sample_rates[s.rate] += 1
        else:
            sample_rates[s.rate] = 1

    all_samples_are_same_rate = False
    # we've tallied the sample rates. let's see if the prevailing sample rate is unanimous...
    if len(sample_rates) == 1:
        all_samples_are_same_rate = True
        prevailing_sample_rate = list(sample_rates.keys())[0]
    else:
        sorted_sample_rates = sorted(sample_rates.items(), key=lambda x: x[1], reverse=True)
        sorted_sample_rates = dict(sorted_sample_rates)

        # let's see if 44100 or 48000 is any of the rates
        if 44100 in sorted_sample_rates:
            prevailing_sample_rate = 44100
        elif 48000 in sorted_sample_rates:
            prevailing_sample_rate = 48000
        else:
            prevailing_sample_rate = 44100

    return prevailing_sample_rate, sample_rates, all_samples_are_same_rate


def sr_pitch_offset(recording_sr,target_sr=44100):
    return 12 * math.log2(target_sr / recording_sr)


if __name__ == '__main__':
    #inst = read_exsfile("/Users/jonkubis/Music/Audio Music Apps/Sampler Instruments/00 Organized/Bass/JK Finger Bass.exs")
    inst = read_exsfile("/Users/jonkubis/Downloads/EXSOUT2/NIK4FL/Band/6 - Bass/NIK4FL Upright Bass.exs")
    resolve_sample_locations(inst)
    samplemerge(inst,'/Users/jonkubis/Desktop/EXSOUT')