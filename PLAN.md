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
and, for R2, in dark (Chrome). Committed as 4f009f5; CI (posters, run 45571628046) regenerated all four at the
pin on Ubuntu with Python 3.12, byte-identical to the committed files.

Still open in Phase 1:

- Read `paper-facts.json` against the rendered Table 1 and Table 3, not only pypdf's text of them.
- Look at a link's framed target in a browser. Headless Chrome's screenshot of `F1…svg#K.3` came out blank.
- Look at R1, F1 and F2 in the dark theme.

## Phase 1b: the route, and where the paper rests on the Lean (2026.11.25)

R3 `route` and F3 `formalization-notes`. `paper-facts.json` gained the seven formalization notes and the passages
of the overview and Appendix Q that they check against (`tools/paper-facts/README.md`), and `vp.py` gained
`route` and `closure`.

Found while building R3: Appendix Q.3 says "the definitions" are off the route of Solution's theorems, but the walk
reaches Definition A.1 through `def_spectral_congr`, the second Lean name Table 3 gives it. No proof names
`def_spectral`. R3 records this as `ON_BY_SECOND` rather than widening the comparison. Every other row agrees
with Q.3, and all seven of Appendix Q's route claims that R3 checks hold.

Done (1b): all six posters build with no WARNING or ERROR. `check-expectations.py`: 6 modules, 30 expectations under 29
names, all literals. `determinism.py`: 7 files byte-identical over two seeds (one failure was fixed first: R3 had
iterated over a set). `check-links.py` passes. R3 and F3 looked at in light (rsvg-convert) and dark (Chrome).

## Phase 1c: two traces and Figure 1 (2026.11.25)

A fix to the reading first. Phase 1b counted a Lean name given to two statements (`Paper.scales_setting`, K.5 and
K.6) as neither one's own, which dropped the uses it makes of J.4. Now it is each one's own, and what it names of
the other co-owner is not counted. Re-recorded: F1 gains J.4 → K.5 and J.4 → K.6 (100 uses, 41 direct); R2's
"K uses J" is now borne out (23 in both, 7 only in Table 1); F3's K.5 and K.6 grow; R3's longest chain is now 14
statements, through the contracting case. The route itself and Q.3's comparison are unchanged.

Then T1 `trace-contracting`, T2 `trace-flat` and F4 `figure-1`. Figure 1 was read from p. 5 rendered with
PyMuPDF (outside the build, in the scratchpad), and its arrows transcribed into `d_f4_figure_1.py`. Of the 25
statements its arrows carry, 15 are used where the figure says, 5 further down (among them Theorem D.2, the case
split, used once by Theorem M.3), 3 through statements the figure leaves out (D.2 reaches C.1 through C.3), and 2
are not seen: Definition D.1, and Corollary E.2 on the contracting branch, which Appendix Q explains.

Done (1c): all nine posters build with no WARNING or ERROR. `check-expectations.py`: 9 modules, 37 expectations
under 34 names, all literals. `determinism.py`: 10 files byte-identical over two seeds. `check-links.py`: 1,032
links. T1 and F4 looked at in Chrome (dark).

## Phase 1d: the layer under Paper (2026.11.25)

F5 `library`: the 25 directories of Nc, NS1 and Ov against the sections, by the lines each section's own statements
reach (`vp.closure`). It is read from the text like the rest, and the reading is shakier here than in Paper, where
names are distinctive. So the poster measures what it misses: 42168 of 46392 declaration lines (91%) are reached by
name from some statement, least in Nc.Sort (61%) and Nc.Tape (63%). Phase 2's export would give exact uses.

Done (1d): ten posters, no WARNING or ERROR. `check-expectations.py`, `determinism.py` and `check-links.py`
pass (counts in the commit). F5 looked at in Chrome (dark).

## Phase 1e: the differences, the vocabularies, the literature (2026.11.25)

F6 `differences`, F7 `vocabulary`, F8 `literature`. The extractor gained the paper's printed Lean names, the rest
of Appendix Q.3, the reference list with its citations, and Appendix P, the last read with PyMuPDF 2.1 from
character positions because its three columns do not survive as text. The Lean reader gained each file's
`variable` binders, so that `vp.polymorphic` sees the field of Lemmas M.1 and N.2, which comes from a `variable`.

Found: all 96 Lean names the paper prints are declared but `native_decide`, which no file uses; Q.3's six
statements in any universe are exactly those whose Lean takes a type in any universe; the Lean never writes four
of the paper's words that Q.3 says it renames (packet, tally, node tensor, upper functional).

Open: pypdf loses the spaces of a few lines, which shows in some quotations (diagrams/TEXT.md); a reading of
those passages with PyMuPDF's positions, as the glossary is read, would fix it. Read `paper-facts.json` against the rendered pages, still open from
Phase 1.

## Phase 1f: the papers (2026.11.25)

`diagrams/src/papers.toml` links each of the 134 references (proof-posters:linking-papers, plugin 0.4.1): 132
linked, 2 not, each with a note (Ald84, a 1984 dissertation with no stable copy; OAI26, an unpublished manuscript).
How each was found is its `via`: Crossref 108, zbMATH 10, arXiv 6, the entry's own url 1, by hand 9. Every DOI was
verified against its own Crossref record (the five LIPIcs DOIs against DataCite's), and every link opened once.

Found along the way: the extractor had missed the two keys with no digits ([Lean], [Mathlib]), which had run into
the entries before them; the first searches matched a conference version or a book chapter where ten entries cite a
journal paper or a book (AW09, Bür00b, FPV13, GKKS14, Gro15, Hya79, KI04, SW14, KLS10, and Wil25 the other way),
which the year check alone would have let through. Each was set right by comparing the cited venue with the
record's, and its note says so.

## Phase 2: checking the uses against the Lean (planned)

Build vp-vnp at its toolchain (Lean 4.33.1, Mathlib `0df444a360e`), export it with lean4export, and derive a pinned
`src/lean-uses.json` (proof-posters:extracting-lean-deps). Then give each use on F1 and R2 a verdict, as
riemann-diagrams' F7 does. Until then, every use is labelled as read from the text.

## Releases

Not set up. There is no release workflow yet. When there is one, the classes are riemann-diagrams': MAJOR for a
change of what a poster is, MINOR for a poster added or removed or a change to `EXPECTED` or `CLAIMS`, and PATCH
otherwise.
