"""T2 — The longest chain of uses through the flat case: from Corollary M.4 through Theorem E.11 down to
Definition A.1. The build fails if a step no longer uses the next, if the last step gains a use, if the chain differs
from CHAIN, or if it is no longer the longest that passes Theorem E.11."""
import functools

import trace
import vp
from vp import anchor_of

ID, SLUG = "T2", "trace-flat"

CHAIN = ["Corollary M.4", "Theorem M.3", "Theorem L.1", "Theorem E.11", "Proposition E.10", "Proposition E.9",
         "Lemma E.8", "Theorem C.1", "Proposition A.8", "Lemma A.2", "Definition A.1"]
THROUGH = "Theorem E.11"


def build():
    src = vp.load()

    @functools.lru_cache(None)
    def height(k):
        return 1 + max((height(u) for u in src.lean_uses[k]), default=0)

    i = CHAIN.index(THROUGH)
    tail = [THROUGH]
    while src.lean_uses[tail[-1]]:
        tail.append(max(src.lean_uses[tail[-1]], key=lambda k: (height(k), [-x for x in vp.order_key(k)])))
    if CHAIN[i:] != tail:
        raise ValueError(f"T2: the longest chain below {THROUGH} is {tail}, recorded {CHAIN[i:]}: re-read it")
    from d_t1_contracting import CHAIN as T1
    meet = next(k for k in CHAIN[i:] if k in T1)
    if meet != "Theorem C.1":                                           # the words "How to read it" says
        raise ValueError(f"T2: below {THROUGH} the chain first meets T1's at {meet}, not Theorem C.1")
    return trace.build(
        ID, f"The longest chain through the flat case, {len(CHAIN)} statements: from {CHAIN[0]} through "
        f"{THROUGH} down to {CHAIN[-1]}",
        "One step per card, in reading order: each numbered statement's header in the paper, its Lean theorem, the "
        "paper's words as that theorem's docstring quotes them, and the next statement, which its Lean proof uses.",
        CHAIN,
        f"**How to read it.** From the top, each statement's Lean proof uses the one below it. From "
        f"`{anchor_of(THROUGH)}`, the lower bound in the flat case, it is the longest chain of the uses read from the "
        "elaborated Lean; " + vp.poster("T1") + " is the longest chain of all, through the contracting case. "
        "The two meet at "
        f"`{anchor_of('Theorem C.1')}`. The colour is the case of the statement's section.")
