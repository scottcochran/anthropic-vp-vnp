"""F4 — The paper's own picture of the proof, Figure 1, with each of its arrows checked against the elaborated Lean.

Figure 1 of the paper, "The structure of the proof", draws a common part that splits into the flat case and the
contracting case, each a column of boxes joined by arrows, some arrows marked with Lean names, and both ending at
Theorem 1.1. The text of the PDF has the figure's words and Lean names but not where its arrows run, so this module
records a transcription of the boxes and arrows (BOXES, ARROWS), made by reading the rendered page, and the build
checks that it uses exactly the Lean names the figure prints (FIGURE_NAMES) and that its Theorem 1.1 is the row of
Table 3 the introduction gives (THEOREM). PAPER_SHA256 stops the build when the PDF changes, so that the
transcription is read again. Each statement an arrow carries then gets a verdict from the uses read from the Lean
text; the build fails if any verdict differs from VERDICTS."""
import collections

import vp
from vp import anchor_of, compare
from lib import Canvas

ID, SLUG = "F4", "figure-1"

W = 2600
S = 13.5

FIGURE_NAMES = ["lem_hubs", "prop_crossing", "thm_cn", "thm_alt", "def_cases", "lem_few", "prop_cube",
                "prop_flat_rate", "thm_flat_rate", "cor_clauses", "lem_fkl_perm", "lem_balanced", "thm_poincare",
                "thm_laws", "thm_tree", "thm_cut", "lem_circuit", "thm_noacc", "thm_contracting", "lem_lowdeg",
                "lem_postpone", "prop_next"]
THEOREM = {"Theorem 1.1": "Theorem M.3"}
# The transcription: box -> (column, row, style, this poster's short wording of the box, the Lean names it prints).
# Column 0 is the flat case, 1 the contracting case, None spans both. A box that prints a chain (a → b → c) lists its
# names in order, and the chain's arrows are in ARROWS.
BOXES = {
    "common": (None, 0, "shaded", "Common part: tensors over the field", ["lem_hubs", "prop_crossing", "thm_cn",
                                                                           "thm_alt"]),
    "flat-hyp": (0, 1, "shaded", "flat hypothesis; the balanced sets cost about k^(3/2) bits",
                 ["def_cases", "lem_few", "prop_cube"]),
    "flat-assume": (0, 2, "dashed", "assume a circuit with L′ gates for PERM_m", []),
    "flat-circuit": (0, 3, "plain", "circuit with L = 5L′ gates for f_k,ℓ", []),
    "flat-sum": (0, 4, "plain", "f_k,ℓ as a sum over the balanced sets", []),
    "flat-compare": (0, 5, "plain", "comparison of lengths", ["prop_flat_rate"]),
    "flat-rate": (0, 6, "plain", "the flat case's bound", ["thm_flat_rate"]),
    "contr-hyp": (1, 1, "shaded", "Poincaré inequality → laws → trees → computations can be cut",
                  ["thm_poincare", "thm_laws", "thm_tree", "thm_cut"]),
    "contr-assume": (1, 2, "dashed", "assume a circuit with v^a gates for PERM_m", []),
    "contr-circuit": (1, 3, "plain", "circuit with O(v^a) gates for Φ", []),
    "contr-acc": (1, 4, "plain", "an accelerator at the scale v", ["lem_circuit"]),
    "contr-none": (1, 5, "plain", "accelerators at all larger scales; there are none", ["thm_noacc"]),
    "contr": (1, 6, "plain", "the contracting case's bound", ["thm_contracting"]),
    "main": (None, 7, "plain", "Theorem 1.1", []),
}
# (from, to, mark, the Lean names on the arrow, the names it carries from its source). An arrow inside a chain box
# runs from one of its names to the next, written box:name.
ARROWS = [
    ("common:lem_hubs", "common:prop_crossing", None, [], ["lem_hubs"]),
    ("common:prop_crossing", "common:thm_cn", None, [], ["prop_crossing"]),
    ("common:thm_cn", "common:thm_alt", None, [], ["thm_cn"]),
    ("common", "flat-hyp", "flat case", [], ["thm_alt"]),
    ("common", "contr-hyp", "contracting case", [], ["thm_alt"]),
    ("flat-assume", "flat-circuit", "P", ["cor_clauses", "lem_fkl_perm"], []),
    ("flat-circuit", "flat-sum", "C", ["lem_balanced"], []),
    ("flat-sum", "flat-compare", None, ["lem_hubs"], []),
    ("flat-hyp", "flat-compare", None, [], ["def_cases", "lem_few", "prop_cube"]),
    ("flat-compare", "flat-rate", None, [], ["prop_flat_rate"]),
    ("flat-rate", "main", None, [], ["thm_flat_rate"]),
    ("contr-hyp:thm_poincare", "contr-hyp:thm_laws", None, [], ["thm_poincare"]),
    ("contr-hyp:thm_laws", "contr-hyp:thm_tree", None, [], ["thm_laws"]),
    ("contr-hyp:thm_tree", "contr-hyp:thm_cut", None, [], ["thm_tree"]),
    ("contr-assume", "contr-circuit", "P", ["cor_clauses"], []),
    ("contr-circuit", "contr-acc", "C", ["lem_lowdeg"], []),
    ("contr-acc", "contr-none", None, ["lem_postpone", "prop_next"], ["lem_circuit"]),
    ("contr-hyp", "contr-none", None, [], ["thm_cut"]),
    ("contr-none", "contr", None, [], ["thm_noacc"]),
    ("contr", "main", None, [], ["thm_contracting"]),
]
# For each arrow (its index in ARROWS) and each statement it carries or names: the verdict, and the statements it
# rests on. "at": the next box with Lean names uses it; "below": a later box uses it (the first such); "around":
# a later box reaches it through statements the figure does not draw (or the arrow's own other names); "unseen".
VERDICTS = [
    (0, "Lemma A.3", "at", ["Proposition B.3"]),
    (1, "Proposition B.3", "at", ["Theorem C.1"]),
    (2, "Theorem C.1", "around", ["Theorem D.2", "Proposition C.3"]),
    (3, "Theorem D.2", "below", ["Theorem M.3"]),
    (4, "Theorem D.2", "below", ["Theorem M.3"]),
    (5, "Corollary E.2", "around", ["Theorem E.11", "Lemma E.3"]),
    (5, "Lemma E.3", "below", ["Theorem E.11"]),
    (6, "Lemma E.4", "at", ["Proposition E.10"]),
    (7, "Lemma A.3", "at", ["Proposition E.10"]),
    (8, "Definition D.1", "unseen", []),
    (8, "Lemma E.7", "at", ["Proposition E.10"]),
    (8, "Proposition E.9", "at", ["Proposition E.10"]),
    (9, "Proposition E.10", "at", ["Theorem E.11"]),
    (10, "Theorem E.11", "at", ["Theorem M.3"]),
    (11, "Theorem F.6", "at", ["Theorem G.2"]),
    (12, "Theorem G.2", "below", ["Theorem J.4"]),
    (13, "Theorem H.2", "around", ["Theorem J.4", "Theorem J.3", "Proposition J.2"]),
    (14, "Corollary E.2", "unseen", []),
    (15, "Lemma K.2", "at", ["Lemma K.3"]),
    (16, "Lemma K.3", "below", ["Theorem K.7"]),
    (16, "Lemma K.4", "at", ["Theorem K.6"]),
    (16, "Proposition K.5", "at", ["Theorem K.6"]),
    (17, "Theorem J.4", "at", ["Theorem K.6"]),
    (18, "Theorem K.6", "at", ["Theorem K.7"]),
    (19, "Theorem K.7", "at", ["Theorem M.3"]),
]
WORDS = {"at": "used at the arrow's end", "below": "used further down",
         "around": "reached through statements the figure leaves out", "unseen": "not seen"}
STYLE = {"at": ("teal", None), "below": ("amber", "8 4"), "around": ("violet", "4 4"), "unseen": ("red", "2 4")}
WORST = ["at", "below", "around", "unseen"]


def build():
    src = vp.load()
    st = src.statements
    fig = src.facts["figure1"]
    compare("F4: the Lean names Figure 1 prints", FIGURE_NAMES, fig["names"], "Figure 1 of paper.pdf (p. 5)")
    used = []
    for b in BOXES.values():
        used += b[4]
    for a in ARROWS:
        used += a[3]
    if sorted(set(used)) != sorted(FIGURE_NAMES):
        raise ValueError(f"F4: the transcription names {sorted(set(used))}, the figure {sorted(FIGURE_NAMES)}")
    intro = {f"{r['kind']} {r['number']}": r["lean"] for r in src.facts["intro"]}
    by_lean = {n: k for n, ks in src.lean_of.items() for k in ks}
    compare("F4: the row of Table 3 that is the figure's Theorem 1.1", THEOREM,
            {"Theorem 1.1": by_lean.get(f"Paper.{intro['Theorem 1.1']}")}, "Sections 1 and Table 3 of paper.pdf")
    if fig["theorem"] != "Theorem 1.1":
        raise ValueError("F4: Figure 1 no longer ends at Theorem 1.1: re-read the figure")

    def stmt(name):
        ks = src.lean_of.get(f"Paper.{name}")
        if not ks:
            raise ValueError(f"F4: Figure 1 prints {name}, which Table 3 gives no statement")
        return ks[0]

    def node_stmts(node):
        if node == "main":
            return [THEOREM["Theorem 1.1"]]
        box, _, name = node.partition(":")
        return [stmt(name)] if name else [stmt(n) for n in BOXES[box][4]]

    nxt = collections.defaultdict(list)
    for a in ARROWS:
        nxt[a[0]].append(a[1])
    drawn = {stmt(n) for n in FIGURE_NAMES} | {THEOREM["Theorem 1.1"]}

    def path(node):
        """The nodes from `node` down to Theorem 1.1, one way; it stops where the figure splits."""
        out = [node]
        while True:
            cur = out[-1]
            box = cur.partition(":")[0]
            if ":" in cur and cur not in nxt:          # the last name of a chain goes on as its box
                cur = box
            if len(nxt.get(cur, [])) != 1:
                return out
            out.append(nxt[cur][0])

    def verdict(arrow, s):
        _, dst, _, names, carried = arrow
        order = [k for n in path(dst) for k in node_stmts(n)]
        firsts = next((node_stmts(n) for n in path(dst) if node_stmts(n)), [])
        for t in firsts:
            if s in src.lean_uses[t]:
                return "at", [t]
        for t in order:
            if t not in firsts and s in src.lean_uses[t]:
                return "below", [t]
        own = {stmt(n) for n in names + carried}
        for t in order:                                 # breadth first, through what the figure does not draw
            prev, queue = {t: None}, [t]
            while queue:
                cur = queue.pop(0)
                for u in src.lean_uses[cur]:
                    if u in prev:
                        continue
                    prev[u] = cur
                    if u == s:
                        chain = [cur]
                        while prev[chain[-1]] is not None:
                            chain.append(prev[chain[-1]])
                        return "around", chain[::-1][:1] + chain[::-1][1:]
                    if u not in drawn or u in own:
                        queue.append(u)
        return "unseen", []

    got = []
    for i, a in enumerate(ARROWS):
        for name in a[4] + a[3]:
            v, via = verdict(a, stmt(name))
            got.append((i, stmt(name), v, via))
    compare("F4: the verdict on each arrow of Figure 1", VERDICTS, got,
            "Figure 1 (p. 5), its transcription in d_f4_figure_1.py, and the uses in src/lean-uses.json")
    by_arrow = collections.defaultdict(list)
    for i, s, v, via in VERDICTS:
        by_arrow[i].append((s, v, via))

    c = Canvas(ID, "The paper's own picture of the proof: Figure 1, each of its arrows checked against the uses the "
               "elaborated Lean shows",
               "Figure 1 of the paper (p. 5) draws the common part, the flat case and the contracting case, ending at "
               "Theorem 1.1. Its boxes and arrows are transcribed here from the rendered page; its Lean names are "
               "read from the PDF's text and joined to the numbered statements through Table 3; each arrow is coloured "
               f"by what the uses of the elaborated Lean of vp-vnp at formal-math {src.commit} say of it (src/lean-uses.json).", W,
               sources=f"anthropics/formal-math {src.commit}, vp-vnp/paper.pdf (Figure 1, Table 3), "
               "vp-vnp/Paper/*.lean.", state=f"Drawn from formal-math {src.commit}")
    x0, y = c.x0, c.y
    n_ok = sum(1 for v in VERDICTS if v[2] == "at")
    c.para(x0, y, c.x1 - x0, "**How to read it.** The boxes are the figure's, in its places; their words are this "
           "poster's short transcription, and each Lean name the figure prints is shown with its statement. An arrow "
           "is numbered as in the table below and coloured by the worst verdict on the statements it carries: teal, "
           "the next box with a Lean name uses them; amber, a later box does; violet, a later box reaches them only "
           "through statements the figure leaves out; red, not seen. Of the "
           f"{len(VERDICTS)} statements carried, {n_ok} are used at the arrow's end. " + vp.NOT_BUILT_LEAN, S + 0.5, "muted")
    y += 84

    # ---- the boxes, in the figure's places
    colw = (c.x1 - x0 - 260) / 2
    colx = [x0 + 60, x0 + 200 + colw]
    rowh = {}
    specs = {}
    for b, (col, row, style, words, names) in BOXES.items():
        body = [f"`{anchor_of(stmt(n))}` `{n}`" for n in names] if b not in ("common", "contr-hyp") else []
        if b == "main":
            body = [f"`{anchor_of(THEOREM['Theorem 1.1'])}` `{intro['Theorem 1.1']}`, the row of Table 3 with the "
                    "theorem the introduction gives Theorem 1.1"]
        specs[b] = dict(name=words, accent="grey", bullets=body,
                        dash="6 4" if style == "dashed" else None, anchor=f"fig-{b}")
    width = {b: (c.x1 - x0 - 120 if BOXES[b][0] is None else colw) for b in BOXES}
    width["main"] = colw * 0.8
    for b in BOXES:
        h = vp.node(c, 0, 0, width[b], draw=False, size=S, tsize=15, pad=14, **specs[b])
        if b in ("common", "contr-hyp"):
            h += 96
        rowh[BOXES[b][1]] = max(rowh.get(BOXES[b][1], 0), h)
    ys, gap = {}, 74
    yy = y
    for r in sorted(rowh):
        ys[r] = yy
        yy += rowh[r] + gap
    pos = {}
    for b, (col, row, style, words, names) in BOXES.items():
        bx = (x0 + 60 if col is None else colx[col]) if b != "main" else x0 + (c.x1 - x0 - width[b]) / 2
        pos[b] = (bx, ys[row], width[b], rowh[row] if b not in ("main",) else None)
    # chain boxes: sub-cards for their names
    sub = {}
    for b in ("common", "contr-hyp"):
        bx, by, bw, bh = pos[b]
        names = BOXES[b][4]
        sw = (bw - 40 - (len(names) - 1) * 50) / len(names)
        for i, n in enumerate(names):
            sub[f"{b}:{n}"] = (bx + 20 + i * (sw + 50), by + 52, sw, 62)

    def box_xy(node):
        if node in sub:
            return sub[node]
        bx, by, bw, bh = pos[node]
        return bx, by, bw, bh if bh else vp.node(c, 0, 0, width[node], draw=False, size=S, tsize=15, pad=14,
                                                 **specs[node])

    def worst(i):
        return max((v for _, v, _ in by_arrow[i]), key=WORST.index)

    # the boxes first, then the arrows over them: a shaded box's fill would hide the arrows of its chain
    for b in BOXES:
        bx, by, bw, bh = pos[b]
        if b in ("common", "contr-hyp"):
            c.region(bx, by, bw, bh, specs[b]["name"], "grey", dash=None, tint=True, size=S + 1)
            for n in BOXES[b][4]:
                sx, sy, sw, sh = sub[f"{b}:{n}"]
                vp.node(c, sx, sy, sw, h=sh, name=f"`{anchor_of(stmt(n))}` `{n}`", accent="grey", size=S, tsize=14,
                        pad=10)
        else:
            vp.node(c, bx, by, bw, h=bh, size=S, tsize=15, pad=14, **specs[b])
    for i, (a, b, mark, names, carried) in enumerate(ARROWS):
        acc, dash = STYLE[worst(i)]
        ax, ay, aw, ah = box_xy(a)
        bx, by, bw, bh = box_xy(b)
        label = f"{i + 1}" + (f" · {mark}" if mark else "") + (" · " + ", ".join(names) if names else "")
        if ":" in a and ":" in b:                       # inside a chain box: left to right
            c.arrow([(ax + aw, ay + ah / 2), (bx - 2, by + bh / 2)], acc, dash=dash, sw=2.4, label=f"{i + 1}",
                    lsize=12)
        elif (a, b) in (("flat-hyp", "flat-compare"), ("contr-hyp", "contr-none")):     # the side arrows
            side = ax - 40 if a == "flat-hyp" else ax + aw + 40
            ex = bx if a == "flat-hyp" else bx + bw
            c.arrow([(ax if a == "flat-hyp" else ax + aw, ay + ah / 2), (side, ay + ah / 2), (side, by + bh / 2),
                     (ex - (2 if a == "flat-hyp" else -2), by + bh / 2)], acc, dash=dash, sw=2.4, label=label,
                    lsize=12, lpos=0.5)
        elif b == "main":
            cx_a = ax + aw / 2
            tx = bx if a == "flat-rate" else bx + bw
            c.arrow([(cx_a, ay + ah), (cx_a, by + bh / 2), (tx + (-2 if a == "flat-rate" else 2), by + bh / 2)],
                    acc, dash=dash, sw=2.4, label=label, lsize=12, lpos=0.3)
        elif a == "common":
            tx = bx + bw / 2
            c.arrow([(tx, ay + ah), (tx, by - 2)], acc, dash=dash, sw=2.4, label=label, lsize=12)
        else:
            cx_a = ax + aw / 2
            c.arrow([(cx_a, ay + ah), (cx_a, by - 2)], acc, dash=dash, sw=2.4, label=label, lsize=12)
    y = yy + 10
    c.legend(x0, y, [("line", STYLE[k][0], WORDS[k], STYLE[k][1]) for k in WORST], title="Arrows", size=S)
    y += 50

    # ---- the verdicts, arrow by arrow
    y += c.heading(x0, y, "Each arrow, and what the elaborated Lean shows of the statements it carries")
    cols = [("Arrow", 110), ("From → to (transcribed)", 560), ("Carries", 330), ("Verdict", 400),
            ("What the elaborated Lean shows", c.x1 - x0 - 1400)]
    rows = []
    for i, (a, b, mark, names, carried) in enumerate(ARROWS):
        for j, (s, v, via) in enumerate(by_arrow[i]):
            what = {"at": lambda: f"`{anchor_of(via[0])}` uses `{anchor_of(s)}`",
                    "below": lambda: f"`{anchor_of(via[0])}`, further down, uses `{anchor_of(s)}`",
                    "around": lambda: " → ".join(f"`{anchor_of(x)}`" for x in via) + f" → `{anchor_of(s)}`",
                    "unseen": lambda: f"no statement below the arrow reaches `{anchor_of(s)}`"}[v]()
            frm = lambda n: BOXES[n.partition(':')[0]][3] if ":" not in n else f"`{n.partition(':')[2]}`"
            rows.append({"cells": [str(i + 1) + (f" · {mark}" if mark and j == 0 else "") if j == 0 else "",
                                   f"{frm(a)} → {frm(b)}" if j == 0 else "",
                                   f"`{anchor_of(s)}`", WORDS[v], what], "accent": STYLE[v][0]})
    y += c.table(x0, y, cols, rows, size=S - 0.5) + 30
    unseen = [(i, s) for i, s, v, _ in VERDICTS if v == "unseen"]
    y += c.card(x0, y, c.x1 - x0, "An interpretation: where the figure and the Lean part",
                [f"{n_ok} of the {len(VERDICTS)} statements the arrows carry are used where the figure says. The case "
                 "split of Theorem D.2 is used once, at the top, by Theorem M.3, not inside either branch (arrows 4 and "
                 "5). Not seen: " + "; ".join(f"`{anchor_of(s)}` on arrow {i + 1}" for i, s in unseen) + ". "
                 "Appendix Q explains the first on the contracting branch: Lemma K.3 uses the general form for "
                 "families complete for grid sums, of which Corollary E.2 is an instance (R3 checks that sentence). "
                 "Definition D.1 is a definition, and no Lean proof names the theorem Table 3 gives a definition (R3).",
                 "Computed from `VERDICTS`, which the build checks; the sentences about arrows 4 and 5 and the two "
                 "statements not seen stand behind the check that fails when the verdicts change."],
                accent="amber", size=S + 0.5) + 30
    c.para(x0, y, c.x1 - x0, "**Not checked here.** The transcription itself: where an arrow starts and ends is read "
           "from the rendered page by hand, and the words in the boxes are this poster's. What a box without a Lean "
           f"name stands for. The caption is the paper's: “{fig['caption']}”", S + 0.5, "muted")
    return c
