# Implementing EXS24 export with `exstools4`

**Audience:** an AI coding agent (or developer) working inside *another* sampler /
instrument codebase — SFZ, DecentSampler, Kontakt, a hardware-sampler ripper, a
folder-of-WAVs packer, etc. — who wants to emit **Logic EXS24 (Sampler)**
instrument files by calling this library, rather than re-deriving the binary format.

This guide is self-contained enough to scaffold an exporter without reading the
binary parser, but the Python source in this folder is the ground truth — see
[Source pointers](#source-pointers). Everything below was verified against this
library and the macOS factory EXS library (~48k files); the scaffold in
[TL;DR](#tldr-the-whole-thing) was run end-to-end (build → write → read-back).

> Already-working examples to copy from: **`akais9xx.py`** (Akai S900/S950 disk →
> EXS, incl. velocity layering + ADSR) and **`samplepackmenu.py`** (folder of WAVs →
> EXS). If your task resembles either, read that file first.

---

## Mental model

An EXS24 instrument is, for export purposes, four lists/dicts on one object:

```
EXSInstrument
├── name           # shown in Logic's Sampler
├── samples[]      # EXSSample — one per distinct audio file referenced
├── zones[]        # EXSZone   — one per (sample × key-range × velocity-range)
├── groups[]       # EXSGroup  — OPTIONAL (round-robin, group mute, xfades). Omit for v1.
└── params{}       # dict {param_id: value} — global instrument params (env, filter, bend…)
```

- A **zone** maps a region of the keyboard+velocity to a **sample**, by index:
  `zone.sampleindex` is the position of its sample in `instrument.samples`.
- **Velocity layers / round-robin** = several zones over the *same* key range with
  different `minvel/maxvel` (or group round-robin).
- **Groups are optional.** `akais9xx.py` creates zero groups and works fine; zones
  default to `group = -1` (ungrouped). Only add groups for group-level behavior.
- The writer always emits **little-endian**, which Logic reads natively.

---

## TL;DR: the whole thing

This function is the proven minimal exporter. Adapt `zone_specs` generation to your
source format; everything else can stay.

```python
import os, sys
sys.path.insert(0, "/ABSOLUTE/PATH/TO/exstools4")   # the folder containing this guide

from exsclasses import EXSInstrument, EXSZone
from exsfile import write_exsfile
from samplesearch import get_sample_info
import exsparams


def export_to_exs24(instrument_name, output_dir, zone_specs, param_overrides=None):
    """
    Write `<output_dir>/<instrument_name>.exs` plus expect the referenced audio
    files to live where Logic can resolve them (simplest: in `output_dir`).

    zone_specs: list of dicts, one per zone:
      {
        "sample_path": "/abs/path/to/audio.wav",  # MUST already exist; WAV/AIFF/CAF
        "root":     60,           # MIDI note at which the sample plays at original pitch
        "key_low":  0, "key_high": 127,
        "vel_low":  1, "vel_high": 127,           # 1..127; layer by giving zones disjoint ranges
        "tune":     0.0,          # semitones as a float; the fractional part becomes cents
        "gain_db":  0.0,          # zone volume in dB (~ -96..+12)
        "pan":      0,            # -50..+50
        "start":    0,            # play-start frame (0 = sample beginning)
        "end":      None,         # play-end frame; None = whole sample (= length)
        "loop":     None,         # None, or (loop_start_frame, loop_end_frame)
        "loop_xfade": 0,          # crossfade in frames (optional)
        "reverse":  False, "oneshot": False, "pitch_track": True,
      }
    """
    os.makedirs(output_dir, exist_ok=True)
    inst = EXSInstrument()
    inst.name = instrument_name
    inst.pathname = os.path.join(output_dir, instrument_name + ".exs")

    for i, spec in enumerate(zone_specs):
        # get_sample_info reads the actual audio file and fills the technical
        # fields (rate, length-in-frames, bitdepth, channels, folder, filename, …).
        s = get_sample_info(spec["sample_path"])
        inst.samples.append(s)

        z = EXSZone()
        z.name = s.name
        z.id = i
        z.sampleindex = i                       # link zone -> samples[i]

        z.rootnote = spec["root"]
        z.startnote = spec.get("key_low", 0)
        z.endnote   = spec.get("key_high", 127)

        z.velrangeenable = True
        z.minvel = spec.get("vel_low", 1)
        z.maxvel = spec.get("vel_high", 127)

        # Sample playback window, in FRAMES (not bytes). Both of these default to
        # None on a fresh EXSZone and MUST be set to ints before writing.
        z.samplestart = spec.get("start", 0)
        z.sampleend   = spec["end"] if spec.get("end") is not None else s.length

        loop = spec.get("loop")
        z.loopenable = loop is not None
        z.loopstart, z.loopend = (loop if loop else (0, z.sampleend))
        z.loopcrossfade = spec.get("loop_xfade", 0)

        tune = spec.get("tune", 0.0)            # split a float into semitones + cents
        z.coarsetune = int(round(tune))
        z.finetune   = int(round(100 * (tune - z.coarsetune)))

        z.volumeadjust = int(round(spec.get("gain_db", 0)))
        z.pan = spec.get("pan", 0)
        z.reverse = spec.get("reverse", False)
        z.oneshot = spec.get("oneshot", False)
        z.pitchtracking = spec.get("pitch_track", True)

        inst.zones.append(z)

    # COPY the shared defaults — never alias exsparams.default_params (see Gotchas).
    inst.params = dict(exsparams.default_params)
    if param_overrides:
        inst.params.update(param_overrides)

    write_exsfile(inst, inst.pathname)          # little-endian; Logic-native
    return inst.pathname
```

---

## Setup

- **Import path:** the modules use bare imports (`import exsclasses`), so put this
  folder on `sys.path` (as above) or run with it as the working directory.
- **Python:** 3.x (dataclasses, f-strings).
- **Dependencies for the core write path** (`exsclasses`, `exsfile`, `exsblock`,
  `exsparams`, `samplesearch`): only the standard library. Light.
- **Optional consolidation** (`samplemerge.py`) additionally needs `numpy`,
  `pydub`, `soundfile`, `tqdm` — only import it if you use it.

---

## Step 1 — get your audio on disk, then `get_sample_info`

EXS24 references samples by **file path + name + audio metadata**; it does not embed
audio. So:

1. Write each sample to a real file. **WAV (PCM 16/24-bit)** is the safe choice;
   AIFF and CAF are also supported. If your source is raw PCM / a proprietary
   codec, decode it and write a WAV first (e.g. with `soundfile.write`).
2. Call `samplesearch.get_sample_info(path)` to get a populated `EXSSample`.

`get_sample_info` reads the file header and fills, correctly:

| field | meaning |
|-------|---------|
| `rate` | sample rate (Hz) |
| `length` | **length in frames** (samples-per-channel) |
| `bitdepth` | 16 / 24 … |
| `channels` | 1 / 2 |
| `wavedatastart` | byte offset of audio data in the file |
| `fourdigitcode` | `b'EVAW'` (WAV) / `b'FFIA'` (AIFF) / `b'ffac'` (CAF) … |
| `filesize`, `iscompressed` | as on disk |
| `folder`, `filename`, `name` | from the path |

Do **not** hand-fill these — let `get_sample_info` do it so `length`/`wavedatastart`
are right. (It raises `FileNotFoundError` for a missing path and only understands
RIFF/AIFF/CAF.)

**Where the audio must live at load time:** the sample block stores `folder` +
`filename`, and `get_sample_info` sets `folder` to the audio file's directory.
Simplest portable recipe: **write the WAVs into `output_dir` and the `.exs` into the
same `output_dir`** → Logic resolves them. If you relocate later, this library's
`samplesearch.resolve_sample_locations(inst)` re-finds samples by name/size.

---

## Step 2 — build zones

One `EXSZone` per sample-region. The fields that matter for export:

| field | type / range | meaning | gotcha |
|-------|--------------|---------|--------|
| `sampleindex` | int | index into `inst.samples` | **must set**; default 0 |
| `rootnote` | 0..127 | MIDI note the sample plays untransposed | |
| `startnote` / `endnote` | 0..127 | key range low / high | |
| `minvel` / `maxvel` | 1..127 | velocity range | set `velrangeenable=True` |
| `velrangeenable` | bool | apply the velocity range | default True |
| `samplestart` / `sampleend` | frames | playback window | **both default `None` — must set ints** |
| `loopenable` | bool | loop on | |
| `loopstart` / `loopend` | frames | loop points within the sample | `loopend` also defaults `None` — **always set it** (use `sampleend` when not looping) |
| `loopcrossfade` | frames | loop crossfade | optional |
| `coarsetune` | semitones (signed) | pitch | split from a float tune |
| `finetune` | cents (signed, ~-50..50) | pitch | `cents = round(100*(tune - round(tune)))` |
| `volumeadjust` | dB (signed, ~-96..+12) | zone gain | |
| `pan` | -50..+50 | | |
| `reverse` / `oneshot` / `pitchtracking` / `mute` | bool | play flags | set booleans, **not** a raw options byte |
| `group` | int | group index, or `-1` for none | default -1 |
| `output` | int | output routing | leave 0 |

**Frames, not bytes.** `samplestart/sampleend/loopstart/loopend` are all frame
counts. For a whole, untrimmed sample: `samplestart=0`, `sampleend=sample.length`.
Loops sit inside `[0, length]`, with `loopend` usually `< sampleend`.

**Velocity layering / round-robin:** emit multiple zones over the same key range.
For two velocity layers split at threshold `T`: layer-A zone `maxvel=T-1`, layer-B
zone `minvel=T` (see `akais9xx.py` lines ~425–434). For round-robin you also need a
group with `enableby_roundrobin` set — out of scope for a first pass.

**Booleans, not bit-twiddling.** The writer packs the zone "options" and "loop
options" bytes from the boolean fields (`oneshot`, `pitchtracking` [inverted on
disk], `reverse`, `velrangeenable`, `mute`, `loopenable`, `loopequalpower`,
`loopplaytoendonrelease`). Just set the booleans.

---

## Step 3 — params

`exsparams.default_params` is a sane baseline for a playable instrument. **Copy it,
then override** only what you need:

```python
inst.params = dict(exsparams.default_params)         # COPY — see Gotchas
inst.params[exsparams.PARAM_PITCH_BEND_UP]   = 2
inst.params[exsparams.PARAM_PITCH_BEND_DOWN] = -2
```

Common overrides (constants live in `exsparams.py`):

| constant | units / range | notes |
|----------|---------------|-------|
| `PARAM_PITCH_BEND_UP` / `_DOWN` | semitones (up 0..24, down -24..0) | down `-1` = mirror up |
| `PARAM_MASTER_VOLUME` | dB-ish | |
| `PARAM_COARSE_TUNE` / `PARAM_FINE_TUNE` | semitones / cents | global tune |
| `PARAM_TRANSPOSE` | semitones | |
| `PARAM_ENV1_ATK_HI_VEL` | 0..127 byte → ms | **ENV1 = amplitude envelope.** Attack; exact ms via `MS_LUT` |
| `PARAM_ENV1_DECAY` / `_RELEASE` | 0..127 byte → ms | Decay / Release; exact ms via `MS_LUT` |
| `PARAM_ENV1_HOLD` / `_DELAY_START` | 0..127 (time) | same time scale (unverified) |
| `PARAM_ENV1_SUSTAIN` | 0..127 (level) | a *level*, not a time |
| `PARAM_ENV1_VEL_SENS` | 0..-60 | more negative = more velocity→volume |
| `PARAM_FILTER1_TOGGLE` | 0 / 1 | enable filter |
| `PARAM_FILTER1_TYPE` | 0=LP24 1=LP18 2=LP12 3=LP6 4=HP12 5=BP12 | |
| `PARAM_FILTER1_CUTOFF` | 0..1000 | normalized; ~`round(cutoff_norm*1000)` |
| `PARAM_FILTER1_RESO` | 0..1000 | |

> **ENV1 is the amp envelope; ENV2 is the filter envelope.** The same time params
> exist for ENV2 (`PARAM_ENV2_*`).

**Envelope Attack / Decay / Release times are exact, not approximate.** The byte value
0..127 maps to a specific number of **milliseconds** via the 128-entry table
`exsparams.MS_LUT` (index = byte value). Convert with the helpers:

```python
import exsparams
exsparams.env_value_to_ms(64)      # -> 644.91   (byte 64 ≈ 645 ms)
exsparams.env_ms_to_value(500)     # -> 60       (nearest byte to 500 ms)

# e.g. 50 ms attack + 1 s release on the amp (ENV1) envelope:
inst.params[exsparams.PARAM_ENV1_ATK_HI_VEL] = exsparams.env_ms_to_value(50)
inst.params[exsparams.PARAM_ENV1_RELEASE]    = exsparams.env_ms_to_value(1000)
```

The curve is steep and non-linear: byte `1` = 0.001 ms, `64` ≈ 645 ms, `100` ≈ 3.84 s,
`127` = 10 s (the full table is in `exsparams.MS_LUT`). `SUSTAIN` is a 0..127 *level*,
not a time. Hold/Delay appear to use the same time scale but are unverified, and the
*filter* envelope (ENV2) feel is still worth confirming by ear in Logic.

---

## Step 4 — write

```python
write_exsfile(inst, output_path)   # all original_*_data flags default False -> build from fields
```

That writes the instrument, all zones, all groups, all samples, then params, as a
little-endian `.exs`. Leave the `original_*_data=` flags at their defaults for a
fresh build (they exist to pass through bytes from a previously-*read* instrument).

**Consolidation (optional).** If your samples are many small files, mixed sample
rates, or you want one self-contained instrument, `samplemerge.samplemerge(inst,
output_dir, ...)` concatenates everything into monolithic CAF(s), repoints every
zone's `samplestart/end/loop` by the monolith offset, and detunes per-zone to
normalize sample rates (`sr_pitch_offset = 12·log2(target/src)` semitones). Needs
the numpy/pydub/soundfile/tqdm deps. Read `samplemerge.py` before using it.

---

## Groups — articulations, round-robin, velocity/key crossfade

Groups are optional for a flat instrument, but anything with **keyswitched
articulations, round-robin, release triggers, or crossfades** needs them. Build
`EXSGroup` objects, append to `inst.groups`, and point each zone at one with
`zone.group = <group index>` (default `-1` = ungrouped). Order in `inst.groups`
defines the index.

```python
from exsclasses import EXSGroup
g = EXSGroup(); g.name = "Legato"
group_idx = len(inst.groups)
inst.groups.append(g)
# ...then for every zone that belongs to this group:
z.group = group_idx
```

Useful `EXSGroup` fields (names as in `exsclasses.py`):

| field(s) | meaning |
|----------|---------|
| `name`, `volume` (dB), `pan` | label / mix |
| `polyphony`, `exclusive` | voice limit / exclusive (choke) group |
| `minvel` / `maxvel`, `startnote` / `endnote` | group velocity / key range (gates its zones) |
| **Keyswitch** | `enableby_note=True` + `enablebynotevalue=<ks note>` — group sounds only when that key is the active keyswitch |
| **Round-robin** | `enableby_roundrobin=True` + `roundrobingrouppos=0,1,2,…` — successive notes cycle the groups sharing it |
| **Velocity crossfade** | `velocityrangexfade` (+ `velocityrangexfadetype`) |
| **Key crossfade** | `keyrangexfade` (+ `keyrangexfadetype`) |
| **Release trigger** | `releasetrigger=True` (+ `releasetriggerdecay`) |
| **Per-group env offsets** | `env1attackoffset/decayoffset/sustainoffset/releaseoffset/holdoffset` (and `env2*`) |

> **The amplitude envelope (ENV1) is global** — it lives in `inst.params`, not on the
> group. If your source has a different envelope per group, pick the prevailing one
> for the global ENV1 and express per-group differences with the `env1*offset` fields
> (an offset on the 0-127 byte scale; verify in Logic). `akais9xx.py` does exactly
> this: it picks the most-common ADSR across keygroups as the global envelope.

These group features round-trip through the library but are exercised less than the
basic zone path, so **confirm articulation/round-robin behavior in Logic**.

---

## Reference: fresh-zone fields you must set

A default `EXSZone()` is *almost* writable, but two fields are `None` and will raise
`struct.error: required argument is not an integer` if left unset:

- `sampleend` → set to `sample.length` (or your trim point)
- `loopend` → set to `sampleend` even when `loopenable=False`

Everything else has a usable default (`startnote=0`, `endnote=127`, `minvel=0`,
`maxvel=127`, `group=-1`, tunings/offsets `0`, flags `False`, `pitchtracking=True`).
`EXSSample` should come from `get_sample_info` (don't construct by hand).

---

## Gotchas (checklist)

- [ ] **Copy `default_params`** (`dict(exsparams.default_params)`). `akais9xx.py` and
      `samplepackmenu.py` assign it directly and then mutate it — that edits the
      shared module-global dict and leaks across instruments. Copy instead.
- [ ] **Set `sampleend` AND `loopend`** to ints on every zone (both default `None`).
- [ ] **Frames, not bytes** for all start/end/loop values.
- [ ] **`sampleindex`** on each zone must match its sample's position in
      `inst.samples`.
- [ ] **Velocity layers = extra zones**, not a field on one zone.
- [ ] **Samples must be resolvable** at load (same folder as the `.exs` is easiest).
- [ ] **Provide WAV/AIFF/CAF** to `get_sample_info` (decode other formats first).
- [ ] **Loop boundary may be off-by-one**: EXS likely stores `loopend` as one-past
      the last looped frame (the reference Java reader subtracts 1 on read / adds 1
      on write). If a loop ticks, try `loopend ± 1` and confirm by ear.

---

## Validate before trusting it

Round-trip every instrument you generate — this library reads its own output:

```python
from exsfile import read_exsfile
back = read_exsfile(output_path)
assert back is not None
assert len(back.zones) == len(inst.zones)
z = back.zones[0]
assert (z.rootnote, z.startnote, z.endnote) == (inst.zones[0].rootnote,
                                                inst.zones[0].startnote,
                                                inst.zones[0].endnote)
```

Then **load it in Logic's Sampler** — that is the real oracle for "does it play and
feel right." Structural correctness (right samples at right keys/velocities, loops,
gross tuning) is reliable from this library; envelope/filter *feel* is the part to
verify and iterate on in Logic.

For a heavier harness pattern (fingerprint parse + writer byte-stability + value
sanity against the factory corpus), see `tests/backport_check.py`.

---

## Not covered / known-approximate

- **Amp envelope A/D/R timing is exact** (`MS_LUT`). Hold/Delay (same scale,
  unverified), the filter envelope (ENV2), and `VEL_SENS` feel are worth an ear check.
- **Modulation matrix** — the `MOD1..MOD11_*` params round-trip and export fine. One
  validated routing (Mod Wheel → Sample Select for mod-wheel dynamics) is in the
  appendix; other routings are plausible but confirm the source/destination enum
  codes in Logic.
- **LFOs, dual filter, the binary-plist layout blocks** — present in the parameter
  tables but unproven for round-trip; the writer doesn't emit the bplist blocks.
- **Big-endian output** — the writer emits little-endian only (Logic reads it). The
  *reader* handles both byte orders.
- A handful of legacy embedded-sample EXS variants are unreadable (and unwritten) by
  design; not relevant to export.

---

## Source pointers (ground truth)

| file | what to read it for |
|------|---------------------|
| `exsclasses.py` | `EXSInstrument` / `EXSZone` / `EXSGroup` / `EXSSample` field definitions + defaults; `export_*` packing |
| `exsfile.py` | `write_exsfile()` (and `read_exsfile()` for validation) |
| `exsparams.py` | every `PARAM_*` id, `default_params`, `parameter_order`, `MS_LUT` |
| `samplesearch.py` | `get_sample_info()` (audio → `EXSSample`), `resolve_sample_locations()` |
| `samplepackmenu.py` | worked example: folder of WAVs → EXS |
| `akais9xx.py` | worked example: hardware sampler (keygroups, velocity layers, ADSR) → EXS |
| `samplemerge.py` | optional sample consolidation into monolithic CAF + zone repointing |
| `exsblock.py` | low-level block/byte-order handling (only if you go below the API) |

---

## Appendix: mapping a Play / Kontakt-style source (e.g. EastWest EWI) to EXS24

A worked mapping for higher-level sampler formats (EastWest Play/EWI, Kontakt, SFZ).
EWI XML attribute names are shown; the conversions generalize.

### Instrument / program level

| source (EWI) | EXS | conversion |
|--------------|-----|------------|
| `Name` | `inst.name` | direct |
| `Transpose` (semitones) | `PARAM_TRANSPOSE` | direct |
| `Tune` | `PARAM_COARSE_TUNE` / `_FINE_TUNE` | **EWI tune is centered at 1.0** (1.0 = none); offset = `Tune - 1.0`, split semitone/cents. Verify the unit on a detuned preset |
| `Volume` (linear 0-1) | `PARAM_MASTER_VOLUME` or bake into zones | **dB = `20*log10(vol)`** (vol>0): 1.0→0 dB, 0.5→-6 dB, 0.251→-12 dB |
| `Pan` (-1..1) | `PARAM_MASTER_PAN` / per-zone `pan` | `pan*50` for the -50..50 zone field |
| `VelocitySens` | `PARAM_ENV1_VEL_SENS` | 0 = none; more negative = more vel→volume |

### Region → zone

| source (EWI Region) | EXS zone field | conversion |
|---------------------|----------------|------------|
| `KeyLow` / `KeyHigh` | `startnote` / `endnote` | direct (0-127) |
| `KeyRoot` | `rootnote` | direct |
| `VelocityLow` / `VelocityHigh` | `minvel` / `maxvel` | direct; set `velrangeenable=True` |
| `Start` / `End` | `samplestart` / `sampleend` | frames (direct) |
| `Volume` (0-1) | `volumeadjust` | dB = `20*log10(vol)` |
| `Pan` (-1..1) | `pan` | `pan*50` |
| `Tune` (centered 1.0) | `coarsetune` + `finetune` | offset `Tune-1.0` → semitone/cents split |
| `VelocityFadeLow/High` | group `velocityrangexfade` | EXS velocity xfade is **group-level**, not per-zone |
| `KeyFadeLow/High` | group `keyrangexfade` | likewise group-level |
| `<Sample Path>` | → `get_sample_info(wav)` | resolve to the decrypted/decoded WAV |

**Playback flags** (booleans; EWI stores these per region or group depending on the
library): `Reverse` → zone `reverse`, `Tracking` (key tracking) → zone `pitchtracking`
(1→True), `OnRelease` (release trigger) → group `releasetrigger`.

### Loop (EWI Region/Loop child → EXS zone loop)

| source | EXS | conversion |
|--------|-----|------------|
| `LoopStart` | `loopstart` | frames |
| `LoopLenght`(sic)/`LoopLength`/`LoopEnd` | `loopend` | `loopstart + length` (or `LoopEnd`) |
| length > 0 | `loopenable` | True for a usable loop |
| `xFadeTime` | `loopcrossfade` | frames |
| `Tune` (centered 1.0) | `looptune` | `(Tune-1.0)` → cents |
| `Mode` 1=until_release / 2=until_end | `loopplaytoendonrelease` / normal | mode 1 ≈ sustain loop; confirm in Logic |
| `Alter` (alternating) | `loopdirection` | alternating / bidirectional |
| `Count` | — | EXS loops are continuous; finite repeat counts aren't represented |

### Envelope (EWI AHDSR modulator → EXS global ENV1) — **exact**

EWI AHDSR `attack`/`hold`/`decay`/`release` are in **milliseconds** (they feed
Kontakt's ms envelope directly — defaults `attack=1`, `decay=1000`, `release=100` ms);
`sustain` is a 0-1 level; `curve` is the attack curve. Convert with the corrected
`MS_LUT` (see the envelope note in Step 3):

```python
import exsparams
p = inst.params  # = dict(exsparams.default_params)
p[exsparams.PARAM_ENV1_ATK_HI_VEL] = exsparams.env_ms_to_value(attack_ms)
p[exsparams.PARAM_ENV1_DECAY]      = exsparams.env_ms_to_value(decay_ms)
p[exsparams.PARAM_ENV1_HOLD]       = exsparams.env_ms_to_value(hold_ms)
p[exsparams.PARAM_ENV1_RELEASE]    = exsparams.env_ms_to_value(release_ms)
p[exsparams.PARAM_ENV1_SUSTAIN]    = round(sustain * 127)        # 0-1 level -> 0-127
# curve (-1..1) -> EXS attack-curve param (approx; encoding in EXS24Creator.java)
```

ENV1 is **global**; for per-group envelopes pick the prevailing one and use the group
`env1*offset` fields (see [Groups](#groups--articulations-round-robin-velocitykey-crossfade)).

### Groups, keyswitches, round-robin

- EWI playable groups (`Group Type="1"`) → `EXSGroup`; skip global (`Type=0`) and
  separator (`Type=3`).
- Keyswitch (from `ArticulationTable` Layer `StartModeContainer` keyswitch modes) →
  group `enableby_note=True` + `enablebynotevalue=<ks note>`.
- Round-robin → group `enableby_roundrobin=True` + `roundrobingrouppos`.
- Pitch bend → EWI always emits ±2 semitones → `PARAM_PITCH_BEND_UP=2`,
  `PARAM_PITCH_BEND_DOWN=-2`.

### Mod-wheel dynamics (CC1 morph) — achievable via Mod Matrix + velocity XFade

EastWest's mod-wheel dynamics **do** map to EXS24. Route **Mod Wheel → Sample Select**
in the Mod Matrix so the mod wheel (not velocity) chooses the active layer, then use
the group **velocity-range XFade** to smooth between layers. The Mod-Matrix enum codes
below were determined empirically from the factory library:

```python
import exsparams
p = inst.params
# Mod slot 1: Mod Wheel (CC1) -> Sample Select, 100%
p[exsparams.PARAM_MOD1_SOURCE]      = 1     # source: CC1 = Mod Wheel (positive source = MIDI CC#)
p[exsparams.PARAM_MOD1_DESTINATION] = 8     # destination: Sample Select
p[exsparams.PARAM_MOD1_AMOUNT_LOW]  = 1000  # 100% (amount scale: 1000 = 100%)
p[exsparams.PARAM_MOD1_AMOUNT_HIGH] = 1000
```

Arrange the dynamic layers as adjacent velocity zones (e.g. MP = vel 1-63, MF = vel
64-127), put them in groups, and set the smoothing on each group (fields from the
[Groups](#groups--articulations-round-robin-velocitykey-crossfade) section):

```python
g.velocityrangexfade     = 40    # XFade width (0 = hard switch)
g.velocityrangexfadetype = 1     # XFade type (0 = off; nonzero enables)
```

**Evidence:** of factory instruments that route something to Sample Select (`dest=8`),
**91% also set group velocity XFade** — i.e. this is the standard factory construction
for crossfade instruments. Enum codes: every positive Mod-Matrix source observed is a
valid MIDI CC# (≤127), so `source=1` = CC1/Mod Wheel; `dest=8` = Sample Select; amount
`1000` = 100%. Confirm against a Logic-made reference if you want certainty.

### Not representable in EXS24 (document / drop)

- **Mic CC mixing** (per-mic CC → that mic's own volume) — the EXS Mod Matrix is
  global (instrument-wide), so per-mic CC→volume isn't clean; emit **one EXS
  instrument per mic** instead.
- **Scripts** (legato/portamento/repetition), **PLAY effects** (convolution reverb,
  delay, ADT), **Elastique** — engine-specific; not convertible (same as the NKI path).

### Suggested first pass

Convert one mic/dynamic layer to a flat, playable EXS first: per-region zones with
key/vel/root/start/end/loop/tune/volume, the prevailing AHDSR as the global ENV1
(exact via `MS_LUT`), pitch bend ±2, and groups only where keyswitch/round-robin is
needed. Add velocity layers next. Treat CC-morph / mic-mixing / scripts as out of
scope or separate instruments. Round-trip with `read_exsfile`, then load in Logic.
