# The posters and what they check

Six posters, each a module `diagrams/src/d_<id>_<slug>.py` that reads the sources at build time, records what it
expects them to say as module-level literals, and fails the build when they differ, in either direction. R is a
reading at one level, F another frame. The generator is `diagrams/gen-diagrams.py`. Any line it prints starting
with WARNING or ERROR is a failure.

## Sources

| Source | Pinned by | Read by |
|---|---|---|
| The vp-vnp folder of anthropics/formal-math: every `.lean` file, `comparator.json`, `README.md` | `FM_COMMIT` in `src/vp.py`; the build fails on a checkout at another commit | `vp.load()` |
| `vp-vnp/paper.pdf` | `PAPER_SHA256`; the build fails if the file is present and hashes otherwise | `tools/paper-facts/extract.py`, outside the build |
| `src/paper-facts.json`: the paper's Table 1, Table 3, statement headers, and the statements of Sections 1 and 2 | `PAPER_FACTS_SHA256`, and `tools/paper-facts/meta.json`, which records the commit and both hashes | `vp.load()` |

How the Lean is read: as text, with comments and strings blanked. Full names come from `namespace`, `section` and
`end`, and a declaration runs from its keyword at the head of a line to the next command at the head of a line. A
statement **uses** another when the text of one of its Lean theorems names one of the other's. It may name it
directly, or through declarations of the Paper library that belong to no statement. A name Table 3 gives two
statements (`Paper.scales_setting`, given to K.5 and K.6) is neither one's own proof. Not seen: a use made
without the name (an instance, a `simp` set, a tactic that finds the lemma), or a name behind an `open`. A local
variable that shares a name with a theorem is counted as a use of it.

**What lies under a statement** (F3, `vp.closure`) is read the same way, across every library: the walk from the
statement's own theorems through every declaration their text names, stopping at the theorems of other statements. A
token names a declaration when it is the declaration's full name, or a dotted suffix of exactly one full name, in a
file the naming file imports, and has at least three characters.

## The posters

| Poster | What it shows | The build fails if any of these differ from what the module records |
|---|---|---|
| R1 `main-theorems` | the five theorems of `Solution.lean`, the 13 definitions of `Statement.lean`, the introduction's statements | the theorems `comparator.json` names, `Solution.lean` proves and `Challenge.lean` states (`CLAIMS`); the statement each is proved from (`CLAIMS`); the definitions (`DEFINITIONS`); Statement's and Challenge's imports; the introduction's statements and their rows of Table 3 (`INTRO`); the permitted axioms (`AXIOMS`); the README sentence it quotes (`QUOTED`) |
| R2 `sections` | the 15 sections of the appendix, and their uses by Table 1 and by the Lean text | each section's case (`CASES`); statements per section (`COUNTS`); Table 1's uses (`EXPECTED`); those the Lean bears out (`BORNE`); those only the Lean shows (`LEAN_ONLY`) |
| R3 `route` | the 54 statements on the route of Solution's theorems as a graph, the longest chain, the 11 off the route, Appendix Q's route claims | the uses drawn are F1's (`EXPECTED` of F1); the statements off the route (`OFF_ROUTE`); Q.3's list (`Q3_OFF`) and that it ends with "the definitions"; the one row of Q.3 the walk reaches, and the Lean name it reaches it by (`ON_BY_SECOND`); that the rest of the route agrees with Q.3; the longest chain (`CHAIN`); each claim of Appendix Q's "Routes of proof" quoted and its check (`ROUTE_CLAIMS`) |
| F1 `paper-lean` | the 65 numbered statements of Table 3, row by row | the count and kinds (`N_STATEMENTS`, `KINDS`); the rows with no Lean theorem (`NOT_FORMALIZED`); the rows whose docstring does not open with the paper's kind and label (`NO_DOC_LABEL`); names given to two rows (`SHARED`); every use between statements (`EXPECTED`) and which are direct (`DIRECT`) |
| F3 `formalization-notes` | the overview's statements left to the Lean, the 7 formalization notes, the Lean under every statement | the overview's four (`OVERVIEW`); each note's page, place, names and statement (`NOTES`); the declarations and lines by library under each of 64 statements (`WEIGHT`) |
| F2 `modules` | the seven libraries, the imports between them, the Paper library file by file, the largest files | files, lines and declarations per library (`LIBRARY`); imports between libraries (`IMPORTS`); the files outside Paper that import a Paper file (`UPWARD`); the statements each Paper file declares (`STATEMENTS_IN`); the 12 largest files (`TOP`) |

Also fails on any poster: a Table 3 name that no file declares, a declaration name used twice outside
`Challenge.lean`, a Lean file outside the seven libraries, a title wider than its card, a cell's word wider than
its cell, two texts that overlap, a character outside the embedded fonts, a link to an id no poster draws, and a link
out that is not at the pinned commit.

## Files

| File | What it is |
|---|---|
| `gen-diagrams.py` | the generator; `manifest.json` is the registry of every poster's anchors, for the links between posters |
| `src/vp.py` | the pins, the commit and hash checks, the Lean reader, the card |
| `src/lib.py`, `src/metrics.py`, `src/fonts/` | the drawing library and its fonts, from riemann-diagrams; `tools/build-fonts.py` rebuilds them |
| `src/paper-facts.json` | the facts of the paper, written by `tools/paper-facts/extract.py` |
| `src/d_*.py` | one module per poster |
