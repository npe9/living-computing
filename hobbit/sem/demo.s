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
# ---------------------------------------------------------------------------
# addr   parcels      PRM assembly and effect
# ---------------------------------------------------------------------------
# 0x000: 0BF8 7021    ENTER R-32            ; p. 3-19: CSP=SP=0x100-32=0x0E0,
#                                           ; MSP stays 0x180 (no flush), E=1
# 0x002:               MOV $1, R4           ; p. 3-32: word at CSP+4=0x0E4
# 0x004: 6022 50A2    MOV R4, R8           ; p. 3-32: word at 0x0E8 = 1
# 0x006:               ADD $5, R8           ; p. 3-5:  0x0E8 = 6, C=V=0
# 0x008: 040C 6041    CALL 0x020           ; p. 3-9:  *(CSP)=*(0x0E0)=0x00A
# 0x00A:               MOV R8, R4           ; p. 3-32: after RETURN, 0x0E4=6
# 0x00C: A0DD 0008    SUB R8, R4           ; p. 3-43: 0x0E4 = 6-6 = 0
# 0x010: 0004 080B    (SUB dest field 4)   ;  ^ 3-parcel: 0xA0DD 0x0008 0x0004
# 0x012:               POPN R32             ; p. 3-38: SP=0x0E0+32=0x100,
#                                           ; MSP stays 0x1A0 (new SP < MSP)
# 0x014: 1C04 1003    JMPTY 0x01C          ; p. 3-28: F=0, not taken
# 0x016:               JMPFN 0x01C          ; p. 3-28: F=0, taken
# 0x018: 2C02 2C02    NOP                  ; p. 3-35 (not reached)
# 0x01A:               NOP                  ; p. 3-35 (not reached)
# 0x01C: 2C02 2C06    NOP                  ; p. 3-35
# 0x01E:               FLUSHD               ; p. 3-22: unimplemented in HW;
#                                           ; trap line, *(CSP)=PC, p. 1-39
# 0x020: 0831 70E3    CATCH R192           ; p. 3-10: MSP fills 0x180..0x19F,
#                                           ; new MSP=0x1A0 (two quad-words)
# 0x022:               MOV $7, R12          ; p. 3-32: word at 0x0EC = 7
# 0x024: 0802 2C02    RETURN R0            ; p. 3-40: PC=*(0x0E0)=0x00A,
#                                           ; SP unchanged (offset 0)
# 0x026:               NOP                  ; p. 3-35 (not reached)
# ---------------------------------------------------------------------------
0BF87021
602250A2
040C6041
A0DD0008
0004080B
1C041003
2C022C02
2C022C06
083170E3
08022C02
