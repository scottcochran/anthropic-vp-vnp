# vp-vnp-posters

Generated SVG posters of *VP ≠ VNP over every field* and its Lean formalization, read from the vp-vnp folder of
anthropics/formal-math at a pinned commit. The build fails when the sources no longer say what a poster draws.
`README.md` says what each poster shows, `diagrams/README.md` what is checked, `PLAN.md` what is planned, decided
and done.

## Rules every change keeps

1. Every fact is read from the files at build time: the Lean source at `FM_COMMIT`, or `diagrams/src/paper-facts.json`,
   pinned by its hash. A poster's own words are marked as its own (`diagrams/TEXT.md`).
2. Each poster records what it expects as module-level literals, compared both ways, so a source change is a
   failing check, never a silent redraw.
3. The source is pinned (`FM_COMMIT`, `PAPER_SHA256`, `PAPER_FACTS_SHA256` in `diagrams/src/vp.py`). Moving one is
   deliberate: bump, regenerate, fix what the checks report.
4. The output is deterministic, and CI fails on the first byte that differs.
5. The posters build no Lean. Uses between statements are read from the source text, and the posters say so; F9
   checks that reading against `diagrams/src/lean-uses.json`, read once from an export of the built Lean outside the
   build (`tools/lean-uses/README.md`) and pinned by its hash (`LEAN_USES_SHA256`).
6. Standard library only for the posters, on Python 3.12+. The one exception is `tools/paper-facts/extract.py`,
   which uses pypdf and PyMuPDF and runs outside the build.

And:

- **Never loosen a check.** Fix a failure by recording what the source now says, traced to a file and line.
- **Never touch a published release or tag.** The custodian (scottcochran) signs and pushes tags. Draft the
  message, and don't push.
- **Stage files by name**, never a directory.
- Run Python with `uv run`. The generator is `uv run python diagrams/gen-diagrams.py`. Any WARNING or ERROR is a
  failure. An exit of 1 with a NOTE means anchors moved: run it again.
- The source is a formal-math checkout's vp-vnp folder: `../vp-np` by default, or `VP_VNP`.

## House style

As riemann-diagrams': plain and exact. Give numbers with what they count ("22 of Table 1's 30 uses"), name pins by
name and value, and say what was not checked. Commit subjects are `<area>: <what changed>` or
`Phase <n>: <poster>, <what it shows>`.

## Skills

The method is the `proof-posters` plugin (from scottcochran/riemann-diagrams), enabled by `.claude/settings.json`.
It reads this repository's paths from `proof-posters.toml`. The poster recipe is this repository's own, in
`.claude/skills/`.

| Skill | When |
|---|---|
| `proof-posters:recording-expectations` | the method for any poster: read, record, compare both ways, four kinds of sentence, deterministic |
| `proof-posters:moving-pins` | formal-math moved; `FM_COMMIT`, `PAPER_SHA256`, `PAPER_FACTS_SHA256` or `LEAN_USES_SHA256` fails |
| `proof-posters:extracting-lean-deps` | `diagrams/src/lean-uses.json` must be rebuilt (`tools/lean-uses/README.md`) |
| `proof-posters:linking-posters` | a link lands on nothing, or a new card or row should be reachable |
| `proof-posters:cutting-releases` | a release is due (no release workflow exists yet: PLAN.md) |
| `drawing-posters` | a poster is added, or its layout or wording changes |
