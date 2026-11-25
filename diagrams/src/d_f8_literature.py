"""F8 — The proof as literature: the paper's references, by decade, and where in the paper each is cited.

The paper's reference list and every citation of its keys in the text are read from paper.pdf
(src/paper-facts.json, references): each citation is placed in the part of the paper it stands in, Section 1, 2 or
3 or an appendix by its letter. The build fails if the number of references or citations, or the parts where any
reference is cited, differ from what is recorded here, or if a reference has no paper in src/papers.toml
(proof-posters:linking-papers), which links each entry to it."""
import collections

import vp
from vp import compare
from lib import Canvas

ID, SLUG = "F8", "literature"

W = 3080
S = 13
PARTS = "front 1 2 3 A B C D E F G H I J K L M N O P Q".split()

N_REFS = 134
N_CITATIONS = 185
CITED = {'AJMV98': ['K'],
 'AKK22': ['H'],
 'Ald84': ['1', 'N'],
 'All99': ['K'],
 'And84': ['B'],
 'AV08': ['1'],
 'AW09': ['1'],
 'BCRL79': ['1'],
 'BCS97': ['1'],
 'BEGKN94': ['I'],
 'Ber84': ['1', '2', 'N'],
 'BGS75': ['1'],
 'BH99': ['2', 'C', 'C', 'C', 'C', 'C'],
 'BIP19': ['1'],
 'BIZ18': ['1'],
 'BLMW11': ['1'],
 'BN08': ['C', 'C'],
 'BS83': ['1'],
 'BS83b': ['A'],
 'BT72': ['2', 'C', 'C'],
 'Bür00': ['1', 'E'],
 'Bür00b': ['1', '1'],
 'Bür04': ['1', 'N'],
 'Bür24': ['1', 'E'],
 'CCL10': ['1'],
 'CDM16': ['H'],
 'CKRST20': ['1'],
 'CKSV22': ['1'],
 'Cur26': ['1'],
 'CVZ19': ['A'],
 'CVZ23': ['1'],
 'CZ19': ['A'],
 'DDS21': ['1'],
 'DHM02': ['H'],
 'DJ02': ['F'],
 'EGOW18': ['1'],
 'Eis95': ['2', 'K'],
 'EJ10': ['F'],
 'Enf69': ['C'],
 'FLMV05': ['K'],
 'For24': ['1'],
 'FPV13': ['M'],
 'Fri21': ['A'],
 'FSV18': ['1'],
 'GKKS14': ['1'],
 'GKKS16': ['1'],
 'GKSS17': ['1'],
 'Gly10': ['1', 'L'],
 'GMOW19': ['1'],
 'GMQ16': ['1'],
 'Gro03': ['F'],
 'Gro15': ['1'],
 'Guo26': ['1'],
 'GS89': ['I'],
 'HPV77': ['I'],
 'HR18': ['B'],
 'Hya79': ['1', '2', 'E'],
 'IN05': ['F'],
 'IP17': ['1'],
 'IS22': ['1'],
 'JS82': ['1', '2', 'K'],
 'Kal85': ['1'],
 'Kas11': ['F'],
 'KI04': ['1'],
 'KLS10': ['B'],
 'KLSS17': ['1'],
 'KO18': ['H'],
 'KO23': ['H'],
 'Koi12': ['1'],
 'KP09': ['K'],
 'KRST22': ['1'],
 'KS17': ['1'],
 'KS93': ['C'],
 'Kum20': ['1'],
 'KV26': ['1'],
 'Lan17': ['1'],
 'Lean': ['3', 'Q'],
 'LMR13': ['1'],
 'LST25': ['1'],
 'Mal03': ['M'],
 'Mathlib': ['3', 'Q'],
 'MN13': ['F'],
 'MP08': ['2', 'K'],
 'MR04': ['1'],
 'MS01': ['1', '1', 'N'],
 'MS08': ['1'],
 'MS08b': ['H'],
 'MW17': ['K'],
 'Nis91': ['1', '1'],
 'NS23': ['F'],
 'NW97': ['1'],
 'OAI26': ['1'],
 'Opp17': ['F'],
 'Orús14': ['A', 'H'],
 'PPST83': ['I'],
 'PS13': ['F'],
 'Raz09': ['1'],
 'Raz10': ['1'],
 'Raz13': ['1'],
 'Raz26': ['1'],
 'Res68': ['C'],
 'Rob91': ['I'],
 'RR97': ['1'],
 'Rys63': ['1', '1', 'L'],
 'RZ21': ['A'],
 'Sap21': ['1'],
 'Sat09': ['C'],
 'Sch78': ['I'],
 'Sch80': ['I'],
 'She26': ['1'],
 'She26b': ['1'],
 'Sto95': ['F'],
 'Str73': ['1'],
 'Str87': ['2', 'A', 'A'],
 'Str88': ['1', '1', '2', 'A', 'A', 'A'],
 'Str91': ['1'],
 'Stu03': ['2', 'C', 'C', 'C'],
 'SW14': ['K'],
 'SY10': ['1'],
 'Tav15': ['1'],
 'Val79': ['1', '1', '1', '2', 'E', 'M', 'M'],
 'Val79b': ['1'],
 'Val82': ['1', '1'],
 'VC17': ['A'],
 'Vin91': ['K'],
 'vM07': ['K'],
 'Vra22': ['A'],
 'VSBR83': ['1', '2', 'E', 'K'],
 'Wan00': ['F'],
 'Wil25': ['I'],
 'WZ26': ['1', 'A'],
 'Yab15': ['1'],
 'Yeh19': ['1'],
 'Zui19': ['A']}


def build():
    src = vp.load()
    r = src.facts["references"]
    reread = "the reference list and the text of paper.pdf (src/paper-facts.json)"
    compare("F8: the number of references", N_REFS, len(r["entries"]), reread)
    compare("F8: the number of citations", N_CITATIONS, len(r["citations"]), reread)
    got = collections.defaultdict(list)
    for ci in r["citations"]:
        got[ci["key"]].append(ci["part"])
    compare("F8: where each reference is cited", CITED,
            {e["key"]: sorted(got[e["key"]], key=PARTS.index) for e in r["entries"]}, reread)
    missing = sorted((k for k in CITED if k not in src.papers), key=str.lower)
    if missing:
        raise ValueError(f"F8: references with no paper in src/papers.toml: {missing}; add them "
                         "(proof-posters:linking-papers)")
    t1 = {t["section"]: t for t in src.facts["table1"]}
    entries = {e["key"]: e for e in r["entries"]}

    c = Canvas(ID, f"The proof as literature: the paper's {N_REFS} references, by decade, and where in the paper "
               "each one is cited",
               f"Read from the reference list of paper.pdf and from its text, {N_CITATIONS} citations in all (pinned in "
               "src/paper-facts.json). The entries in quotation marks are the paper's.", W,
               sources=f"anthropics/formal-math {src.commit}, vp-vnp/paper.pdf (References, the whole text).",
               state=f"Drawn from formal-math {src.commit}")
    x0, y = c.x0, c.y
    by_part = collections.Counter(p for ps in CITED.values() for p in ps)
    c.para(x0, y, c.x1 - x0, "**How to read it.** Section 1 is the introduction, 2 the overview, 3 the Lean "
           "formalization; A to O are the appendices of the proof. A citation is a key inside square brackets; "
           "[Str87, Str88] cites two. An entry links to its paper (src/papers.toml): a DOI where there is one. "
           "Nothing here reads the cited papers.", S + 1,
           "muted")
    y += 50

    # ---- citations by part, references by decade
    y += c.heading(x0, y, "Where the citations stand, and when the cited work appeared")
    half = (c.x1 - x0 - 80) / 2
    parts = [p for p in PARTS if by_part[p]]
    mx = max(by_part.values())
    yy = y
    for p in parts:
        lab = {"1": "Section 1, introduction", "2": "Section 2, overview", "3": "Section 3, Lean"}.get(
            p, f"{p} · {vp.abridge(t1[p]['what'], 40)}" if p in t1 else f"Appendix {p}")
        c.text(x0, yy + 15, lab, S, "ink")
        c.rect(x0 + 380, yy + 3, (half - 480) * by_part[p] / mx, 16, "blue", rx=2, sw=1)
        c.text(x0 + 390 + (half - 480) * by_part[p] / mx, yy + 15, str(by_part[p]), S, "muted")
        yy += 24
    dec = collections.Counter(e["year"] // 10 * 10 for e in r["entries"])
    mx2 = max(dec.values())
    y2 = y
    bx = x0 + half + 80
    for d in sorted(dec):
        c.text(bx, y2 + 15, f"{d}s", S, "ink")
        c.rect(bx + 90, y2 + 3, (half - 200) * dec[d] / mx2, 16, "teal", rx=2, sw=1)
        c.text(bx + 100 + (half - 200) * dec[d] / mx2, y2 + 15, f"{dec[d]} references", S, "muted")
        y2 += 24
    y = max(yy, y2) + 30
    top = sorted(CITED, key=lambda k: (-len(CITED[k]), k))[:10]
    y += c.card(x0, y, c.x1 - x0, "The most cited",
                ["; ".join(f"[{k}] {len(CITED[k])}×" for k in top) + ". Computed from `CITED`.",
                 f"{len([k for k in CITED if len(CITED[k]) == 1])} of the {N_REFS} references are cited once; "
                 f"{len([k for k in CITED if set(CITED[k]) <= {'1', '2', '3', 'front'}])} only in Sections 1 to 3, "
                 f"{len([k for k in CITED if not set(CITED[k]) & {'1', '2', '3', 'front'}])} only in the appendices."],
                accent="amber", size=S + 0.5) + 40

    # ---- every reference
    y += c.heading(x0, y, f"The {N_REFS} references")
    cols = [("Key", 150), ("Year", 80), ("The entry (the paper's reference list)", 2050), ("Cited in", c.x1 - x0 - 2280)]
    rows = []
    for k in sorted(entries, key=lambda k: k.lower()):
        e = entries[k]
        cnt = collections.Counter(CITED[k])
        where = ", ".join((vp.to(f"sec-{p}", p) if p.isalpha() and len(p) == 1 else p)   # an appendix: its card on R2
                          + (f" ×{cnt[p]}" if cnt[p] > 1 else "") for p in PARTS if cnt[p])
        pp = src.papers[k]
        tail = f" ({pp['via']})" if pp.get("url") else " (not linked: no stable copy)"
        rows.append({"cells": [f"`{k}`", str(e["year"]),
                               vp.linked(pp.get("url"), f"“{vp.abridge(e['text'], 250)}”") + tail, where],
                     "anchor": f"ref-{k.replace('+', '-')}"})
    y += c.table(x0, y, cols, rows, size=S - 0.5) + 30
    c.para(x0, y, c.x1 - x0, "**Not checked here.** That a key in brackets is a citation and not notation: a bracket is "
           "read as a citation only when it holds a key of the list. The year is the last year an entry prints.", S,
           "muted")
    return c
