"""T1 — The longest chain of uses: fourteen statements from Corollary M.4 down to Definition A.1, through the
contracting case. The same chain R3 marks; the build fails if a step no longer uses the next, if the last step gains a
use, or if the chain differs from CHAIN."""
import trace
from vp import anchor_of

ID, SLUG = "T1", "trace-contracting"

CHAIN = ["Corollary M.4", "Theorem M.3", "Theorem L.1", "Theorem K.7", "Theorem K.6", "Proposition K.5", "Theorem J.4",
         "Theorem G.2", "Theorem F.6", "Proposition C.3", "Theorem C.1", "Proposition A.8", "Lemma A.2",
         "Definition A.1"]


def build():
    from d_r3_route import CHAIN as R3_CHAIN
    if CHAIN != R3_CHAIN:
        raise ValueError(f"T1: the chain is {CHAIN}, R3 marks {R3_CHAIN} as the longest: re-read both")
    secs = "".join(k.split(" ", 1)[1][0] for k in CHAIN[CHAIN.index("Theorem L.1") + 1:])
    if secs.rstrip("CA").strip("FGHIJK") or not secs.endswith("A"):     # the words "How to read it" says
        raise ValueError(f"T1: below L.1 the chain's sections are {secs}, not the contracting case, then C and A")
    return trace.build(
        ID, f"The longest chain of uses, {len(CHAIN)} statements through the contracting case: from "
        f"{CHAIN[0]} down to {CHAIN[-1]}",
        "One step per card, in reading order: each numbered statement's header in the paper, its Lean theorem, the "
        "paper's words as that theorem's docstring quotes them, and the next statement, which its Lean proof uses.",
        CHAIN,
        f"**How to read it.** From the top, each statement's Lean proof uses the one below it. It is the longest chain "
        f"of the uses in the elaborated Lean (R3 draws all of them). From `{anchor_of('Theorem L.1')}` it takes the "
        "contracting case down to its cuts and laws, and from there to the prices of Sections C and A. The colour is "
        "the case of the statement's section.")
