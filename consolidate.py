# ░█▀▀░█▀█░█▀█░█▀▀░█▀█░█░░░▀█▀░█▀▄░█▀█░▀█▀░█▀▀░░░█▀█░█░█
# ░█░░░█░█░█░█░▀▀█░█░█░█░░░░█░░█░█░█▀█░░█░░█▀▀░░░░█▀▀░░█░
# ░▀▀▀░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀▀░░▀░▀░░▀░░▀▀▀░▀░▀░░░░▀░
#
# Replicates Logic Sampler's "Save with Audio" + "Consolidated" monolithic CAF save.
# Matches the byte layout Logic's Sampler produces for that save.
#
# Exact behaviour matched:
#   * samples bucketed by (sampleRate, channels, bitDepth) -> one CAF per bucket
#     (NO rate normalisation / pitch-adjust; native rate kept per bucket)
#   * layout: 8192-frame silence lead, then StartFrame(n)=roundUp1024(EndFrame(n-1)+8192)
#   * size cap 1,800,000,000 decoded bytes -> continuation CAF
#   * lpcm CAF written byte-faithfully (desc big-endian + free(4016) + data; dataOffset=4096)
#   * alac via Apple's afconvert (0 priming -> frame-exact); dataOffset=0
#   * zones repointed: Start/End/Loop += sample base; FileName = monolith index
import os
import re
import struct
import subprocess
import tempfile

from exsclasses import EXSSample
from exsfile import read_exsfile, write_exsfile
from samplesearch import resolve_sample_locations

GUARD_FRAMES   = 8192          # silence lead + inter-sample guard band
ALIGN_FRAMES   = 1024          # StartFrames are rounded up to this
SIZE_CAP_BYTES = 1_800_000_000 # decoded-byte cap before a continuation CAF  (const 0x6b49d200)


def _roundup(x, n):
    return ((x + n - 1) // n) * n


def sum_frames(pcm_parts, bpf):
    return sum(len(p) for p in pcm_parts) // bpf


def afinfo_format(path):
    """(sampleRate:int, channels:int, bits:int, is_float:bool) via Apple's afinfo.
    Parses ONLY the 'Data format:' and 'source bit depth:' lines -- never the whole
    output -- so digits in the file path/name (e.g. a sample named 'F4.wav') can't be
    mistaken for a format value. Bit depth is printed as 'Int16', '24-bit ... integer',
    or on the 'source bit depth:' line as 'I16'/'F32'."""
    r = subprocess.run(["afinfo", path], capture_output=True, text=True)
    if r.returncode != 0:
        raise ValueError(f"afinfo could not open {path}: {r.stderr.strip() or 'returncode %d' % r.returncode}")
    out = r.stdout
    dfl = next((ln for ln in out.splitlines() if "Data format" in ln), "")
    sbd = next((ln for ln in out.splitlines() if "source bit depth" in ln.lower()), "")
    mch = re.search(r"(\d+)\s*ch", dfl)
    mrate = re.search(r"([\d.]+)\s*Hz", dfl)
    if not (mch and mrate):
        raise ValueError(f"afinfo could not parse format of {path}:\n{out}")
    ch = int(mch.group(1))
    rate = int(round(float(mrate.group(1))))
    is_float = bool(re.search(r"float", dfl, re.I)) or "0x00000009" in dfl \
        or bool(re.search(r"\bF\d", sbd))
    bits = None
    for pat in (r"(\d+)-bit", r"Int(\d+)"):       # inline on the data-format line
        m = re.search(pat, dfl)
        if m:
            bits = int(m.group(1)); break
    if bits is None and sbd:                       # else 'source bit depth: I16' / 'F32'
        m = re.search(r"[A-Za-z](\d+)", sbd)
        if m:
            bits = int(m.group(1))
    if bits is None and is_float:
        bits = 32
    if bits is None:
        raise ValueError(f"afinfo could not parse bit depth of {path}:\n{out}")
    return rate, ch, bits, is_float


def _read_caf_pcm(path):
    """Return (raw_pcm_bytes, frames, channels, bits, rate) from a CAF lpcm file."""
    d = open(path, "rb").read()
    if d[:4] != b"caff":
        raise ValueError(f"not a CAF: {path}")
    pos, desc = 8, None
    while pos + 12 <= len(d):
        ctype = d[pos:pos + 4]
        csize = struct.unpack(">q", d[pos + 8 - 4:pos + 12])[0]
        body = pos + 12
        if ctype == b"desc":
            rate = struct.unpack(">d", d[body:body + 8])[0]
            ch, bits = struct.unpack(">II", d[body + 24:body + 32])
            bpp = struct.unpack(">I", d[body + 16:body + 20])[0]
            desc = (rate, ch, bits, bpp)
        elif ctype == b"data":
            if desc is None:
                raise ValueError(f"data chunk before desc in {path}")
            if csize < 0:
                csize = len(d) - body
            audio = d[body + 4:body + csize]   # skip the 4-byte mEditCount
            rate, ch, bits, bpp = desc
            return audio, len(audio) // bpp, ch, bits, int(round(rate))
        pos = body + (csize if csize >= 0 else len(d) - body)
    raise ValueError(f"no data chunk in {path}")


def _source_to_be_pcm(src_path, bits, is_float=False, expect_ch=None):
    """afconvert any source -> big-endian interleaved PCM bytes (float -> BEF32 to avoid
    a lossy int conversion). Native rate/channels are preserved (the bucket shares them)."""
    dformat = "BEF32" if is_float else f"BEI{bits}"
    tmp = tempfile.mktemp(suffix=".caf")
    try:
        subprocess.run(["afconvert", "-f", "caff", "-d", dformat, src_path, tmp],
                       check=True, capture_output=True)
        pcm, frames, ch, b, rate = _read_caf_pcm(tmp)
        if expect_ch is not None and ch != expect_ch:
            raise ValueError(f"{src_path}: channel count {ch} != expected {expect_ch}")
        return pcm, frames
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _write_caf_lpcm(out_path, pcm, frames, channels, bits, rate, is_float=False):
    """Hand-write a Logic-identical lpcm CAF: caff + desc(BE) + free(4016) + data.
    Header is exactly 4096 bytes so audio (dataOffset) begins at 4096."""
    bytes_per_packet = channels * (bits // 8)
    if len(pcm) != frames * bytes_per_packet:
        raise ValueError("pcm length does not match frames/format")
    # CAF desc flags: bit0=float. Signed-int big-endian => 0 (matches Logic); float => 1.
    flags = 1 if is_float else 0
    with open(out_path, "wb") as f:
        f.write(b"caff" + struct.pack(">HH", 1, 0))
        f.write(b"desc" + struct.pack(">q", 32))
        f.write(struct.pack(">d", float(rate)) + b"lpcm" +
                struct.pack(">IIIII", flags, bytes_per_packet, 1, channels, bits))
        f.write(b"free" + struct.pack(">q", 4016) + b"\x00" * 4016)
        f.write(b"data" + struct.pack(">q", 4 + len(pcm)))
        f.write(struct.pack(">I", 1))          # mEditCount
        f.write(pcm)


# codec -> afconvert data-format. lpcm is hand-written; the rest go through afconvert and
# read back FRAME-ACCURATE: alac is lossless w/ 0 priming; aac is lossy but CoreAudio trims
# the encoder priming via the CAF 'pakt' chunk so the pre-encode frame offsets stay valid
# (verified: 88274 valid -> +2112 priming -> decodes 88274). HE-AAC ('aach') is deliberately
# NOT offered: SBR halves the core rate (desc shows 22050) and decodes off-by-one, which
# would corrupt the frame offsets and sample rate.
_AFCONVERT_CODECS = {"alac": "alac", "aac": "aac"}

# AAC only encodes these sample rates; anything else (e.g. EMU/SF2 native 31570 Hz) gets
# silently resampled, which shifts frame counts and breaks the zone offsets. For such a
# bucket we fall back to ALAC (lossless, rate-preserving). lpcm/alac handle any rate.
AAC_SAMPLE_RATES = {8000, 11025, 12000, 16000, 22050, 24000, 32000,
                    44100, 48000, 64000, 88200, 96000}


def _finalise_caf(lpcm_path, out_path, codec, aac_bitrate=None):
    """lpcm: keep the hand-written CAF. alac/aac: re-encode via afconvert."""
    if codec == "lpcm":
        if lpcm_path != out_path:
            os.replace(lpcm_path, out_path)
        return
    dfmt = _AFCONVERT_CODECS.get(codec)
    if dfmt is None:
        raise ValueError(f"unsupported codec {codec!r} (use lpcm, alac, or aac)")
    cmd = ["afconvert", "-d", dfmt, "-f", "caff"]
    if codec == "aac" and aac_bitrate:
        cmd += ["-b", str(aac_bitrate)]          # bits/sec, e.g. 256000
    cmd += [lpcm_path, out_path]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except Exception:
        if os.path.exists(out_path):
            os.unlink(out_path)                  # drop a partial/failed encode
        raise
    finally:
        if os.path.exists(lpcm_path):
            os.unlink(lpcm_path)                 # always remove the lpcm temp


def _monolith_name(root, part_index, naming):
    """part_index is 0-based. naming: 'interactive' -> '<root>_NN'; 'consolidated' -> Logic factory."""
    if naming == "consolidated":
        return root + ("" if part_index == 0 else f"_{part_index + 1}") + "_consolidated"
    return f"{root}_{part_index + 1:02d}"          # interactive "Save with Audio" style


def consolidate(instrument, output_path, codec="lpcm", naming="interactive",
                prefix=None, aac_bitrate=None,
                resolve=True, write_instrument=True,
                original_group_data=True, original_param_data=True):
    """Consolidate `instrument`'s samples into monolithic CAF(s) in `output_path`,
    repointing every zone, the way Logic's Sampler does.

    codec       : 'lpcm' (Logic's interactive default, byte-faithful), 'alac' (lossless,
                  factory-style), or 'aac' (lossy; frame-accurate via pakt priming).
    naming      : 'interactive' (<root>_NN.caf) or 'consolidated' (<root>_consolidated.caf).
    prefix      : if set, prepended to the instrument/monolith name root ("<prefix> <root>").
    aac_bitrate : bits/sec for aac (e.g. 256000); afconvert default if None.
    Returns the list of monolith EXSSample records that replaced instrument.samples.

    Samples are bucketed by (sampleRate, channels, bitDepth, float?) -> one CAF per bucket,
    with a 1.8 GB-decoded cap forcing _N continuations. NOTE vs Logic: Logic ALSO splits on
    output bus and articulation-group (so a multi-articulation factory instrument ships
    several named monoliths) -- that is NOT replicated here, so the monolith set/names can
    differ for such instruments, though playback is identical. Layout always uses the factory
    algorithm (8192-frame lead + roundUp1024); 'interactive' chooses only the file naming,
    not Logic's overlapping single-source interactive packing.
    """
    os.makedirs(output_path, exist_ok=True)
    if instrument.pathname is None:
        instrument.pathname = (instrument.name or "instrument") + ".exs"
    if resolve:
        if not resolve_sample_locations(instrument):
            raise FileNotFoundError("could not locate all source samples")
    root = os.path.splitext(os.path.basename(instrument.pathname))[0]
    if prefix:
        root = f"{prefix} {root}"

    srcs = instrument.samples
    if not srcs:
        raise ValueError("instrument has no samples to consolidate")
    # bucket every source sample by its native format
    buckets = {}      # key -> list of original-sample indices
    fmt = {}          # original index -> (rate, channels, bits, is_float, src_path)
    for si, s in enumerate(srcs):
        path = os.path.join(s.folder, s.filename)
        rate, ch, bits, is_float = afinfo_format(path)
        key = (rate, ch, bits, is_float)
        buckets.setdefault(key, []).append(si)
        fmt[si] = (rate, ch, bits, is_float, path)

    mono_samples = []                 # the new EXSSample monolith records
    base_of = {}                      # original index -> (mono_sample_index, base_frame)
    part_index = 0

    for key, indices in buckets.items():
        rate, ch, bits, is_float = key
        bpf = ch * (bits // 8)        # bytes per frame (float32 -> 4)
        pcm_parts = [b"\x00" * (GUARD_FRAMES * bpf)]   # 8192-frame silence lead
        cursor = GUARD_FRAMES         # frame position where the next sample will start
        placements = []               # (orig_index, start_frame)

        def flush():
            nonlocal part_index, pcm_parts, cursor, placements
            if not placements:
                return
            total_frames = cursor      # ends at the last sample's end (no trailing guard)
            pcm = b"".join(pcm_parts)
            name = _monolith_name(root, part_index, naming)
            lpcm_tmp = os.path.join(output_path, name + (".caf" if codec == "lpcm" else ".lpcm.tmp.caf"))
            _write_caf_lpcm(lpcm_tmp, pcm, total_frames, ch, bits, rate, is_float)
            out_caf = os.path.join(output_path, name + ".caf")
            eff_codec = codec
            if codec == "aac" and rate not in AAC_SAMPLE_RATES:
                eff_codec = "alac"   # AAC would resample this rate and break offsets
                print(f"  note: {rate} Hz is not AAC-encodable; using ALAC for {name}.caf")
            _finalise_caf(lpcm_tmp, out_caf, eff_codec, aac_bitrate)

            ms = EXSSample()
            ms.Name = ms.filename = name + ".caf"
            ms.folder = output_path
            ms.sampleRate, ms.channels, ms.bitdepth = rate, ch, bits
            ms.fileType = b"ffac"
            ms.frameCount = total_frames
            ms.isCompressed = (codec != "lpcm")
            ms.dataOffset = 0 if ms.isCompressed else 4096
            ms.fileSize = (total_frames * bpf) if ms.isCompressed else (4096 + total_frames * bpf)
            mono_idx = len(mono_samples)
            mono_samples.append(ms)
            for oi, start in placements:
                base_of[oi] = (mono_idx, start)
            part_index += 1
            pcm_parts = [b"\x00" * (GUARD_FRAMES * bpf)]
            cursor = GUARD_FRAMES
            placements = []

        for oi in indices:
            srate, sch, sbits, sfloat, path = fmt[oi]
            pcm, frames = _source_to_be_pcm(path, bits, is_float, expect_ch=ch)
            # first sample sits after the 8192 lead; each next at roundUp1024(prev_end + 8192)
            start = _roundup(cursor + GUARD_FRAMES, ALIGN_FRAMES) if placements else GUARD_FRAMES
            # if placing it here would push the monolith past the decoded-byte cap, roll over
            if placements and (start + frames) * bpf > SIZE_CAP_BYTES:
                flush()
                start = GUARD_FRAMES
            # pad silence from current cursor up to `start`
            pad = start - sum_frames(pcm_parts, bpf)
            if pad > 0:
                pcm_parts.append(b"\x00" * (pad * bpf))
            pcm_parts.append(pcm)
            placements.append((oi, start))
            cursor = start + frames
        flush()

    # repoint every zone to its sample's monolith region
    for z in instrument.zones:
        if z.FileName is None or z.FileName < 0 or z.FileName >= len(srcs):
            continue
        placed = base_of.get(z.FileName)
        if placed is None:               # source skipped/unplaced -> leave zone untouched
            continue
        mono_idx, base = placed
        z.StartFrame = (z.StartFrame or 0) + base
        z.EndFrame = (z.EndFrame or 0) + base
        z.SustainLoopStart = (z.SustainLoopStart or 0) + base
        z.SustainLoopEnd = (z.SustainLoopEnd or 0) + base
        z.FileName = mono_idx

    instrument.samples = mono_samples

    if write_instrument:
        out_name = root + (".exs" if not root.endswith(".exs") else "")
        write_exsfile(instrument, os.path.join(output_path, out_name),
                      original_group_data=original_group_data,
                      original_param_data=original_param_data)
    return mono_samples


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        description="Consolidate a Sampler/EXS24 instrument's samples into monolithic "
                    "CAF(s) and repoint its zones, like Logic's 'Save with Audio + Consolidated'.")
    ap.add_argument("exs", help="input .exs instrument")
    ap.add_argument("output_dir", help="folder for the consolidated .exs + monolith CAF(s)")
    ap.add_argument("--codec", choices=["lpcm", "alac", "aac"], default="lpcm",
                    help="monolith codec (default lpcm = Logic's interactive default)")
    ap.add_argument("--naming", choices=["interactive", "consolidated"], default="interactive",
                    help="'<root>_NN.caf' (default) or '<root>_consolidated.caf'")
    ap.add_argument("--prefix", default=None, help="prepend '<prefix> ' to output names")
    ap.add_argument("--aac-bitrate", type=int, default=None, help="bits/sec for aac")
    ap.add_argument("--no-resolve", action="store_true",
                    help="skip sample-location resolution (paths already correct)")
    args = ap.parse_args()

    inst = read_exsfile(args.exs)
    if inst is None:
        raise SystemExit(f"could not read {args.exs}")
    monos = consolidate(inst, args.output_dir, codec=args.codec, naming=args.naming,
                        prefix=args.prefix, aac_bitrate=args.aac_bitrate,
                        resolve=not args.no_resolve)
    print(f"consolidated {os.path.basename(args.exs)} -> {len(monos)} monolith(s) "
          f"in {args.output_dir}  [{args.codec}]")
