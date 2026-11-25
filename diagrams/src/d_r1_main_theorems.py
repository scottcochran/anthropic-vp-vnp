"""R1 — What is claimed: the five theorems of Solution.lean, the definitions they are stated with, and the paper's
statements they are proved from.

Comparator, the check the formal-math repository's CI runs, compares the theorems named in comparator.json with the
same theorems stated with sorry in Challenge.lean, and re-checks their proofs. This poster draws those five theorems,
each with the numbered statement of the paper whose Lean theorem its proof names; the definitions of Statement.lean,
which imports Mathlib alone, that they are stated with; and where the paper's introduction states each result. The
build fails if the theorems Comparator checks, the statement each is proved from, the definitions, the
introduction's statements and their appendix counterparts, the permitted axioms, or the sentence quoted from the
README differ from what is recorded here, in either direction."""
import json

import vp
from vp import anchor_of, code, compare, linked
from lib import Canvas

ID, SLUG = "R1", "main-theorems"

W = 3080
S = 13.5
G = 40

# Solution's theorems, each with the numbered statements whose Lean theorems its proof names.
CLAIMS = {
    "Solution.mainTheorem": ["Theorem M.3"],
    "Solution.mainTheoremApprox": ["Theorem N.5"],
    "Solution.separation": ["Corollary M.4"],
    "Solution.separationClosure": ["Theorem N.5"],
    "Solution.permanent_over_real": ["Theorem L.1"],
}
DEFINITIONS = ["Statement.Computes", "Statement.perm", "Statement.hc", "Statement.Beyond", "Statement.MainTheorem",
               "Statement.Approximates", "Statement.MainTheoremApprox", "Statement.Family", "Statement.VP",
               "Statement.VPBar", "Statement.VNP", "Statement.Separation", "Statement.SeparationClosure"]
# The numbered statements of Sections 1 and 2, each with the row of Table 3 that has its Lean theorem.
INTRO = {"Theorem 1.1": "Theorem M.3", "Corollary 1.2": "Corollary M.4", "Definition 1.3": "Definition N.1",
         "Theorem 1.4": "Theorem N.5", "Definition 2.1": "Definition D.1", "Theorem 2.2": "Theorem D.2"}
AXIOMS = ["propext", "Quot.sound", "Classical.choice"]
QUOTED = "Both were written by AI models, and no human mathematician has checked the proof."


def build():
    src = vp.load()
    full = src.full
    cmp_ = json.loads((vp.VP / "comparator.json").read_text(encoding="utf-8"))
    readme = (vp.VP / "README.md").read_text(encoding="utf-8")
    reread = "Solution.lean, Challenge.lean and comparator.json at FM_COMMIT"
    compare("R1: the theorems comparator.json names", sorted(CLAIMS), sorted(cmp_["theorem_names"]), reread)
    sol = [n for n, d in src.decls.items() if d["module"] == "Solution" and d["kind"] == "theorem"]
    compare("R1: the theorems of Solution.lean", sorted(CLAIMS), sorted(sol), reread)
    compare("R1: the theorems Challenge.lean states", sorted(CLAIMS),
            sorted(n for n, d in src.challenge.items() if d["kind"] == "theorem"), reread)
    compare("R1: the statements each theorem is proved from", CLAIMS,
            {n: vp.statements_named(src, src.decls[n]) for n in sorted(CLAIMS)}, "the proofs in Solution.lean")
    compare("R1: the permitted axioms", AXIOMS, cmp_["permitted_axioms"], "comparator.json")
    defs = [n for n, d in sorted(src.decls.items(), key=lambda t: t[1]["line"]) if d["module"] == "Statement"]
    compare("R1: the definitions of Statement.lean", DEFINITIONS, defs, "Statement.lean")
    compare("R1: what Statement.lean imports", ["Mathlib"], src.modules["Statement"]["imports"], "Statement.lean")
    compare("R1: what Challenge.lean imports", ["Statement"], src.modules["Challenge"]["imports"], "Challenge.lean")
    by_lean = {n: k for n, ks in src.lean_of.items() for k in ks}
    intro = {f"{r['kind']} {r['number']}": by_lean.get(f"Paper.{r['lean']}") for r in src.facts["intro"]}
    compare("R1: the statements of Sections 1 and 2 and their rows of Table 3", INTRO, intro,
            "Sections 1 and 2 of paper.pdf (src/paper-facts.json)")
    if QUOTED not in " ".join(readme.split()):
        raise ValueError(f"R1: README.md no longer says {QUOTED!r}: re-read it and the card that quotes it")

    c = Canvas(ID, "What is claimed: the five theorems Comparator checks, the definitions they are stated with, and "
               "the statements of the paper they are proved from",
               "Read from the Lean source of vp-vnp at formal-math "
               f"{src.commit}: comparator.json, Solution.lean, Challenge.lean and Statement.lean, and from the paper's "
               "Sections 1 and 2 and Table 3 (pinned in src/paper-facts.json). Code is quoted from the files; the words "
               "in italics are the Lean files' own docstrings.", W,
               sources=f"anthropics/formal-math {src.commit}, vp-vnp/comparator.json, Solution.lean, Challenge.lean, "
               "Statement.lean, README.md, paper.pdf (Sections 1 and 2, Table 3).",
               state=f"Drawn from formal-math {src.commit}")
    x0, y = c.x0, c.y
    st = src.statements

    # ---- band 1: the five theorems
    y += c.heading(x0, y, "1 · The five theorems that comparator.json names, as Solution.lean proves them")
    cw = (c.x1 - x0 - 4 * G) / 5
    cols = vp.columns(cw, fsize=12.5)
    specs = []
    for n in CLAIMS:
        d = src.decls[n]
        sig = d["signature"].replace("theorem ", "", 1)
        rows = CLAIMS[n]
        used = [f"`{anchor_of(k)}` " + (st[k]["header"]["title"] if st[k]["header"] and st[k]["header"]["title"]
                                        else st[k]["kind"].lower()) for k in rows]
        stated = [x for x in DEFINITIONS if x.split(".")[1] in {t.split(".")[0] for t in d["sig_tokens"]}]
        intro_of = [i for i, r in INTRO.items() if r in rows]
        bullets = [f"**Proved from** `Paper.{st[rows[0]]['lean'][0]}`, the paper's " + "; ".join(used),
                   "**Stated with** " + (", ".join(f"`{x.split('.')[1]}`" for x in stated) or "Mathlib alone")]
        if intro_of:
            bullets.append("**In the introduction** " + ", ".join(intro_of))
        else:
            bullets.append("**In the introduction** not stated; the main text's special case")
        foot = [f"**Lean** {linked(vp.lean_url(full, d['file'], d['line']), code(d['file'] + ':' + str(d['line'])))}"
                f" · stated with sorry in {linked(vp.lean_url(full, 'Challenge.lean', src.challenge[n]['line']), code('Challenge.lean:' + str(src.challenge[n]['line'])))}"]
        specs.append(dict(name=f"`{n.split('.')[1]}`", accent="blue", pill="Comparator",
                          formula=vp.lean_block(sig, cols, 6), say=d["doc"], bullets=bullets, foot=foot,
                          anchor=n))
    hs = [vp.node(c, 0, 0, cw, draw=False, size=S, fsize=12.5, **sp) for sp in specs]
    for i, sp in enumerate(specs):
        vp.node(c, x0 + i * (cw + G), y, cw, h=max(hs), size=S, fsize=12.5, **sp)
    y += max(hs) + 50

    # ---- band 2: the definitions of Statement.lean
    y += c.heading(x0, y, f"2 · The {len(DEFINITIONS)} definitions of Statement.lean, which imports Mathlib and "
                   "nothing else")
    ncol = 4
    cw = (c.x1 - x0 - (ncol - 1) * G) / ncol
    cols = vp.columns(cw, fsize=12.5)
    users = {x: [] for x in DEFINITIONS}
    for n, d in src.decls.items():
        if d["module"] in ("Statement", "Solution"):
            # a definition's whole text, a theorem's statement only: a proof's local names (hc) are not uses
            toks = {t.split(".")[0] for t in (d["tokens"] if d["module"] == "Statement" else d["sig_tokens"])}
            for x in DEFINITIONS:
                if x != n and x.split(".")[1] in toks:
                    users[x].append(n.split(".")[1])
    specs = []
    for n in DEFINITIONS:
        d = src.decls[n]
        body = "\n".join(ln for ln in d["source"].split("\n") if not ln.lstrip().startswith(("/--", "-/"))
                         and not ln.startswith("open ") and not ln.startswith("attribute "))
        body = vp.blank(body)[0]                       # the docstrings of a structure's fields are drawn as words
        body = "\n".join(ln for ln in body.split("\n") if ln.strip())
        specs.append(dict(name=f"`{n.split('.')[1]}`", accent="violet", pill=d["kind"],
                          formula=vp.lean_block(body, cols, 9), say=d["doc"],
                          foot=["**Used by** " + (", ".join(f"`{u}`" for u in sorted(users[n])) or "none"),
                                f"**Lean** {linked(vp.lean_url(full, d['file'], d['line']), code(d['file'] + ':' + str(d['line'])))}"],
                          anchor=n))
    for row in range(0, len(specs), ncol):
        chunk = specs[row:row + ncol]
        hs = [vp.node(c, 0, 0, cw, draw=False, size=S, fsize=12.5, **sp) for sp in chunk]
        for i, sp in enumerate(chunk):
            vp.node(c, x0 + i * (cw + G), y, cw, h=max(hs), size=S, fsize=12.5, **sp)
        y += max(hs) + G
    y += 10

    # ---- band 3: the introduction's statements
    y += c.heading(x0, y, "3 · Where the paper states them: Sections 1 and 2, and the appendix rows that prove them")
    cols = [("In the paper", 260), ("Its title", 420), ("Its Lean theorem (prefix Paper.)", 460),
            ("The row of Table 3 with that theorem", 520), ("Its title there", c.x1 - x0 - 1660)]
    rows = []
    for r in src.facts["intro"]:
        key = f"{r['kind']} {r['number']}"
        k = INTRO[key]
        d = src.decls[f"Paper.{r['lean']}"]
        h = st[k]["header"]
        rows.append([key, r["title"] or "no title in its header",
                     linked(vp.lean_url(full, d["file"], d["line"]), code(r["lean"])) + f" {d['file']}:{d['line']}",
                     f"`{anchor_of(k)}` {k.split()[0].lower()}, p. {h['page']}", (h["title"] or "no title in its header")])
    y += c.table(x0, y, cols, rows, size=S) + 50

    # ---- band 4: what is checked, and by whom
    y += c.heading(x0, y, "4 · What is checked, and by whom")
    cw = (c.x1 - x0 - 2 * G) / 3
    specs = [
        dict(name="Comparator, in formal-math's CI", accent="teal", pill="comparator.json",
             formula=vp.lean_block(json.dumps(cmp_, indent=1), vp.columns(cw, fsize=12.5), 24),
             bullets=[f"It compares the {len(CLAIMS)} theorems named with Challenge.lean, which states them with sorry "
                      "and imports Statement.lean alone, and re-checks the proofs, with the second kernel nanoda "
                      "when `enable_nanoda` is true.",
                      "The axioms permitted: " + ", ".join(f"`{a}`" for a in AXIOMS) + "."],
             foot=[f"**File** {linked(vp.lean_url(full, 'comparator.json'), code('comparator.json'))}"]),
        dict(name="Who has read the proof", accent="red", pill="README.md",
             say=QUOTED,
             bullets=["Quoted from the folder's README.md. The paper's Appendix Q says the same of the statement "
                      "file: that it says what is meant was judged by AI readers only."],
             foot=[f"**File** {linked(vp.lean_url(full, 'README.md'), code('README.md'))}"]),
        dict(name="What these posters check", accent="grey", pill="this repository",
             bullets=[vp.NOT_BUILT,
                      "The build checks that the files say what each poster records: the theorems above, the "
                      "statements they are proved from, the definitions, and the paper's tables as extracted."],
             foot=["**Pins** `FM_COMMIT`, `PAPER_SHA256`, `PAPER_FACTS_SHA256` in diagrams/src/vp.py"]),
    ]
    hs = [vp.node(c, 0, 0, cw, draw=False, size=S, fsize=12.5, **sp) for sp in specs]
    for i, sp in enumerate(specs):
        vp.node(c, x0 + i * (cw + G), y, cw, h=max(hs), size=S, fsize=12.5, **sp)
    return c
