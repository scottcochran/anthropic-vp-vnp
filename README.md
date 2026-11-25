# VP ≠ VNP proof posters

Generated SVG posters of *VP ≠ VNP over every field* and its Lean 4 formalization, the vp-vnp folder of
[anthropics/formal-math](https://github.com/anthropics/formal-math/tree/main/vp-vnp), read at one pinned commit
(`FM_COMMIT = 11b6c7e3c9` in `diagrams/src/vp.py`). The build fails when the sources no longer say what a poster
records.

Nothing here builds the Lean. The posters read two things. The first is the Lean source as text: 323 files, 72920
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
  uses the Lean text shows: 23 in both, 7 only in Table 1, 7 only in the Lean.
- [The route to the main theorems](diagrams/R3-route-2026.11.25.svg): the 54 numbered statements that Solution's
  theorems reach, drawn as a graph of the uses the Lean text shows, with the longest chain, 14 statements from
  Corollary M.4 through the contracting case down to Definition A.1. The 11 statements off the route are set against Appendix Q.3's list,
  which matches except for Definition A.1: the walk reaches it through its second Lean name,
  `def_spectral_congr`. Seven of Appendix Q's claims about the route are checked against the uses.
- Two traces, one chain of uses each, a card per statement in reading order:
  [the longest chain](diagrams/T1-trace-contracting-2026.11.25.svg), 14 statements through the contracting case,
  and [the longest chain through the flat case](diagrams/T2-trace-flat-2026.11.25.svg), 11 statements through
  Theorem E.11. The two meet at Theorem C.1.
- [The paper against the Lean](diagrams/F1-paper-lean-2026.11.25.svg): the 65 numbered statements of the appendix,
  row by row, each with its Lean theorems and their file and line, the label and the quotation of the paper in
  the first theorem's docstring, and the 100 uses between statements read from the Lean text.
- [Where the paper rests on the Lean](diagrams/F3-formalization-notes-2026.11.25.svg): the overview's four
  statements whose proofs only the Lean verifies, the paper's seven formalization notes, each placed in the text,
  and the Lean under each of the 64 statements that have a Lean theorem. By lines, the overview's four rank 1, 2,
  4 and 5.
- [Figure 1, checked](diagrams/F4-figure-1-2026.11.25.svg): the paper's own picture of the proof, transcribed
  box by box and arrow by arrow, with a verdict from the Lean uses for each of the 25 statements its arrows carry.
  15 are used where the figure says, 5 further down, 3 through statements the figure leaves out, and 2 are not
  seen.
- [The proof as code](diagrams/F2-modules-2026.11.25.svg): the seven Lean libraries, the imports between them, the 44
  files of the Paper library with the part of the paper each one's docstring names, and the 12 largest files.

What each poster checks is in [diagrams/README.md](diagrams/README.md). Which of a poster's words are quoted,
computed or its own is in [diagrams/TEXT.md](diagrams/TEXT.md), and how the paper's tables were read is in
[tools/paper-facts/README.md](tools/paper-facts/README.md). On a poster opened on its own, a statement number
links to its row on F1, and a Lean name, file or line links to formal-math at the pinned commit.

## Building

```sh
uv run python diagrams/gen-diagrams.py        # all four; exits 1 with a NOTE when anchors moved: run it again
```

Standard library only, Python 3.12 or later. The source is the vp-vnp folder of a formal-math checkout at
`FM_COMMIT`. By default that is `../vp-np`; set `VP_VNP` to use another. CI
(`.github/workflows/posters.yml`) checks formal-math out at the pin, regenerates the posters and fails on any byte
that differs.

## Licence

Code under Apache-2.0 (`LICENSE`), prose and posters under CC BY 4.0 (`LICENSE-DOCS`). The quotations of vp-vnp's
Lean source, README and paper stay under that folder's Apache-2.0 licence. `NOTICE` records the details.
