# exstools4

Python code for reading, writing, and exporting Logic Pro **Sampler / EXS24** (`.exs`) instrument files.

## Modules

- `exsfile.py` — read/write `.exs` instruments (`read_exsfile`, `write_exsfile`). The writer can
  round-trip a parsed instrument byte-for-byte by passing the original block data through.
- `exsclasses.py` — the instrument / zone / group / sample dataclasses and their (de)serialization.
- `exsparams.py`, `sampler_param_table.py` — the Sampler parameter set: ids, names, ranges, defaults.
- `consolidate.py` — replicate Logic's **Save with Audio → Consolidated** (a single monolithic `.caf`
  holding every sample, with the instrument's zones re-pointed at frame offsets). LPCM, ALAC, or AAC.
- `set_polyphony.py` — set an instrument's polyphony (max voices), including values above the UI cap.
- `samplesearch.py`, `samplepackmenu.py`, `akais9xx.py` — sample relinking, packing, and Akai import helpers.

## Set polyphony (max voices)

Polyphony is parameter id 5, a plain per-instrument voice count. The Sampler UI only lets you *pick*
values up to its dropdown maximum (≈99), but a larger stored value is accepted as-is — this is how
Logic's Studio Piano instruments ship at 256. `set_polyphony.py` writes the value with a 2-byte
overlay, leaving the rest of the file byte-identical:

```bash
python3 set_polyphony.py "Grand Piano.exs" 256
# -> writes "Grand Piano (256 voices).exs" next to the source
```

The field is a 16-bit integer (max 32767); 256 matches Logic's own Studio Piano.

### Two separate limits

The instrument's polyphony value is only a *per-instrument* voice budget. Sampler also has an internal
voice pool that is the real ceiling on simultaneous voices, and by default it tracks the same ≈99–100.
So **raising an instrument's polyphony alone is not enough** — past ≈100 voices you also have to enlarge
the pool, which Logic governs with a hidden preference, `EXSVoiceLimit`:

```bash
# quit Logic first; the value is read once when the first Sampler loads in a session
defaults write com.apple.logic10 EXSVoiceLimit -int 999
```

`EXSVoiceLimit` ranges 16–999 (values outside that are clamped; absent ≈ 99). With it raised, a
patched high-polyphony instrument can play well past 100 voices; without it, you stay near ≈100
regardless of the value you patch in. Either way the practical limit is your CPU.

## Consolidate to a single .caf

```bash
python3 consolidate.py "Instrument.exs" ./out_dir --codec lpcm   # lpcm (default) | alac | aac
```
