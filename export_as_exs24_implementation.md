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

> **Field & parameter names match Logic's Sampler 1:1** (`KeyNote`, `NumFadeOutFrames`, `Tune`/`TuneFine`, `SelByNote`, …).

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
  `zone.FileName` is the position of its sample in `instrument.samples`.
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
        z.Name = s.Name
        z.id = i
        z.FileName = i                       # link zone -> samples[i]

        z.KeyNote = spec["root"]
        z.FirstNote = spec.get("key_low", 0)
        z.LastNote   = spec.get("key_high", 127)

        z.velrangeenable = True
        z.LowestVelocity = spec.get("vel_low", 1)
        z.HighestVelocity = spec.get("vel_high", 127)

        # Sample playback window, in FRAMES (not bytes). Both of these default to
        # None on a fresh EXSZone and MUST be set to ints before writing.
        z.StartFrame = spec.get("start", 0)
        z.EndFrame   = spec["end"] if spec.get("end") is not None else s.frameCount

        loop = spec.get("loop")
        z.SustainLoop = loop is not None
        z.SustainLoopStart, z.SustainLoopEnd = (loop if loop else (0, z.EndFrame))
        z.SustainLoopXFade = spec.get("loop_xfade", 0)

        tune = spec.get("tune", 0.0)            # split a float into semitones + cents
        z.Tune = int(round(tune))
        z.TuneFine   = int(round(100 * (tune - z.Tune)))

        z.Volume = int(round(spec.get("gain_db", 0)))
        z.Pan = spec.get("pan", 0)
        z.Reverse = spec.get("reverse", False)
        z.OneShot = spec.get("oneshot", False)
        z.Pitched = spec.get("pitch_track", True)

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
| `dataOffset` | byte offset of audio data in the file |
| `fileType` | `b'EVAW'` (WAV) / `b'FFIA'` (AIFF) / `b'ffac'` (CAF) … |
| `fileSize`, `isCompressed` | as on disk |
| `folder`, `filename`, `name` | from the path |

Do **not** hand-fill these — let `get_sample_info` do it so `length`/`dataOffset`
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
| `FileName` | int | index into `inst.samples` | **must set**; default 0 |
| `KeyNote` | 0..127 | MIDI note the sample plays untransposed | |
| `FirstNote` / `LastNote` | 0..127 | key range low / high | |
| `LowestVelocity` / `HighestVelocity` | 1..127 | velocity range | set `velrangeenable=True` |
| `velrangeenable` | bool | apply the velocity range | default True |
| `StartFrame` / `EndFrame` | frames | playback window | **both default `None` — must set ints** |
| `SustainLoop` | bool | loop on | |
| `SustainLoopStart` / `SustainLoopEnd` | frames | loop points within the sample | `SustainLoopEnd` also defaults `None` — **always set it** (use `EndFrame` when not looping) |
| `SustainLoopXFade` | frames | loop crossfade | optional |
| `Tune` | semitones (signed) | pitch | split from a float tune |
| `TuneFine` | cents (signed, ~-50..50) | pitch | `cents = round(100*(tune - round(tune)))` |
| `Volume` | dB (signed, ~-96..+12) | zone gain | |
| `pan` | -50..+50 | | |
| `reverse` / `OneShot` / `Pitched` / `mute` | bool | play flags | set booleans, **not** a raw options byte |
| `group` | int | group index, or `-1` for none | default -1 |
| `output` | int | output routing | leave 0 |

**Frames, not bytes.** `samplestart/sampleend/loopstart/loopend` are all frame
counts. For a whole, untrimmed sample: `samplestart=0`, `sampleend=sample.frameCount`.
Loops sit inside `[0, length]`, with `SustainLoopEnd` usually `< sampleend`.

**Velocity layering / round-robin:** emit multiple zones over the same key range.
For two velocity layers split at threshold `T`: layer-A zone `maxvel=T-1`, layer-B
zone `minvel=T` (see `akais9xx.py` lines ~425–434). For round-robin you also need a
group with `SelByGroup` set — out of scope for a first pass.

**Booleans, not bit-twiddling.** The writer packs the zone "options" and "loop
options" bytes from the boolean fields (`OneShot`, `Pitched` [inverted on
disk], `reverse`, `velrangeenable`, `mute`, `SustainLoop`, `SustainLoopXFadeEQPwr`,
`LoopDisableOnRelease`). Just set the booleans.

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
`zone.Group = <group index>` (default `-1` = ungrouped). Order in `inst.groups`
defines the index.

```python
from exsclasses import EXSGroup
g = EXSGroup(); g.Name = "Legato"
group_idx = len(inst.groups)
inst.groups.append(g)
# ...then for every zone that belongs to this group:
z.Group = group_idx
```

Useful `EXSGroup` fields (names as in `exsclasses.py`):

| field(s) | meaning |
|----------|---------|
| `name`, `volume` (dB), `pan` | label / mix |
| `Voices`, `ExclusiveClass` | voice limit / exclusive (choke) group |
| `LowestVelocity` / `HighestVelocity`, `FirstNote` / `LastNote` | group velocity / key range (gates its zones) |
| **Keyswitch** | `enableby_note=True` + `enablebynotevalue=<ks note>` — group sounds only when that key is the active keyswitch |
| **Round-robin** | `enableby_roundrobin=True` + `roundrobingrouppos=0,1,2,…` — successive notes cycle the groups sharing it |
| **Velocity crossfade** | `VelocityXFade` (+ `VelocityXFadeType`) |
| **Key crossfade** | `NoteXFade` (+ `NoteXFadeType`) |
| **Release trigger** | `releasetrigger=True` (+ `ReleaseTriggerDecay`) |
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

- `EndFrame` → set to `sample.frameCount` (or your trim point)
- `SustainLoopEnd` → set to `EndFrame` even when `loopenable=False`

Everything else has a usable default (`startnote=0`, `endnote=127`, `minvel=0`,
`maxvel=127`, `group=-1`, tunings/offsets `0`, flags `False`, `pitchtracking=True`).
`EXSSample` should come from `get_sample_info` (don't construct by hand).

---

## Gotchas (checklist)

- [ ] **Copy `default_params`** (`dict(exsparams.default_params)`). `akais9xx.py` and
      `samplepackmenu.py` assign it directly and then mutate it — that edits the
      shared module-global dict and leaks across instruments. Copy instead.
- [ ] **Set `EndFrame` AND `SustainLoopEnd`** to ints on every zone (both default `None`).
- [ ] **Frames, not bytes** for all start/end/loop values.
- [ ] **`FileName`** on each zone must match its sample's position in
      `inst.samples`.
- [ ] **Velocity layers = extra zones**, not a field on one zone.
- [ ] **Samples must be resolvable** at load (same folder as the `.exs` is easiest).
- [ ] **Provide WAV/AIFF/CAF** to `get_sample_info` (decode other formats first).
- [ ] **Loop boundary may be off-by-one**: EXS likely stores `SustainLoopEnd` as one-past
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
assert (z.KeyNote, z.FirstNote, z.LastNote) == (inst.zones[0].rootnote,
                                                inst.zones[0].startnote,
                                                inst.zones[0].endnote)
```

Then **load it in Logic's Sampler** — that is the real test for "does it play and
feel right." Structural correctness (right samples at right keys/velocities, loops,
gross tuning) is reliable from this library; envelope/filter *feel* is the part to
verify and iterate on in Logic.

For a heavier harness pattern (fingerprint parse + writer byte-stability + value
sanity against the factory corpus), see `tests/backport_check.py`.

---

## Resolved & still-approximate (updated 2026-06)

Most original caveats are now **resolved** — parameter semantics were recovered directly
from Logic's Sampler behaviour, not guessed. See
`sampler_param_table.py` and the constants/enums in `exsparams.py`.

- **Envelope A/D/R timing — EXACT.** The engine encodes `ms = 10000 * (byte/127)**4`
  (`env_value_to_ms` / `env_ms_to_value` now use this); Hold/Delay share the same curve.
  Env types are in `exsparams.ENV_TYPES` (0=AD … 5=DAHDSR; 2=ADSR is universal in the
  factory library). The amp envelope is **ENV1**, the filter envelope is **ENV2**; the
  `0x38`/`0x58` Hold ids (previously swapped) are now fixed.
- **Modulation matrix — fully decoded & corpus-validated.** Complete destination
  (`exsparams.MOD_DESTINATIONS` — 2=Sample Select, 6=Pitch, **8=Filter 1 Cutoff**, …)
  and source (`MOD_SOURCES` — +N = MIDI CC#, −12=LFO1, −3=Velocity, …) enums, with
  `mod_dest_name()` / `mod_src_name()`. Amount 1000 = 100%; an empty slot's destination ∈
  {0, −1, −1234567}.
- **Filter type & LFO waveform — decoded.** `exsparams.FILTER_TYPES` (0=LP 12 dB,
  1=LP 18, 2=LP 24, 3=LP 6, 4=BP, 5=HP — this **corrects** the order in earlier drafts)
  and `LFO_WAVEFORMS` (0=Triangle is the default … 7=Sine).
- **Full parameter set named — complete engine coverage.** A 2026-06 audit extracted
  Logic Sampler's entire parameter table (367 serializable ids,
  verified by exact min/max/default match). `sampler_param_table.py` now names **every**
  one of them (377 entries, id → long/short/group/max/default), and `parameter_order` is
  a verified **superset** of that universe — so the normalized writer can never silently
  drop a synth param. None of the 79 newly-added ids appear in the factory corpus (they
  cover Quick Sampler, Flex, and advanced envelope/LFO features), but Logic *can*
  serialize them, so they now round-trip. Legacy EXS24 mkI control ids (decoded from
  the legacy-control conversion) are named `PARAM_LEGACY_*` and preserved.
- **Rebuild path is now byte-faithful.** `export_zone`/`export_group`/`export_sample`
  overlay edited fields onto a copy of the source chunk (`_merge_passthrough`), keeping
  every byte the struct map doesn't model — so an *unedited* parse→export is
  byte-identical for little-endian chunks, and engine fields that live in struct padding
  (e.g. a zone's precise sub-dB volume float at chunk 0xd0, a group boolean at body 0x08)
  survive editing instead of being zeroed. Two of those are now first-class:
  `zone.VolumePrecise` (float) and `group.unknown_byte_0x08`; the rest are preserved
  verbatim. Constructed (from-scratch) zones/groups are unaffected.
- **Binary-plist blocks** (0x0A = NSKeyedArchiver editor/UI layout, 0x0B = per-sample
  CFURL bookmark) are **round-tripped verbatim** for files that carry them
  (`instrument.passthrough_blocks`) and not synthesized for fresh exports. Adversarial
  audit confirmed the 0x0A archive holds **only** UI state (column layouts, panel sizes,
  slot display order) — no sound parameter exists only there; even its param-named keys
  (`GroupColumns`/`ZoneColumns`) store column widths, not DSP values.
- **Big-endian output** — the writer emits little-endian only (Logic reads it). The
  *reader* handles both byte orders; a big-endian source is re-emitted little-endian
  (its raw bytes are not spliced into the overlay).
- A handful of legacy embedded-sample EXS variants remain unreadable (and unwritten) by
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
| `KeyLow` / `KeyHigh` | `FirstNote` / `LastNote` | direct (0-127) |
| `KeyRoot` | `KeyNote` | direct |
| `VelocityLow` / `VelocityHigh` | `LowestVelocity` / `HighestVelocity` | direct; set `velrangeenable=True` |
| `Start` / `End` | `StartFrame` / `EndFrame` | frames (direct) |
| `Volume` (0-1) | `Volume` | dB = `20*log10(vol)` |
| `Pan` (-1..1) | `pan` | `pan*50` |
| `Tune` (centered 1.0) | `Tune` + `TuneFine` | offset `Tune-1.0` → semitone/cents split |
| `VelocityFadeLow/High` | group `VelocityXFade` | EXS velocity xfade is **group-level**, not per-zone |
| `KeyFadeLow/High` | group `NoteXFade` | likewise group-level |
| `<Sample Path>` | → `get_sample_info(wav)` | resolve to the decrypted/decoded WAV |

**Playback flags** (booleans; EWI stores these per region or group depending on the
library): `Reverse` → zone `reverse`, `Tracking` (key tracking) → zone `Pitched`
(1→True), `OnRelease` (release trigger) → group `ReleaseTrigger`.

### Loop (EWI Region/Loop child → EXS zone loop)

| source | EXS | conversion |
|--------|-----|------------|
| `LoopStart` | `SustainLoopStart` | frames |
| `LoopLenght`(sic)/`LoopLength`/`LoopEnd` | `SustainLoopEnd` | `loopstart + length` (or `LoopEnd`) |
| length > 0 | `SustainLoop` | True for a usable loop |
| `xFadeTime` | `SustainLoopXFade` | frames |
| `Tune` (centered 1.0) | `SustainLoopDeTune` | `(Tune-1.0)` → cents |
| `Mode` 1=until_release / 2=until_end | `LoopDisableOnRelease` / normal | mode 1 ≈ sustain loop; confirm in Logic |
| `Alter` (alternating) | `SustainLoopMode` | alternating / bidirectional |
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
- Round-robin → group `enableby_roundrobin=True` + `SelByGroupCycle`.
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
p[exsparams.PARAM_MOD1_DESTINATION] = exsparams.MOD_DEST_SAMPLE_SELECT  # = 2 (RE-confirmed; was wrongly 8)
p[exsparams.PARAM_MOD1_AMOUNT_LOW]  = 1000  # 100% (amount scale: 1000 = 100%)
p[exsparams.PARAM_MOD1_AMOUNT_HIGH] = 1000
```

Arrange the dynamic layers as adjacent velocity zones (e.g. MP = vel 1-63, MF = vel
64-127), put them in groups, and set the smoothing on each group (fields from the
[Groups](#groups--articulations-round-robin-velocitykey-crossfade) section):

```python
g.VelocityXFade     = 40    # XFade width (0 = hard switch)
g.VelocityXFadeType = 1     # XFade type (0 = off; nonzero enables)
```

**Evidence (corrected 2026-06):** the Sample-Select destination
code is **`2`**, not `8` — confirmed against Logic and corpus-validated. The slot is
located by `destination == 2`; the value is stored literally on disk (no transform).
Enum codes: a positive Mod-Matrix source is a MIDI CC#
(`source=1` = Mod Wheel); `dest=2` = Sample Select; `dest=6` = Pitch; `source=-12` = LFO1;
`source=-1` = none; amount `1000` = 100%; an unassigned slot's destination is `0` or
`-1234567`. The **full** destination and source enums (corpus-validated) live in
`exsparams.MOD_DESTINATIONS`
/ `MOD_SOURCES`, with helpers `mod_dest_name()` / `mod_src_name()`. Notably `dest=8` =
**Filter 1 Cutoff** (the single most common factory routing), `dest=2` = Sample Select,
`dest=6` = Pitch; sources `−12`=LFO 1, `−3`=Velocity, `−13`/`−14`=Env 1/2, positive = MIDI CC#.

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
