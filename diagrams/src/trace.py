"""A trace: one chain of uses between numbered statements, as cards in reading order, for the T posters.

build(ID, title, chain, why) checks that each step uses the next (vp.uses, read from the Lean text), draws each
statement in full (its header in the paper, its first Lean theorem's signature, the paper's words as that theorem's
docstring quotes them, and its other uses), and joins the cards with an arrow that says how the use was read."""
import vp
from vp import anchor_of, code, linked
from lib import Canvas

W = 1900
S = 14


def build(ident, title, subtitle, chain, how_read):
    src = vp.load()
    st = src.statements
    for a, b in zip(chain, chain[1:]):
        if b not in src.uses[a]:
            raise ValueError(f"{ident}: {a} no longer uses {b} in the Lean text: re-read the chain")
    if src.uses[chain[-1]]:
        raise ValueError(f"{ident}: {chain[-1]}, the chain's last step, now uses {list(src.uses[chain[-1]])}")
    case = {t["section"]: t["case"] for t in src.facts["table1"]}
    used_by = {k: [u for u in st if k in src.uses[u]] for k in chain}
    c = Canvas(ident, title, subtitle, W,
               sources=f"anthropics/formal-math {src.commit}, vp-vnp/Paper/*.lean, paper.pdf (Table 1, Table 3, the "
               "statement headers).", state=f"Drawn from formal-math {src.commit}")
    x0, y = c.x0, c.y
    c.para(x0, y, c.x1 - x0, how_read + " " + vp.NOT_BUILT, S, "muted")
    y += 100
    cw = c.x1 - x0 - 120
    cx = x0 + 120
    cols = vp.columns(cw, fsize=13)
    for i, k in enumerate(chain):
        r = st[k]
        d = src.decls[r["decls"][0]]
        h = r["header"] or {}
        title_k = h.get("title") or ("a display" if r["kind"] == "Display" else r["kind"].lower())
        nxt = chain[i + 1] if i + 1 < len(chain) else None
        others = [u for u in src.uses[k] if u != nxt]
        bullets = []
        if nxt:
            bullets.append(f"**Uses next** `{anchor_of(nxt)}`, " + ("named by its own Lean theorem" if
                           src.uses[k][nxt] == "direct" else "through helpers of the Paper library"))
        else:
            bullets.append("**Uses** no other numbered statement in the Lean text: the chain ends here")
        bullets.append("**Its other uses** " + (", ".join(f"`{anchor_of(u)}`" for u in others) or "none"))
        bullets.append("**Used by** " + (", ".join(f"`{anchor_of(u)}`" for u in used_by[k]) or
                                         "no numbered statement: Solution.lean names it"))
        url = vp.lean_url(src.full, d["file"], d["line"])
        foot = [f"**Lean** {linked(url, code(r['lean'][0], 40))} at {d['file']}:{d['line']}"
                + (f" · and {', '.join(code(n) for n in r['lean'][1:])}" if len(r["lean"]) > 1 else ""),
                f"**Paper** {k}" + (f", p. {h['page']}" if h.get("page") else "") + f" · Section {r['section']}, "
                f"{vp.CASE_LABEL[case[r['section']]]}"]
        spec = dict(name=f"{k} · {title_k}" if h.get("title") else k, accent=vp.CASE_ACCENT[case[r["section"]]], pill=f"step {i + 1}",
                    formula=vp.lean_block(d["signature"], cols, 10),
                    say=f"“{vp.abridge(r['quote'], 600)}”" if r["quote"] else None,
                    bullets=bullets, foot=foot, anchor=anchor_of(k))
        hh = vp.node(c, cx, y, cw, size=S, fsize=13, **spec)
        c.text(x0, y + 34, f"{i + 1}", 34, vp.CASE_ACCENT[case[r["section"]]], bold=True)
        y += hh
        if nxt:
            c.arrow([(cx + 60, y + 4), (cx + 60, y + 52)], "ink", sw=2.2,
                    dash=None if src.uses[k][nxt] == "direct" else "6 4")
            c.text(cx + 80, y + 33, "uses" + ("" if src.uses[k][nxt] == "direct" else ", through helpers"), S - 1,
                   "muted")
            y += 58
    return c
