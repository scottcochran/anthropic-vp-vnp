"""R3 — The route to the main theorems: every numbered statement that Solution's theorems reach, as a graph.

Solution.lean proves its five theorems from four numbered statements (R1). This poster follows the uses between
statements that the elaborated Lean shows (F1, src/lean-uses.json) down from those four, draws every statement it reaches in layers
by its longest distance from Solution, with an arrow from each statement to each one its Lean proof uses, and
marks the longest chain. Below, the statements the walk does not reach are set against the paper's own list of
what is not on that route (Appendix Q.3), and the paper's notes on how the route departs from the printed proofs
(Appendix Q, "Routes of proof") are each checked against the uses. The build fails if the statements off the
route, the longest chain, Q.3's list, or any of those checks differ from what is recorded here; the arrows are
F1's uses, which F1 records."""
import collections
import functools

import vp
from vp import anchor_of, compare
from lib import Canvas, light
from d_f1_paper_lean import EXPECTED as F1_USES

ID, SLUG = "R3", "route"

W = 3080
S = 12.5
G = 22
ROW_GAP = 70

OFF_ROUTE = ["Definition A.4", "Definition D.1", "Proposition E.5", "Theorem E.6",
             "Definition G.1", "Definition J.1", "Definition K.1", "Theorem L.2", "Corollary L.3", "Definition N.1",
             "Remark N.6"]
# Appendix Q.3: the statements it says are not on the route of Solution's theorems, besides "the definitions".
Q3_OFF = ["Theorem L.2", "Corollary L.3", "Proposition E.5", "Theorem E.6"]
# The one row of Q.3's "the definitions" that the walk reaches, with the only Lean name of it that any proof names:
# Table 3 gives Definition A.1 two theorems, and the proofs name the second, never the first.
ON_BY_SECOND = {"Definition A.1": "Paper.def_spectral_congr"}
CHAIN = ["Corollary M.4", "Theorem M.3", "Theorem L.1", "Theorem K.7", "Theorem K.6", "Proposition K.5", "Theorem J.4",
         "Theorem G.2", "Theorem F.6", "Proposition C.3", "Theorem C.1", "Proposition A.8", "Lemma A.2",
         "Definition A.1"]
# Appendix Q, "Routes of proof": a phrase of the paper, how this poster reads it, and what must then hold of the uses
# in the elaborated Lean. ("absent", user, used): user's walk does not reach used's theorems; ("through", user,
# used): it reaches them only through helpers; ("reaches", user, name): its walk passes the Paper declaration name.
ROUTE_CLAIMS = [
    ("Proposition N.4 repeats the iteration of Proposition K.5, as printed",
     [("absent", "Proposition N.4", "Proposition K.5")]),
    ("Lemma K.3, Theorem M.3 and Theorem N.5 use the general forms for families that are complete for grid sums, of "
     "which Corollary E.2 and the statements about the permanent are instances",
     [("absent", "Lemma K.3", "Corollary E.2"), ("absent", "Theorem M.3", "Corollary E.2"),
      ("absent", "Theorem N.5", "Corollary E.2")]),
    ("Proposition E.10 uses the step prop_flat_lower_sum of the proof of Proposition E.5, not the proposition",
     [("reaches", "Proposition E.10", "Paper.prop_flat_lower_sum"), ("absent", "Proposition E.10", "Proposition E.5")]),
    ("Lemma N.2 repeats the argument of Lemma M.1 on coefficients", [("absent", "Lemma N.2", "Lemma M.1")]),
    ("Theorem N.5 does not cite Lemma K.3, Theorem K.7 and Theorem M.3",
     [("absent", "Theorem N.5", "Lemma K.3"), ("absent", "Theorem N.5", "Theorem K.7"),
      ("absent", "Theorem N.5", "Theorem M.3")]),
    ("Instead it uses the step thm_allfields_exceeds of the proof of the last of them and approximate analogues of "
     "the first two",
     [("reaches", "Theorem N.5", "Paper.thm_allfields_exceeds"), ("reaches", "Theorem N.5", "Paper.lem_circuit_approx"),
      ("reaches", "Theorem N.5", "Paper.contracting_approx_complete")]),
    ("Theorem H.2 uses parts (a) and (b) of Proposition H.1 through the named theorems that also prove the "
     "proposition", [("through", "Theorem H.2", "Proposition H.1")]),
]


def holds(src, check):
    kind, user, obj = check
    if kind == "absent":
        return obj not in src.lean_uses[user]
    if kind == "through":
        return src.lean_uses[user].get(obj) == "through"
    return obj in src.lean_reach[user]


def build():
    src = vp.load()
    st = src.statements
    q = src.facts["appendix_q"]
    roots, on = vp.route(src, src.lean_uses)
    edges = [(u, k) for k in st for u in src.lean_uses[k]]
    compare("R3: the uses drawn are F1's", sorted(F1_USES), sorted(edges), "d_f1_paper_lean.py and src/lean-uses.json")
    off = sorted((k for k in st if k not in on), key=vp.order_key)
    compare("R3: the statements off the route of Solution's theorems", OFF_ROUTE, off,
            "Solution.lean and the uses in src/lean-uses.json")
    compare("R3: Appendix Q.3's list of what is not on the route", Q3_OFF, q["off_route"]["names"],
            "Appendix Q.3 of paper.pdf (src/paper-facts.json)")
    if not q["off_route"]["definitions"]:
        raise ValueError("R3: Appendix Q.3 no longer ends its list with 'the definitions': re-read it")
    q3 = set(Q3_OFF) | {k for k in st if st[k]["kind"] == "Definition"}
    unformalized = {k for k in st if not st[k]["decls"]}
    named = {n for user in src.lean["met"].values() for ns in user.values() for n in ns}   # names a walk arrives at
    second = {}
    for k in sorted(q3 & on, key=vp.order_key):
        hit = sorted(n for n in st[k]["decls"] if n in named)
        second[k] = hit[0] if len(hit) == 1 and hit[0] != st[k]["decls"][0] else hit
    compare("R3: the rows of Q.3's list that the walk reaches, and the one Lean name of each that a proof names",
            ON_BY_SECOND, second, "Appendix Q.3, Table 3, and the proofs that name those theorems")
    if set(off) - unformalized != q3 - set(ON_BY_SECOND):
        raise ValueError(f"R3: off the route {sorted(set(off) - unformalized)}, Appendix Q.3 says {sorted(q3)}")
    users = collections.defaultdict(list)
    for u, k in edges:
        if k in on:
            users[u].append(k)

    @functools.lru_cache(None)
    def depth(k):
        ups = [x for x in users[k] if x in on]
        return 1 if not ups else 1 + max(depth(x) for x in ups)

    @functools.lru_cache(None)
    def height(k):
        return 1 + max((height(u) for u in src.lean_uses[k]), default=0)

    top = max(roots, key=lambda k: (height(k), [-c for c in vp.order_key(k)]))
    chain = [top]
    while src.lean_uses[chain[-1]]:
        chain.append(max(src.lean_uses[chain[-1]], key=lambda k: (height(k), [-c for c in vp.order_key(k)])))
    compare("R3: the longest chain of uses", CHAIN, chain, "the uses in src/lean-uses.json")
    routes = " ".join(q["routes"])
    results = []
    for phrase, checks in ROUTE_CLAIMS:
        if phrase not in routes:
            raise ValueError(f"R3: Appendix Q's routes of proof no longer say {phrase!r}: re-read them")
        bad = [c for c in checks if not holds(src, c)]
        if bad:
            raise ValueError(f"R3: the elaborated Lean no longer bears out {phrase!r}: {bad}")
        results.append((phrase, checks))

    claims = {n: vp.statements_named(src, d) for n, d in src.decls.items()
              if d["module"] == "Solution" and d["kind"] == "theorem"}

    c = Canvas(ID, f"The route to the main theorems: the {len(on)} numbered statements that Solution's theorems "
               "reach, as a graph of the uses the elaborated Lean shows",
               "Each card is a numbered statement of the paper; an arrow runs from a statement to each statement whose "
               "Lean theorem its elaborated Lean proof uses, directly (solid) or through helpers of vp-vnp (dashed). "
               f"Rows are the longest distance from Solution.lean. Read from the Lean source of vp-vnp at formal-math "
               f"{src.commit}, its export (src/lean-uses.json), and the paper's Table 3 and Appendix Q (src/paper-facts.json).", W,
               sources=f"anthropics/formal-math {src.commit}, vp-vnp/Solution.lean, vp-vnp/Paper/*.lean, paper.pdf "
               "(Table 3, Appendix Q).", state=f"Drawn from formal-math {src.commit}")
    x0, y = c.x0, c.y
    c.para(x0, y, c.x1 - x0, f"**How to read it.** The top row is the five theorems of Solution.lean. Below them, "
           f"{len(on)} of the paper's {len(st)} numbered statements, coloured by the case of their section (amber flat, "
           "pink contracting, grey both). The thick blue arrows are the longest chain of uses, "
           f"{len(CHAIN)} statements from `{anchor_of(CHAIN[0])}` to `{anchor_of(CHAIN[-1])}`. A statement number links "
           "to its card here. " + vp.NOT_BUILT_LEAN, S + 1.5, "muted")
    y += 70

    # ---- layers, ordered by barycentres
    layers = collections.defaultdict(list)
    for k in sorted(on, key=vp.order_key):
        layers[depth(k)].append(k)
    rows = [sorted(claims, key=lambda n: list(claims).index(n))] + \
        [sorted(layers[d], key=vp.order_key) for d in sorted(layers)]
    ncol = max(len(r) for r in rows)
    cw = (c.x1 - x0 - (ncol - 1) * G) / ncol
    slot = cw + G

    def place(row):
        left = x0 + (c.x1 - x0 - (len(row) * slot - G)) / 2
        return {k: left + i * slot for i, k in enumerate(row)}

    down = {n: claims[n] for n in claims}
    for k in sorted(on, key=vp.order_key):     # never a set's order: the sums below are of floats
        down[k] = [u for u in src.lean_uses[k] if u in on]
    up = collections.defaultdict(list)
    for k, us in down.items():
        for u in us:
            up[u].append(k)
    xs = {}
    for _ in range(4):                          # sweeps down and up; ties keep the paper's order
        for i, row in enumerate(rows):
            xs.update(place(row))
        for i in range(1, len(rows)):
            rows[i].sort(key=lambda k: (sum(xs[p] for p in up[k]) / len(up[k]) if up[k] else xs[k], vp.order_key(k)))
            xs.update(place(rows[i]))
        for i in range(len(rows) - 2, 0, -1):
            rows[i].sort(key=lambda k: (sum(xs[d] for d in down[k]) / len(down[k]) if down[k] else xs[k],
                                        vp.order_key(k)))
            xs.update(place(rows[i]))

    def spec(k):
        if k in claims:
            return dict(name=f"`{k.split('.')[1]}`", accent="blue", pill=None,
                        bullets=["Solution.lean", "**From** " + ", ".join(f"`{anchor_of(x)}`" for x in claims[k])],
                        anchor=None)
        r = st[k]
        title = (r["header"] or {}).get("title") or ("a display" if r["kind"] == "Display" else "no title")
        pill = f"chain {CHAIN.index(k) + 1}" if k in CHAIN else None
        return dict(name=f"`{anchor_of(k)}` {r['kind'].lower()}", accent=vp.CASE_ACCENT[case[r["section"]]], pill=pill, bullets=[title, f"`{r['lean'][0]}`"], anchor=anchor_of(k))

    case = {t["section"]: t["case"] for t in src.facts["table1"]}
    specs = {k: spec(k) for row in rows for k in row}
    ch = max(vp.node(c, 0, 0, cw, draw=False, size=S, tsize=15, pad=12, **specs[k]) for k in specs)
    ys = {}
    for i, row in enumerate(rows):
        for k in row:
            ys[k] = y + i * (ch + ROW_GAP)
    # ---- the arrows first, so that the cards cover them
    out_order = {k: sorted(down[k], key=lambda d: xs[d]) for k in down}
    in_order = {u: sorted(up[u], key=lambda p: xs[p]) for u in up}

    def port(k, other, order):
        lst = order[k]
        i = lst.index(other)
        return xs[k] + cw * (i + 1) / (len(lst) + 1)

    chain_edges = set(zip(CHAIN[1:], CHAIN[:-1]))
    plain, thick = [], []                   # the chain last, so that it is drawn over the other arrows
    for k in sorted(down, key=lambda k: (ys[k], xs[k])):
        for d in down[k]:
            item = (port(k, d, out_order), ys[k] + ch, port(d, k, in_order), ys[d] - 2,
                    "direct" if k in claims else src.lean_uses[k][d], (d, k) in chain_edges)
            (thick if item[-1] else plain).append(item)
    for item in plain + thick:
        draw_edge(c, *item)
    for k in specs:
        vp.node(c, xs[k], ys[k], cw, h=ch, size=S, tsize=15, pad=12, **specs[k])
    y += len(rows) * (ch + ROW_GAP) + 10
    c.legend(x0, y, [("arrow", "faint", "the proof refers to the statement's Lean theorem", None, 1.6),
                     ("arrow", "faint", "through helpers of vp-vnp", "5 4", 1.6),
                     ("arrow", "blue", "the longest chain", None, 3.5),
                     ("box", "amber", "flat case"), ("box", "pink", "contracting case"), ("box", "grey", "both cases")],
             title="Key", size=S + 1)
    y += 60

    # ---- off the route, against Appendix Q.3
    y += c.heading(x0, y, f"Off the route: the {len(off)} statements the walk from Solution does not reach")
    ncol2 = 6
    cw2 = (c.x1 - x0 - (ncol2 - 1) * G) / ncol2
    ospecs = []
    for k in off:
        r = st[k]
        title = (r["header"] or {}).get("title") or "no title in its header"
        why = ("Table 3 gives it no Lean theorem" if k in unformalized else
               "a definition: Appendix Q.3 lists the definitions" if r["kind"] == "Definition" else
               "named in Appendix Q.3")
        ub = [x for x in st if k in src.lean_uses[x]]
        ospecs.append(dict(name=f"`{anchor_of(k)}` {r['kind'].lower()}", accent="grey", pill=None,
                           bullets=[title, "**Why** " + why,
                                    "**Uses** " + (", ".join(f"`{anchor_of(u)}`" for u in src.lean_uses[k]) or "none named"),
                                    "**Used by** " + (", ".join(f"`{anchor_of(u)}`" for u in ub) or "none")],
                           anchor=f"off-{anchor_of(k)}"))
    for row in range(0, len(ospecs), ncol2):
        chunk = ospecs[row:row + ncol2]
        hh = max(vp.node(c, 0, 0, cw2, draw=False, size=S, tsize=15, pad=12, **sp) for sp in chunk)
        for i, sp in enumerate(chunk):
            vp.node(c, x0 + i * (cw2 + G), y, cw2, h=hh, size=S, tsize=15, pad=12, **sp)
        y += hh + G
    y += 10
    ndef = len([k for k in st if st[k]["kind"] == "Definition"])
    exc = ", ".join(f"`{anchor_of(k)}`, which the walk reaches only through `{n[len('Paper.'):]}`, the second of the "
                    f"theorems Table 3 gives it; no proof names the first, `{st[k]['lean'][0]}`"
                    for k, n in ON_BY_SECOND.items())
    y += c.card(x0, y, c.x1 - x0, f"Appendix Q.3 against the walk: they agree but for one row",
                [f"The paper: “The theorems of Solution are proved through them, with these exceptions, which are not "
                 f"on that route: {q['off_route']['text']}.”",
                 f"The walk: off the route are the {len(Q3_OFF)} statements Q.3 names, "
                 f"{len([k for k in off if st[k]['kind'] == 'Definition'])} of the {ndef} definitions, and "
                 f"{', '.join(sorted(unformalized))}, which has no Lean theorem. The other definition is {exc}. Q.3 "
                 "itself names that theorem as the one by which spectral points respect the identifications. The build "
                 "fails if any of this changes (`OFF_ROUTE`, `Q3_OFF`, `ON_BY_SECOND`).",
                 "A definition is off the route here because the Lean proofs use its Lean definition (`Flat`, "
                 "`Contracting`, …), not the theorem Table 3 gives it."], accent="teal", size=S + 1) + 40

    # ---- Appendix Q's routes of proof, checked
    y += c.heading(x0, y, "Appendix Q, “Routes of proof”: where the route leaves the printed references, checked")
    cols = [("The paper (Appendix Q), quoted", 1300), ("Read here as", c.x1 - x0 - 1300 - 160), ("Holds", 160)]
    trows = []
    for phrase, checks in results:
        said = []
        for kind, user, obj in checks:
            if kind == "absent":
                said.append(f"`{anchor_of(user)}` does not reach `{anchor_of(obj)}`")
            elif kind == "through":
                said.append(f"`{anchor_of(user)}` reaches `{anchor_of(obj)}` only through helpers")
            else:
                said.append(f"`{anchor_of(user)}` passes `{obj[len('Paper.'):]}`")
        trows.append([f"“{phrase}”", "; ".join(said), "yes"])
    y += c.table(x0, y, cols, trows, size=S + 0.5) + 40
    c.para(x0, y, c.x1 - x0, "**Not checked here.** The bullets of Appendix Q that this table leaves out say what a "
           "proof takes from a statement (only some clauses of Lemma A.2, a clause of Lemma K.4 never cited), which "
           "the walk, at the level of whole theorems, cannot see. That a use reached only through helpers is the use "
           "the paper means. The column “Read as” is this poster's reading of the paper's words.", S + 1, "muted")
    return c


def draw_edge(c, x1, y1, x2, y2, how, on_chain):
    acc = "blue" if on_chain else "faint"
    sw = 3.5 if on_chain else 1.3
    dash = ' stroke-dasharray="5 4"' if how != "direct" and not on_chain else ""
    dy = max(30.0, (y2 - y1) * 0.45)
    c.add(f'<path d="M {x1:.1f} {y1:.1f} C {x1:.1f} {y1 + dy:.1f} {x2:.1f} {y2 - dy:.1f} {x2:.1f} {y2:.1f}" '
          f'fill="none" stroke="{light(acc)}" class="s-{acc}" stroke-width="{sw}"{dash} '
          f'marker-end="url(#arw-{acc})" opacity="{1 if on_chain else 0.75}"/>', y2)
    c.n_arrows += 1
