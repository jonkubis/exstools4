#!/usr/bin/env python3
"""Set the polyphony (maximum voices) of a Sampler/EXS .exs instrument.

Polyphony is parameter id 5 in the instrument's parameter chunk, stored as a
plain int16 voice count. The Sampler UI only lets you *pick* values up to its
polyphony dropdown's maximum, but the stored value can be larger and is played
back as-is -- which is how Logic's Studio Piano instruments ship at 256 voices
(useful for multi-mic / long-tail content like sustained piano or cymbals).

This patches the value with a 2-byte overlay on the raw parameter chunk, so the
output is byte-identical to the input apart from the polyphony field: zones,
groups, samples and every other parameter are passed through verbatim.

Usage:
    python3 set_polyphony.py "Instrument.exs" 256
    python3 set_polyphony.py "Instrument.exs" 256 -o "Instrument (256 voices).exs"

If no -o is given, writes "<name> (<N> voices).exs" next to the source.
The field is an int16, so values up to 32767 are accepted. 256 matches Logic's
own Studio Piano; very high values are still bounded by available CPU.
"""
import argparse
import os
import struct
import sys

import exsfile

POLYPHONY_ID = 5
INT16_MAX = 32767


def _endian(param_data):
    # The chunk magic sits at +8 (the first 8 bytes are zero padding):
    # TBOS/JBOS => little-endian, SOBT/SOBJ => big-endian.
    return '>' if param_data[8:12] in (b'SOBT', b'SOBJ') else '<'


def find_polyphony_offset(param_data):
    """Return (style, byte_offset) of the polyphony value inside param_data, or (None, None).

    Layout: 100 single-byte ids @ +80, 100 int16 values @ +180 ("old style"); then a
    count @ +380 and up to 200 (id:int16, value:int16) pairs @ +384 ("new style").
    """
    en = _endian(param_data)
    ids = list(param_data[80:180])
    if POLYPHONY_ID in ids:
        k = ids.index(POLYPHONY_ID)
        return ('old', 180 + k * 2)
    if len(param_data) >= 384:
        cnt = struct.unpack_from(en + 'I', param_data, 380)[0]
        cnt = min(cnt, (len(param_data) - 384) // 4)
        for j in range(cnt):
            pid = struct.unpack_from(en + 'h', param_data, 384 + j * 4)[0]
            if pid == POLYPHONY_ID:
                return ('new', 384 + j * 4 + 2)
    return (None, None)


def set_polyphony(src, voices, out=None):
    """Patch the polyphony of the instrument at `src` to `voices`. Returns the output path."""
    if not (1 <= voices <= INT16_MAX):
        raise ValueError(f"voices must be 1..{INT16_MAX} (got {voices})")

    inst = exsfile.read_exsfile(src)
    if not getattr(inst, 'param_data', None):
        raise ValueError("This instrument has no parameter chunk (relies on engine "
                         "defaults); add one before setting polyphony.")

    en = _endian(inst.param_data)
    style, off = find_polyphony_offset(inst.param_data)
    if style is None:
        raise ValueError("Polyphony (param id 5) not present in this instrument's chunk.")

    old = struct.unpack_from(en + 'h', inst.param_data, off)[0]
    pd = bytearray(inst.param_data)
    struct.pack_into(en + 'h', pd, off, voices)
    inst.param_data = bytes(pd)

    if out is None:
        root, ext = os.path.splitext(src)
        out = f"{root} ({voices} voices){ext}"

    exsfile.write_exsfile(
        inst, out,
        original_zone_data=True, original_group_data=True,
        original_sample_data=True, original_param_data=True,
    )
    print(f"Polyphony {old} -> {voices}  ({style}-style, +{off})")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Set EXS/Sampler instrument polyphony (max voices).")
    ap.add_argument("exs", help="source .exs instrument")
    ap.add_argument("voices", type=int, help="number of voices (1..32767; 256 = Studio Piano)")
    ap.add_argument("-o", "--out", help="output path (default: '<name> (<N> voices).exs')")
    args = ap.parse_args()
    try:
        set_polyphony(args.exs, args.voices, args.out)
    except ValueError as e:
        sys.exit(str(e))
