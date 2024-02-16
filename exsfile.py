# started 2/12/2024

import exsclasses
import struct
import os
import exsparams

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
        elif chunk_signature == b'\x01\x01\x00\x01' or chunk_signature == b'\x01\x01\x00\x41': # zone
            zone_ctr += 1
            zone = exsclasses.parse_zone(chunk_data,id=zone_ctr)
            instrument.zones.append(zone)
        elif chunk_signature == b'\x01\x01\x00\x02': # group
            group_ctr += 1
            group = exsclasses.parse_group(chunk_data,id=group_ctr)
            instrument.groups.append(group)
        elif chunk_signature == b'\x01\x01\x00\x03': # sample
            sample_ctr += 1
            sample = exsclasses.parse_sample(chunk_data, id=sample_ctr)
            instrument.samples.append(sample)
        elif chunk_signature == b'\x01\x01\x00\x04': # params
            instrument.param_data = chunk_data
            instrument.params = exsclasses.parse_params(chunk_data)
        else:
            print ("UNKNOWN CHUNK SIGNATURE!",chunk_signature)

        offset += chunk_length

    return instrument

def write_exsfile(instrument,outfile,original_zone_data=False,original_group_data=False,original_sample_data=False,original_param_data=False):
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
                    exsout.write(struct.pack('<I', len(g.data) - 76))
                    exsout.write(g.data)

        if len(instrument.samples) > 0:
            for s in instrument.samples:
                exsout.write(b'\x01\x01\x00\x03') # sample header 0x01010003
                if original_sample_data:
                    exsout.write(struct.pack('<I', len(s.data) - 76))
                    exsout.write(s.data)

        exsout.write(b'\x01\x01\x00\x04')  # param header 0x01010004
        if original_param_data:
            exsout.write(struct.pack('<I', len(instrument.param_data) - 76))
            exsout.write(instrument.param_data)



if __name__ == '__main__':
    inst = read_exsfile("/Users/jonkubis/Music/Audio Music Apps/Sampler Instruments/00 Organized/Keys/JK SRX11Piano Final.exs")
    write_exsfile(
        inst,
        "/Users/jonkubis/Desktop/test_out.exs",
        original_zone_data=False,
        original_group_data=True,
        original_sample_data=True,
        original_param_data=True
    )

    # import os
    # from time import sleep
    # pathname = '/Users/jonkubis/Desktop/test.exs'
    #
    # last_m_time = os.path.getmtime(pathname)
    # prev_instrument = read_exsfile(pathname)
    #
    # id_to_param = exsparams.id_to_param
    #
    # for k, v in prev_instrument.params.items():
    #     keyname = ""
    #     if k in id_to_param: keyname = id_to_param[k] + " "
    #     print(f"{keyname}{hex(k)} ({k}) = {v}")
    #
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