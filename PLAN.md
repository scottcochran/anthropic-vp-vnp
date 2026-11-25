# Plan

## Decisions

- **Source.** The vp-vnp folder of anthropics/formal-math, pinned at `FM_COMMIT = 11b6c7e3c9` (2026.11.23, the merge
  of PR #51). There is no blueprint and no published export of the Lean, so both readings are new to this
  repository.
- **Uses between statements are read from the Lean text** (2026.11.25), not from a build. A statement uses another
  when its Lean proof names one of the other's theorems, directly or through Paper declarations that belong to no
  statement. Building and exporting the Lean (lake build, lean4export, the way formal-math's comparator check does)
  was considered and set aside for now: it means a Mathlib cache download and a long build. It is the way to check
  these uses later (Phase 2).
- **The paper's tables are extracted once** with pypdf into `diagrams/src/paper-facts.json`, which is pinned by its
  hash and by the hash of the PDF. The posters stay standard-library only.
- **No map set.** riemann-diagrams has one because the proof's source there is unlicensed. vp-vnp is Apache-2.0, so
  the posters quote it under that licence (NOTICE).
- **The light page** is riemann-diagrams' measured `#eeeeee`, not measured again for these posters.

## Phase 1: the first four posters (2026.11.25)

R1 `main-theorems`, R2 `sections`, F1 `paper-lean`, F2 `modules`. What each checks: `diagrams/README.md`.

Done: all four build with no WARNING or ERROR at `FM_COMMIT = 11b6c7e3c9`. The plugin's checks run from
`../riemann-diagrams/skills/` all pass. `check-expectations.py`: 4 modules, 22 expectations under 21 names, all
literals. `determinism.py`: 5 files byte-identical over `PYTHONHASHSEED` 0 and 1. `check-links.py`: 578 links, 261
within a poster, 154 to another poster's id, 163 to formal-math at the pin. Looked at in light (rsvg-convert)
and, for R2, in dark (Chrome). Not yet committed, and CI has not run.

Still open in Phase 1:

- Read `paper-facts.json` against the rendered Table 1 and Table 3, not only pypdf's text of them.
- Look at a link's framed target in a browser. Headless Chrome's screenshot of `F1…svg#K.3` came out blank.
- Look at R1, F1 and F2 in the dark theme.

## Phase 2: checking the uses against the Lean (planned)

Build vp-vnp at its toolchain (Lean 4.33.1, Mathlib `0df444a360e`), export it with lean4export, and derive a pinned
`src/lean-uses.json` (proof-posters:extracting-lean-deps). Then give each use on F1 and R2 a verdict, as
riemann-diagrams' F7 does. Until then, every use is labelled as read from the text.

## Releases

Not set up. There is no release workflow yet. When there is one, the classes are riemann-diagrams': MAJOR for a
change of what a poster is, MINOR for a poster added or removed or a change to `EXPECTED` or `CLAIMS`, and PATCH
otherwise.
