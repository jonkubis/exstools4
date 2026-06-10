"""Regression harness for the ConvertWithMoss backport (big-endian read support).

Usage:
    python3 tests/backport_check.py baseline   # capture current behavior -> baseline.json
    python3 tests/backport_check.py verify      # re-check + big-endian + round-trip

The harness reads a deterministic sample of real factory .exs files, fingerprints
the *semantic* parsed fields (not raw bytes), and compares runs so we can prove the
refactor leaves little-endian parsing byte-for-byte identical while newly supporting
big-endian (SOBT) and JBOS files.
"""
import sys, os, glob, json, hashlib, random, traceback
from dataclasses import fields, is_dataclass

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG)

import exsfile  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BASELINE = os.path.join(HERE, "baseline.json")
SAMPLE_SIZE = 250
SEED = 42

ROOTS = [
    "/Library/Application Support/Logic/Sampler Instruments",
    os.path.expanduser("~/Music/Audio Music Apps/Sampler Instruments"),
]

# Fields that are incidental (raw bytes / file positions) and must NOT be fingerprinted.
SKIP_FIELDS = {"data", "param_data", "exsfile_pos", "objects", "header", "pathname"}


def classify(path):
    try:
        with open(path, "rb") as fh:
            head = fh.read(20)
    except Exception:
        return None
    if len(head) < 20:
        return None
    return ("BIG" if head[0] == 0x00 else "LITTLE", bytes(head[16:20]))


def collect():
    files = set()
    for r in ROOTS:
        files.update(glob.glob(os.path.join(r, "**", "*.exs"), recursive=True))
    le, be, jbos = [], [], []
    for f in sorted(files):
        c = classify(f)
        if c is None:
            continue
        endian, magic = c
        if endian == "BIG":
            be.append(f)
        elif magic == b"JBOS":
            jbos.append(f)
        else:
            le.append(f)
    return le, be, jbos


def _fp_obj(obj):
    if is_dataclass(obj):
        out = {}
        for fld in fields(obj):
            if fld.name in SKIP_FIELDS:
                continue
            v = getattr(obj, fld.name)
            if isinstance(v, list):
                out[fld.name] = [_fp_obj(x) for x in v]
            elif isinstance(v, bytes):
                out[fld.name] = v.decode("latin-1")
            else:
                out[fld.name] = v
        return out
    if isinstance(obj, bytes):
        return obj.decode("latin-1")
    return obj


def fingerprint(inst):
    payload = {
        "name": inst.name,
        "zones": [_fp_obj(z) for z in inst.zones],
        "groups": [_fp_obj(g) for g in inst.groups],
        "samples": [_fp_obj(s) for s in inst.samples],
        "params": {str(k): v for k, v in sorted(inst.params.items())},
    }
    blob = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest(), {
        "name": inst.name,
        "n_zones": len(inst.zones),
        "n_groups": len(inst.groups),
        "n_samples": len(inst.samples),
        "n_params": len(inst.params),
    }


def sample_le(le):
    return random.Random(SEED).sample(le, min(SAMPLE_SIZE, len(le)))


def writer_hashes(inst):
    """sha256 of write_exsfile output via (a) full re-export and (b) full passthrough."""
    import tempfile
    out = {}
    for label, kw in (
        ("reexport", {}),
        ("passthrough", dict(original_zone_data=True, original_group_data=True,
                             original_sample_data=True, original_param_data=True)),
    ):
        with tempfile.NamedTemporaryFile(suffix=".exs", delete=False) as tf:
            tmp = tf.name
        try:
            exsfile.write_exsfile(inst, tmp, **kw)
            with open(tmp, "rb") as fh:
                out[label] = hashlib.sha256(fh.read()).hexdigest()
        except Exception as e:
            out[label] = f"ERR {type(e).__name__}: {e}"
        finally:
            os.unlink(tmp)
    return out


def run_baseline():
    le, be, jbos = collect()
    print(f"corpus: {len(le)} LE / {len(be)} BIG-endian / {len(jbos)} JBOS")
    chosen = sample_le(le)
    out = {}
    errors = 0
    for f in chosen:
        try:
            inst = exsfile.read_exsfile(f)
            fp, summary = fingerprint(inst)
            out[f] = {"fp": fp, **summary}
        except Exception as e:
            out[f] = {"error": f"{type(e).__name__}: {e}"}
            errors += 1
    # Writer byte-stability: hash output for a fixed small subset.
    wout = {}
    for f in chosen[:40]:
        try:
            inst = exsfile.read_exsfile(f)
            wout[f] = writer_hashes(inst)
        except Exception as e:
            wout[f] = {"error": f"{type(e).__name__}: {e}"}
    out["__writer__"] = wout

    with open(BASELINE, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"baseline: wrote {len(out) - 1} entries ({errors} errored) + "
          f"{len(wout)} writer hashes -> {BASELINE}")


def run_verify():
    with open(BASELINE) as fh:
        base = json.load(fh)
    writer_base = base.pop("__writer__", {})
    le, be, jbos = collect()

    # 1) LE parsing must be byte-for-byte identical to baseline.
    changed = 0
    newly_ok = 0
    for f, prev in base.items():
        try:
            inst = exsfile.read_exsfile(f)
            fp, _ = fingerprint(inst)
        except Exception as e:
            if "error" not in prev:
                print(f"  REGRESSION (now errors): {f}\n    {type(e).__name__}: {e}")
                changed += 1
            continue
        if "error" in prev:
            newly_ok += 1
            continue
        if fp != prev["fp"]:
            print(f"  REGRESSION (fingerprint changed): {f}")
            changed += 1
    print(f"[1] LE re-parse: {len(base)} files, {changed} regressions, {newly_ok} newly parseable")

    # 2) Big-endian + JBOS files must now parse without error.
    be_fail = 0
    for f in be:
        try:
            exsfile.read_exsfile(f)
        except Exception as e:
            be_fail += 1
            if be_fail <= 5:
                print(f"  BIG-endian FAIL: {f}\n    {type(e).__name__}: {e}")
    print(f"[2] BIG-endian: {len(be)} files, {be_fail} failed")

    jbos_fail = 0
    for f in jbos:
        try:
            exsfile.read_exsfile(f)
        except Exception as e:
            jbos_fail += 1
            if jbos_fail <= 5:
                print(f"  JBOS FAIL: {f}\n    {type(e).__name__}: {e}")
    print(f"[3] JBOS: {len(jbos)} files, {jbos_fail} failed")

    # 4) Pass-through round-trip (LE): read -> write replaying the original chunk
    #    bytes -> read must reproduce identical fields. (The default re-export is
    #    intentionally lossy -- that is what original_*_data pass-through is for --
    #    so this exercises the faithful path.)
    import tempfile
    rt_files = sample_le(le)[:80]
    rt_fail = 0
    for f in rt_files:
        try:
            inst = exsfile.read_exsfile(f)
            fp1, _ = fingerprint(inst)
            with tempfile.NamedTemporaryFile(suffix=".exs", delete=False) as tf:
                tmp = tf.name
            exsfile.write_exsfile(inst, tmp, original_zone_data=True, original_group_data=True,
                                  original_sample_data=True, original_param_data=True)
            inst2 = exsfile.read_exsfile(tmp)
            fp2, _ = fingerprint(inst2)
            os.unlink(tmp)
            if fp1 != fp2:
                rt_fail += 1
                if rt_fail <= 8:
                    print(f"  PASSTHROUGH drift: {os.path.basename(f)}")
        except Exception as e:
            rt_fail += 1
            if rt_fail <= 8:
                print(f"  PASSTHROUGH ERROR: {os.path.basename(f)}\n    {type(e).__name__}: {e}")
    print(f"[4] passthrough round-trip (LE): {len(rt_files)} files, {rt_fail} drifted/errored")

    # 6) Value sanity for big-endian + JBOS: a wrong byte order turns multi-byte
    #    numbers into garbage, so check that the strong signals stay plausible.
    def insane_values(inst):
        bad = []
        for s in inst.samples:
            if not (s.rate == 0 or 4000 <= s.rate <= 768000):
                bad.append(("rate", s.rate))
            if s.bitdepth not in (0, 8, 16, 24, 32):
                bad.append(("bitdepth", s.bitdepth))
            if s.channels not in (0, 1, 2):
                bad.append(("channels", s.channels))
        return bad

    for label, lst in (("BIG-endian", be), ("JBOS", jbos)):
        ok = bad = none = 0
        examples = []
        for f in lst:
            try:
                inst = exsfile.read_exsfile(f)
            except Exception:
                continue
            if inst is None:
                none += 1
                continue
            problems = insane_values(inst)
            if problems:
                bad += 1
                if len(examples) < 3:
                    examples.append((os.path.basename(f), problems[:3]))
            else:
                ok += 1
        print(f"[6] {label} value-sanity: {ok} sane, {bad} with garbage values, "
              f"{none} unsupported-layout(None)")
        for name, ex in examples:
            print(f"     {name}: {ex}")

    # 5) Writer byte-stability: output hashes must match the baseline exactly.
    w_changed = 0
    for f, prev in writer_base.items():
        if "error" in prev:
            continue
        try:
            inst = exsfile.read_exsfile(f)
            now = writer_hashes(inst)
        except Exception as e:
            print(f"  WRITER now errors: {os.path.basename(f)}: {e}")
            w_changed += 1
            continue
        for label in ("reexport", "passthrough"):
            if now.get(label) != prev.get(label):
                print(f"  WRITER drift [{label}]: {os.path.basename(f)}")
                w_changed += 1
    print(f"[5] writer byte-stability: {len(writer_base)} files, {w_changed} drifted")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    if mode == "baseline":
        run_baseline()
    elif mode == "verify":
        run_verify()
    else:
        print(__doc__)
        sys.exit(1)
