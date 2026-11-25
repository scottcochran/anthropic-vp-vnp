"""R2 — The proof, section by section: the paper's Table 1 against what the Lean names.

The paper's Table 1, "Map of the proof", gives each of its fifteen appendix sections A to O what it proves, the
sections it uses and the case it serves: the flat case, the contracting case or both. This poster draws the fifteen
sections as cards, then the table's uses as a matrix beside the uses between sections that the Lean text shows: a
statement of one section whose Lean proof names a theorem of a statement of another (src/paper-facts.json, Table 3,
gives each statement its theorems; vp.py says how a proof is read). The build fails if the cases, the statements per
section, Table 1's uses, the uses the Lean bears out, or the uses only the Lean shows differ from what is recorded
here, in either direction."""
import collections

import vp
from vp import anchor_of, compare
from lib import Canvas, text_width, render_line, wrap

ID, SLUG = "R2", "sections"

W = 3080
S = 13.5
NCOLS = 5
G = 40

CASES = {"A": "both", "B": "both", "C": "both", "D": "both", "E": "flat", "F": "contracting", "G": "contracting",
         "H": "contracting", "I": "contracting", "J": "contracting", "K": "contracting", "L": "both", "M": "both",
         "N": "both", "O": "both"}
COUNTS = {"A": 8, "B": 3, "C": 4, "D": 2, "E": 11, "F": 7, "G": 2, "H": 2, "I": 2, "J": 4, "K": 7, "L": 3, "M": 4,
          "N": 6, "O": 0}
# Table 1's uses, as (used, user).
EXPECTED = [
    ("A", "B"), ("A", "C"), ("B", "C"), ("C", "D"), ("A", "E"), ("C", "E"), ("D", "E"), ("C", "F"), ("D", "F"),
    ("A", "G"), ("F", "G"), ("G", "H"), ("G", "I"), ("H", "I"), ("H", "J"), ("I", "J"), ("E", "K"), ("G", "K"),
    ("I", "K"), ("J", "K"), ("D", "L"), ("E", "L"), ("K", "L"), ("D", "M"), ("E", "M"), ("K", "M"), ("E", "N"),
    ("K", "N"), ("M", "N"), ("C", "O"),
]
# Those of Table 1's uses that a statement of the user names a statement of the used section in the Lean text.
BORNE = [
    ("A", "B"), ("A", "C"), ("B", "C"), ("C", "D"), ("A", "E"), ("C", "E"), ("C", "F"), ("A", "G"), ("F", "G"),
    ("H", "J"), ("I", "J"), ("E", "K"), ("I", "K"), ("D", "L"), ("E", "L"), ("K", "L"), ("D", "M"), ("E", "M"),
    ("K", "M"), ("E", "N"), ("K", "N"), ("M", "N"),
]
# Uses between sections that the Lean text shows and Table 1 does not list.
LEAN_ONLY = [("A", "N"), ("D", "N"), ("G", "J"), ("I", "N"), ("J", "N"), ("L", "M"), ("L", "N")]


def sec(key):
    return key.split(" ", 1)[1].strip("()")[0]


def build():
    src = vp.load()
    t1 = {r["section"]: r for r in src.facts["table1"]}
    letters = list(t1)
    reread = "Table 1 of paper.pdf (src/paper-facts.json)"
    compare("R2: the case of each section", CASES, {k: r["case"] for k, r in t1.items()}, reread)
    counts = {k: 0 for k in letters}
    for st in src.statements.values():
        counts[st["section"]] += 1
    compare("R2: numbered statements per section", COUNTS, counts, "Table 3 of paper.pdf (src/paper-facts.json)")
    paper = [(u, k) for k in letters for u in t1[k]["uses"]]
    compare("R2: Table 1's uses", sorted(EXPECTED), sorted(paper), reread)
    lean = collections.defaultdict(list)
    for k, us in src.uses.items():
        for t, how in us.items():
            if sec(k) != sec(t):
                lean[(sec(t), sec(k))].append((t, k, how))
    compare("R2: Table 1's uses that the Lean text bears out", sorted(BORNE), sorted(e for e in paper if e in lean),
            "the proofs of the Lean theorems of the sections named, at FM_COMMIT")
    compare("R2: uses between sections that only the Lean text shows", sorted(LEAN_ONLY),
            sorted(e for e in lean if e not in paper), "the proofs of the Lean theorems of the sections named")
    unseen = [e for e in paper if e not in lean]

    c = Canvas(ID, f"The proof, section by section: the paper's map of its {len(letters)} appendix sections, against "
               "the uses between them that the Lean text shows",
               "Read from Table 1 of the paper, “Map of the proof” (what each section proves, what it uses, and the "
               "case it serves), and from the Lean source of vp-vnp at formal-math "
               f"{src.commit}: a section uses another in the Lean when a statement of the one names, in its Lean proof, "
               "a theorem of a statement of the other.", W,
               sources=f"anthropics/formal-math {src.commit}, vp-vnp/paper.pdf (Table 1, Table 3), vp-vnp/Paper/*.lean.",
               state=f"Drawn from formal-math {src.commit}")
    x0, y = c.x0, c.y
    nb, nt, nl = len(BORNE), len(EXPECTED), len(LEAN_ONLY)
    c.para(x0, y, c.x1 - x0, f"**How to read it.** The cards are the sections in the paper's order, coloured by the "
           "case Table 1 says each serves. The words in italics are Table 1's. Below them, the matrix sets each section "
           "(a row) against the sections it uses (the columns), by Table 1, by the Lean text, or by both. A statement "
           "number links to its row on F1. " + vp.NOT_BUILT, S + 0.5, "muted")
    y += 64

    # ---- the cards
    cw = (c.x1 - x0 - (NCOLS - 1) * G) / NCOLS
    modules = {}
    for k, st in src.statements.items():
        if st["decls"]:
            modules.setdefault(st["section"], set()).add(src.decls[st["decls"][0]]["file"].split("/")[-1])
    by_sec = collections.defaultdict(list)
    for k in sorted(src.statements, key=vp.order_key):
        by_sec[src.statements[k]["section"]].append(k)
    lean_uses = {k: sorted({u for (u, v) in lean if v == k}) for k in letters}
    specs = []
    for k in letters:
        r = t1[k]
        kinds = collections.Counter(src.statements[s]["kind"].lower() for s in by_sec[k])
        kind_s = ", ".join(f"{n} {kd}{'s' if n > 1 else ''}" for kd, n in sorted(kinds.items(), key=lambda t: (-t[1], t[0])))
        bullets = [
            f"**{counts[k]} numbered statements**" + (f": {kind_s}" if kind_s else "; Table 3 lists none"),
            "**Uses, by Table 1:** " + (", ".join(r["uses"]) or "nothing"),
            "**Uses, in the Lean text:** " + (", ".join(lean_uses[k]) or "nothing"),
        ]
        foot = []
        if by_sec[k]:
            foot.append("**Statements** " + ", ".join(f"`{anchor_of(s)}`" for s in by_sec[k]))
        if modules.get(k):
            foot.append("**Lean files** " + ", ".join(sorted(modules[k])))
        specs.append(dict(name=f"Section {k}", accent=vp.CASE_ACCENT[r["case"]], pill=vp.CASE_LABEL[r["case"]],
                          say=f"“{r['what']}”", bullets=bullets, foot=foot or ["No Lean theorem of its own"],
                          anchor=f"sec-{k}"))
    for row in range(0, len(specs), NCOLS):
        chunk = specs[row:row + NCOLS]
        hs = [vp.node(c, 0, 0, cw, draw=False, size=S, **sp) for sp in chunk]
        h = max(hs)
        for i, sp in enumerate(chunk):
            vp.node(c, x0 + i * (cw + G), y, cw, h=h, size=S, **sp)
        y += h + G
    y += 20

    # ---- the matrix
    y += c.heading(x0, y, "Which section uses which: Table 1 and the Lean text")
    cell, head = 74, 210
    STYLE = {"both": ("teal", "both"), "paper": ("amber", "Table 1"), "lean": ("violet", "Lean")}
    c.text(x0 + head + 15 * cell / 2, y + 16, "used", S, "faint", anchor="middle", bold=True)
    y += 28
    for j, u in enumerate(letters):
        c.text(x0 + head + j * cell + cell / 2, y + 18, u, 15, vp.CASE_ACCENT[CASES[u]], anchor="middle", bold=True)
    y += 30
    my = y
    for i, k in enumerate(letters):
        ry = my + i * (cell * 0.55)
        rh = cell * 0.55
        c.rect(x0, ry, head + 15 * cell, rh, "line", tint=False, rx=0, sw=0.8, fill_token="bg" if i % 2 == 0 else "zebra")
        c.text(x0 + 12, ry + rh / 2 + 5, f"**{k}** uses", 15, vp.CASE_ACCENT[CASES[k]])
        for j, u in enumerate(letters):
            e = (u, k)
            kind = "both" if e in BORNE else ("paper" if e in EXPECTED else ("lean" if e in LEAN_ONLY else None))
            if not kind:
                continue
            acc, lab = STYLE[kind]
            cx = x0 + head + j * cell
            c.rect(cx + 4, ry + 4, cell - 8, rh - 8, acc, rx=5, dash=None if kind == "both" else "4 3")
            c.text(cx + cell / 2, ry + rh / 2 + 4.5, lab, 12, acc, anchor="middle", bold=True)
    c.blocks.append((x0, my, x0 + head + 15 * cell, my + 15 * cell * 0.55, "table matrix"))
    mx1 = x0 + head + 15 * cell
    # the key, beside the matrix
    kx, ky = mx1 + 60, my
    kw = c.x1 - kx
    ky += c.para(kx, ky, kw, f"**both**: Table 1 lists the use, and a statement of the row names one of the column's "
                 f"in its Lean proof. {nb} of Table 1's {nt} uses.", S + 1, "teal") + 14
    ky += c.para(kx, ky, kw, f"**Table 1**: the paper lists the use, and no statement of the row names one of the "
                 f"column's. {len(unseen)} of {nt}. A section whose statements use another's definitions only through "
                 "Lean predicates (`Flat`, `Contracting`) or through declarations of the Nc library is not seen, and "
                 "Section O proves facts that Lemma C.4 states, so no statement of its own names them.", S + 1,
                 "amber") + 14
    ky += c.para(kx, ky, kw, f"**Lean**: a statement of the row names one of the column's, and Table 1 does not list "
                 f"the use. {nl} uses; the table below names the statements behind each.", S + 1, "violet") + 14
    y = max(my + 15 * cell * 0.55, ky) + 50

    # ---- the disagreements, statement by statement
    y += c.heading(x0, y, "Behind each disagreement")
    cols = [("Use", 220), ("Which way", 260), ("The statements behind it, in the Lean text", c.x1 - x0 - 480)]
    rows = []
    for e in sorted(LEAN_ONLY):
        pairs = sorted(lean[e], key=lambda t: (vp.order_key(t[1]), vp.order_key(t[0])))
        rows.append({"cells": [f"{e[1]} uses {e[0]}", "only in the Lean text",
                               "; ".join(f"`{anchor_of(k)}` names `{anchor_of(t)}`" + (" through helpers" if h != "direct"
                                                                                       else "") for t, k, h in pairs)],
                     "accent": "violet"})
    for e in sorted(unseen):
        rows.append({"cells": [f"{e[1]} uses {e[0]}", "only in Table 1",
                               f"no statement of {e[1]} names, in its Lean proof, a theorem of a statement of {e[0]}"
                               + (" (Section O has no numbered statement)" if "O" in e else "")],
                     "accent": "amber"})
    y += c.table(x0, y, cols, rows, size=S) + 40
    c.para(x0, y, c.x1 - x0, "**Not checked here.** Whether a use the Lean text shows is one the proof needs: a name in a "
           "proof is counted wherever it stands. That Table 1 is complete or minimal as a map: the paper's caption "
           "adds that Sections I and K use only the ring A of Section G, and Section I only the notion of a network of "
           "Section H.", S + 0.5, "muted")
    return c
