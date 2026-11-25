"""F7 — The two vocabularies: the paper's coined terms (Appendix P) and the other words the Lean uses for them
(Appendix Q.3), each counted in the Lean's declaration names and in its source text.

Appendix P lists the terms the paper coins or uses in a special sense, and where each is defined; Appendix Q.3 says
the Lean development says gauge for an upper functional, unit for a packet, and so on. This poster reads both
(src/paper-facts.json) and counts each word in the Lean at FM_COMMIT: in the declaration names, split at dots,
underscores and capitals, and in the whole source text, comments included, as a word or its plural. The build fails
if the glossary's terms or places, the renamings, or any count differ from what is recorded here."""
import re

import vp
from vp import compare
from lib import Canvas

ID, SLUG = "F7", "vocabulary"

W = 3080
S = 13.5

GLOSSARY = [('wire ⟨q⟩uv', '§A'), ('spectral point φ', 'Def. A.1'), ('gφ(P), dφ(u, v)', 'Lemma A.2'),
 ('price; |xy|', 'Def. A.4'), ('hub', 'Lemma A.3'), ('price space', '§C'), ('clause sum', '§E'),
 ('complete network; fk,ℓ', '§E'), ('load', '§G'), ('law; slot; channel', 'Def. G.1'), ('packet', '§H'),
 ('network; node tensor; value; outcome', '§H'), ('run; weight; tally', '§I'), ('instance z; sum(z)', '§I'),
 ('τ-plain', '§I'), ('tape automaton', '§I'), ('accelerator', 'Def. K.1')]
RENAMES = [('gauge', 'upper functional'), ('unit', 'packet'), ('table', 'node tensor'), ('bill', 'tally'),
 ('near pair', 'edge'), ('window', 'box'), ('state', 'symbol')]
IN_NAMES = {'accelerator': 0,
 'bill': 1,
 'box': 1,
 'channel': 0,
 'clause sum': 3,
 'complete network': 0,
 'edge': 17,
 'gauge': 15,
 'hub': 8,
 'instance': 0,
 'law': 14,
 'load': 12,
 'near pair': 0,
 'network': 1,
 'node tensor': 0,
 'outcome': 2,
 'packet': 0,
 'plain': 6,
 'price': 108,
 'price space': 0,
 'run': 35,
 'slot': 15,
 'spectral point': 0,
 'state': 3,
 'sum': 217,
 'symbol': 0,
 'table': 3,
 'tally': 0,
 'tape automaton': 0,
 'unit': 28,
 'upper functional': 0,
 'value': 4,
 'weight': 3,
 'window': 7,
 'wire': 15}
IN_TEXT = {'accelerator': 34,
 'bill': 175,
 'box': 0,
 'channel': 87,
 'clause sum': 8,
 'complete network': 5,
 'edge': 215,
 'gauge': 62,
 'hub': 172,
 'instance': 89,
 'law': 209,
 'load': 276,
 'near pair': 18,
 'network': 30,
 'node tensor': 0,
 'outcome': 60,
 'packet': 0,
 'plain': 96,
 'price': 217,
 'price space': 5,
 'run': 1057,
 'slot': 144,
 'spectral point': 42,
 'state': 150,
 'sum': 1278,
 'symbol': 17,
 'table': 101,
 'tally': 0,
 'tape automaton': 2,
 'unit': 681,
 'upper functional': 0,
 'value': 279,
 'weight': 139,
 'window': 45,
 'wire': 142}


def name_words(name):
    out = []
    for part in re.split(r"[._]", name):
        out += [w.lower() for w in re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+", part)]
    return out


def term_words(term):
    """The words a glossary term is searched by: each part between semicolons, letters only, words of three letters
    or more (so the notation, `⟨q⟩uv`, `sum(z)`, is left out)."""
    out = []
    for part in term.split(";"):
        ws = [w.lower() for w in re.sub(r"[^A-Za-z ]+", " ", part).split() if len(w) >= 3]
        if ws:
            out.append(" ".join(ws))
    return out


def head(phrase):
    """The paper's word in a renaming: 'an edge of the Cayley graph of Uh' -> edge, 'the boxes of …' -> box."""
    p = re.sub(r"^(an?|the) ", "", phrase)
    p = re.split(r" of | as well as", p)[0]
    w = p.split()
    last = w[-1][:-2] if w[-1].endswith("xes") else (w[-1][:-1] if w[-1].endswith("s") else w[-1])
    return " ".join(w[:-1] + [last])


def build():
    src = vp.load()
    f = src.facts
    reread = "Appendices P and Q.3 of paper.pdf (src/paper-facts.json)"
    compare("F7: the glossary's terms and where each is defined", GLOSSARY,
            [(g["term"], g["defined"]) for g in f["glossary"]], reread)
    compare("F7: the renamings of Appendix Q.3", RENAMES, [(a, head(b)) for a, b in f["q3"]["words"]["pairs"]], reread)
    names = [name_words(n) for n in src.decls]
    raw = " ".join(p.read_text(encoding="utf-8").lower() for p in sorted(vp.VP.rglob("*.lean")) if ".lake" not in p.parts)
    words = sorted({w for g in f["glossary"] for w in term_words(g["term"])} | {w for p in RENAMES for w in p})
    in_names = {w: sum(1 for nw in names if any(nw[i:i + len(w.split())] == w.split() for i in range(len(nw))))
                for w in words}
    in_text = {w: len(re.findall(r"\b" + r"\s+".join(map(re.escape, w.split())) + r"s?\b", raw)) for w in words}
    compare("F7: the declaration names that use each word", IN_NAMES, in_names, "the Lean files at FM_COMMIT")
    compare("F7: each word's occurrences in the Lean source", IN_TEXT, in_text, "the Lean files at FM_COMMIT")

    c = Canvas(ID, "The two vocabularies: the paper's coined terms and the Lean's own words for them, each counted "
               "in the Lean's names and text",
               "Read from Appendix P, the paper's glossary of coined terms, and Appendix Q.3's list of the other words "
               f"the Lean uses (pinned in src/paper-facts.json), and from the Lean source of vp-vnp at formal-math "
               f"{src.commit}. The words in quotation marks are the paper's.", W,
               sources=f"anthropics/formal-math {src.commit}, vp-vnp/paper.pdf (Appendices P and Q.3), "
               "vp-vnp/**/*.lean.", state=f"Drawn from formal-math {src.commit}")
    x0, y = c.x0, c.y
    c.para(x0, y, c.x1 - x0, "**How to read it.** A count in names is the number of declarations whose name, split at "
           "dots, underscores and capitals, contains the word (`NodeTable` has node and table). A count in text is the "
           "number of times the word or its plural stands in the Lean files, comments and docstrings included; for "
           "instance it includes Lean's keyword `instance`, and for sum and run every ordinary use. A zero says the Lean "
           "never writes the word. " + vp.NOT_BUILT, S + 0.5, "muted")
    y += 70

    y += c.heading(x0, y, "1 · Appendix Q.3: the words the Lean uses instead")
    cols = [("The Lean says", 260), ("for the paper's", 1000), ("paper's word", 260),
            ("Lean's word: in names", 260), ("in text", 220), ("paper's word: in names", 280), ("in text", 220)]
    cols[-1] = ("in text", c.x1 - x0 - sum(w for _, w in cols[:-1]))
    rows = []
    for (lw, pw), (_, phrase) in zip(RENAMES, f["q3"]["words"]["pairs"]):
        rows.append({"cells": [f"**{lw}**", f"“{phrase}”", pw, str(IN_NAMES[lw]), str(IN_TEXT[lw]), str(IN_NAMES[pw]),
                               str(IN_TEXT[pw])], "accent": "teal" if IN_TEXT[pw] < IN_TEXT[lw] else "amber"})
    y += c.table(x0, y, cols, rows, size=S) + 20
    fewer = [lw for lw, pw in RENAMES if IN_TEXT[pw] < IN_TEXT[lw]]
    never = [pw for lw, pw in RENAMES if IN_TEXT[pw] == 0]
    y += c.card(x0, y, c.x1 - x0, "An interpretation: the Lean writes its own word",
                [f"For {len(fewer)} of the {len(RENAMES)} renamings the Lean's word stands more often in its source than "
                 f"the paper's (teal rows); the paper's word is never written for " + ", ".join(never) + ". Computed "
                 "from `IN_TEXT`, which the build checks."], accent="amber", size=S + 0.5) + 40

    y += c.heading(x0, y, f"2 · Appendix P: the {len(GLOSSARY)} coined terms, where the paper defines them, and the Lean")
    cols = [("Term", 380), ("Its meaning (Appendix P)", 1260), ("Defined in", 170), ("Searched as", 300),
            ("In names", 160), ("In text", c.x1 - x0 - 2270)]
    rows = []
    for g in f["glossary"]:
        ws = term_words(g["term"])
        rows.append({"cells": [f"**{g['term']}**", f"“{g['meaning']}”", g["defined"],
                               "\n".join(ws) or "notation only", "\n".join(str(IN_NAMES[w]) for w in ws) or "—",
                               "\n".join(str(IN_TEXT[w]) for w in ws) or "—"],
                     "accent": "red" if ws and all(IN_TEXT[w] == 0 for w in ws) else None})
    y += c.table(x0, y, cols, rows, size=S) + 30
    c.para(x0, y, c.x1 - x0, "**Not checked here.** That a word in the Lean means what the term means in the paper: a "
           "count says the word is written, not what it names. The glossary's formulas are set as the PDF's text "
           "gives them, superscripts inline (vH for v^H).", S + 0.5, "muted")
    return c
