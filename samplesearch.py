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
    if not os.path.exists(pathname): raise FileNotFoundError

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
            sample.iscompressed = values[0] == 1
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
        else:
            print ("UNSUPPORTED SAMPLE FORMAT:",first_four,"-- ABORTING!")
            quit()

    return sample

def resolve_sample_locations(instrument):
    previously_found_paths = []
    exsfile_path = os.path.split(instrument.pathname)[0]
    user_path = os.path.expanduser("~")
    music_apps_path = os.path.join(user_path, "Music/Audio Music Apps/Sampler Instruments/")

    for s in instrument.samples:
        if s.filename is None: s.filename = s.name

        pathname = os.path.join(s.folder,s.filename)

        if os.path.exists(pathname): continue #pathname is correct and exists - move on!

        # okay -- the pathname doesn't exist.

        # first off, is it in the SAME folder as the EXS file?
        if os.path.exists(os.path.join(exsfile_path,s.filename)):
            s.folder = exsfile_path
            continue

        # is it in a folder with the same name as the instrument (as stored in the instrument file)?
        pathname_to_try = os.path.join(exsfile_path,instrument.name,s.filename)
        if os.path.exists(pathname_to_try):
            s.folder = os.path.split(pathname_to_try)[0]
            continue

        # is it in a folder with the same name as the EXS file?
        pathname_to_try = os.path.join(os.path.splitext(instrument.pathname)[0], s.filename)
        if os.path.exists(pathname_to_try):
            s.folder = os.path.split(pathname_to_try)[0]
            continue

        # let's see if this file was originally in the old Library/Application Support folder but has moved to the new Audio Music Apps folder
        if pathname.startswith('/Library/Application Support/Logic/Sampler Instruments/'):
            pathname_to_try = os.path.join(music_apps_path,pathname[55:])
            if os.path.exists(pathname_to_try):
                s.folder = os.path.split(pathname_to_try)[0]
                continue

        elif '/Library/Application Support/Logic/Sampler Instruments/' in pathname:
            pathname_to_try = pathname.replace('/Library/Application Support/Logic/Sampler Instruments/','/Music/Audio Music Apps/Sampler Instruments/')
            if os.path.exists(pathname_to_try):
                s.folder = os.path.split(pathname_to_try)[0]
                continue

        print ("CAN'T FIND",pathname)

    all_samples_found = True
    for s in instrument.samples:
        if not os.path.exists(os.path.join(s.folder,s.filename)):
            all_samples_found = False
            break

        # for k, v in s.__dict__.items():
        #     if k == 'data': continue
        #     print (k,v)

        get_sample_info(os.path.join(s.folder,s.filename))


    if all_samples_found: print ("All samples found!")


        #print (s.folder)
        #print (s.filename)

if __name__ == '__main__':
    print (get_sample_info('/Users/jonkubis/Music/Audio Music Apps/Sampler Instruments/00 Organized/Bass/JK Finger Bass/(2014914 102959)-1JWA.wav'))