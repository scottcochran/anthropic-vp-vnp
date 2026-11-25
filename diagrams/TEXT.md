# What on a poster is quoted, computed or its own

Every sentence on a poster is one of four kinds (proof-posters:recording-expectations, section 3).

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

**Inferred relations.** Every use between statements, and so every use between sections that is marked "Lean", is
inferred from names in the source text (`diagrams/README.md`, "How the Lean is read"). The posters say so where they
draw them, and F1 and R2 record every one.
