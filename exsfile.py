# ███████╗██╗  ██╗███████╗███████╗██╗██╗     ███████╗   ██████╗ ██╗   ██╗
# ██╔════╝╚██╗██╔╝██╔════╝██╔════╝██║██║     ██╔════╝   ██╔══██╗╚██╗ ██╔╝
# █████╗   ╚███╔╝ ███████╗█████╗  ██║██║     █████╗     ██████╔╝ ╚████╔╝
# ██╔══╝   ██╔██╗ ╚════██║██╔══╝  ██║██║     ██╔══╝     ██╔═══╝   ╚██╔╝
# ███████╗██╔╝ ██╗███████║██║     ██║███████╗███████╗██╗██║        ██║
# ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚══════╝╚══════╝╚═╝╚═╝        ╚═╝


import exsclasses
import struct
import os
import exsparams
import samplesearch

def read_exsfile(pathname):
    data = open(pathname,'rb').read()

    if data[0:4] == b'\x01\x01\x00\x00' or data[0:4] == b'\x01\x01\x00\x40':
        pass
    else:
        print ("FILE IS NOT AN EXS FILE")
        return

    if data[16:20] != b'TBOS':
        print ("FILE IS NOT AN EXS FILE")
        return

    instrument = None
    chunks = []
    offset = 0
    zone_ctr, group_ctr, sample_ctr = -1, -1, -1
    while offset < len(data):
        chunk_signature = data[offset : offset+4]
        chunk_length    = struct.unpack_from('<I', data[offset + 4: offset + 8])[0] + 84
        chunk_data      = data[offset + 8: offset + chunk_length]

        if chunk_signature == b'\x01\x01\x00\x00' or chunk_signature == b'\x01\x01\x00\x40': # EXS header
            instrument = exsclasses.parse_instrument(chunk_data)
            if instrument.name == "(null)": instrument.name = os.path.split(pathname)[1]
            instrument.pathname = pathname
        elif chunk_signature == b'\x01\x01\x00\x01' or chunk_signature == b'\x01\x01\x00\x41': # zone
            zone_ctr += 1
            zone = exsclasses.parse_zone(chunk_data,id=zone_ctr)
            instrument.zones.append(zone)
        elif chunk_signature == b'\x01\x01\x00\x02' or chunk_signature == b'\x01\x01\x00\x42': # group
            group_ctr += 1
            group = exsclasses.parse_group(chunk_data,id=group_ctr)
            instrument.groups.append(group)
        elif chunk_signature == b'\x01\x01\x00\x03' or chunk_signature == b'\x01\x01\x00\x43': # sample
            sample_ctr += 1
            sample = exsclasses.parse_sample(chunk_data, id=sample_ctr)
            sample.exsfile_pos = offset
            instrument.samples.append(sample)
        elif chunk_signature == b'\x01\x01\x00\x04' or chunk_signature == b'\x01\x01\x00\x44': # params
            instrument.param_data = chunk_data
            instrument.params = exsclasses.parse_params(chunk_data)
        else:
            print ("UNKNOWN CHUNK SIGNATURE!",chunk_signature)

        offset += chunk_length

    return instrument

def write_exsfile(instrument,outfile,original_zone_data=False,original_group_data=False,original_sample_data=False,original_param_data=False,relink_only=True):
    with open(outfile,'wb') as exsout:
        exsout.write(b'\x01\x01\x00\x00\x58\x00\x00\x00\x00\x00\x00\x00')  # instrument chunk header
        exsout.write(b'\x40\x00\x00\x00TBOS')  # subheader
        exsout.write(instrument.name.encode().ljust(152,b'\x00'))
        #exsout.write(b'\x00' * 152)

        if len(instrument.zones) > 0:
            for z in instrument.zones:
                exsout.write(b'\x01\x01\x00\x01') # zone header 0x01010001
                if original_zone_data:
                    data = z.data
                else:
                    data = exsclasses.export_zone(z)

                exsout.write(struct.pack('<I', len(data) - 76))
                exsout.write(data)

        if len(instrument.groups) > 0:
            for g in instrument.groups:
                exsout.write(b'\x01\x01\x00\x02') # group header 0x01010002
                if original_group_data:
                    data = g.data
                else:
                    data = exsclasses.export_group(g)

                exsout.write(struct.pack('<I', len(data) - 76))
                exsout.write(data)

        if len(instrument.samples) > 0:
            for s in instrument.samples:
                exsout.write(b'\x01\x01\x00\x03') # sample header 0x01010003
                if original_zone_data:
                    data = s.data
                else:
                    data = exsclasses.export_sample(s)

                exsout.write(struct.pack('<I', len(data) - 76))
                exsout.write(data)

        exsout.write(b'\x01\x01\x00\x04')  # param header 0x01010004
        if original_param_data:
            data = instrument.param_data
        else:
            data = exsclasses.export_params(instrument.params)

        exsout.write(struct.pack('<I', len(data) - 76))
        exsout.write(data)

    print (f'Wrote: {outfile}')

def relink_samples(pathname):
    inst = read_exsfile(pathname)
    found_all_samples = samplesearch.resolve_sample_locations(inst)
    if found_all_samples:
        with open(pathname, 'r+b') as infile:
            for s in inst.samples:
                infile.seek(s.exsfile_pos+164,os.SEEK_SET)
                to_write = struct.pack('256s',s.folder.encode())
                infile.write(to_write)
        print (f"Relinked {len(inst.samples)} samples!")
    else:
        print ("Could not find all samples. Aborting!")


if __name__ == '__main__':
    import glob

    # for pathname in glob.glob("/Users/jonkubis/Desktop/EXS STUFF/Mo'Phatt/*.exs"):
    #     print(pathname)
    #     relink_samples(pathname)
    # quit()

    #inst = read_exsfile("/Users/jonkubis/Desktop/EXS STUFF/JK Finger Bass.exs") # already sample merged with CAF
    inst = read_exsfile("/Users/jonkubis/Desktop/EXSOUT/EW/Bass Tripper Master.exs") # not sample merged
    #inst = read_exsfile("/Library/Application Support/Logic/Sampler Instruments/03 Drums & Percussion/04 Drum Kit Designer/Drum Kit Designer/Stereo/Sunset Kit.exs")
    #samplesearch.resolve_sample_locations(inst)


    #inst = read_exsfile('/Users/jonkubis/Desktop/sampler_default.exs')
    # write_exsfile(
    #     inst,
    #     "/Users/jonkubis/Desktop/test_out.exs",
    #     original_zone_data=False,
    #     original_group_data=False,
    #     original_sample_data=False,
    #     original_param_data=False
    # )
    quit()

    # import os
    # from time import sleep
    # pathname = '/Users/jonkubis/Desktop/test.exs'
    #
    # last_m_time = os.path.getmtime(pathname)
    # prev_instrument = read_exsfile(pathname)

    id_to_param = exsparams.id_to_param

    parameter_order = []

    for k, v in inst.params.items():
        keyname = ""
        if k in id_to_param: keyname = id_to_param[k] + " "
        #print(f"{keyname}{hex(k)} ({k}) = {v}")
        parameter_order.append(k)

    # print (inst.params)
    # print (parameter_order)

    # print ('\n')
    #
    # while 1==1:
    #     if os.path.getmtime(pathname) == last_m_time:
    #         sleep(1.0)
    #         continue
    #
    #     print ("FILE MODIFIED!")
    #     instrument = read_exsfile(pathname)
    #
    #     for k, v in instrument.params.items():
    #         keyname = ""
    #         if k in id_to_param: keyname = id_to_param[k] + " "
    #
    #         if k in prev_instrument.params:
    #             if v != prev_instrument.params[k]:
    #                 print(f"{keyname}{hex(k)} ({k}) = {prev_instrument.params[k]} => {v}")
    #         else:
    #             print (f"{keyname}NEW: {hex(k)} ({k}) = {v}")
    #
    #
    #     last_m_time = os.path.getmtime(pathname)
    #     prev_instrument = instrument


     #"/Users/jonkubis/Downloads/EXSOUT2/NIK4FL Grand Piano.exs") #'/Users/jonkubis/Desktop/test.exs'