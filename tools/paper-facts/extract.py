#!/usr/bin/env python3
"""Read the facts the posters need from the paper, vp-vnp/paper.pdf at FM_COMMIT, into diagrams/src/paper-facts.json.

    uv run --with pypdf==7.1.1 --with pymupdf==2.1 python tools/paper-facts/extract.py [VP_VNP_DIR]

VP_VNP_DIR is the vp-vnp folder of a formal-math checkout (default: $VP_VNP, else ../vp-np). The paper exists only as
a PDF, and the standard library cannot read one, so this script is run once per move of FM_COMMIT, outside the build;
the build reads the JSON it writes, which diagrams/src/vp.py pins by its hash (PAPER_FACTS_SHA256) and by the hash of
the PDF it was read from (PAPER_SHA256). It writes, from the text pypdf extracts:

- table1: Table 1 of the paper, "Map of the proof": for each section A to O, what it proves, the sections it uses,
  and the case it serves (flat, contracting or both), as printed.
- table3: Table 3, "The Lean theorems that belong to the numbered statements": for each numbered statement of
  Sections A to N, its kind, its number and the Lean theorems (prefix Paper.) the table names, as printed and
  with a range such as "lem_toolkit_a to _f" spelled out; Remark N.6 has none ("not formalized").
- headers: for each statement of table3, the paper's own header for it in the text: the page and the title in
  parentheses, where the header has one.
- intro: the numbered statements of Sections 1 and 2, whose headers name their Lean theorem in parentheses.

It stops with an error, writing nothing, when a table does not parse as these expect: a row it cannot read, a
section of table1 out of order, a statement of table3 with no header in the text. tools/paper-facts/meta.json
records the commit, the PDF's hash, the pypdf version and the output's hash.
"""
import hashlib
import importlib.metadata
import json
import os
import pathlib
import re
import subprocess
import sys
import unicodedata

import pypdf

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "diagrams" / "src" / "paper-facts.json"
META = ROOT / "tools" / "paper-facts" / "meta.json"
KINDS = ("Theorem", "Lemma", "Proposition", "Corollary", "Definition", "Remark", "Display")
SECTIONS = "ABCDEFGHIJKLMNO"


def plain(s):
    """A title or a cell as plain text: the paper's math italic letters, which pypdf returns as Mathematical
    Alphanumeric Symbols (U+1D400 to U+1D7FF) and as ℎ (U+210E, the italic h that block leaves out), become plain
    ones by NFKC (𝑈𝑛 -> Un), every other character is kept
    (ℓ stays ℓ), and runs of white space become one space."""
    if s is None:
        return None
    s = "".join(unicodedata.normalize("NFKC", ch) if 0x1D400 <= ord(ch) <= 0x1D7FF or ch == "ℎ" else ch for ch in s)
    s = re.sub("[\ufe00-\ufe0f]", "", s)               # variation selectors (∑︀): invisible, and in no font
    s = re.sub("\u0338\\s*=", " ≠", s).replace("=\u0338", "≠")   # the PDF sets ≠ as a slash before =: u̸ = v
    return re.sub(r"\s+", " ", s).strip()


def fail(msg):
    sys.exit(f"extract: {msg}")


def pages(pdf):
    r = pypdf.PdfReader(str(pdf))
    return [p.extract_text() or "" for p in r.pages]


def table1(text):
    """The rows between the header "Section what is proved uses case" and the caption "Table 1."."""
    m = re.search(r"^Section what is proved uses case\n(.*?)^Table 1\. ", text, re.M | re.S)
    if not m:
        fail("no Table 1 (the header 'Section what is proved uses case')")
    rows = []
    for ln in m.group(1).splitlines():
        r = re.fullmatch(r"([A-O]) (.+?) ((?:[A-O](?:, [A-O])*)|–) (both|flat|contracting)", ln.strip())
        if not r:
            fail(f"Table 1: a row that does not parse: {ln!r}")
        uses = [] if r.group(3) == "–" else r.group(3).split(", ")
        rows.append({"section": r.group(1), "what": plain(r.group(2)), "uses": uses, "case": r.group(4)})
    if [r["section"] for r in rows] != list(SECTIONS):
        fail(f"Table 1: sections {[r['section'] for r in rows]}, expected A to O in order")
    return rows


def expand(names):
    """'lem_toolkit_a to _f' -> lem_toolkit_a ... lem_toolkit_f."""
    out = []
    for n in names:
        r = re.fullmatch(r"(\w+_)([a-z]) to _([a-z])", n)
        if r:
            out += [r.group(1) + chr(c) for c in range(ord(r.group(2)), ord(r.group(3)) + 1)]
        else:
            out.append(n)
    return out


def table3(text):
    """The rows between the header "Statement Lean (prefix Paper.)" and the caption "Table 3.". The table is printed
    in two columns, each with the header; a row's Lean names may wrap onto the next lines."""
    m = re.search(r"^Statement Lean \(prefix Paper\.\)\n(.*?)^Table 3\. ", text, re.M | re.S)
    if not m:
        fail("no Table 3 (the header 'Statement Lean (prefix Paper.)')")
    body = m.group(1).replace("Statement Lean (prefix Paper.)\n", "")
    rows, section = [], None
    row_re = re.compile(r"(" + "|".join(KINDS) + r") ((?:[A-O]\.\d+)|\(([A-O])\.\d+\)) (.+)")
    for ln in body.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        s = re.fullmatch(r"(?:Section|Appendix) ([A-O])", ln)
        if s:
            section = s.group(1)
            continue
        r = row_re.fullmatch(ln)
        if r:
            num = r.group(2)
            sec = num.strip("()")[0]
            if sec != section:
                fail(f"Table 3: {r.group(1)} {num} under Section {section}")
            rows.append({"kind": r.group(1), "number": num, "section": sec, "printed": r.group(4)})
            continue
        if not rows:
            fail(f"Table 3: a line before the first row: {ln!r}")
        rows[-1]["printed"] += " " + ln          # a wrapped Lean cell
    for r in rows:
        p = re.sub(r"\s+", " ", r["printed"]).replace(" _", "_") if "to _" not in r["printed"] else \
            re.sub(r"\s+", " ", r["printed"])
        r["printed"] = p
        if p == "not formalized":
            r["lean"] = []
            continue
        names = [n.strip() for n in p.split(",")]
        if not all(re.fullmatch(r"\w+( to _[a-z])?", n) for n in names):
            fail(f"Table 3: {r['kind']} {r['number']}: Lean cell {p!r} is not a list of names")
        r["lean"] = expand(names)
    return rows


def headers(page_texts, rows):
    """For each statement of table3, its header in the text: the first line that starts with its kind and number
    followed by a title in parentheses or a full stop."""
    out = {}
    for r in rows:
        if r["kind"] == "Display":
            continue
        key = f"{r['kind']} {r['number']}"
        pat = re.compile(r"^" + re.escape(key) + r"(?: \(([^\n]*?)\))?\.", re.M)
        for i, t in enumerate(page_texts):
            m = pat.search(t)
            if m:
                out[key] = {"page": i + 1, "title": plain(m.group(1))}
                break
        else:
            fail(f"no header in the text for {key}")
    return out


def intro(text):
    """The numbered statements of Sections 1 and 2: 'Theorem 1.1 (main theorem; thm_allfields).'"""
    out = []
    for m in re.finditer(r"^(" + "|".join(KINDS) + r") ([12]\.\d+) \((?:([^;)]*); )?(\w+)\)\.", text, re.M):
        out.append({"kind": m.group(1), "number": m.group(2), "title": plain(m.group(3)), "lean": m.group(4)})
    if not out:
        fail("no numbered statement in Sections 1 and 2")
    return out


REF = re.compile(r"\b(Theorem|Lemma|Proposition|Corollary|Definition|Remark) ([A-O]\.\d+)")


def prose(s):
    """A passage of the text as one line: a word broken at a line end is joined (devel-\nopment -> development;
    a hyphen at a line end before a lower-case letter is taken to be a break), then as plain()."""
    return plain(re.sub(r"-\n(?=[a-z])", "", s))


def refs(s):
    """The numbered statements a passage names, in order of first mention, as 'Theorem H.2'."""
    out = []
    for m in REF.finditer(s.replace("\n", " ")):
        k = f"{m.group(1)} {m.group(2)}"
        if k not in out:
            out.append(k)
    return out


def notes(text, page_texts, rows):
    """Every "Formalization note." of the text: its page; the note itself, up to the first line that ends with a
    full stop (a page's running head inside it is dropped); the last statement header and the last subsection
    heading before it; and the statements it names."""
    starts = []
    for r in rows:
        if r["kind"] == "Display":
            continue
        key = f"{r['kind']} {r['number']}"
        m = re.search(r"^" + re.escape(key) + r"(?: \(([^\n]*?)\))?\.", text, re.M)
        starts.append((m.start(), key))
    starts.sort()
    subs = [(m.start(), m.group(1), plain(m.group(2))) for m in
            re.finditer(r"^([A-O]\.\d+)\. ([A-Z][^.\n]*?)\.", text, re.M)]
    page_at = []
    pos = 0
    for i, t in enumerate(page_texts):
        page_at.append(pos)
        pos += len(t) + 1
    out = []
    for m in re.finditer(r"^Formalization note\. ", text, re.M):
        lines = []
        for ln in text[m.end():].split("\n"):
            if re.fullmatch(r"VP ̸= VNP \d+|\d+ CLAUDE", ln.strip()):
                continue
            lines.append(ln)
            if ln.rstrip().endswith("."):
                break
            if len(lines) > 6:
                fail(f"a formalization note at offset {m.start()} does not end within six lines")
        body = prose("\n".join(lines))
        after = [k for o, k in starts if o < m.start()][-1]
        sub = [(n, t) for o, n, t in subs if o < m.start()][-1]
        page = max(i for i, o in enumerate(page_at) if o <= m.start()) + 1
        out.append({"page": page, "text": body, "after": after, "subsection": f"{sub[0]} {sub[1]}",
                    "names": refs(body)})
    if not out:
        fail("no formalization note in the text")
    return out


def between(text, start, end, what):
    m = re.search(re.escape(start) + r"(.*?)" + re.escape(end), text, re.S)
    if not m:
        fail(f"no passage {what}: from {start!r} to {end!r}")
    return m.group(1)


def appendix_q(text):
    """The passages of the overview and of Appendix Q that say where the proof rests on the Lean and what is not on
    the route of Solution's theorems, each quoted whole and with the statements it names."""
    lean_only = between(text, "The proofs\nof ", " describe machines", "naming the proofs that only Lean checks")
    overview = "The printed proofs differ in completeness. " + prose(between(
        text, "The printed proofs differ in completeness. ", "\nTable 1 shows", "of the overview on the printed proofs"))
    off = between(text, "with these exceptions, which are not on that route:\n", ". Many unnumbered",
                  "of Appendix Q.3 on the route")
    routes = between(text, "Routes of proof. The theorems of the main route follow the references between the "
                     "printed\nproofs, with these exceptions.\n", "\nThe proofs of Proposition A.5",
                     "of Appendix Q's routes of proof")
    library = between(text, "Some steps exist only under names of the underlying library and not as\ntheorems "
                      "with prefix Paper. ", " Lean proofs can be\ncoarser", "on steps only in the library")
    not_lean = between(text, "Not in Lean. ", "\nComments in the Lean files", "on what is not in Lean")
    return {
        "overview": overview,
        "overview_lean": refs(lean_only),
        "off_route": {"text": prose(off), "names": refs(off), "definitions": prose(off).endswith("the definitions")},
        "routes": [prose(b) for b in routes.split("∙") if b.strip()],
        "library_only": prose(library),
        "not_in_lean": prose(not_lean),
    }


def figure1(text):
    """Figure 1, "The structure of the proof": the Lean names its boxes and arrows print, in the order pypdf reads
    them, and its caption. Where its arrows run is not in the text; the poster that draws it records that itself."""
    body = between(text, "Common part: tensors over the field k.\n", "\nFigure 1. The structure of the proof.",
                   "of Figure 1")
    names = []
    for n in re.findall(r"\b(?:thm|lem|prop|cor|def)_[a-z_]+\b", body):
        if n not in names:
            names.append(n)
    caption = prose("The structure of the proof." + between(text, "\nFigure 1. The structure of the proof.",
                                                            " (Section 2.5).", "the caption of Figure 1")
                    + " (Section 2.5).")
    return {"names": names, "caption": caption, "theorem": "Theorem 1.1" if "\nTheorem 1.1\n" in body + "\n" else None}


SINGULAR = {"Theorems": "Theorem", "Lemmas": "Lemma", "Propositions": "Proposition", "Corollaries": "Corollary",
            "Definitions": "Definition"}


def refs_all(s):
    """refs(), and plural lists too: 'Theorems M.3 and N.5' -> Theorem M.3, Theorem N.5."""
    s = s.replace("\n", " ")
    out = []
    pl = re.compile(r"\b(Theorems|Lemmas|Propositions|Corollaries|Definitions) ((?:[A-O]\.\d+(?:, and |, | and ))+"
                    r"[A-O]\.\d+)")
    marks = []
    for m in pl.finditer(s):
        for num in re.findall(r"[A-O]\.\d+", m.group(2)):
            marks.append((m.start(), f"{SINGULAR[m.group(1)]} {num}"))
    for m in REF.finditer(s):
        marks.append((m.start(), f"{m.group(1)} {m.group(2)}"))
    for _, k in sorted(marks):
        if k not in out:
            out.append(k)
    return out


LEAN_NAME = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-zA-Z0-9]+)+\b")


def lean_names(s):
    out = []
    for n in LEAN_NAME.findall(s):
        if n not in out:
            out.append(n)
    return out


def paper_names(page_texts):
    """Every Lean name the paper prints (a word with an underscore, which only the typewriter names have), with
    the pages it is printed on."""
    pages = {}
    for i, t in enumerate(page_texts):
        for n in LEAN_NAME.findall(t):
            pages.setdefault(n, [])
            if i + 1 not in pages[n]:
                pages[n].append(i + 1)
    return [{"name": n, "pages": pages[n]} for n in sorted(pages)]


def q3_more(text):
    """Appendix Q.3 beyond the route: the renamings, the universes, the stronger forms, and its list of differences
    between the statements of the text and of the Lean, bullet by bullet."""
    # pypdf sets the page of Table 3 inside this sentence: cut that page, from its running head to the next one
    flow = re.sub(r"VP ̸= VNP \d+\nStatement Lean \(prefix Paper\.\).*?belong to the numbered statements\.\n\d+ CLAUDE\n",
                  "", text, flags=re.S)
    words = prose(between(flow, "The Lean development uses some other words. It says ", ". The other differences",
                          "of Appendix Q.3 on the Lean's words"))
    pairs = []
    for item in re.split(r", and |, (?=[a-z]+(?: [a-z]+)? for )", words):
        m = re.fullmatch(r"([a-z]+(?: [a-z]+)?) for (.+)", item.strip())
        if not m:
            fail(f"Appendix Q.3: a renaming that does not read 'X for Y': {item!r}")
        pairs.append([m.group(1), m.group(2)])
    uni = prose(between(text, "The exception is the given field in ", ", which may lie in any universe",
                        "of Appendix Q.3 on universes"))
    stronger = prose(between(text, "∙ Lemmas ", " are\nproved in stronger or more general forms",
                             "of Appendix Q.3 on stronger forms"))
    body = between(text, "Statements. The statements differ in the following points.\n", "\nRoutes of proof.",
                   "of Appendix Q.3's differences")
    bullets = []
    for b in body.split("∙"):
        if b.strip():
            t = prose(re.sub(r"\n(=== page \d+|VP ̸= VNP \d+|\d+ CLAUDE)(?=\n)", "", b))
            bullets.append({"text": t, "names": refs_all(t), "lean": lean_names(t)})
    return {"words": {"text": words, "pairs": pairs},
            "universes": {"text": uni, "names": refs_all(uni)},
            "stronger": {"text": "Lemmas " + stronger, "names": refs_all("Lemmas " + stronger)},
            "differences": bullets}


KEY = r"(?:[^\W\d_]|\+)+\d\d[a-z]?"                  # a reference key: letters (Bür, vM, BCS+), two digits, a letter


def references(text):
    """The reference list, entry by entry (key, text, year), and every citation of a key in the rest of the text,
    with the part of the paper it stands in (Section 1, 2 or 3, or an appendix by its letter)."""
    body = between(text, "\nReferences\n", "\nAppendix: the full proof", "of the reference list")
    body = re.sub(r"\n(=== page \d+|VP ̸= VNP \d+|\d+ CLAUDE)(?=\n)", "", body)
    entries = []
    for m in re.finditer(r"^\[(" + KEY + r")\] (.*?)(?=^\[" + KEY + r"\] |\Z)", body, re.M | re.S):
        t = prose(m.group(2))
        two = re.search(r"\d\d", m.group(1)).group(0)          # a key's digits are its year's last two
        years = []
        for y, end in re.findall(r"\b((?:1[89]|20)\d\d)(?:/(\d\d))?\b", t):    # a volume year may be 1996/97
            years += [y] if y.endswith(two) else ([y[:2] + end] if end == two else [])
        if not years:
            fail(f"reference [{m.group(1)}] prints no year ending in {two}")
        entries.append({"key": m.group(1), "text": t, "year": int(years[-1])})
    keys = {e["key"] for e in entries}
    start = text.index("\nReferences\n")
    end = text.index("\nAppendix: the full proof")
    heads = [(m.start(), m.group(1)) for m in re.finditer(r"^([123])\. [A-Z]", text, re.M)]
    heads += [(m.start(), m.group(1)) for m in re.finditer(r"^Appendix ([A-Q])\. ", text, re.M)]
    heads.sort()
    cites = []
    for m in re.finditer(r"\[([^\[\]]{2,160})\]", text):          # a group may break across a line
        if start <= m.start() < end:
            continue
        found = [k for k in re.findall(KEY, m.group(1)) if k in keys]
        if not found:
            continue
        part = [h for o, h in heads if o < m.start()]
        for k in found:
            cites.append({"key": k, "part": part[-1] if part else "front"})
    if not entries or not cites:
        fail("no references or no citations")
    return {"entries": entries, "citations": cites}


def glossary(pdf):
    """Appendix P, "Glossary of coined terms", by the columns of its table: each row's term, meaning and where it is
    defined. PyMuPDF gives every character's box; a space is put where two characters of a line are further apart
    than a fifth of the font size (the PDF has no space after a letter of a formula), a line ending in a hyphen joins
    the next without one, and a term continues onto the next line when its line ends with ';'."""
    import pymupdf
    doc = pymupdf.open(str(pdf))
    lines = []
    for pno in range(len(doc)):
        page = doc[pno]
        words = page.get_text("words")
        hdr = {w[4]: w for w in words if w[4] in ("term", "meaning", "defined")}
        if set(hdr) != {"term", "meaning", "defined"} or abs(hdr["term"][1] - hdr["meaning"][1]) > 2:
            continue
        top = hdr["term"][3]
        stop = min([w[1] for w in words if w[4] == "Appendix" and w[1] > top] + [1e9])
        cuts = (hdr["meaning"][0] - 4, hdr["defined"][0] - 4)
        rows = {}
        for block in page.get_text("rawdict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    for ch in span["chars"]:
                        x0, y0, x1, y1 = ch["bbox"]
                        if top < y0 and y1 < stop - 1:
                            rows.setdefault(round(y1), []).append((x0, x1, ch["c"], span["size"]))
        merged = {}
        for y in sorted(rows):                          # a sub- or superscript sits off the line: same line within 5 pt
            key = next((k for k in merged if abs(k - y) <= 5), y)
            merged.setdefault(key, []).extend(rows[y])
        for y in sorted(merged):
            cols = ["", "", ""]
            last = [None, None, None]
            for x0, x1, c, size in sorted(merged[y]):
                col = 0 if x0 < cuts[0] else (1 if x0 < cuts[1] else 2)
                if last[col] is not None and x0 - last[col] > 0.2 * size and not cols[col].endswith(" ") and c != " ":
                    cols[col] += " "
                cols[col] += c
                last[col] = x1
            lines.append(tuple(re.sub(r"\s+", " ", t).strip() for t in cols))
    if not lines:
        fail("no Appendix P table")
    out, prev = [], ""
    for term, meaning, where in lines:
        if term and not prev.endswith(";"):
            out.append({"term": term, "meaning": meaning, "defined": where})
        else:
            if not out:
                fail(f"Appendix P: a line before the first term: {term!r} {meaning!r}")
            r = out[-1]
            r["term"] = (r["term"] + " " + term).strip()
            r["meaning"] = (r["meaning"][:-1] + meaning if r["meaning"].endswith("-") else
                            r["meaning"] + " " + meaning).strip()
            r["defined"] = (r["defined"] + " " + where).strip()
        if term:
            prev = term
    for r in out:
        for k in r:
            r[k] = plain(r[k])
        if not re.fullmatch(r"§[A-O]|(Def\.|Lemma) [A-O]\.\d+", r["defined"]):
            fail(f"Appendix P: {r['term']!r} is defined in {r['defined']!r}, not a section or a statement")
    return out


def main(argv):
    src = pathlib.Path(argv[0] if argv else os.environ.get("VP_VNP") or ROOT.parent / "vp-np")
    pdf = src / "paper.pdf"
    if not pdf.is_file():
        fail(f"no paper.pdf in {src}")
    commit = subprocess.run(["git", "-C", str(src), "rev-parse", "HEAD"], capture_output=True, text=True,
                            check=True).stdout.strip()
    texts = pages(pdf)
    text = "\n".join(texts)
    t3 = table3(text)
    facts = {"table1": table1(text), "table3": t3, "headers": headers(texts, t3), "intro": intro(text),
             "pages": len(texts), "notes": notes(text, texts, t3), "appendix_q": appendix_q(text), "figure1": figure1(text),
             "paper_names": paper_names(texts), "q3": q3_more(text), "references": references(text),
             "glossary": glossary(pdf)}
    data = json.dumps(facts, indent=1, ensure_ascii=False, sort_keys=True) + "\n"
    OUT.write_text(data, encoding="utf-8")
    meta = {"commit": commit, "file": "vp-vnp/paper.pdf",
            "paper_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(), "pypdf": pypdf.__version__,
            "pymupdf": importlib.metadata.version("pymupdf"),
            "output": OUT.relative_to(ROOT).as_posix(),
            "output_sha256": hashlib.sha256(data.encode("utf-8")).hexdigest()}
    META.write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(facts['table1'])} sections, {len(t3)} statements, "
          f"{len(facts['intro'])} in Sections 1 and 2, {len(facts['notes'])} formalization notes, read at {commit[:10]}")
    print(f"  PAPER_SHA256 = \"{meta['paper_sha256']}\"")
    print(f"  PAPER_FACTS_SHA256 = \"{meta['output_sha256']}\"")


if __name__ == "__main__":
    main(sys.argv[1:])
