"""F3 — Where the paper rests on the Lean: its formalization notes, and how much Lean stands under each statement.

The paper's overview says that the printed proofs of four statements describe machines and programs, that only the
Lean development verifies they do what is claimed, and that each of the four is followed by a formalization note; the
text has seven such notes. This poster quotes the overview and the seven notes, places each note in the text, and
measures, for every numbered statement, the declarations of vp-vnp under its Lean theorems in the elaborated Lean
(src/lean-uses.json: the walk through every constant of their terms, in any library, stopping at the theorems of other
statements). The build fails if the overview's
four, the notes (page, place, the statements they name), or any statement's count of declarations and lines by
library differ from what is recorded here, in either direction."""
import vp
from vp import anchor_of, code, compare, linked
from lib import Canvas

ID, SLUG = "F3", "formalization-notes"

W = 3080
S = 13.5
G = 36
LIBS = ["Paper", "Nc", "NS1", "Ov"]
LIB_ACCENT = {"Paper": "teal", "Nc": "brown", "NS1": "amber", "Ov": "pink"}

# The statements whose printed proofs, the overview says, only the Lean verifies.
OVERVIEW = ["Proposition I.1", "Theorem H.2", "Theorem J.3", "Proposition N.4"]
# Every formalization note: (page, the last statement header before it, the subsection it stands in, the statements
# it names, the statement it is about). It is about the statement whose header it follows, unless it stands in another
# section than that statement, when it is about the first statement it names.
NOTES = [
    (42, "Theorem F.6", "G.1 Edges, loads and the choice of h", ["Theorem H.2"], "Theorem H.2"),
    (44, "Proposition H.1", "H.1 A tower of finite groups", [], "Proposition H.1"),
    (46, "Theorem H.2", "H.3 The decomposition theorem", [], "Theorem H.2"),
    (49, "Proposition I.1", "I.2 Tape automata", [], "Proposition I.1"),
    (52, "Proposition J.2", "J.2 The pieces of a tree network", ["Theorem H.2"], "Proposition J.2"),
    (53, "Theorem J.3", "J.3 One cut", [], "Theorem J.3"),
    (63, "Proposition N.4", "N.3 Approximate accelerators in the contracting case", [], "Proposition N.4"),
]
# statement -> (declarations under its Lean theorems, and their lines in Paper, Nc, NS1, Ov)
WEIGHT = {
    'Definition A.1': (15, 17, 0, 0, 58), 'Lemma A.2': (99, 150, 5, 0, 853), 'Lemma A.3': (49, 86, 0, 0, 421),
    'Definition A.4': (47, 14, 40, 0, 228), 'Proposition A.5': (74, 318, 0, 0, 424),
    'Theorem A.6': (96, 210, 104, 0, 500), 'Proposition A.7': (104, 236, 0, 0, 632),
    'Proposition A.8': (91, 333, 75, 0, 489), 'Lemma B.1': (24, 172, 152, 0, 0),
    'Proposition B.2': (78, 601, 403, 0, 0), 'Proposition B.3': (121, 472, 262, 0, 517),
    'Theorem C.1': (180, 1095, 508, 0, 258), 'Lemma C.2': (126, 454, 576, 0, 258),
    'Proposition C.3': (59, 299, 44, 0, 258), 'Lemma C.4': (34, 433, 111, 0, 0),
    'Definition D.1': (19, 40, 17, 0, 30), 'Theorem D.2': (191, 937, 659, 0, 258),
    'Proposition E.1': (33, 42, 439, 0, 0), 'Corollary E.2': (13, 103, 40, 0, 0), 'Lemma E.3': (28, 145, 104, 0, 0),
    'Lemma E.4': (25, 63, 249, 0, 0), 'Proposition E.5': (148, 445, 396, 0, 468), 'Theorem E.6': (19, 55, 35, 0, 30),
    'Lemma E.7': (78, 21, 313, 0, 445), 'Lemma E.8': (123, 285, 82, 0, 870),
    'Proposition E.9': (90, 152, 107, 0, 515), 'Proposition E.10': (153, 541, 292, 0, 536),
    'Theorem E.11': (17, 99, 24, 0, 30), 'Display (F.1)': (79, 200, 406, 0, 0), 'Lemma F.1': (44, 137, 301, 0, 0),
    'Lemma F.2': (44, 96, 434, 0, 0), 'Lemma F.3': (95, 252, 800, 0, 0), 'Lemma F.4': (84, 326, 493, 0, 0),
    'Lemma F.5': (67, 257, 419, 0, 0), 'Theorem F.6': (137, 832, 825, 0, 30), 'Definition G.1': (2, 7, 43, 0, 0),
    'Theorem G.2': (194, 528, 776, 0, 650), 'Proposition H.1': (256, 30, 2140, 0, 0),
    'Theorem H.2': (947, 1553, 10733, 4, 0), 'Proposition I.1': (561, 148, 5769, 159, 0),
    'Lemma I.2': (110, 27, 1491, 0, 0), 'Definition J.1': (33, 34, 0, 215, 0),
    'Proposition J.2': (261, 1618, 1283, 4, 0), 'Theorem J.3': (1076, 466, 10832, 2431, 0),
    'Theorem J.4': (160, 170, 297, 1332, 30), 'Definition K.1': (29, 15, 0, 198, 0),
    'Lemma K.2': (222, 121, 1348, 948, 0), 'Lemma K.3': (199, 651, 1358, 348, 0), 'Lemma K.4': (152, 37, 0, 1764, 0),
    'Proposition K.5': (184, 336, 13, 1395, 30), 'Theorem K.6': (186, 397, 13, 1374, 30),
    'Theorem K.7': (50, 152, 99, 122, 30), 'Theorem L.1': (22, 79, 28, 0, 30), 'Theorem L.2': (22, 76, 43, 0, 30),
    'Corollary L.3': (30, 95, 180, 0, 0), 'Lemma M.1': (7, 20, 71, 0, 0), 'Proposition M.2': (63, 133, 633, 0, 0),
    'Theorem M.3': (87, 527, 200, 122, 30), 'Corollary M.4': (49, 38, 407, 0, 0),
    'Definition N.1': (4, 12, 12, 0, 0), 'Lemma N.2': (21, 33, 231, 0, 0), 'Lemma N.3': (79, 68, 307, 0, 445),
    'Proposition N.4': (388, 1008, 263, 3479, 30), 'Theorem N.5': (476, 1778, 2455, 433, 536),
}


def subject(after, sub, names):
    return after if after.split(" ", 1)[1][0] == sub[0] else names[0]


def build():
    src = vp.load()
    st = src.statements
    q = src.facts["appendix_q"]
    reread = "the overview (p. 17) and the formalization notes of paper.pdf (src/paper-facts.json)"
    compare("F3: the statements the overview says only the Lean verifies", OVERVIEW, q["overview_lean"], reread)
    notes = [(n["page"], n["after"], n["subsection"], n["names"], subject(n["after"], n["subsection"], n["names"]))
             for n in src.facts["notes"]]
    compare("F3: the formalization notes", NOTES, notes, reread)
    weight = {}
    for k in sorted(st, key=vp.order_key):
        if not st[k]["decls"]:
            continue
        cl = src.lean_under[k]
        lines = {lib: 0 for lib in LIBS}
        for n in cl:
            lib = src.decls[n]["module"].split(".")[0]
            if lib not in lines:
                raise ValueError(f"F3: {k} reaches {n}, in {lib}, a library this poster does not draw")
            lines[lib] += src.decls[n]["lines"]
        weight[k] = (len(cl),) + tuple(lines[lib] for lib in LIBS)
    compare("F3: the declarations and lines under each statement's Lean", WEIGHT, weight,
            "src/lean-uses.json (under) and the Lean files of vp-vnp at FM_COMMIT")
    _, on = vp.route(src)
    total = {k: sum(v[1:]) for k, v in WEIGHT.items()}
    ranked = sorted(total, key=lambda k: (-total[k], vp.order_key(k)))
    rank = {k: i + 1 for i, k in enumerate(ranked)}
    subjects = sorted({n[4] for n in NOTES}, key=vp.order_key)

    c = Canvas(ID, "Where the paper rests on the Lean: its seven formalization notes, and how much Lean stands under "
               "each numbered statement",
               "The paper's overview names four statements whose printed proofs describe machines and programs, and "
               "says that only the Lean verifies them. This poster quotes it and the notes, places each note in the "
               f"text, and counts the Lean under every statement, in the elaborated Lean of vp-vnp at formal-math "
               f"{src.commit} (src/lean-uses.json). The words in quotation marks are the paper's.", W,
               sources=f"anthropics/formal-math {src.commit}, vp-vnp/paper.pdf (p. 17, the formalization notes, "
               "Appendix Q), vp-vnp/**/*.lean.", state=f"Drawn from formal-math {src.commit}")
    x0, y = c.x0, c.y
    c.para(x0, y, c.x1 - x0, "**How to read it.** The amber card quotes the overview. The cards below it are the "
           "notes in the order of the text. The bars measure, for each numbered statement, the declarations under its "
           "Lean theorems: the walk from them through every constant of their elaborated terms, in any library, "
           "stopping at another statement's theorems, each constant counted as the source declaration it belongs to. "
           "A statement number links to its row on F1. " + vp.NOT_BUILT_LEAN, S + 0.5,
           "muted")
    y += 64

    # ---- the overview
    y += c.card(x0, y, c.x1 - x0, "The overview, on the printed proofs (p. 17)",
                [f"“{q['overview']}”",
                 "It names " + ", ".join(f"`{anchor_of(k)}`" for k in OVERVIEW) + f": {len(OVERVIEW)} statements. "
                 f"The text has {len(NOTES)} formalization notes, about {len(subjects)} statements: "
                 + ", ".join(f"`{anchor_of(k)}`" for k in subjects) + "."], accent="amber", size=S + 0.5) + 40

    # ---- the notes
    y += c.heading(x0, y, f"The {len(NOTES)} formalization notes, in the order of the text")
    ncol = 4
    cw = (c.x1 - x0 - (ncol - 1) * G) / ncol
    specs = []
    for n, (page, after, sub, names, subj) in zip(src.facts["notes"], NOTES):
        r = st[subj]
        d = src.decls[r["decls"][0]]
        url = vp.lean_url(src.full, d["file"], d["line"])
        v = WEIGHT[subj]
        parts = ", ".join(f"{lib} {v[1 + i]}" for i, lib in enumerate(LIBS) if v[1 + i])
        title = (r["header"] or {}).get("title") or r["kind"].lower()
        specs.append(dict(
            name=f"p. {page} · {sub}", accent="pink" if subj in OVERVIEW else "grey",
            pill="about one of the overview's four" if subj in OVERVIEW else "about another statement",
            say=f"“{n['text']}”",
            bullets=[f"**About** `{anchor_of(subj)}` {title}",
                     f"**Stands** after the header of `{anchor_of(after)}`" + (f"; names " + ", ".join(
                         f"`{anchor_of(x)}`" for x in names) if names else ""),
                     f"**Its Lean** {linked(url, code(r['lean'][0], 30))} at {d['file']}:{d['line']}",
                     f"**Under it** {v[0]} declarations, {sum(v[1:])} lines ({parts}); rank {rank[subj]} of "
                     f"{len(WEIGHT)}",
                     "**On the route** to Solution's theorems: " + ("yes" if subj in on else "no")],
            anchor=f"note-{page}"))
    for row in range(0, len(specs), ncol):
        chunk = specs[row:row + ncol]
        hh = max(vp.node(c, 0, 0, cw, draw=False, size=S, tsize=15, **sp) for sp in chunk)
        for i, sp in enumerate(chunk):
            vp.node(c, x0 + i * (cw + G), y, cw, h=hh, size=S, tsize=15, **sp)
        y += hh + G
    y += 14

    # ---- the interpretation, computed
    ov_ranks = sorted(rank[k] for k in OVERVIEW)
    other = [k for k in subjects if k not in OVERVIEW]
    top = ranked[:len(OVERVIEW) + len(other)]
    y += c.card(x0, y, c.x1 - x0, "An interpretation: the statements the paper leaves to the Lean are where the Lean is",
                [f"By lines under their Lean, the overview's {len(OVERVIEW)} statements rank "
                 + ", ".join(str(r) for r in ov_ranks) + f" of {len(WEIGHT)}; the other statements with a note rank "
                 + ", ".join(f"{rank[k]} (`{anchor_of(k)}`)" for k in other) + ". The "
                 f"{len(top)} heaviest are " + ", ".join(f"`{anchor_of(k)}`" for k in top) + ", of which "
                 f"{len([k for k in top if k in subjects])} carry a note.",
                 "Computed from `WEIGHT`, which the build checks. A count of declarations and lines is not a measure "
                 "of difficulty, and a declaration under two statements is counted under both."],
                accent="amber", size=S + 0.5) + 40

    # ---- the bars
    y += c.heading(x0, y, f"The Lean under each of the {len(WEIGHT)} statements with a Lean theorem, by lines")
    lab = 470
    bw = c.x1 - x0 - lab - 260
    maxl = total[ranked[0]]
    for k in ranked:
        v = WEIGHT[k]
        mark = " · note" if k in subjects else ""
        acc = "pink" if k in OVERVIEW else ("ink" if k in subjects else "muted")
        c.text(x0, y + 15, f"{rank[k]:>2}  `{anchor_of(k)}` {st[k]['kind'].lower()}{mark}", S, acc,
               bold=k in subjects)
        bx = x0 + lab
        for i, lib in enumerate(LIBS):
            wpx = bw * v[1 + i] / maxl
            if wpx > 0:
                c.rect(bx, y + 3, wpx, 16, LIB_ACCENT[lib], rx=2, sw=1)
                bx += wpx
        c.text(bx + 10, y + 15, f"{sum(v[1:])} lines, {v[0]} declarations", S - 1, "muted")
        y += 24
    y += 14
    y += c.legend(x0, y, [("box", LIB_ACCENT[lib], lib) for lib in LIBS], title="Lines in", size=S) + 40

    # ---- the other passages of Appendix Q on what only the library holds
    y += c.heading(x0, y, "Appendix Q on what is only in the library, and what is not in Lean")
    cw = (c.x1 - x0 - G) / 2
    for i, (title, text) in enumerate([("Steps only under the library's names", q["library_only"]),
                                       ("Not in Lean", q["not_in_lean"])]):
        hh = c.card(x0 + i * (cw + G), y, cw, title, [f"“{text}”"], accent="grey", size=S, draw=False)
        c.card(x0 + i * (cw + G), y, cw, title, [f"“{text}”"], accent="grey", size=S)
    y += hh + 40
    c.para(x0, y, c.x1 - x0, "**Not checked here.** Where a note ends: the extractor takes a note to its first line "
           "that ends with a full stop (tools/paper-facts/README.md). What a note is about, when it stands in another "
           "section than the statement before it: the first statement it names. That every declaration under a "
           "statement is needed: a constant counts wherever it stands in a term, its type included. That the Lean of a "
           "statement proves what the note says it does.", S + 0.5, "muted")
    return c
