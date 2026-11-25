"""F5 — Where the formal work is: the 25 directories of the libraries under Paper (Nc, NS1, Ov), each set against
the sections of the paper whose statements reach it.

Three quarters of the Lean is outside the Paper library. This poster reads every declaration of Nc, NS1 and Ov at
FM_COMMIT, groups them by directory, and for each section of the paper takes the declarations its numbered
statements reach (vp.closure: names read from the text, in files the naming file imports, stopping at the theorems of
other statements), so that a cell is the formal work a section's own statements stand on in a directory. It also
measures how much of each directory no statement reaches by name. The build fails if any directory's files, lines or
declaration lines, any cell, or any directory's reached lines differ from what is recorded here, in either
direction."""
import collections

import vp
from vp import compare
from lib import Canvas, light

ID, SLUG = "F5", "library"

W = 3080
S = 13.5
G = 30
LIB_ACCENT = {"Nc": "brown", "NS1": "amber", "Ov": "pink"}

# directory -> (files, lines, lines of the declarations at the head of a line)
DIRS = {
    'Nc.Tow': (37, 8860, 7427),
    'NS1': (29, 7308, 6405),
    'Nc.Grp': (28, 6382, 5501),
    'Nc.Dl': (22, 5297, 4500),
    'Nc.Uni': (20, 4878, 4337),
    'Nc.Flag': (16, 2452, 2072),
    'Nc': (15, 2443, 1889),
    'Nc.Tower': (11, 2348, 2082),
    'Nc.G': (7, 2019, 1698),
    'Nc.Acc': (8, 1652, 1440),
    'Nc.Cut': (12, 1635, 1235),
    'Ov.Core': (7, 1429, 1132),
    'Nc.Price': (10, 1218, 913),
    'Nc.Tape': (8, 1212, 984),
    'Nc.Cat': (7, 1088, 907),
    'Nc.Hc': (3, 977, 821),
    'Nc.Cross': (9, 855, 606),
    'Nc.Sort': (4, 771, 661),
    'Nc.CaseI': (6, 765, 610),
    'Nc.Rate': (4, 450, 296),
    'Ov.Duality': (4, 426, 300),
    'Nc.End': (4, 324, 236),
    'Nc.Final': (1, 234, 186),
    'Nc.Vp': (2, 193, 147),
    'Nc.Plus': (2, 41, 7),
}
# directory -> the declaration lines that some numbered statement reaches by name
REACHED = {
    'Nc.Tow': 6939, 'NS1': 5924, 'Nc.Grp': 5325, 'Nc.Dl': 4090, 'Nc.Uni': 3668, 'Nc.Flag': 1834, 'Nc': 1693,
    'Nc.Tower': 1978, 'Nc.G': 1662, 'Nc.Acc': 1302, 'Nc.Cut': 1235, 'Ov.Core': 948, 'Nc.Price': 852, 'Nc.Tape': 619,
    'Nc.Cat': 757, 'Nc.Hc': 804, 'Nc.Cross': 588, 'Nc.Sort': 405, 'Nc.CaseI': 600, 'Nc.Rate': 227, 'Ov.Duality': 248,
    'Nc.End': 183, 'Nc.Final': 133, 'Nc.Vp': 147, 'Nc.Plus': 7,
}
# section -> directory -> the declaration lines its numbered statements reach there (each declaration once a section)
MATRIX = {
    'A': {'Ov.Core': 891, 'Nc.Price': 120, 'Nc.Rate': 5, 'Ov.Duality': 248},
    'B': {'Ov.Core': 225, 'Nc.Price': 109, 'Nc.Cross': 588, 'Nc.Rate': 5},
    'C': {'Ov.Core': 108, 'Nc.Price': 20, 'Nc.Cat': 740},
    'D': {'Nc.Flag': 594, 'Ov.Core': 104, 'Nc.Price': 20, 'Nc.Cat': 4},
    'E': {'NS1': 129, 'Nc.Flag': 13, 'Nc': 541, 'Nc.Tower': 19, 'Nc.Cut': 6, 'Ov.Core': 461, 'Nc.Price': 425,
        'Nc.Tape': 43, 'Nc.CaseI': 600, 'Nc.Rate': 18, 'Nc.Final': 11},
    'F': {'Nc.Flag': 1320, 'Nc.Tower': 51, 'Ov.Core': 112, 'Nc.Price': 9, 'Nc.Cat': 49, 'Nc.Vp': 125},
    'G': {'Nc.Tow': 70, 'Nc.Flag': 22, 'Nc.Tower': 95, 'Nc.G': 43, 'Nc.Cut': 6, 'Ov.Core': 303, 'Nc.Price': 292,
        'Nc.Tape': 43, 'Ov.Duality': 33, 'Nc.Vp': 142},
    'H': {'Nc.Tow': 6855, 'NS1': 107, 'Nc.Flag': 25, 'Nc': 265, 'Nc.Tower': 1943, 'Nc.G': 1262, 'Nc.Cut': 385,
        'Ov.Core': 112, 'Nc.Price': 27, 'Nc.Tape': 142, 'Nc.Cat': 15, 'Nc.Vp': 136, 'Nc.Plus': 4},
    'I': {'NS1': 165, 'Nc.Dl': 84, 'Nc.Uni': 3665, 'Nc.G': 280, 'Nc.Cut': 870, 'Nc.Tape': 584, 'Nc.Sort': 405},
    'J': {'Nc.Tow': 685, 'NS1': 2752, 'Nc.Grp': 5325, 'Nc.Dl': 4015, 'Nc.Uni': 3, 'Nc.Flag': 9, 'Nc': 174,
        'Nc.Tower': 69, 'Nc.G': 436, 'Nc.Cut': 387, 'Ov.Core': 182, 'Nc.Price': 9, 'Nc.Tape': 195, 'Nc.Cat': 15,
        'Nc.Vp': 6, 'Nc.Plus': 7},
    'K': {'Nc.Tow': 3, 'NS1': 3083, 'Nc.Dl': 4, 'Nc': 983, 'Nc.Tower': 19, 'Nc.Acc': 1204, 'Ov.Core': 109,
        'Nc.Price': 9, 'Nc.Tape': 51, 'Nc.Rate': 8, 'Nc.End': 183, 'Nc.Final': 25},
    'L': {'NS1': 129, 'Nc': 11, 'Ov.Core': 94, 'Nc.Price': 9, 'Nc.Hc': 10, 'Nc.Final': 111},
    'M': {'Nc.Tow': 3, 'NS1': 163, 'Nc.Flag': 4, 'Nc': 101, 'Ov.Core': 111, 'Nc.Price': 9, 'Nc.Tape': 141,
        'Nc.Hc': 804, 'Nc.CaseI': 6, 'Nc.Rate': 71, 'Nc.End': 32, 'Nc.Final': 122},
    'N': {'Nc.Tow': 6, 'NS1': 3163, 'Nc.Dl': 4, 'Nc.Uni': 118, 'Nc.Flag': 13, 'Nc': 992, 'Nc.Tower': 23,
        'Nc.Acc': 247, 'Nc.Cut': 10, 'Ov.Core': 465, 'Nc.Price': 324, 'Nc.Tape': 227, 'Nc.Hc': 237, 'Nc.CaseI': 229,
        'Nc.Rate': 227, 'Nc.End': 183, 'Nc.Final': 122},
}


def dir_of(module):
    p = module.split(".")
    return f"{p[0]}.{p[1]}" if p[0] in ("Nc", "Ov") and len(p) > 2 else p[0]


def build():
    src = vp.load()
    reread = "the Lean files of Nc, NS1 and Ov at FM_COMMIT (vp.closure)"
    dirs = collections.defaultdict(lambda: [0, 0, 0])
    for m, d in src.modules.items():
        if d["library"] in LIB_ACCENT:
            t = dirs[dir_of(m)]
            t[0] += 1; t[1] += d["lines"]
    for n, d in src.decls.items():
        if d["module"].split(".")[0] in LIB_ACCENT:
            dirs[dir_of(d["module"])][2] += d["lines"]
    compare("F5: files, lines and declaration lines per directory", DIRS,
            {k: tuple(v) for k, v in sorted(dirs.items(), key=lambda t: (-t[1][1], t[0]))}, reread)
    by_sec = collections.defaultdict(set)
    reached = set()
    for k, st in src.statements.items():
        if st["decls"]:
            cl = vp.closure(src, k)
            by_sec[st["section"]] |= cl
            reached |= cl
    matrix = {}
    for sec in sorted(by_sec):
        row = collections.Counter()
        for n in by_sec[sec]:
            dd = dir_of(src.decls[n]["module"])
            if dd in DIRS:
                row[dd] += src.decls[n]["lines"]
        if row:
            matrix[sec] = {dd: row[dd] for dd in DIRS if row[dd]}
    compare("F5: the lines each section's statements reach in each directory", MATRIX, matrix, reread)
    got = collections.Counter()
    for n in reached:
        dd = dir_of(src.decls[n]["module"])
        if dd in DIRS:
            got[dd] += src.decls[n]["lines"]
    compare("F5: the declaration lines of each directory that some statement reaches", REACHED,
            {dd: got[dd] for dd in DIRS}, reread)
    t1 = {r["section"]: r for r in src.facts["table1"]}
    home = {}
    for dd in DIRS:
        col = {sec: MATRIX[sec].get(dd, 0) for sec in MATRIX}
        tot = sum(col.values())
        best = max(sorted(col), key=lambda sec: col[sec])
        home[dd] = (best, col[best], tot)
    heads = collections.defaultdict(list)
    for m, d in sorted(src.modules.items(), key=lambda t: (-t[1]["lines"], t[0])):
        if d["library"] in LIB_ACCENT and d["doc"]:
            h = d["doc"].split("\n")[0].lstrip("# ").strip()
            if h:
                heads[dir_of(m)].append(h)

    c = Canvas(ID, f"Where the formal work is: the {len(DIRS)} directories of Nc, NS1 and Ov, set against the "
               "sections of the paper whose statements reach them",
               f"Read from the Lean source of vp-vnp at formal-math {src.commit}. A cell is the lines of the "
               "declarations in a directory that a section's numbered statements reach by name, before they reach "
               "another statement's theorem: the formal work that section's own statements stand on there. The words "
               "in quotation marks are the files' docstrings.", W,
               sources=f"anthropics/formal-math {src.commit}, vp-vnp/{{Nc,NS1,Ov}}/**/*.lean, vp-vnp/Paper/*.lean, "
               "paper.pdf (Table 1, Table 3).", state=f"Drawn from formal-math {src.commit}")
    x0, y = c.x0, c.y
    total = sum(v[2] for v in DIRS.values())
    nreach = sum(REACHED.values())
    c.para(x0, y, c.x1 - x0, f"**How to read it.** The {sum(v[1] for v in DIRS.values())} lines of Nc, NS1 and Ov "
           f"hold {total} lines of declarations; {nreach} of them ({100 * nreach / total:.0f}%) are reached by name "
           "from some numbered statement. The rest are reached by nothing this reading sees: an instance, a `simp` "
           "lemma, a lemma a tactic finds, or code no statement uses. Each directory card names its home, the "
           "section whose statements reach most of it. " + vp.NOT_BUILT, S + 0.5, "muted")
    y += 70

    # ---- the matrix
    y += c.heading(x0, y, "Section against directory: the lines each section's own statements reach")
    order = list(DIRS)
    head = 330
    cw = (c.x1 - x0 - head) / len(order)
    for j, dd in enumerate(order):
        lib = dd.split(".")[0]
        lab = dd.split(".")[1] if "." in dd else ("(top)" if dd == "Nc" else dd)
        c.text(x0 + head + j * cw + cw / 2, y + 14, lib if dd != "NS1" else "", 11.5, "faint", anchor="middle")
        c.text(x0 + head + j * cw + cw / 2, y + 32, lab, 13, LIB_ACCENT[lib], anchor="middle", bold=True)
    y += 44
    rh = 34
    vmax = max(v for row in MATRIX.values() for v in row.values())
    for i, sec in enumerate(sorted(MATRIX)):
        ry = y + i * rh
        c.rect(x0, ry, c.x1 - x0, rh, "line", tint=False, rx=0, sw=0.6, fill_token="bg" if i % 2 == 0 else "zebra")
        acc = vp.CASE_ACCENT[t1[sec]["case"]]
        c.text(x0 + 10, ry + 22, f"**{sec}** {vp.abridge(t1[sec]['what'], 34)}", 12.5, acc)
        for j, dd in enumerate(order):
            v = MATRIX[sec].get(dd)
            if not v:
                continue
            cx = x0 + head + j * cw
            op = 0.18 + 0.82 * (v / vmax) ** 0.5
            lib = dd.split(".")[0]
            c.add(f'<rect x="{cx + 3:.1f}" y="{ry + 3:.1f}" width="{cw - 6:.1f}" height="{rh - 6}" rx="4" '
                  f'fill="{light(LIB_ACCENT[lib])}" class="f-{LIB_ACCENT[lib]}" fill-opacity="{op:.2f}"/>', ry + rh)
            c.text(cx + cw / 2, ry + 22, str(v), 12, "ink", anchor="middle", bold=home[dd][0] == sec)
    nrows = len(MATRIX)
    c.blocks.append((x0, y, c.x1, y + nrows * rh, "table matrix"))
    y += nrows * rh + 16
    c.para(x0, y, c.x1 - x0, "A cell's shade grows with its lines (by their square root); the number in bold is the "
           "directory's home. A declaration reached by two sections counts in both rows.", S, "muted")
    y += 50

    # ---- the directories
    y += c.heading(x0, y, f"The {len(DIRS)} directories, largest first")
    ncol = 5
    wcard = (c.x1 - x0 - (ncol - 1) * G) / ncol
    specs = []
    for dd in order:
        f, ln, dl = DIRS[dd]
        best, bl, tot = home[dd]
        share = f"{100 * bl / tot:.0f}%" if tot else "—"
        hs = heads.get(dd, [])[:3]
        specs.append(dict(
            name=dd if dd != "Nc" else "Nc, files at the top", accent=LIB_ACCENT[dd.split(".")[0]], pill=f"home {best} · {share}",
            bullets=[f"**{f} files**, {ln} lines, {dl} in declarations",
                     f"**Reached by name** {REACHED[dd]} of {dl} declaration lines ({100 * REACHED[dd] / dl:.0f}%)",
                     f"**Home** Section {best}, “{vp.abridge(t1[best]['what'], 60)}”: {bl} of the {tot} lines "
                     "the sections reach here"]
            + [f"“{h}”" for h in hs], anchor=f"dir-{dd.replace('.', '-')}"))
    for row in range(0, len(specs), ncol):
        chunk = specs[row:row + ncol]
        hh = max(vp.node(c, 0, 0, wcard, draw=False, size=S - 0.5, tsize=16, **sp) for sp in chunk)
        for i, sp in enumerate(chunk):
            vp.node(c, x0 + i * (wcard + G), y, wcard, h=hh, size=S - 0.5, tsize=16, **sp)
        y += hh + G
    y += 10

    # ---- the interpretation, computed
    strong = [dd for dd in order if home[dd][2] and home[dd][1] / home[dd][2] >= 0.8]
    shared = [dd for dd in order if home[dd][2] and home[dd][1] / home[dd][2] < 0.5]
    low = [dd for dd in order if REACHED[dd] / DIRS[dd][2] < 0.75]
    y += c.card(x0, y, c.x1 - x0, "An interpretation: most directories belong to one section",
                [f"In {len(strong)} of the {len(DIRS)} directories one section's statements reach at least 80% of the "
                 "lines the sections reach there: " + ", ".join(f"{dd} ({home[dd][0]})" for dd in strong) + ". "
                 f"In {len(shared)} no section reaches half: " + ", ".join(f"{dd}" for dd in shared) + ", shared work.",
                 f"Least reached by name: " + ", ".join(f"{dd} ({100 * REACHED[dd] / DIRS[dd][2]:.0f}%)" for dd in low)
                 + ". There the text reading sees least of how the code is used.",
                 "Computed from `MATRIX`, `REACHED` and `DIRS`, which the build checks."], accent="amber",
                size=S + 0.5) + 30
    c.para(x0, y, c.x1 - x0, "**Not checked here.** Whether a declaration reached by name is used: a name in a proof "
           "counts wherever it stands. Whether one that is not reached is used in a way the text does not show. A "
           "directory's home is where the most lines are reached, which says where its code is used from, not what "
           "it is about; its docstrings say that.", S + 0.5, "muted")
    return c
