# hobbit/sem/demo.s -- hand-encoded demo for hobbit/sem/hobbit_sem.py
#
# The model prints one HRI (Hobbit Retirement Interface) line per retired
# instruction, or the unimplemented-instruction trap line.  HRI is the
# Hobbit analogue of riscv-formal's RVFI; this is a per-instruction trace
# comparison against the core, not a formal proof.
#
# This file is both the listing and the image.  The model's CLI reads one
# 8-hex-digit 32-bit word per line and ignores everything from a '#' on,
# so this file can be passed directly as --image.  Each word holds two
# 16-bit parcels: bits 31:16 are the even-address parcel, bits 15:0 the
# following odd-address parcel (big-endian, p. 1-4, Figure 1-2).
#
# Reference pre-state (from the parent checker):
#   PC = 0x00000000, SP = 0x00000100, MSP = 0x00000180, PSW = 0x00000200
#   (PSW bit 9 = 1 selects SP as CSP; Table 1-8 sheet 2, p. 1-15),
#   SHAD = 0x00000100, CONFIG = 0.  The model does not keep SHAD (no
#   modelled instruction reads it) and fixes CONFIG = 0 (PC extension off,
#   big-endian, caches/MMU irrelevant to this subset).
#
# Run:
#   python3 hobbit/sem/hobbit_sem.py --image hobbit/sem/demo.s \
#       --sp 0x100 --msp 0x180
#
# Cycle values are the Chapter 4 base times under the four p. 4-1
# assumptions, with A_CYC = 1, D_CYC = 2 and Q_CYC = 4 (model choices;
# p. 4-2 defines the symbols but prints no values).  Every cyc value below
# names the printed table and page in hobbit/sem/README.md; the base
# values are Table 4-32 (p. 4-3) except ENTER (Table 4-36, p. 4-5),
# conditional jumps (Table 4-35, p. 4-5) and the trap (Table 4-36).
#
# ---------------------------------------------------------------------------
# addr   parcels             PRM assembly        effect / why the cyc value
# ---------------------------------------------------------------------------
# 0x000: 0BF8                ENTER R-32          ; CSP=SP=0x100-32=0x0E0,
#                                               ; MSP stays 0x180: the flush
#                                               ; loop moves 0 blocks, so
#                                               ; cyc = 1 + Q*0 = 1 (Table 4-36
#                                               ; p. 4-5; loop pp. 3-19/3-20)
# 0x002: 7021                MOV $1, R4          ; word at CSP+4=0x0E4; cyc 1
# 0x004: 6022                MOV R4, R8          ; word at 0x0E8 = 1; cyc 1
# 0x006: 50A2                ADD $5, R8          ; 0x0E8 = 6, C=V=0; cyc 1
# 0x008: 041F                CALL 0x046          ; *(CSP)=*(0x0E0)=0x00A; cyc 1
# 0x00A: 6041                MOV R8, R4          ; after RETURN, 0x0E4=6; cyc 1
# 0x00C: A0DD 0008 0004      SUB R8, R4          ; 3-parcel; 0x0E4 = 0; cyc 1
# 0x012: 080B                POPN R32            ; SP=0x0E0+32=0x100; cyc 2
# 0x014: 4020                CMPEQ $1, R0        ; 1 == 0 is false, so F=0; cyc 1
# 0x016: 181B                JMPTN 0x04C         ; F=0, not taken; prediction N,
#                                               ; correct, folded into the
#                                               ; previous 1-parcel CMPEQ:
#                                               ; cyc 0 (Table 4-35)
# 0x018: 4020                CMPEQ $1, R0        ; F=0 again; cyc 1
# 0x01A: 1C03                JMPTY 0x020         ; F=0, not taken; prediction Y,
#                                               ; wrong, folded, jump directly
#                                               ; after compare: cyc 3
#                                               ; (Table 4-35, p. 4-5)
# 0x01C: 1002                JMPFN 0x020         ; F=0, taken; prediction N,
#                                               ; wrong, unfolded (previous is
#                                               ; a jump), 2nd instruction after
#                                               ; compare: cyc 2
# 0x01E: 2C02                NOP                 ; not reached (JMPFN taken)
# 0x020: 2C02                NOP                 ; fold target for the JMP below
# 0x022: 0C02                JMP 0x026           ; folded into the NOP: cyc 0
#                                               ; (Table 4-32 note, p. 4-3)
# 0x024: 2C02                NOP                 ; not reached
# 0x026: 0803                POPN R0             ; offset 0: SP unchanged; cyc 2
# 0x028: 0C01                JMP 0x02A           ; previous POPN cannot receive a
#                                               ; fold (opcode 0x02 is in the
#                                               ; p. 4-7 0x00..0x07 class): cyc 1
# 0x02A: 0803                POPN R0             ; cyc 2
# 0x02C: 1810                JMPTN 0x04C         ; F=0, not taken; prediction N,
#                                               ; correct, unfolded: cyc 1
# 0x02E: DFFD 0000 0000 0000 0000  .5 CMPEQ $0,R0 ; 5-parcel compare, F=1; cyc 1
# 0x038: 1802                JMPTN 0x03C         ; F=1, taken; prediction N, wrong;
#                                               ; previous is a 5-parcel
#                                               ; instruction, which cannot
#                                               ; receive a fold: cyc 3
# 0x03A: 2C02                NOP                 ; not reached
# 0x03C: 0803                POPN R0             ; cyc 2
# 0x03E: 1802                JMPTN 0x042         ; F=1, taken; prediction N, wrong,
#                                               ; unfolded, 3rd instruction after
#                                               ; compare: cyc 1 (Table 4-35)
# 0x040: 2C02                NOP                 ; not reached
# 0x042: 2C02                NOP                 ; cyc 1
# 0x044: 2C06                FLUSHD              ; unimplemented sequence (p. 3-22):
#                                               ; trap=1, store PC 0x044 at CSP,
#                                               ; cyc = 7 + A = 8
#                                               ; (Table 4-36, p. 4-5)
# 0x046: 0831                CATCH R192          ; MSP fills 0x180..0x19F -> 0x1A0;
#                                               ; cyc 1 (Table 4-36)
# 0x048: 70E3                MOV $7, R12         ; word at 0x0EC = 7; cyc 1
# 0x04A: 0802                RETURN R0           ; PC=*(0x0E0)=0x00A, SP unchanged;
#                                               ; cyc 2 (Table 4-32; no
#                                               ; indirection delay, p. 4-3)
# 0x04C:                     (end of image)      ; JMPTN targets land here; the
#                                               ; run stops at the image end or
#                                               ; at the trap above
# ---------------------------------------------------------------------------
0BF87021
602250A2
041F6041
A0DD0008
0004080B
4020181B
40201C03
10022C02
2C020C02
2C020803
0C010803
1810DFFD
00000000
00000000
18022C02
08031802
2C022C02
2C060831
70E30802
