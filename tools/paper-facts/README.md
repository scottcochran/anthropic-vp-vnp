# The facts of the paper

`vp-vnp/paper.pdf` is the only form of the paper in formal-math, and the posters' build uses the standard library
only, so the parts of the paper the posters read are extracted once, outside the build, into
`diagrams/src/paper-facts.json`. The build pins that file by its hash (`PAPER_FACTS_SHA256` in `diagrams/src/vp.py`)
and the PDF by its own (`PAPER_SHA256`), and `meta.json` here records both with the commit they were read at.

```sh
uv run --with pypdf==7.1.1 --with pymupdf==2.1 python tools/paper-facts/extract.py ../vp-np
```

What it reads, from the text pypdf 7.1.1 extracts (and, for the glossary only, PyMuPDF 2.1's character positions):

| Key | From the paper | Read as |
|---|---|---|
| `table1` | Table 1, "Map of the proof" | 15 rows, A to O in order: what the section proves, the sections it uses, the case |
| `table3` | Table 3, "The Lean theorems that belong to the numbered statements" | 65 rows: kind, number, section, the Lean cell as printed, and its names; "lem_toolkit_a to _f" is spelled out as six names |
| `headers` | each statement's header in the text | the first line that starts with the statement's kind and number followed by `(` or `.`: its page, and the title in parentheses where there is one |
| `intro` | the numbered statements of Sections 1 and 2 | 6 headers of the form "Theorem 1.1 (main theorem; thm_allfields)." |
| `notes` | every "Formalization note." | 7 notes: the page, the note up to its first line that ends with a full stop, the last statement header and the last subsection heading before it, and the statements it names |
| `figure1` | Figure 1, "The structure of the proof" | the 22 Lean names its text prints, in pypdf's order, its caption, and that it ends at Theorem 1.1; not its arrows, which F4 transcribes |
| `paper_names` | every word with an underscore in the text | 96 Lean names, each with its pages |
| `q3` | Appendix Q.3: the renamings, the universes, the stronger forms, the differences | 7 renamings "X for Y" (the page of Table 3 that pypdf sets inside that sentence is cut out first), the statements of the universe and stronger-forms sentences (plural lists too: "Lemmas M.1 and N.2"), and 15 bullets of differences with the statements and Lean names each mentions |
| `references` | the reference list and every citation | 134 entries (a key is letters, two digits and perhaps a letter, as in Bür00b and vM07, or letters alone, as in Lean and Mathlib; the year is the printed one that ends in the key's digits, 1996/97 read as 1997, or for a key of letters the last printed) and 185 citations, each placed in Section 1, 2 or 3 or an appendix |
| `glossary` | Appendix P, by the columns of its table | 17 rows, read with PyMuPDF from the characters' positions: a space where two characters stand apart by more than a fifth of the font size, a superscript set on its line |
| `appendix_q` | the overview's passage on the printed proofs (p. 17); Appendix Q.3's list of what is off the route; Q's "Routes of proof", "Some steps exist only under names of the underlying library", and "Not in Lean" | quoted whole, with the statements they name; the routes as their 6 bullets |

It stops without writing if a row does not parse, Table 1's sections are out of order, a row of Table 3 sits under
the wrong section, or a statement has no header. Titles and quoted passages are normalized only where pypdf returns Mathematical
Alphanumeric Symbols (U+1D400 to U+1D7FF), or ℎ (U+210E), the italic h that block leaves out: those become
plain letters by NFKC. In a quoted passage, a word broken at a line end before a lower-case letter is
joined.

**Spacing.** pypdf loses the spaces of some lines ("Thepermanentiswrittenthereas"). Every passage the script quotes
is therefore respaced from PyMuPDF 2.1's reading of the same page: a space where two characters of a line stand
further apart than a fifth of the font size, a space before an operator that has one after it (d+ 1 -> d + 1),
running heads dropped. A passage is respaced only when its characters, spaces aside, stand in that reading exactly;
at FM_COMMIT that holds for 158 passages, and 13 are kept as pypdf reads them. The script prints both counts.

**Read against the rendered pages** on 2026.11.25, with PyMuPDF 2.1 at FM_COMMIT:

- by eye, Table 1 (p. 17, 15 rows), Table 3 (p. 67, 65 rows in two columns), the glossary of Appendix P (pp.
  65–66, 17 rows) and Figure 1 (p. 5, its 22 Lean names): every row agrees, but for the typography of formulas,
  whose sub- and superscripts are set inline (fk,ℓ for f_{k,ℓ}, vH for v^H, a stacked ?= as "? =");
- against PyMuPDF's own reading of the text, by script: the page and title of all 64 statement headers, the pages
  of the 7 formalization notes, the 6 statements of Sections 1 and 2, the 134 reference keys in order and each
  entry's year; and, by the respacing above, the characters of 158 quoted passages. No disagreement.

**Not checked:** the 14 passages that are not respaced, beyond reading them (each holds a formula the two readers
order differently, or runs across a page); and where pypdf and the print could both differ from what the author
meant. When `FM_COMMIT` moves and the PDF changed, run the
script again, read the diff of `paper-facts.json` against the new PDF, then bump both hashes in `vp.py`.
