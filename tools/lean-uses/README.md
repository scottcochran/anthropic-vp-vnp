# The uses between statements, from the elaborated Lean (Phase 2)

`diagrams/src/lean-uses.json` holds the uses between the numbered statements of the paper as the elaborated Lean shows
them. It is made outside the build, once per move of `FM_COMMIT`, and the build pins it by its hash
(`LEAN_USES_SHA256` in `diagrams/src/vp.py`) and by `meta.json` here, which records the commit, the export's hash and
line count, the exporter and the Lean version. F9 sets it against the text reading of `vp.py`.

## What it takes

About 11 GB on a disk with room, outside this repository (the run of 2026.11.25 used
`/Volumes/2TB-APFS-CS/dev/sandbox/vp-vnp-lean-data`), and about 50 minutes, almost all of it the build of vp-vnp.

| Step | Time (2026.11.25, Apple silicon) | Size |
|---|---|---|
| Mathlib's compiled files, `lake exe cache get` | 1 min, 8690 files | most of the 11 GB |
| `lake build` of vp-vnp (9032 jobs, 323 modules of its own) | 47 min | 1 to 2 GB |
| lean4export of the 92 declarations and their closure | 50 s | 625 MB, 11,700,833 lines |
| `read_export.py` | 54 s, 2.6 GB of memory | the JSON file here |

## The commands

```sh
D=/Volumes/2TB-APFS-CS/dev/sandbox/vp-vnp-lean-data             # or another disk with room
git clone --filter=blob:none https://github.com/anthropics/formal-math.git $D/formal-math
git -C $D/formal-math checkout <FM_COMMIT, in full>
export MATHLIB_CACHE_DIR=$D/mathlib-cache XDG_CACHE_HOME=$D/xdg-cache   # keep the cache off the home disk
(cd $D/formal-math/vp-vnp && lake exe cache get && lake build)

# lean4export at the release for the project's toolchain (v4.33.1 has none: v4.33.0, 15f6055, built with
# v4.33.1, as formal-math's .github/scripts/comparator-check.sh does)
git clone https://github.com/leanprover/lean4export.git $D/tools/lean4export
git -C $D/tools/lean4export checkout 15f6055e299ad5b89345e533cc2192f4cc00f659
(cd $D/tools/lean4export && lake +leanprover/lean4:v4.33.1 build lean4export)

# the modules that hold Solution's theorems and Table 3's, and those declarations, from vp.py
uv run python - <<'PY' > $D/export-args.txt
import sys; sys.path.insert(0, "diagrams/src"); import vp
s = vp.load()
names = sorted({n for st in s.statements.values() for n in st["decls"]}
               | {n for n, d in s.decls.items() if d["module"] == "Solution" and d["kind"] == "theorem"})
print(" ".join(sorted({s.decls[n]["module"] for n in names})), "--", " ".join(names))
PY
(cd $D/formal-math/vp-vnp && lake env $D/tools/lean4export/.lake/build/bin/lean4export $(cat $D/export-args.txt)) \
    > $D/export/vp-vnp.ndjson

VP_VNP=$D/formal-math/vp-vnp uv run python tools/lean-uses/read_export.py $D/export/vp-vnp.ndjson
```

The reader prints the new `LEAN_USES_SHA256`; set it in `vp.py`, then regenerate. F9 fails wherever the uses moved:
re-read them against the export and record what it now says.

## The method

The export holds the 92 declarations named and every declaration they depend on, with their elaborated types and
values. `read_export.py` keeps, for each expression, its children and the constant it names, and for each numbered
statement walks breadth first from its Lean theorems through every declaration of vp-vnp that belongs to no
statement, stopping at another statement's theorem: that is a use, direct when one of the statement's own theorems
names it. A name Table 3 gives two statements is each one's own, and what it names of the other is not a use (as in
`vp.py`). A constant is vp-vnp's own when the source declares its name, when it extends such a name (`._proof_1`,
`.match_1`, `.eq_1`, a structure's constructor and fields), or when it is private to a module of vp-vnp; every other
constant is the library's and is not walked. For each use the file keeps one shortest chain of declarations.

**Not checked:** that the rule for vp-vnp's own constants is complete (a declaration vp-vnp makes under a library's
name is read as the library's); the export itself against a second reading of the compiled modules, as
proof-posters:extracting-lean-deps does with a build cache: here the second reading is the text reading of Phase 1,
and F9 sets the two against each other.
