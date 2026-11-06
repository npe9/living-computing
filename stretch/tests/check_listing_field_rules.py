#!/usr/bin/env python3
"""A bare integer in a shift or Add Immediate to Exponent is a signed
11-bit count; E-I defaults to unnormalized; a null VFL address is 0;
an alphabetic entry mode's terminator may be "("; a DR with no dds is
a DR(N); an indicator-bit system symbol carries (BU,1,8).

COUNT.  C28-6129 printed p.33 (PDF p.37), the address-environment
table, category 4: "Signed 11-Bit Address ... of shift and Add
Immediate to Exponent instructions ... Integer counts number of bits
in shift or number of bits to be added to exponent of floating point
word".  MCP printed p.356 line 42 prints "E-I,48" as 014000.57 60 and
p.357 line 29 prints "SHFR,4" as 001000.37 20: the count sits 7 bits
up the word field.  strap_asm took the integer as a WORD address
(000060, 000004) unless it carried a written sign.

DEFAULT.  C28-6129 printed p.46 (PDF p.50): for E+I, E-I, E+AI and
E-AI "The unnormalized mode is given unless overruled by dds = (N)".
strap_asm gave the default only to the unmodified mnemonic E+I, so
E-I assembled normalized (.17 for the printed .57).

NULL ADDRESS.  C28-6129 printed p.4 (PDF p.8): "A major field may be
null even if other non-null fields follow"; its VFL drop-out ends at
"OP (dds), A".  MCP printed p.357 line 44 prints "CV(BU,48)" -- no
address at all -- as address 000000.00.  strap_asm refused it ("CV
needs an address field") and aborted the deck.

TERMINATOR.  C28-6129 printed p.29 (PDF p.33): "(Az)DD(BU, FL, BS),
alphabetic information to "z"" -- z is any one character.  MCP printed
p.360 lines 38-47 print "(A()DD(BU),..." because their data hold "*";
strap_asm's prefix scan counted parentheses and refused the card.

DR DEFAULT.  C28-6129 printed p.18 (PDF p.22): "If no dds is given, the
symbol appearing in the name field is assigned the normalized floating
point use mode", and a floating use mode "is forced to begin at a full
word address".  MCP printed p.363 line 33 "J FLD B DRZ,(12)" prints a
twelve-word reservation at 234560.00, up from 234557.40; strap_asm
crashed on it (IndexError on stmt.mods[0]).

INDICATOR DDS.  C28-6129 printed p.11 (PDF p.15): system symbols of
classes 1-3 "are assigned standard data descriptions with mode BU, byte
size 8 and a field length equal to the length of the particular
register or bit".  MCP printed p.373 line 12 prints "CM1111,Z ASU IN"
(Z ASU IN SYN,$PG5, p.376) with length 1, 001000.36 F0; strap_asm gave
$PG5 no dds and assembled 000000.36.

CHECKS
  e_minus_i_48_as_printed    E-I,48      -> 014000.57 60  (p.356 l.42)
  shfr_4_as_printed          SHFR,4      -> 001000.37 20  (p.357 l.29)
  shfl_u_1_as_printed        SHFL(U),1   -> 000200.67 20  (F212)
  signed_count_unchanged     E+I(U),-1791 -> 677700.47 60 (F213XA)
  bit_address_unchanged      SHFL(U),128.0 -> 000200.67 20 (F212 decks)
  cv_null_address_is_zero    CV(BU,48) assembles as CV(BU,48),0
  paren_terminator           (A()DD(BU),1*  2( assembles as (A$)...$
  dr_no_dds_is_dr_n          DRZ,(12) after a half word places what
                             follows as DRZ(N),(12) does
  dr_u_aligns_as_n           DRZ(U),(12) aligns to a word as (N) does
  indicator_syn_is_bu_1      CM1111,Z with Z SYN,$PG5 = CM1111(BU,1),$PG5
  indicator_direct_is_bu_1   CM1111,$PG5 = CM1111(BU,1),$PG5

MEASURED INJECTIONS (python3 check_listing_field_rules.py --inject):
    control, assembler as is               PASS
    bare integers back to word addresses   FAIL e_minus_i_48_as_printed,
                                                shfr_4_as_printed,
                                                shfl_u_1_as_printed
    default read off the unstripped op     FAIL e_minus_i_48_as_printed
    null address refused again             FAIL cv_null_address_is_zero
    the "(" terminator rule removed        FAIL paren_terminator
    the DR default removed                 FAIL dr_no_dds_is_dr_n
    word alignment back to mode N only     FAIL dr_u_aligns_as_n
    indicator dds removed                  FAIL indicator_syn_is_bu_1,
                                                indicator_direct_is_bu_1
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))

BARE = """                                          or base.strip().isdigit()):\n"""
FAM = """            fp_mode = 'U' if _fam in ('E+', 'E+I') else 'N'\n"""
NULL = """            stmt.fields = ["0"] + list(stmt.fields[1:])\n"""
IND = """        return 'BU,1,8'\n    return None\n"""
UALIGN = """        return (64 if _mode in ('N', 'U') else 0), \\\n"""
DRDEF = """            stmt.mods = ['N'] + list(stmt.mods[1:])\n"""
TERM = """    if m:\n        entry, text = text[1:m.end() - 1], text[m.end():]\n"""


def half(asm, card):
    """The half word at 100.0 as the listing prints it, or the error."""
    try:
        p = asm.assemble("        SLC, 100.0\n        " + card + "\n")
    except Exception as e:
        return "ERROR " + str(e)
    w = p.words.get(0o144, 0) >> 32
    return f"{w >> 14:06o}.{(w >> 8) & 63:02o} {w & 255:02X}"


def word(asm, card):
    try:
        p = asm.assemble("        SLC, 100.0\n        " + card + "\n")
    except Exception as e:
        return "ERROR " + str(e)
    return oct(p.words.get(0o144, 0))


def _w(asm, src):
    try:
        p = asm.assemble(src + "\n")
    except Exception as e:
        return "ERROR " + str(e)
    return oct(p.words.get(0o144, 0))


def main(asm):
    fails = 0

    def check(name, got, want):
        nonlocal fails
        ok = got == want and not got.startswith("ERROR")
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} {name} = {got}" + ("" if ok else f" expected {want}"))

    check("e_minus_i_48_as_printed", half(asm, "E-I,48"), "014000.57 60")
    check("shfr_4_as_printed", half(asm, "SHFR,4"), "001000.37 20")
    check("shfl_u_1_as_printed", half(asm, "SHFL(U),1"), "000200.67 20")
    check("signed_count_unchanged", half(asm, "E+I(U), -1791"), "677700.47 60")
    check("bit_address_unchanged", half(asm, "SHFL(U), 128.0"), "000200.67 20")
    check("cv_null_address_is_zero", word(asm, "CV(BU,48)"),
          word(asm, "CV(BU,48),0"))
    check("paren_terminator",
          word(asm, "(A()DD(BU),1*  2("), word(asm, "(A$)DD(BU),1*  2$"))
    def after(dr):
        try:
            p = asm.assemble("        SLC, 100.0\n        B,0\nX       " + dr
                             + "\nY       DD(BU,64),7\n")
        except Exception as e:
            return "ERROR " + str(e)
        return " ".join(oct(a) for a, v in sorted(p.words.items()) if v == 7)
    check("dr_no_dds_is_dr_n", after("DRZ,(12)"), after("DRZ(N),(12)"))
    ind = "Z       SYN,$PG5\n        SLC, 100.0\n        "
    check("indicator_syn_is_bu_1", _w(asm, ind + "CM1111,Z"),
          _w(asm, ind + "CM1111(BU,1),$PG5"))
    check("indicator_direct_is_bu_1", _w(asm, ind + "CM1111,$PG5"),
          _w(asm, ind + "CM1111(BU,1),$PG5"))
    check("dr_u_aligns_as_n", after("DRZ(U),(12)"), after("DRZ(N),(12)"))
    print("ALL TESTS PASSED" if not fails else f"{fails} TEST(S) FAILED")
    return fails


def patched(old, new):
    import types
    path = os.path.join(HERE, "..", "strap", "strap_asm.py")
    src = open(path).read()
    assert src.count(old) == 1, old
    m = types.ModuleType("strap_asm_injected")
    m.__file__ = path
    exec(compile(src.replace(old, new), path, "exec"), m.__dict__)
    return m


if __name__ == "__main__":
    import strap_asm
    if sys.argv[1:] == ["--inject"]:
        res = [("control", main(strap_asm))]
        print("-- injected: bare integers back to word addresses")
        res.append(("bare", main(patched(BARE, "                                          ):\n"))))
        print("-- injected: default read off the unstripped op")
        res.append(("default", main(patched(FAM, "            fp_mode = 'U' if base_op in ('E+', 'E+I') else 'N'\n"))))
        print("-- injected: null address refused again")
        res.append(("null", main(patched(NULL, '            raise AssemblerError(f"{op} needs an address field", stmt.lineno)\n'))))
        print('-- injected: the "(" terminator rule removed')
        res.append(("term", main(patched(TERM, "    if False:\n        pass\n"))))
        print("-- injected: the DR default removed")
        res.append(("drdef", main(patched(DRDEF, "            pass\n"))))
        print("-- injected: word alignment back to mode N only")
        res.append(("ualign", main(patched(UALIGN, "        return (64 if _mode == 'N' else 0), \\\n"))))
        print("-- injected: indicator dds removed")
        res.append(("ind", main(patched(IND, "        return None\n    return None\n"))))
        print("INJECTIONS: " + ", ".join(f"{n} -> {'FAIL' if r else 'PASS'}" for n, r in res))
    else:
        sys.exit(main(strap_asm))
