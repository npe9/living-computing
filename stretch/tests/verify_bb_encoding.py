#!/usr/bin/env python3
"""verify_bb_encoding.py -- field-by-field check of the BRANCH ON BIT
(BB family) encoding against the exact bit positions StretchDecode.bsv
reads.

BRANCH ON BIT is a full-word instruction (X22-6533 pocket card
"BRANCH ON BIT -- Strap Format: OP,B,(I),A(K)"; semantics Reference
Manual p.41). The decoder (StretchDecode.decodeFullWord) identifies it
by the 9-bit literal 111000000 at IBM bits 51-59 and unpacks:

    bit address  IBM 0-23   (BSV w[63:40])   -- a.addr from vflAddrOf
    literal 1000 IBM 24-27  (BSV w[39:36])
    index  I     IBM 28-31  (BSV w[35:32])   -- a.i1 from vflAddrOf
    branch addr  IBM 32-50  (BSV w[31:13])   -- addr2
    literal      IBM 51-59  (BSV w[12:4])    -- 111000000
    modAbc[2:1]  IBM 60-61  (BSV w[3:2])     -- set-modifier
    modAbc[0]    IBM 62     (BSV w[1])       -- branch-condition bit
    idx  K       IBM 63     (BSV w[0])       -- X1 flag for branch addr

This proves the assembler and the model's decoder agree on the layout.
Per AGENTS.md rule 2 it does NOT prove the shared reading of the format
is correct -- a printed-listing cross-check against a real BB line
(jb_af1c uses BB for sign tests) remains an open item.

Exit status is nonzero on any mismatch, so run_tests.sh can gate on it.
"""
import sys
from strap_asm import assemble
from opcodes import BB_CODES


def decode(w):
    """Unpack a 64-bit BB word exactly as StretchDecode.bsv does."""
    return {
        'bitaddr': (w >> 40) & 0xFFFFFF,   # IBM 0-23
        'lit1000': (w >> 36) & 0xF,        # IBM 24-27
        'i1':      (w >> 32) & 0xF,        # IBM 28-31
        'addr19':  (w >> 13) & 0x7FFFF,    # IBM 32-50
        'lit9':    (w >> 4)  & 0x1FF,      # IBM 51-59
        'mod':     (w >> 2)  & 0x3,        # IBM 60-61
        'cond':    (w >> 1)  & 0x1,        # IBM 62
        'idxK':    w & 0x1,                # IBM 63
    }


def main():
    # One program exercising all eight mnemonics plus the two index
    # forms (K on the branch address, I on the bit address).
    lines = ['        SLC, (8)2000.0']
    for m in BB_CODES:
        lines.append(f'        {m}, 10.4, TGT')
    lines.append('        BB,  7.63, TGT($X1)')   # branch index K = 1
    lines.append('        BBN, 5.0($X3), TGT')    # bit-address index I = 3
    lines.append('TGT     BEW, $')
    lines.append('        END, TGT')
    prog = assemble('\n'.join(lines))
    words = [prog.words[wa] for wa in sorted(prog.words)]
    names = list(BB_CODES) + ['BB(K)', 'BBN(I)']

    failures = 0

    def check(cond, msg):
        nonlocal failures
        if not cond:
            failures += 1
            print(f"  FAIL: {msg}")

    for i, name in enumerate(names):
        d = decode(words[i])
        base = name.split('(')[0]
        emod, econd = BB_CODES[base]
        check(d['lit9'] == 0b111000000, f"{name}: identifying literal (IBM 51-59) is {d['lit9']:#b}, not 111000000")
        check(d['lit1000'] == 0b1000, f"{name}: literal (IBM 24-27) is {d['lit1000']:#b}, not 1000")
        check(d['mod'] == emod, f"{name}: modifier (IBM 60-61) is {d['mod']:02b}, expected {emod:02b}")
        check(d['cond'] == econd, f"{name}: condition (IBM 62) is {d['cond']}, expected {econd}")
        print(f"  {name:8} bitaddr={d['bitaddr']:#08x} i1={d['i1']} "
              f"addr19={d['addr19']:#06x} mod={d['mod']:02b} cond={d['cond']} K={d['idxK']}")

    # Field-placement spot checks: the index and address fields land in
    # the right bits.
    check(decode(words[names.index('BB')])['bitaddr'] == 10 * 64 + 4,
          "bit address 10.4 did not encode as word 10, bit 4")
    check(decode(words[names.index('BB(K)')])['idxK'] == 1,
          "K flag (branch-address index) not set by TGT($X1)")
    check(decode(words[names.index('BB(K)')])['bitaddr'] == 7 * 64 + 63,
          "bit address 7.63 did not encode as word 7, bit 63")
    check(decode(words[names.index('BBN(I)')])['i1'] == 3,
          "bit-address index I not set to 3 by 5.0($X3)")

    if failures:
        print(f"verify_bb_encoding: {failures} mismatch(es)")
        return 1
    print("verify_bb_encoding: all BB encoding field checks pass")
    return 0


if __name__ == '__main__':
    sys.exit(main())
