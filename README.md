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

Polyphony is parameter id 5, a plain voice count. The Sampler UI only lets you *pick* values up to its
dropdown maximum, but a larger stored value is played back as-is — this is how Logic's Studio Piano
instruments ship at 256 voices. `set_polyphony.py` writes the value with a 2-byte overlay, leaving the
rest of the file byte-identical:

```bash
python3 set_polyphony.py "Grand Piano.exs" 256
# -> writes "Grand Piano (256 voices).exs" next to the source
```

The field is a 16-bit integer (max 32767); 256 matches Logic's own Studio Piano. Very high counts are
still bounded by available CPU.

## Consolidate to a single .caf

```bash
python3 consolidate.py "Instrument.exs" ./out_dir --codec lpcm   # lpcm (default) | alac | aac
```
