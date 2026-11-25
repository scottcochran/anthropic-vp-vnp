# What on a poster is quoted, computed or its own

Every sentence on a poster is one of four kinds (proof-posters:recording-expectations, section 3), and F4 adds a
fifth, a transcription.

1. **Quoted.** Lean code in a panel, set in the code face, from the file the card's footer links to at the pinned
   commit. Words in italics on a card: the Lean files' own docstrings (R1), Table 1's "what is proved" (R2's
   cards). Words in quotation marks in a table: the paper's words as a docstring quotes them (F1), a file's module
   docstring (F2), Table 1's text (F1's section rows). The statement titles on F1 and R1 are the paper's own headers,
   read by `tools/paper-facts/extract.py`, with the paper's math italic letters made plain (𝑈𝑛 is written Un).
2. **Computed.** Counts, lists of statements, sections or files, and the uses: templates filled at build time from
   the sources. Each module records the same values as literals, and the build compares the two.
3. **Framing.** Titles, "How to read it", headings, legends, and the "Not checked here" notes. Among them, the one
   caveat every poster carries (`vp.NOT_BUILT`): nothing is built or elaborated, and a card says what a statement is,
   not that it is proved. F2's "Holds" lines are marked as the poster's own words.
4. **Interpretations**, in an amber card or in a key, worded from the data:
   - F2, "Paper is not only the top of the proof": computed from the imports and guarded by `UPWARD`.
   - R2's key, "Table 1": a section's statements may use another section's definitions only through Lean predicates
     (`Flat`, `Contracting`) or through declarations of the Nc library, and that use is not seen. This sentence says
     what the method cannot see. It is not a finding about any one cell, and the 8 cells it covers are guarded by
     `EXPECTED` and `BORNE`.
   - R3, "Appendix Q.3 against the walk": computed, and guarded by `OFF_ROUTE`, `Q3_OFF` and `ON_BY_SECOND`. Its
     last sentence, that a definition is off the route because the proofs use its Lean definition, says why the
     method finds no use of the theorem Table 3 gives a definition. It is not a reading of each proof.
   - R3's table, the column "Read as": this poster's reading of each quoted claim of Appendix Q as a check on the
     uses (`ROUTE_CLAIMS`). The build fails if a quoted phrase leaves the paper or a check stops holding.
   - F3, "the statements the paper leaves to the Lean are where the Lean is": computed from `WEIGHT`. Each note is
     placed by a recorded rule (`NOTES`): the statement whose header it follows, unless it stands in another
     section, when it is the first statement it names.

   - F5, "most directories belong to one section": computed from `MATRIX`, `REACHED` and `DIRS`. A directory's
     "home" is a computed label, the section that reaches most of its lines; it says where the code is used from,
     not what it is about.
   - F7, "the Lean writes its own word": computed from `IN_TEXT`. F8's "The most cited": computed from `CITED`.
5. **A transcription.** F4's boxes and arrows (`BOXES`, `ARROWS`) are this repository's reading of Figure 1 as
   rendered (p. 5), since the PDF's text has the figure's words but not its arrows. The words in its boxes are this
   poster's short wording. What the build checks: that the transcription uses exactly the Lean names the figure
   prints, and that the PDF is the one it was read from (`PAPER_SHA256`). F4's interpretation card is computed
   from `VERDICTS`. The traces' "How to read it" sentences stand behind assertions in T1 and T2.

**The spacing of the quotations.** pypdf loses the spaces of a few lines of the PDF, so each quoted passage is
respaced from PyMuPDF's reading of the page, where a space stands wherever two characters are further apart than a
fifth of the font size (tools/paper-facts/README.md). The characters, spaces aside, must match pypdf's exactly, or
the passage is kept as pypdf reads it. In a formula the spacing is PyMuPDF's, not the printed one.

**Inferred relations.** Every use between statements, and so every use between sections that is marked "Lean", is
inferred from names in the source text (`diagrams/README.md`, "How the Lean is read"). The posters say so where they
draw them, and F1 and R2 record every one.
