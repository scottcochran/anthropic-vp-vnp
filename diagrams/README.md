# The posters and what they check

Fifteen posters, each a module `diagrams/src/d_<id>_<slug>.py` that reads the sources at build time, records what it
expects them to say as module-level literals, and fails the build when they differ, in either direction. R is a
reading at one level, T a trace, F another frame. The generator is `diagrams/gen-diagrams.py`. Any line it prints starting
with WARNING or ERROR is a failure.

## Sources

| Source | Pinned by | Read by |
|---|---|---|
| The vp-vnp folder of anthropics/formal-math: every `.lean` file, `comparator.json`, `README.md` | `FM_COMMIT` in `src/vp.py`; the build fails on a checkout at another commit | `vp.load()` |
| `vp-vnp/paper.pdf` | `PAPER_SHA256`; the build fails if the file is present and hashes otherwise | `tools/paper-facts/extract.py`, outside the build |
| `src/paper-facts.json`: the paper's Table 1, Table 3, statement headers, and the statements of Sections 1 and 2 | `PAPER_FACTS_SHA256`, and `tools/paper-facts/meta.json`, which records the commit and both hashes | `vp.load()` |
| `src/papers.toml`: the paper behind each reference | this repository's own data, checked both ways against the references | `vp.load()`, F8 |
| `src/lean-uses.json`: the uses between statements in the elaborated Lean, from an export of vp-vnp built at the pin | `LEAN_USES_SHA256`, and `tools/lean-uses/meta.json`, which records the commit and the export's hash | `vp.load()`, F9 |
| `src/lean-modules.json`: the same uses read from the compiled modules by Lean itself, the second Lean reading | `LEAN_MODULES_SHA256`, and `tools/lean-uses/meta-modules.json` | `vp.load()`, F9 |

Which reading a poster draws: every poster that draws uses between statements, or the Lean under one (F1, F3, F4,
F5, R2, R3, T1, T2), reads the elaborated Lean (`src/lean-uses.json`, Phase 2: an export of vp-vnp built once at the
pin, read by `tools/lean-uses/read_export.py`). The text reading below is Phase 1's; F9 sets the two against each
other, and it is still how vp.py finds the source's declarations, files and lines.

How the Lean is read as text: comments and strings blanked, full names come from `namespace`, `section` and
`end`, and a declaration runs from its keyword at the head of a line to the next command at the head of a line. A
statement **uses** another when the text of one of its Lean theorems names one of the other's. It may name it
directly, or through declarations of the Paper library that belong to no statement. A name Table 3 gives two
statements (`Paper.scales_setting`, given to K.5 and K.6) is each one's own, but what it names of the other
co-owner is not counted as a use: it states the two together, in J.4's setting. Not seen: a use made
without the name (an instance, a `simp` set, a tactic that finds the lemma), or a name behind an `open`. A local
variable that shares a name with a theorem is counted as a use of it.

**What lies under a statement**, in the text reading (`vp.closure`, which no poster draws now), is read the same
way, across every library: the walk from the
statement's own theorems through every declaration their text names, stopping at the theorems of other statements. A
token names a declaration when it is the declaration's full name, or a dotted suffix of exactly one full name, in a
file the naming file imports, and has at least three characters.

## The posters

| Poster | What it shows | The build fails if any of these differ from what the module records |
|---|---|---|
| R1 `main-theorems` | the five theorems of `Solution.lean`, the 13 definitions of `Statement.lean`, the introduction's statements | the theorems `comparator.json` names, `Solution.lean` proves and `Challenge.lean` states (`CLAIMS`); the statement each is proved from (`CLAIMS`); the definitions (`DEFINITIONS`); Statement's and Challenge's imports; the introduction's statements and their rows of Table 3 (`INTRO`); the permitted axioms (`AXIOMS`); the README sentence it quotes (`QUOTED`) |
| R2 `sections` | the 15 sections of the appendix, and their uses by Table 1 and by the elaborated Lean | each section's case (`CASES`); statements per section (`COUNTS`); Table 1's uses (`EXPECTED`); those the Lean bears out (`BORNE`); those only the Lean shows (`LEAN_ONLY`) |
| R3 `route` | the 54 statements on the route of Solution's theorems as a graph, the longest chain, the 11 off the route, Appendix Q's route claims | the uses drawn are F1's (`EXPECTED` of F1); the statements off the route (`OFF_ROUTE`); Q.3's list (`Q3_OFF`) and that it ends with "the definitions"; the one row of Q.3 the walk reaches, and the Lean name it reaches it by (`ON_BY_SECOND`); that the rest of the route agrees with Q.3; the longest chain (`CHAIN`); each claim of Appendix Q's "Routes of proof" quoted and its check (`ROUTE_CLAIMS`) |
| T1 `trace-contracting` | the longest chain of uses, 14 statements, one card each | the chain (`CHAIN`), which must be R3's; that each step uses the next and the last uses nothing; that below L.1 it runs through the contracting sections, then C and A |
| T2 `trace-flat` | the longest chain through Theorem E.11, 11 statements | the chain (`CHAIN`); that each step uses the next; that below E.11 it is the longest; that it first meets T1's at C.1 |
| F1 `paper-lean` | the 65 numbered statements of Table 3, row by row | the count and kinds (`N_STATEMENTS`, `KINDS`); the rows with no Lean theorem (`NOT_FORMALIZED`); the rows whose docstring does not open with the paper's kind and label (`NO_DOC_LABEL`); names given to two rows (`SHARED`); every use between statements (`EXPECTED`) and which are direct (`DIRECT`) |
| F3 `formalization-notes` | the overview's statements left to the Lean, the 7 formalization notes, the Lean under every statement | the overview's four (`OVERVIEW`); each note's page, place, names and statement (`NOTES`); the declarations and lines by library under each of 64 statements (`WEIGHT`) |
| F4 `figure-1` | Figure 1 of the paper, transcribed, each arrow coloured by a verdict from the uses | the Lean names the figure prints (`FIGURE_NAMES`), which the transcription (`BOXES`, `ARROWS`) must use exactly; the row of Table 3 that is its Theorem 1.1 (`THEOREM`); the verdict on every statement an arrow carries (`VERDICTS`) |
| F5 `library` | the 25 directories of Nc, NS1 and Ov against the 14 sections whose statements reach them | files, lines and declaration lines per directory (`DIRS`); the lines each section's statements reach in each directory (`MATRIX`); the lines of each directory some statement reaches (`REACHED`) |
| F6 `differences` | every Lean name the paper prints, the universes, Appendix Q.3's differences | the count of printed names (`N_PAPER_NAMES`); those no file declares (`NOT_DECLARED`), and that no file uses them; those beyond Table 3 and their declarations (`BEYOND_TABLE3`); the universes of Q.3 and of the signatures (`UNIVERSES`); the stronger forms (`STRONGER`); each bullet's statements and Lean names (`DIFFERENCES`), every name declared |
| F7 `vocabulary` | the glossary and the renamings, each word counted in the Lean | the glossary's terms and places (`GLOSSARY`); the renamings (`RENAMES`); each word's count in declaration names (`IN_NAMES`) and in the source text (`IN_TEXT`) |
| F8 `literature` | the references by decade, where each is cited, each linked to its paper | the number of references and citations (`N_REFS`, `N_CITATIONS`); where each reference is cited (`CITED`); that every reference has an entry in `src/papers.toml` and every entry names a reference (with `vp.load`), each with a url or a note saying why not |
| F9 `text-lean` | every use between statements in the text reading and in the Lean reading (`src/lean-uses.json`) | the export's counts (`LEAN_COUNTS`); the uses only the text shows (`TEXT_ONLY`, none) and those the two give different kinds (`KIND_DIFFERS`, none); the uses only the Lean shows (`EXPORT_ONLY`) and the helper outside Paper behind each (`OUTSIDE`); the uses between sections the Lean adds (`SECTIONS_ADDED`); the second Lean reading's counts (`MODULES_COUNTS`), that the two Lean readings give the same uses (`READINGS_DIFFER`, none), the export rule's false and missed constants (`RULE_FALSE`, `RULE_MISSED`), and where they find different declarations under a statement (`UNDER_DIFFERS`) |
| F2 `modules` | the seven libraries, the imports between them, counted and then file by file, the Paper library file by file, the largest files | files, lines and declarations per library (`LIBRARY`); imports between libraries (`IMPORTS`), and the 126 import lines between them file by file (`ACROSS`); the files outside Paper that import a Paper file (`UPWARD`); the statements each Paper file declares (`STATEMENTS_IN`); the 12 largest files (`TOP`) |
| F10 `files` | every one of the 323 Lean files, by library and by F5's directories: its lines, its declarations, each linked to its line at the pin, and the files it imports and is imported by; a header row per library and directory, which F2's and F5's counts open | the files, lines and declarations of each library and each directory (`GROUPS`); not each file's, so a declaration renamed or replaced within a directory is not caught |

Also fails on any poster: a Table 3 name that no file declares, a declaration name used twice outside
`Challenge.lean`, a Lean file outside the seven libraries, a title wider than its card, a cell's word wider than
its cell, two texts that overlap, a character outside the embedded fonts, a link to an id no poster draws, and a link
out that is not at the pinned commit.

## Links

The posters link to each other and to formal-math at `FM_COMMIT`. `Canvas.link()` (`src/lib.py`) makes every link
after the layout, so a link adds nothing to the measured text and moves nothing. A name links to where the set, or
the source, draws it:

| The text names | It opens |
|---|---|
| a statement number (`K.3`), or a display in parentheses (`(F.1)`) | its card on the same poster, else its row on F1; a display only where F1 has a row for it, so `(B.2)` stays text |
| a section (`Section K`, `Sections C and A`, `Appendix O`), or an appendix in F8's Cited in | its card on R2 |
| a directory (`Nc.Price`) | its card on F5 |
| a library, where a poster marks it (F2, F3, F5, F9, F10) | its card on F2 |
| a count of a library's files, lines and declarations on F2, or of a directory's on F5 | its header row on F10, above the files it counts |
| an import count on F2 (`Imports Nc (50)`, and the cells of its import table) | the import lines it counts, in F2's band 3; within one library, its files on F10 |
| a module (`Nc.Price.Cross`), in code or in plain text | its row on F10 |
| a reference's key (`Val79`) | its row on F8 |
| one of Solution's theorems or Statement's definitions, by its full name or, in code, by its last part | its card on R1 |
| another poster by its id, where a poster marks it (`R3 checks that sentence`) | that poster's title |
| a Lean declaration, by its full name, or by a short name that one declaration has and that is four letters or more, in code or as the paper prints one (a word with an underscore) | its line in formal-math at the pin |
| a file of vp-vnp by its path (`Paper/Tree.lean`), or a `file:line` | the file, or the line, at the pin |

A name stays text inside the card or row it would open, inside a Lean panel (which quotes code), and wherever it does
not resolve. A link to a poster is made only to an id the committed `manifest.json` lists, which the generator writes
with every poster's anchors; when a run moves any poster's anchors, it updates the manifest, prints a NOTE and exits
1, and the second run makes the links follow. A link to formal-math is made only to a declaration or file read at the
pin, and to a line that file has. `check-links.py` (proof-posters:linking-posters) checks that every link lands; at
2026.11.25 it counts 9,075 links: 1,465 to another poster, 1,797 within a poster, 5,681 to formal-math at the pin and
132 to the papers of F8. That count is written here by hand.

A link's target is framed when it opens (CSS `:target`): a card by its halo, a table row by its own background, and
without the pulse under reduced motion. This works wherever a browser opens the SVG as a document (the Pages site, a
release asset, a file), not in GitHub's file viewer, which shows an SVG as an image, without its links.

Not checked: that a short name in code is the declaration and not a local of the same name (hence only names of four
letters or more that one declaration has); that the framing works in Firefox and Safari (measured in Chrome).

## Files

| File | What it is |
|---|---|
| `gen-diagrams.py` | the generator; `manifest.json` is the registry of every poster's anchors, for the links between posters |
| `src/vp.py` | the pins, the commit and hash checks, the Lean reader, the card |
| `src/lib.py`, `src/metrics.py`, `src/fonts/` | the drawing library and its fonts, from riemann-diagrams; `tools/build-fonts.py` rebuilds them |
| `src/paper-facts.json` | the facts of the paper, written by `tools/paper-facts/extract.py` |
| `src/lean-uses.json` | the uses between statements in the elaborated Lean, written by `tools/lean-uses/read_export.py` (Phase 2) |
| `src/papers.toml` | the paper behind each reference, with how it was found (proof-posters:linking-papers) |
| `src/d_*.py` | one module per poster |
