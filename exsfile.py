# ███████╗██╗  ██╗███████╗███████╗██╗██╗     ███████╗   ██████╗ ██╗   ██╗
# ██╔════╝╚██╗██╔╝██╔════╝██╔════╝██║██║     ██╔════╝   ██╔══██╗╚██╗ ██╔╝
# █████╗   ╚███╔╝ ███████╗█████╗  ██║██║     █████╗     ██████╔╝ ╚████╔╝
# ██╔══╝   ██╔██╗ ╚════██║██╔══╝  ██║██║     ██╔══╝     ██╔═══╝   ╚██╔╝
# ███████╗██╔╝ ██╗███████║██║     ██║███████╗███████╗██╗██║        ██║
# ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚══════╝╚══════╝╚═╝╚═╝        ╚═╝


import exsclasses
import exsblock
import struct
import os
import exsparams
import samplesearch

def read_exsfile(pathname):
    data = open(pathname,'rb').read()

    # Accept either byte order: the first header byte is 0x00 (big-endian) or
    # 0x01 (little-endian), and the magic at offset 16 must be one we recognize.
    valid_magics = exsblock.LITTLE_ENDIAN_MAGICS + exsblock.BIG_ENDIAN_MAGICS
    if len(data) < exsblock.HEADER_SIZE or data[0] not in (0x00, 0x01) \
            or bytes(data[16:20]) not in valid_magics:
        print ("FILE IS NOT AN EXS FILE")
        return

    instrument = None
    zone_ctr, group_ctr, sample_ctr = -1, -1, -1
    blocks = exsblock.iter_blocks(data)
    while True:
        try:
            block = next(blocks)
        except StopIteration:
            break
        except ValueError as e:
            # We hit a header we cannot make sense of. Either trailing
            # padding/garbage after an otherwise complete instrument (keep what
            # we have), or an unsupported container layout -- e.g. some legacy
            # embedded-sample EXS variants that even ConvertWithMoss cannot read,
            # where blocks are non-contiguous. Never fabricate data: bail.
            if instrument is None or not instrument.zones:
                print (f"UNSUPPORTED EXS LAYOUT: {os.path.split(pathname)[1]} ({e})")
                return None
            print (f"NOTE: stopped reading {os.path.split(pathname)[1]} early ({e})")
            break

        endian = block.endian

        try:
            if block.type == exsblock.TYPE_INSTRUMENT:
                instrument = exsclasses.parse_instrument(block.legacy_data)
                if instrument.name == "(null)": instrument.name = os.path.split(pathname)[1]
                instrument.pathname = pathname
            elif instrument is None:
                # The file did not start with an instrument block -- not
                # something we know how to read.
                print (f"UNSUPPORTED EXS LAYOUT: {os.path.split(pathname)[1]} (no instrument header)")
                return None
            elif block.type == exsblock.TYPE_ZONE:
                zone_ctr += 1
                zone = exsclasses.parse_zone(block.legacy_data, id=zone_ctr, endian=endian)
                instrument.zones.append(zone)
            elif block.type == exsblock.TYPE_GROUP:
                group_ctr += 1
                group = exsclasses.parse_group(block.legacy_data, id=group_ctr, endian=endian)
                instrument.groups.append(group)
            elif block.type == exsblock.TYPE_SAMPLE:
                sample_ctr += 1
                sample = exsclasses.parse_sample(block.legacy_data, id=sample_ctr, endian=endian)
                sample.exsfile_pos = block.offset
                instrument.samples.append(sample)
            elif block.type == exsblock.TYPE_PARAMS:
                instrument.param_data = block.legacy_data
                instrument.params = exsclasses.parse_params(block.legacy_data, endian=endian)
            elif block.type in exsblock.SKIPPABLE_TYPES:
                # Recognized but unused: zero-padding and the binary-plist
                # metadata blocks newer Logic/Sampler files carry. Skipped; the
                # writer doesn't emit them.
                pass
            else:
                print ("UNKNOWN EXS BLOCK TYPE!", hex(block.type), repr(block.name))
        except (ValueError, struct.error) as e:
            # A core block we could not decode (e.g. a truncated/degenerate zone
            # in some legacy files). Don't return a half-built instrument.
            print (f"UNSUPPORTED EXS LAYOUT: {os.path.split(pathname)[1]} (cannot parse {hex(block.type)} block: {e})")
            return None

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