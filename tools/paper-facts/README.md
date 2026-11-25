# The facts of the paper

`vp-vnp/paper.pdf` is the only form of the paper in formal-math, and the posters' build uses the standard library
only, so the parts of the paper the posters read are extracted once, outside the build, into
`diagrams/src/paper-facts.json`. The build pins that file by its hash (`PAPER_FACTS_SHA256` in `diagrams/src/vp.py`)
and the PDF by its own (`PAPER_SHA256`), and `meta.json` here records both with the commit they were read at.

```sh
uv run --with pypdf==7.1.1 python tools/paper-facts/extract.py ../vp-np
```

What it reads, from the text pypdf 7.1.1 extracts:

| Key | From the paper | Read as |
|---|---|---|
| `table1` | Table 1, "Map of the proof" | 15 rows, A to O in order: what the section proves, the sections it uses, the case |
| `table3` | Table 3, "The Lean theorems that belong to the numbered statements" | 65 rows: kind, number, section, the Lean cell as printed, and its names; "lem_toolkit_a to _f" is spelled out as six names |
| `headers` | each statement's header in the text | the first line that starts with the statement's kind and number followed by `(` or `.`: its page, and the title in parentheses where there is one |
| `intro` | the numbered statements of Sections 1 and 2 | 6 headers of the form "Theorem 1.1 (main theorem; thm_allfields)." |
| `notes` | every "Formalization note." | 7 notes: the page, the note up to its first line that ends with a full stop, the last statement header and the last subsection heading before it, and the statements it names |
| `appendix_q` | the overview's passage on the printed proofs (p. 17); Appendix Q.3's list of what is off the route; Q's "Routes of proof", "Some steps exist only under names of the underlying library", and "Not in Lean" | quoted whole, with the statements they name; the routes as their 6 bullets |

It stops without writing if a row does not parse, Table 1's sections are out of order, a row of Table 3 sits under
the wrong section, or a statement has no header. Titles and quoted passages are normalized only where pypdf returns Mathematical
Alphanumeric Symbols (U+1D400 to U+1D7FF), or ℎ (U+210E), the italic h that block leaves out: those become
plain letters by NFKC. In a quoted passage, a word broken at a line end before a lower-case letter is
joined.

**Not checked:** that pypdf's text order matches the printed layout beyond these parses. On 2026.11.25 the rows
were read against pypdf's text of pages 17 and 67, not against the rendered pages; a reading against the printed
tables is still to be done (PLAN.md). When `FM_COMMIT` moves and the PDF changed, run the
script again, read the diff of `paper-facts.json` against the new PDF, then bump both hashes in `vp.py`.
