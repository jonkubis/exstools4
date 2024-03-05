# ███████╗ █████╗ ███╗   ███╗██████╗ ██╗     ███████╗███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗   ██████╗ ██╗   ██╗
# ██╔════╝██╔══██╗████╗ ████║██╔══██╗██║     ██╔════╝██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║   ██╔══██╗╚██╗ ██╔╝
# ███████╗███████║██╔████╔██║██████╔╝██║     █████╗  ███████╗█████╗  ███████║██████╔╝██║     ███████║   ██████╔╝ ╚████╔╝
# ╚════██║██╔══██║██║╚██╔╝██║██╔═══╝ ██║     ██╔══╝  ╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║   ██╔═══╝   ╚██╔╝
# ███████║██║  ██║██║ ╚═╝ ██║██║     ███████╗███████╗███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║██╗██║        ██║
# ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═╝        ╚═╝

import os
import struct

from exsclasses import EXSSample


def get_sample_info(pathname):
    if not os.path.exists(pathname):
        raise FileNotFoundError("Can't find "+pathname)

    sample = EXSSample()
    os_size = os.stat(pathname).st_size # reported size by the OS
    sample.folder, sample.filename = os.path.split(pathname)
    sample.name = os.path.splitext(sample.filename)[0]

    with open(pathname,'rb') as infile:
        infile.seek(0, os.SEEK_END)
        f_size = infile.tell() # actual size by seeking to EOF
        infile.seek(0, os.SEEK_SET)

        first_four = infile.read(4)
        if first_four == b'RIFF': #RIFF wave
            main_chunk_size = struct.unpack("<I",infile.read(4))[0] #should be filesize - 8
            fourdigitcode = infile.read(4)

            chunk_id, chunk_size = None, 0
            while chunk_id != b'fmt ': #seek 'til we find the fmt chunk
                infile.seek(chunk_size, os.SEEK_CUR)
                chunk_id, chunk_size = struct.unpack("<4sI", infile.read(8))

            #print (first_four,main_chunk_size)

            data = infile.read(chunk_size)

            fmt_chunk_struct_format = "<HHIIHH"
            struct_size = struct.calcsize(fmt_chunk_struct_format)

            values = list(struct.unpack(fmt_chunk_struct_format, data[:struct_size]))

            frame_length = values[4] # divide the data chunk length by this to get the total number of samples later

            sample.fourdigitcode = b'EVAW'
            sample.filesize = f_size
            sample.iscompressed = values[0] != 1
            sample.channels     = values[1]
            sample.rate         = values[2]
            sample.bitdepth     = values[5]

            chunk_size = 0
            while chunk_id != b'data':
                infile.seek(chunk_size, os.SEEK_CUR)
                chunk_id, chunk_size = struct.unpack("<4sI", infile.read(8))

            sample.wavedatastart = infile.tell()
            sample.length = chunk_size // frame_length # length in samples of the audio file

        elif first_four == b'caff':
            caf_file_version, caf_file_flags = struct.unpack(">HH", infile.read(4))

            first_subchunk_pos = infile.tell()
            chunk_id, chunk_size = None, 0
            while chunk_id != b'desc':
                infile.seek(chunk_size, os.SEEK_CUR)
                chunk_id, chunk_size = struct.unpack(">4sQ", infile.read(12))

            data = infile.read(chunk_size)

            fmt_chunk_struct_format = ">d4sIIIII"
            struct_size = struct.calcsize(fmt_chunk_struct_format)

            values = list(struct.unpack(fmt_chunk_struct_format, data[:struct_size]))

            frame_length = values[3] # divide the data chunk length by this to get the total number of samples later

            sample.fourdigitcode = b'ffac'
            sample.filesize = f_size
            sample.iscompressed = values[1] != b'lpcm'
            sample.rate = int(values[0])
            sample.bitdepth = values[6]

            if sample.iscompressed: # we need to grab the length in samples from the 'pakt' chunk
                infile.seek(first_subchunk_pos,os.SEEK_SET)
                chunk_size = 0
                while chunk_id != b'pakt':
                    infile.seek(chunk_size, os.SEEK_CUR)
                    chunk_id, chunk_size = struct.unpack(">4sQ", infile.read(12))

                pakt_chunk_struct_format = ">qqii"
                struct_size = struct.calcsize(pakt_chunk_struct_format)

                data = infile.read(chunk_size)
                values = list(struct.unpack(pakt_chunk_struct_format, data[:struct_size]))
                sample.length = values[1]

            chunk_size = 0
            while chunk_id != b'data':
                infile.seek(chunk_size, os.SEEK_CUR)
                chunk_id, chunk_size = struct.unpack(">4sQ", infile.read(12))
                if not sample.iscompressed: sample.length = (chunk_size-4) // frame_length

            sample.wavedatastart = infile.tell() + 4  # first 4 bytes of the CAF Data chunk are 'UInt32 mEditCount;' THEN the wave data
        elif first_four == b'FORM':  # AIF format
            main_chunk_size = struct.unpack(">I", infile.read(4))[0]  # should be filesize - 8
            fourdigitcode = infile.read(4)

            chunk_id, chunk_size = None, 0
            while chunk_id != b'COMM': #seek 'til we find the COMM chunk, the AIFF equivalent of the RIFF WAVE 'fmt ' chunk
                infile.seek(chunk_size, os.SEEK_CUR)
                chunk_id, chunk_size = struct.unpack(">4sI", infile.read(8))

            data = infile.read(chunk_size)

            COMM_chunk_struct_format = ">HIHhLL"
            struct_size = struct.calcsize(COMM_chunk_struct_format)

            values = list(struct.unpack(COMM_chunk_struct_format, data[:struct_size]))

            expon, himant, lomant = values[3:6]
            # sign = -1 if expon < 0 else 1
            # expon = expon + 0x8000 if expon < 0 else expon
            # if expon == himant == lomant == 0: sample.rate = 0.0
            # elif expon == 0x7FFF: sample.rate = sign * 1.79769313486231e+308  # Approximation of huge value
            # else: sample.rate = sign * (himant * 0x100000000 + lomant) * pow(2.0, expon - 16383 - 63)
            sample_rate = 0.0 if expon == himant == lomant == 0 else (-1 if expon < 0 else 1) * (1.79769313486231e+308 if expon == 0x7FFF else (himant * 0x100000000 + lomant) * pow(2.0, (expon + 0x8000 if expon < 0 else expon) - 16383 - 63))

            sample.fourdigitcode = b'FFIA'
            sample.filesize     = f_size
            sample.iscompressed = 0
            sample.channels     = values[0]
            sample.rate         = int(sample_rate)
            sample.bitdepth     = values[2]
            frame_length = (sample.bitdepth // 8) * sample.channels

            chunk_size = 0

            while chunk_id != b'SSND':
                infile.seek(chunk_size, os.SEEK_CUR)
                chunk_id, chunk_size = struct.unpack(">4sI", infile.read(8))

            # infile.seek(chunk_size, os.SEEK_CUR)
            sample_start_offset, sample_block_size = struct.unpack(">II", infile.read(8))

            sample.wavedatastart = infile.tell()
            sample.length = chunk_size // frame_length # length in samples of the audio file

        else:
            print ("UNSUPPORTED SAMPLE FORMAT:",first_four,"-- ABORTING!")
            quit()

    return sample


def check_if_match(sample,pathname,match_filesize=False):
    """
    This is sort of a 'gauntlet' of tests to make sure a sample file candidate actually matches the sample referred to
    in the EXS file.

    :param sample:
    :param pathname:
    :param match_filesize:
    :return:
    """

    # does provided path even exist?
    if not(os.path.exists(pathname)):
        #print(f"PATHNAME {pathname} DOES NOT EXIST!")
        return False

    # see if we were only passed a folder. if we were, then append the filename
    if os.path.isdir(pathname):
        pathname = os.path.join(pathname,sample.filename)
        #print (f"PATHNAME {pathname} DOES NOT EXIST!")
        if not(os.path.exists(pathname)): return False

    # if the filename doesn't match the sample filename
    if os.path.basename(pathname) != sample.filename:
        #print (f"{os.path.basename(pathname)} DOES NOT MATCH")
        return False

    # if we are required to match filesize, let's check it!
    if match_filesize:
        if sample.filesize != os.path.getsize(pathname):
            print(f"{pathname} FILE SIZE DOES NOT MATCH! should be {sample.filesize} but is {os.path.getsize(pathname)}")
            candidate = get_sample_info(pathname)
            print("HERE ARE THE SAMPLE LENGTHS:",sample.length, candidate.length)

            return False

    #print (f"FOUND {pathname}")

    return True


def resolve_sample_locations(instrument,search_path=None,match_filesize=True):
    previously_found_paths = []
    exsfile_path = os.path.split(instrument.pathname)[0]
    user_path = os.path.expanduser("~")
    music_apps_path = os.path.join(user_path, "Music/Audio Music Apps/Sampler Instruments/")

    for s in instrument.samples:
        if s.filename is None: s.filename = s.name

        # check first if the folder+filename in the EXS file is good -- if so, we don't need to do anything
        if check_if_match(s,s.folder,match_filesize=match_filesize): continue

        # okay -- the pathname doesn't exist.

        # first off, is it in the SAME folder as the EXS file?
        if check_if_match(s,exsfile_path,match_filesize=match_filesize):
            s.folder = exsfile_path
            continue

        # is it in a folder with the same name as the instrument (as stored in the instrument file)?
        pathname_to_try = os.path.join(exsfile_path,instrument.name)
        if check_if_match(s, pathname_to_try, match_filesize=match_filesize):
            s.folder = pathname_to_try
            continue

        # is it in a folder with the same name as the EXS file?
        pathname_to_try = os.path.join(os.path.splitext(instrument.pathname)[0])
        if check_if_match(s, pathname_to_try, match_filesize=match_filesize):
            s.folder = pathname_to_try
            continue

        # let's see if this file was originally in the old Library/Application Support folder but has moved to the new Audio Music Apps folder
        original_pathname = os.path.join(s.folder)
        if original_pathname.startswith('/Library/Application Support/Logic/Sampler Instruments/'):
            pathname_to_try = os.path.join(music_apps_path,original_pathname[55:])
            if check_if_match(s, pathname_to_try,match_filesize=match_filesize):
                s.folder = os.path.split(pathname_to_try)[0]
                continue

        elif '/Library/Application Support/Logic/Sampler Instruments/' in original_pathname:
            pathname_to_try = original_pathname.replace('/Library/Application Support/Logic/Sampler Instruments/','/Music/Audio Music Apps/Sampler Instruments/')
            if check_if_match(s, pathname_to_try,match_filesize=match_filesize):
                s.folder = os.path.split(pathname_to_try)[0]
                continue

        if search_path is not None:
            pathname_to_try = search_path
            if check_if_match(s, pathname_to_try, match_filesize=match_filesize):
                s.folder = pathname_to_try
                continue

            # is it in a folder with the same name as the EXS file?
            exs_file_name = os.path.basename(instrument.pathname)
            pathname_to_try = os.path.join(search_path,os.path.splitext(exs_file_name)[0])
            if check_if_match(s, pathname_to_try, match_filesize=match_filesize):
                s.folder = pathname_to_try
                continue



        print (f"******\nINST: {instrument.pathname}, CAN'T FIND {s.filename}\nORIGINAL PATH: {s.folder}{s.filename}\n******")

    all_samples_found = True
    for s in instrument.samples:
        if not os.path.exists(os.path.join(s.folder,s.filename)):
            print (os.path.join(s.folder,s.filename))
            all_samples_found = False
            break

        # for k, v in s.__dict__.items():
        #     if k == 'data': continue
        #     print (k,v)

        get_sample_info(os.path.join(s.folder,s.filename))


    if all_samples_found:
        #print ("All samples found!")
        return True

    return False


if __name__ == '__main__':


    print (get_sample_info('/Users/jonkubis/Music/Audio Music Apps/Sampler Instruments/00 Organized/Bass/JK Finger Bass/(2014914 102959)-1JWA.wav'))