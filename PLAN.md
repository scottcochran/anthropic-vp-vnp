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
- **CI runs the method's checks** (2026.11.25). `posters.yml` runs, after the byte comparison, proof-posters'
  `check-expectations.py --strict`, `check-links.py` and `determinism.py`, from riemann-diagrams at
  `PROOF_POSTERS_COMMIT = 37fecad` (proof-posters 0.4.2), so that a pull request and a release tag are held to what
  each phase's done note records by hand. The plugin pin is moved deliberately, like `FM_COMMIT`. `sources.yml`
  checks daily whether formal-math's main has commits after `FM_COMMIT` that touch vp-vnp, or has lost the pin; it
  only reports, since every file is read at the pin and nothing drawn changes until the pin moves.
- **A merge into main needs the posters check** (2026.11.25). The ruleset "main: posters must pass" (id 28073225)
  requires `regenerate`, the posters job, from GitHub Actions; a branch need not be up to date with main. The admin
  role bypasses it, so the custodian still pushes to main directly, and posters runs on that push. It names the job:
  renaming `regenerate` means changing the ruleset with it.

## Phase 1: the first four posters (2026.11.25)

R1 `main-theorems`, R2 `sections`, F1 `paper-lean`, F2 `modules`. What each checks: `diagrams/README.md`.

Done: all four build with no WARNING or ERROR at `FM_COMMIT = 11b6c7e3c9`. The plugin's checks run from
`../riemann-diagrams/skills/` all pass. `check-expectations.py`: 4 modules, 22 expectations under 21 names, all
literals. `determinism.py`: 5 files byte-identical over `PYTHONHASHSEED` 0 and 1. `check-links.py`: 578 links, 261
within a poster, 154 to another poster's id, 163 to formal-math at the pin. Looked at in light (rsvg-convert)
and, for R2, in dark (Chrome). Committed as 4f009f5; CI (posters, run 45571628046) regenerated all four at the
pin on Ubuntu with Python 3.12, byte-identical to the committed files.

Still open in Phase 1: nothing (the framed target was looked at in Phase 1i). Headless Chrome's screenshot of `F1…svg#K.3` came out blank.
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

(Both items once open here are done: the quotations that lost their spaces in Phase 1g, and the reading of
`paper-facts.json` against the rendered pages in Phase 1h.)

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

## Phase 1g: the spacing of the quotations (2026.11.25)

pypdf loses the spaces of some lines of the PDF. The extractor now respaces every quoted passage from PyMuPDF's
reading of the page, keeping pypdf's characters and requiring them to match exactly (158 passages respaced, 13 kept).
At FM_COMMIT this changes 7 passages: Q.3's second difference ("Thepermanentiswrittenthereas"), the reference Vin91
("Countingauxiliarypushdownautomata…"), and the spacing around commas and full stops in five others. No recorded
expectation moved.

## Phase 1h: paper-facts.json against the rendered pages (2026.11.25)

Read by eye against the pages PyMuPDF 2.1 renders: Table 1, Table 3, the glossary and Figure 1, every row agreeing
but for the typography of formulas (sub- and superscripts inline). Checked by script against PyMuPDF's own reading:
the 64 statement headers (page and title), the 7 notes, the 6 statements of Sections 1 and 2, the 134 reference keys
and years. No disagreement; nothing in `paper-facts.json` changed. tools/paper-facts/README.md lists what was read.

## Phase 1i: a link's target, framed, in a browser (2026.11.25)

Looked at in Chrome, driven by Playwright (`channel="chrome"`, outside the build), and measured, since a headless
capture of a scrolled poster is not to be trusted (proof-posters:linking-posters, target-highlighting.md). A card
opened at its id (R2#sec-K) shows its halo and lands 92 px below the top; a link from R2 to F1#K.3 opens F1 at the
row. The rows of a table were not framed well: their halo was drawn first and the row's own background and the next
row covered it. They now follow the plugin's form for a row, a group `rd-row` whose background, its first child, the
style frames (3 px, amber), as `[links].frame_classes` now lists. Both themes; with reduced motion the frame stays
and does not pulse.

## Phase 2: checking the uses against the Lean (2026.11.25)

vp-vnp built once at `FM_COMMIT` with its toolchain (Lean 4.33.1, Mathlib `0df444a360e`) in a fresh clone outside the
repository (11 GB, 47 minutes), Solution's theorems and Table 3's exported with their dependency closure by
lean4export 3.1.0 (625 MB), and the uses between statements read from the elaborated terms into
`diagrams/src/lean-uses.json`, pinned by `LEAN_USES_SHA256` (tools/lean-uses/README.md).

Found: the export holds 63,346 declarations, 9,995 of them vp-vnp's. All 100 uses of the text reading are in it,
each of the same kind (41 direct); none is only in the text. It shows 24 more, all through helpers, and on the
shortest chain of each lies a declaration outside the Paper library (Nc.Price, Ov.Spec, Nc.Flag, NS1), which the text
reading does not walk by design. At the level of sections it adds A→D and F→H; the 7 uses that only Table 1 lists
are not made by the elaborated Lean either. F9 draws this.

Then F1, R2, R3 and the traces were switched to the Lean reading: F1 records 124 uses (41 direct), R2 9 uses between
sections that only the Lean shows (A→D and F→H added). R3's route, its longest chain, Appendix Q.3's comparison (the
exception of Definition A.1, reached only through `def_spectral_congr`, holds in the export too: no walk arrives at
`def_spectral`) and the seven route claims hold unchanged, and so do T1 and T2. src/lean-uses.json gained, for each
statement, the Paper declarations its walk passes and the used statements' names it arrives at, which R3's checks
read.

Then F3, F4 and F5 too. src/lean-uses.json gained, for each statement, every source declaration under its Lean
theorems (a compiler-made or private constant counted as the one it belongs to). F4's 25 verdicts hold unchanged.
F3's weights grow a little (J.3: 1,076 declarations, against 1,014 read from the text), and the overview's four now
rank 1, 2, 3 and 5. F5's coverage was the text reading's blind spot: 46,338 of 46,392 declaration lines (99.9%) lie
under some statement in the elaborated Lean, against 42,168 (91%) reached by name; only 54 lines are under none,
most in Nc.Rate. Every poster that draws uses now reads the Lean; only F9 draws the text reading, to compare.

Then the second Lean reading proof-posters:extracting-lean-deps asks for: the compiled modules, read by Lean itself
(tools/lean-uses/ReadModules.lean, `lake env lean --run`, 2 minutes) into `diagrams/src/lean-modules.json`, pinned by
`LEAN_MODULES_SHA256`. It gives the same 124 uses as the export, each of the same kind. It decides what is vp-vnp's by
the defining module, which checks the export reader's rule by name: that rule takes nothing a library defines, and
misses 480 compiler-made constants (derived instances, equation lemmas), through which the modules find up to 7
more declarations under 6 statements (A.5, A.6, A.7, G.2, L.3, M.4). F9 records all of it; F3 and F5 draw the
export's counts. Nothing is open in Phase 2.

## Phase 3: a link wherever a mapping is (2026.11.25)

Before it, every link between posters opened a statement or a Lean name, nearly all on F1; nothing linked to the 215
anchors of R2's sections, F2's libraries, F3's notes, F4's boxes, F5's directories, F6's differences or F8's
references, and F5 and F7 had no links. `Canvas.link()` now makes every link in one pass after the layout, by the
rules `diagrams/README.md` (Links) lists: in code and in plain text, to a card or row of the set through the manifest,
and to formal-math at the pin through the declarations, modules and files `vp.load` reads. A library and another
poster's id are linked only where a poster marks them (`vp.library`, `vp.poster`), since "Paper" and "T1" are also
words and a variable.

Done: 869 links added and none changed or removed: `check-links.py` counts 2,615 (1,746 before): 1,075 to another
poster (742), 635 within a poster (497), 773 to formal-math at the pin (375), 132 to papers (132). No anchor moved,
no WARNING, a second run changes nothing; `check-expectations.py --strict` and `determinism.py` pass. In Chrome
(Playwright, outside the build): every one of the 2,615 links is the element at the centre of its own text, so none
is covered; one link of each new kind, clicked there, opened its target framed, 91 to 92 px below the top of the window
(R2 `sec-H` and `sec-K`, F2 `lib-Nc`, F5 `dir-Nc-Price`, F1 `F.1-display`, R1 `Statement.MainTheorem`; F8 `ref-Val79`
at 373 px, its row too near the end of the page to scroll higher), and R3's title for a poster's id. No glyph is added, so the drawn text is unchanged: a
PATCH (Releases).

Left as text, with no target: F1's LaTeX labels (`def:spectral`); the paper's Sections 1 to 3, which no poster draws
as a card; Appendix Q.3 and the formalization notes, which no poster names by a form a rule could read; a name inside
its own card or row; names inside the Lean panels, which quote code.

## Releases

A release is a version tag, `vMAJOR.MINOR.PATCH`, annotated and signed, on `main`, pushed by the custodian
(scottcochran) and never moved, re-pointed, deleted or re-created; a release found wrong gets a successor. On the tag,
`.github/workflows/release.yml` runs the posters check, writes `pins.json` (the formal-math commit, the four pinned
hashes, the run) and `SHA256SUMS`, and publishes every poster's SVG with notes from `tools/release-notes.py`
(proof-posters:cutting-releases). Each release is then published by `.github/workflows/pages.yml` to the Pages site,
https://scottcochran.github.io/anthropic-vp-vnp/, which serves one release at a time, checked against its
`SHA256SUMS`. The site is public, though the repository is private.

| Part | When it changes | What a reader of a cited poster has to do |
|---|---|---|
| MAJOR | The checks change: what a poster is verified against (a kind of check added, removed or redefined), or the source of the uses is replaced | Re-read every poster |
| MINOR | `FM_COMMIT` moves, or a poster is added or removed, or a recorded `EXPECTED` or `CLAIMS` changes | Re-read the posters the tag message names |
| PATCH | Layout, wording or library; no pin moves and every recorded list is unchanged | Nothing: the same statements and uses, drawn again |

Before 1.0 a MAJOR change may go out as MINOR, and its tag message then says what is checked differently. The
date in the posters' file names changes with every regeneration, and is not a move by itself.

Done, v0.1.0 (2026.11.25): the first release, signed and pushed by the custodian on c23e2d0. Release run
45605568786 passed (tag, check, release); it published 16 assets, the 14 posters, `pins.json` and `SHA256SUMS`.
`verify-release.py v0.1.0`: the 14 posters match the tree at the tag by their checksums, and `pins.json` names the
tag (formal-math 11b6c7e3c927, Python 3.12 in the run). Published to the Pages site afterwards, by pages.yml run by
hand from main at 1723c26 (run 45606514259): the build checked every file against the release's `SHA256SUMS`, and the
deploy confirmed the site serves v0.1.0; `verify-release.py v0.1.0` then passed with the site check too.

