# started 2/12/2024

import exsclasses
import struct
import os

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
    while offset < len(data):
        chunk_signature = data[offset : offset+4]
        chunk_length    = struct.unpack_from('<I', data[offset + 4: offset + 8])[0] + 84
        chunk_data      = data[offset + 8: offset + chunk_length]

        if chunk_signature == b'\x01\x01\x00\x00' or chunk_signature == b'\x01\x01\x00\x40': # EXS header
            instrument = exsclasses.parse_instrument(chunk_data)
            if instrument.name == "(null)": instrument.name = os.path.split(pathname)[1]
        elif chunk_signature == b'\x01\x01\x00\x01' or chunk_signature == b'\x01\x01\x00\x41': # zone
                zone = exsclasses.parse_zone(chunk_data)
                pass
        elif chunk_signature == b'\x01\x01\x00\x02': # group
                pass
        elif chunk_signature == b'\x01\x01\x00\x03': # sample
                pass
        elif chunk_signature == b'\x01\x01\x00\x04': # params
                pass
        else:
            print ("UNKNOWN CHUNK SIGNATURE!",chunk_signature)

        offset += chunk_length

if __name__ == '__main__':
    read_exsfile('/Users/jonkubis/Desktop/test.exs') #"/Users/jonkubis/Downloads/EXSOUT2/NIK4FL Grand Piano.exs")