"""strap2 -- host-side RECONSTRUCTION of STRAP II, from C22-6729.

>>> A RECONSTRUCTION.  IBM's program is lost; this follows its internals
>>> guide, in its phases and with its formats (docs/strap2/).  Whatever the
>>> guide does not fix is marked CHOSEN where it is decided. <<<

This is the executable specification for the 7030 STRAP II, as strap/smac.py
was for the 7030 SMAC, so the formats are bits wherever the guide gives them.
It is not strap_asm.py restructured.  What it takes from there is only the
facts the listings have verified: operation codes and field positions.
"""
import strap_asm as _a

from .cards import deck_cards
from .getfld import FieldError
from .pass1 import Pass1
from .pass2 import Pass2, Unresolved


class StrapError(_a.AssemblerError):
    pass


def compile_cards(cards, origin_bits=None, edition="N28-1081"):
    """All three phases.  Returns the Pass2 object, with its messages.  edition
    selects the flags' reading, pass2.EDITIONS."""
    p1 = Pass1(cards)
    try:
        p1.run()
    except FieldError as x:
        raise StrapError(f"message {x}, near card {p1.g.i}: {p1.g.card!r}")
    p2 = Pass2(p1, origin_bits, edition)
    p2.run()
    return p2


def assemble(source, origin_bits=None, strict=True):
    """The same result shape as strap_asm.assemble, so the verify_* oracles can
    run on it.  strict raises on the first message that STRAP II would have
    flagged as an error, which the shim needs in place of reading a listing."""
    p2 = compile_cards(deck_cards(source), origin_bits)
    if strict:
        # What would reject a COMPILGO's GO phase is COMREC 7.41 or 7.42 (p.8,
        # N28-1081 page 7).  This refuses more: every message the host marks
        # fatal (a host rule, CHOSEN: strap_asm's oracles expect an error to stop
        # the assembly), then 7.41.  7.42 is messages 1-7, all fatal here.
        for number, text, _unit, fatal in p2.msg.items:
            if fatal:
                raise StrapError(f"message {number}: {text}")
        if 41 in p2.comrec_errors():
            bad = {k: [n for n, _ in v] for k, v in p2.lists.items() if v and k != "unused"}
            st = p2.st
            ctg = [n for n, f in st.dictionary.items() if st.get(f, "ZSTCTG")]
            if ctg:
                bad["contagious"] = ctg
            raise StrapError(f"symbols in error (COMREC 7.41): {bad}")
    symtab = _a.SymTab()
    st = p2.st
    for name in st.sorted_names():
        f = st.dictionary[name]
        if st.get(f, "ZST26"):
            v = st.get(f, "ZVALB") + st.get(f, "ZVALI")
            symtab[name] = v
            if "*" in name:
                symtab.setdefault(name.split("*")[0], v)
    prog = _a.AssembledProgram(p2.image.words, symtab, p2.end_pc,
                               p2.image.reservations, p2.image.skips)
    prog.diagnostics = list(p2.image.diagnostics)
    prog.written_words = frozenset(w for w, m in p2.image._written.items() if m)
    prog.messages = list(p2.msg.items)
    return prog
