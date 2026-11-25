# VP ≠ VNP proof posters

Generated SVG posters of *VP ≠ VNP over every field* and its Lean 4 formalization, the vp-vnp folder of
[anthropics/formal-math](https://github.com/anthropics/formal-math/tree/main/vp-vnp), read at one pinned commit
(`FM_COMMIT = 11b6c7e3c9` in `diagrams/src/vp.py`). The build fails when the sources no longer say what a poster
records.

The posters build no Lean. The posters read two things. The first is the Lean source as text: 323 files, 72920
lines. The second is three parts of the paper: Table 1, its map of the sections; Table 3, its list of the Lean
theorems for each numbered statement; and the statement headers. These are read from `paper.pdf` once, into
`diagrams/src/paper-facts.json`, which is pinned by its hash. The formal-math README says of the paper and the
formalization: "Both were written by AI models, and no human mathematician has checked the proof." These posters do
not check it either.

## Posters

Open them on their own and zoom in.

- [What is claimed](diagrams/R1-main-theorems-2026.11.25.svg): the five theorems Comparator checks, each with the
  numbered statement of the paper whose Lean theorem its proof names, the 13 definitions of `Statement.lean` they
  are stated with, and where the paper's introduction states each result.
- [The proof, section by section](diagrams/R2-sections-2026.11.25.svg): the paper's 15 appendix sections as cards,
  coloured by the case each serves (flat, contracting or both), and Table 1's 30 uses between them set against the
  uses the elaborated Lean shows: 23 in both, 7 only in Table 1, 9 only in the Lean.
- [The route to the main theorems](diagrams/R3-route-2026.11.25.svg): the 54 numbered statements that Solution's
  theorems reach, drawn as a graph of the uses the elaborated Lean shows, with the longest chain, 14 statements from
  Corollary M.4 through the contracting case down to Definition A.1. The 11 statements off the route are set against Appendix Q.3's list,
  which matches except for Definition A.1: the walk reaches it through its second Lean name,
  `def_spectral_congr`. Seven of Appendix Q's claims about the route are checked against the uses.
- Two traces, one chain of uses each, a card per statement in reading order:
  [the longest chain](diagrams/T1-trace-contracting-2026.11.25.svg), 14 statements through the contracting case,
  and [the longest chain through the flat case](diagrams/T2-trace-flat-2026.11.25.svg), 11 statements through
  Theorem E.11. The two meet at Theorem C.1.
- [The paper against the Lean](diagrams/F1-paper-lean-2026.11.25.svg): the 65 numbered statements of the appendix,
  row by row, each with its Lean theorems and their file and line, the label and the quotation of the paper in
  the first theorem's docstring, and the 124 uses between statements in the elaborated Lean.
- [Where the paper rests on the Lean](diagrams/F3-formalization-notes-2026.11.25.svg): the overview's four
  statements whose proofs only the Lean verifies, the paper's seven formalization notes, each placed in the text,
  and the Lean under each of the 64 statements that have a Lean theorem. By lines, the overview's four rank 1, 2,
  3 and 5.
- [Figure 1, checked](diagrams/F4-figure-1-2026.11.25.svg): the paper's own picture of the proof, transcribed
  box by box and arrow by arrow, with a verdict from the Lean uses for each of the 25 statements its arrows carry.
  15 are used where the figure says, 5 further down, 3 through statements the figure leaves out, and 2 are not
  seen.
- [Where the formal work is](diagrams/F5-library-2026.11.25.svg): the 25 directories of Nc, NS1 and Ov, which
  hold three quarters of the code, set against the sections whose statements reach them. 46338 of their 46392
  declaration lines (99.9%) lie under some numbered statement in the elaborated Lean. In 10 directories one section
  reaches at least 80%, for example Nc.Tow under H (trees) and Nc.Grp and Nc.Dl under J (cuts).
- [Where the Lean and the text differ](diagrams/F6-differences-2026.11.25.svg): every Lean name the paper
  prints (96; all declared but `native_decide`, a tactic no file uses), the 11 beyond Table 3, Appendix Q.3's
  universes set against the signatures (the same 6 statements), and Q.3's 15 listed differences, quoted.
- [The two vocabularies](diagrams/F7-vocabulary-2026.11.25.svg): Appendix P's 17 coined terms and Appendix Q.3's
  7 renamings, each word counted in the Lean's names and text. The Lean never writes packet, tally, node tensor or
  upper functional, and writes unit, bill, table and gauge instead.
- [The proof as literature](diagrams/F8-literature-2026.11.25.svg): the 134 references by decade, where each of
  the 185 citations stands, Section 1 to 3 or an appendix, and each entry linked to its paper: 132 linked, 120 of
  them by a DOI verified against its own record (`diagrams/src/papers.toml`).
- [The text against the Lean](diagrams/F9-text-lean-2026.11.25.svg): every use between statements as the source text
  shows it and as the elaborated Lean shows it, from an export of vp-vnp built at the pin. All 100 uses of the text
  reading are confirmed, of the same kind; the Lean shows 24 more, each through a helper outside the Paper library,
  which the text reading does not walk. A second Lean reading, from the compiled modules read by Lean itself, gives the
  same 124 uses. Every poster that draws uses reads the Lean.
- [The proof as code](diagrams/F2-modules-2026.11.25.svg): the seven Lean libraries, the imports between them, the 44
  files of the Paper library with the part of the paper each one's docstring names, and the 12 largest files.

What each poster checks is in [diagrams/README.md](diagrams/README.md). Which of a poster's words are quoted,
computed or its own is in [diagrams/TEXT.md](diagrams/TEXT.md), and how the paper's tables were read is in
[tools/paper-facts/README.md](tools/paper-facts/README.md). On a poster opened on its own (not in GitHub's file
viewer), a statement number, section, library, directory or reference key links to the poster that draws it, and a
Lean name, module, file or line links to formal-math at the pinned commit ([diagrams/README.md](diagrams/README.md),
Links).

## Building

```sh
uv run python diagrams/gen-diagrams.py        # all four; exits 1 with a NOTE when anchors moved: run it again
```

Standard library only, Python 3.12 or later. The source is the vp-vnp folder of a formal-math checkout at
`FM_COMMIT`. By default that is `../vp-np`; set `VP_VNP` to use another. CI
(`.github/workflows/posters.yml`, on every push to main and every pull request) checks formal-math out at the pin,
regenerates the posters and fails on any byte that differs, then runs the proof-posters plugin's
`check-expectations.py --strict`, `check-links.py` and `determinism.py` from riemann-diagrams at
`PROOF_POSTERS_COMMIT` (proof-posters 0.4.2). A daily run (`.github/workflows/sources.yml`) fails when formal-math's
main has commits after `FM_COMMIT` that touch vp-vnp, or when the pin is no longer on main; it only reports, and the
pin is moved by hand (proof-posters:moving-pins).

## Releases

A release is a signed version tag, pushed by the custodian; its workflow (`.github/workflows/release.yml`) checks the
posters at the tag and publishes every SVG with `SHA256SUMS` and `pins.json`, which names the formal-math commit and the
four pinned hashes, so that a poster can be cited by release (PLAN.md, Releases). The latest release is also served at
https://scottcochran.github.io/anthropic-vp-vnp/, where a poster opens in the browser.

## Licence

Code under Apache-2.0 (`LICENSE`), prose and posters under CC BY 4.0 (`LICENSE-DOCS`). The quotations of vp-vnp's
Lean source, README and paper stay under that folder's Apache-2.0 licence. `NOTICE` records the details.
