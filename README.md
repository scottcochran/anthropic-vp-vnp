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
  uses the Lean text shows: 22 in both, 8 only in Table 1, 7 only in the Lean.
- [The paper against the Lean](diagrams/F1-paper-lean-2026.11.25.svg): the 65 numbered statements of the appendix,
  row by row, each with its Lean theorems and their file and line, the label and the quotation of the paper in
  the first theorem's docstring, and the 98 uses between statements read from the Lean text.
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
