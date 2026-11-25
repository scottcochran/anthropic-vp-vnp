---
name: drawing-posters
description: "Adds a vp-vnp poster or reworks one, applying proof-posters:recording-expectations with this repository's library: the diagrams/src/d_<id>_<slug>.py module and its recorded expectations, the vp.py sources, the link registry, the build deterministic, a look in both themes, and every doc that lists posters or checks. Use when asked for a new poster, or to change a poster's layout, wording or cards. Not for moving FM_COMMIT or the paper hashes (proof-posters:moving-pins)."
---

# Drawing posters

The method is the plugin's **recording-expectations**: read every fact, record what you expect and compare it both
ways, write four kinds of sentence, keep the bytes deterministic, say what is not checked, and update the docs that
count. Read it first. This skill is how each step is done here. The shared rules are in `CLAUDE.md`.

## Before writing

- Read `PLAN.md`. A poster with no entry gets one first, saying what it shows and what it does not.
- Pick the id and slug. R is a reading at one level, F another frame, and the id is the next free number in its
  family. The file is `diagrams/src/d_<id lowercase>_<slug with underscores>.py`, and the output is
  `<ID>-<slug>-<DATE>.svg`.
- Start from the nearest module: cards in rows (`d_r1_main_theorems.py`), cards and a matrix (`d_r2_sections.py`),
  one long table with anchored rows (`d_f1_paper_lean.py`), tables and bars (`d_f2_modules.py`).

## The module

- Expose `ID`, `SLUG` and `build() -> Canvas`. The generator finds `d_*.py` on its own.
- Read everything through `vp.load()`: `.statements` (Table 3 joined to the Lean), `.uses`, `.decls`, `.modules`,
  `.facts`, `.challenge`. A fact it does not hold is added to `vp.py`, or to `paper-facts.json` through
  `tools/paper-facts/extract.py`, which means bumping `PAPER_FACTS_SHA256`.
- Record each expectation as a module-level literal under a name in `proof-posters.toml` `[build].expected_names`.
  Compare it with `vp.compare(what, expected, actual, reread)`, which fails both ways and names what to re-read.
- Cards are `vp.node`; table rows take `"anchor"` so that a link lands on them. An id set on a card or row is a
  link target. A code run whose text is an anchor of any poster becomes a link, through `manifest.json`. Add a
  poster that draws statements in full to `lib.HOME_ORDER`. A link out must be to formal-math at `FM_COMMIT`
  (`vp.lean_url`).
- Every poster carries `vp.NOT_BUILT` where a reader first meets a claim.

## Build and look

```sh
uv run python diagrams/gen-diagrams.py <ID>      # exits 1 with NOTE if anchors moved: run again
uv run python diagrams/gen-diagrams.py           # all, so that every poster's links follow
P=../riemann-diagrams/skills                     # or the installed plugin's skills directory
uv run python $P/recording-expectations/scripts/check-expectations.py
uv run python $P/moving-pins/scripts/determinism.py
uv run python $P/linking-posters/scripts/check-links.py
```

Any WARNING or ERROR is a failure. A character outside the fonts means adding it to `WANT` in
`tools/build-fonts.py` and rebuilding: `uv run --with fonttools==4.68.0 --with brotli==1.2.0 python
tools/build-fonts.py SRC_DIR`, with the four Noto files at the google/fonts commit the script names.

Look at it in both themes: `rsvg-convert -w 1600` for light, and Chrome on a copy with `data-theme="dark"` on the
root for dark.

## The docs a poster touches

In the same commit: `README.md` (the list), `diagrams/README.md` (the posters table and the checks),
`diagrams/TEXT.md` (any interpretation), `PLAN.md` (the phase's done note), and `proof-posters.toml` if a new name
is recorded.
