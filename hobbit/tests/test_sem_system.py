#!/usr/bin/env python3
"""Unit tests for the reference model's privileged machine (hobbit_sem.System).

Each test drives ``sem/hobbit_sem.py`` with a ``System`` and a small RAM
bus, and checks one printed rule; the page is in the test.  The
encodings are hand-assembled from the PRM's tables (and agree with the
instructions s9term's `_startup` carries, docs/p9boot.md).

These features exist only with a ``System``: ``test_without_system_*``
pin that the user-level model still refuses them.

Discriminating checks, observed 2026-11-23.  Each injection was one edit
to ``sem/hobbit_sem.py``; this file and ``test_sem_extended.py`` were
run, and the file was put back by the reverse edit (its sha256 checked
equal).  ``test_sem_extended.py`` (the user-level model) stayed green
under every one of them.  Observed failures of this file:

* ``State.csp`` always SP: FAIL test_enter_call_and_operands_use_isp,
  ERROR test_trapped_niladic_uses_vb_plus_8 (the *(CSP) save).
* PX ignored (16-bit absolutes zero-extended): FAIL
  test_pc_extension_of_16_bit_absolutes.
* no R/M write-back to the PTE: FAIL test_paged_read_sets_r_write_sets_m.
* the event sequence not clearing PSW[15:0] before its stores: FAIL
  test_interrupt_sequence, FAIL test_write_to_read_only_page_is_exception_9,
  ERROR test_user_access_to_kernel_segment_faults (the user-level frame
  store faults, "reset").
* CRET without its CATCH fill: FAIL
  test_cret_fills_the_cache_under_the_new_psw.
* an SP write not setting MSP: FAIL test_sp_write_sets_msp_and_shad.
* the stack cache hit with CONFIG.SE = 0: FAIL
  test_stack_cache_disabled_without_config_se.
* trapped niladics through VB+12: FAIL test_trapped_niladic_uses_vb_plus_8.
* CRET's CATCH as a plain fill (no exception 8 on a fault): FAIL
  test_cret_catch_fault_is_exception_8_at_the_restored_pc.
* the vector read made at the PSW's level: FAIL
  test_kcall_from_user_level_uses_the_kernel_stack_and_vector, ERROR
  test_unimplemented_at_user_level_reads_the_vector.
* KCALL's frame stores made at the PSW's level: FAIL
  test_kcall_from_user_level_uses_the_kernel_stack_and_vector.
* no store check of ENTER's target (p. 3-21): FAIL
  test_enter_into_an_invalid_page_is_exception_8_and_restarts.
* System.cret_clamp ignored (2026-11-23, the clamp's two lines removed
  in a scratch copy): ERROR test_cret_msp_beyond_the_cache (the
  "unpredictable" refusal); MSP taken literally instead (no refusal, no
  clamp): FAIL test_cret_msp_beyond_the_cache ("Unsupported not raised",
  the default's refusal gone).
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "sem"))

import hobbit_sem as h  # noqa: E402

CPU = 0x2C00


class Ram:
    """A physical word store with byte lanes (mask bit 3 = bits 31:24)."""

    def __init__(self):
        self.m = {}
        self.writes = []

    def read(self, pa):
        return self.m.get(pa & ~3, 0)

    def write(self, pa, data, mask):
        self.writes.append((pa & ~3, data, mask))
        exp = 0
        for bit in range(4):
            if mask & (1 << bit):
                exp |= 0xFF << (8 * bit)
        old = self.m.get(pa & ~3, 0)
        self.m[pa & ~3] = (old & ~exp) | (data & exp)


def code(ram, addr, parcels):
    """Place parcels from `addr`: the even parcel is bits 31:16 (p. 1-4)."""
    for i, p in enumerate(parcels):
        a = addr + 2 * i
        w = ram.m.get(a & ~3, 0)
        if a & 2:
            w = (w & 0xFFFF0000) | p
        else:
            w = (w & 0x0000FFFF) | (p << 16)
        ram.m[a & ~3] = w


def machine(pc=0x1000, psw=h.PSW_SP, sp=0x800, msp=0x800, isp=0x400,
            vb=0x100, cache=False, config=0):
    ram = Ram()
    sysm = h.System(bus=ram, config=config)
    st = h.State(pc=pc, sp=sp, msp=msp, psw=psw, isp=isp, vb=vb,
                 system=sysm, cache=[0] * 64 if cache else None)
    return ram, sysm, st


class ControlRegisterTest(unittest.TestCase):
    def test_cpu_mov_immediate_to_config_and_back(self):
        # CPU; MOV $0x3F0000,%CONFIG (c6f7 003f 0000 0000 0004), then
        # CPU; MOV %CONFIG,R4 (867d 0004 0004) -- Table 1-22/1-24, p. 1-26.
        ram, sysm, st = machine()
        code(ram, 0x1000, [CPU, 0xC6F7, 0x003F, 0x0001, 0x0000, 0x0004,
                           CPU, 0x867D, 0x0004, 0x0004])
        rec, st = h.step(st)
        self.assertEqual(st.pc, 0x100C)         # CPU + five parcels
        self.assertEqual(sysm.config, 0x3F0000)  # bits 15:0 reserved
        self.assertTrue(st.config_kl)           # KL is bit 16
        rec, st = h.step(st)
        self.assertEqual(st.pc, 0x1014)
        self.assertEqual(ram.m[0x804], 0x3F0000)

    def test_sp_write_sets_msp_and_shad(self):
        # CPU; MOV $0x900,%SP -- "the MSP is updated with the same value"
        # (p. 1-13); SHAD follows the CSP (p. 1-16).
        ram, sysm, st = machine()
        code(ram, 0x1000, [CPU, 0x86F7, 0x0900, 0x0003])
        rec, st = h.step(st)
        self.assertEqual((st.sp, st.msp, sysm.shad), (0x900, 0x900, 0x900))

    def test_psw_write_does_not_move_shad(self):
        # CPU; MOV $0,%PSW: CSP becomes ISP, but SHAD is left for the
        # program to set (p. 1-15).
        ram, sysm, st = machine()
        sysm.shad = 0x800
        code(ram, 0x1000, [CPU, 0x86F7, 0x0000, 0x0005])
        rec, st = h.step(st)
        self.assertEqual(st.psw, 0)
        self.assertEqual(sysm.shad, 0x800)

    def test_register_write_at_user_level_is_exception_5(self):
        # p. 1-27: "if there is a register write in user mode, a privilege
        # violation exception sequence, exception ID 0x5, is performed".
        ram, sysm, st = machine(psw=h.PSW_SP | h.PSW_USER)
        ram.m[0x104] = 0x2000                   # *(VB+4): exception PC
        code(ram, 0x1000, [CPU, 0x86F7, 0x0000, 0x0005])
        rec, st = h.step(st)
        self.assertEqual(rec.trap, 1)
        self.assertEqual(st.pc, 0x2000)
        self.assertEqual(ram.m[0x400 - 12], h.EXC_PRIV)
        self.assertEqual(ram.m[0x400 - 8], 0x1000)   # the CPU's PC
        self.assertEqual(st.isp, 0x3F0)

    def test_register_0_is_exception_6(self):
        ram, sysm, st = machine()
        ram.m[0x104] = 0x2000
        code(ram, 0x1000, [CPU, 0x867D, 0x0000, 0x0004])
        rec, st = h.step(st)
        self.assertEqual(ram.m[0x400 - 12], h.EXC_REG)

    def test_pc_extension_of_16_bit_absolutes(self):
        # MOV *$0x74,*$0x8 (86cc 0074 0008) at 0x80001000 with CONFIG.PX:
        # bits 31:29 come from the PC (p. 1-23), so 0x80000074 -> 0x80000008.
        ram, sysm, st = machine(pc=0x80001000, config=h.CONFIG_PX)
        ram.m[0x80000074] = 0x12345678
        code(ram, 0x80001000, [0x86CC, 0x0074, 0x0008])
        rec, st = h.step(st)
        self.assertEqual(ram.m.get(0x80000008), 0x12345678)
        # Without PX the upper half is zero.
        ram, sysm, st = machine(pc=0x80001000)
        ram.m[0x74] = 0x9
        code(ram, 0x80001000, [0x86CC, 0x0074, 0x0008])
        rec, st = h.step(st)
        self.assertEqual(ram.m.get(0x8), 0x9)

    def test_without_system_cpu_is_refused(self):
        st = h.State(pc=0, sp=0x800, msp=0x800)
        st.memory[0] = (CPU << 16) | 0x86F7
        st.memory[4] = 0x00000003
        with self.assertRaises(h.Unsupported):
            h.step(st)


class InterruptStackPointerTest(unittest.TestCase):
    def test_enter_call_and_operands_use_isp(self):
        # PSW = 0: the ISP is the CSP (p. 1-12).  ENTER R-16 (0bfc) moves
        # ISP, not SP; MOV $1,R0 then stores at *(ISP); CALL stores the
        # return PC at *(ISP) (p. 3-9).
        ram, sysm, st = machine(psw=0)
        code(ram, 0x1000, [0x0BFC, 0x7020, 0x0402])  # ENTER; MOV $1,R0; CALL
        rec, st = h.step(st)
        self.assertEqual((st.isp, st.sp, st.msp), (0x3F0, 0x800, 0x800))
        self.assertEqual(sysm.shad, 0x3F0)
        self.assertTrue(st.psw & h.PSW_E)
        rec, st = h.step(st)
        self.assertEqual(ram.m[0x3F0], 1)
        rec, st = h.step(st)
        self.assertEqual(ram.m[0x3F0], 0x1006)
        self.assertEqual(st.pc, 0x1008)

    def test_return_and_popn_move_isp(self):
        # RETURN R16 (0806): PC = *(ISP+16), ISP += 16 (p. 3-40).
        ram, sysm, st = machine(psw=0, isp=0x3F0)
        ram.m[0x400] = 0x2222
        code(ram, 0x1000, [0x0806])
        rec, st = h.step(st)
        self.assertEqual((st.pc, st.isp, st.sp), (0x2222, 0x400, 0x800))

    def test_catch_is_a_no_op(self):
        # CATCH R16 (0805) with CSP = ISP is a no-op (p. 3-10).
        ram, sysm, st = machine(psw=0, sp=0x800, msp=0x800)
        code(ram, 0x1000, [0x0805])
        rec, st = h.step(st)
        self.assertEqual((st.sp, st.msp, st.isp), (0x800, 0x800, 0x400))

    def test_without_system_isp_is_refused(self):
        st = h.State(pc=0, sp=0x800, msp=0x800, psw=0)
        st.memory[0] = 0x0BFC0000
        with self.assertRaises(h.Unsupported):
            h.step(st)


def mmu(ram, stb=0x10000):
    """A segment table at `stb`: segment 0 nonpaged at 0 (1 MB, kernel,
    writable); segment 1 (0x400000) paged through a table at 0x20000."""
    ram.m[stb + 0] = h.STE_S | h.STE_W | h.STE_V | (0xFF << 12)
    ram.m[stb + 4] = 0x20000 | h.STE_V
    # page 0 of segment 1 -> 0x30000, writable, user; page 1 read-only.
    ram.m[0x20000] = 0x30000 | h.PTE_W | h.PTE_U | h.PTE_V
    ram.m[0x20004] = 0x31000 | h.PTE_V
    return stb


class MmuTest(unittest.TestCase):
    def setUp(self):
        self.ram, self.sysm, self.st = machine(
            psw=h.PSW_SP | h.PSW_VIRTUAL)
        self.sysm.stb = mmu(self.ram)
        self.ram.m[0x104] = 0x2000                 # exception vector

    def test_paged_read_sets_r_write_sets_m(self):
        # MOV *$0x400010,R4 (c6cd 0040 0010 0000 0004), then
        # MOV R4,*$0x400014 (c6dc 0000 0004 0040 0014): Table 2-3.
        self.ram.m[0x30010] = 0xCAFE
        code(self.ram, 0x1000, [0xC6CD, 0x0040, 0x0010, 0x0000, 0x0004,
                                0xC6DC, 0x0000, 0x0004, 0x0040, 0x0014])
        rec, st = h.step(self.st)
        self.assertEqual(self.ram.m[0x804], 0xCAFE)
        self.assertEqual(self.ram.m[0x20000] & (h.PTE_R | h.PTE_M), h.PTE_R)
        rec, st = h.step(st)
        self.assertEqual(self.ram.m[0x30014], 0xCAFE)
        self.assertEqual(self.ram.m[0x20000] & (h.PTE_R | h.PTE_M),
                         h.PTE_R | h.PTE_M)

    def test_write_to_read_only_page_is_exception_9(self):
        code(self.ram, 0x1000, [0xC6DC, 0x0000, 0x0004, 0x0040, 0x1000])
        rec, st = h.step(self.st)
        self.assertEqual(st.pc, 0x2000)
        self.assertEqual(self.ram.m[0x400 - 12], h.EXC_WRITE)
        self.assertEqual(self.ram.m[0x400 - 8], 0x1000)
        self.assertEqual(self.ram.m[0x400 - 4], h.PSW_SP | h.PSW_VIRTUAL)
        self.assertEqual(self.sysm.fault, 0x401000)      # p. 1-39
        self.assertEqual(st.psw, h.PSW_VIRTUAL)          # &= 0xFFFF0000
        self.assertEqual(self.sysm.shad, st.isp)
        self.assertNotIn(0x31000, self.ram.m)

    def test_nonpaged_bound_is_a_read_fault(self):
        # Segment 0's bound is 0xFF: page 0x100 (0x100000) is outside.
        code(self.ram, 0x1000, [0xC6CD, 0x0010, 0x0000, 0x0000, 0x0004])
        rec, st = h.step(self.st)
        self.assertEqual(self.ram.m[0x400 - 12], h.EXC_READ)
        self.assertEqual(self.sysm.fault, 0x100000)

    def test_user_access_to_kernel_segment_faults(self):
        self.st.psw |= h.PSW_USER
        code(self.ram, 0x1000, [0x2C02])           # NOP, fetched at user level
        rec, st = h.step(self.st)
        self.assertEqual(rec.trap, 1)
        self.assertIn("exception 0x7", rec.reason)

    def test_without_system_virtual_is_refused(self):
        st = h.State(pc=0, sp=0x800, msp=0x800,
                     psw=h.PSW_SP | h.PSW_VIRTUAL)
        st.memory[0] = 0x2C020000
        with self.assertRaises(h.Unsupported):
            h.step(st)


class EventTest(unittest.TestCase):
    def test_unimplemented_instruction_sequence_completes(self):
        # Three-parcel opcode 0x08 is unimp* (Table 1-18): *(CSP) = PC,
        # PC = *(VB+12); PSW and ISP unchanged (p. 1-39).
        ram, sysm, st = machine(psw=h.PSW_SP | h.PSW_E)
        ram.m[0x10C] = 0x3000
        code(ram, 0x1000, [0x88DD, 0x0000, 0x0004])
        rec, st = h.step(st)
        self.assertEqual(st.pc, 0x3000)
        self.assertEqual(ram.m[0x800], 0x1000)
        self.assertEqual((st.psw, st.isp), (h.PSW_SP | h.PSW_E, 0x400))

    def test_trapped_niladic_uses_vb_plus_8(self):
        ram, sysm, st = machine(psw=0)
        ram.m[0x108] = 0x3100
        code(ram, 0x1000, [0x2E00])                # niladic 0x200
        rec, st = h.step(st)
        self.assertEqual(st.pc, 0x3100)
        self.assertEqual(ram.m[0x400], 0x1000)     # *(CSP), CSP = ISP

    def test_interrupt_sequence(self):
        # p. 1-37: PC and PSW at ISP-8/-4, ISP -= 16, SHAD = ISP,
        # PC = *(VB + 16 + 4 x level), PSW &= 0xFFFF0000.
        ram, sysm, st = machine(psw=h.PSW_SP | (7 << 12) | h.PSW_F)
        sysm.shad = st.sp
        ram.m[0x100 + 16 + 24] = 0x4000
        self.assertTrue(h.interrupt_accepted(st, 6))
        h.take_interrupt(st, 6)
        self.assertEqual(ram.m[0x3F8], 0x1000)
        self.assertEqual(ram.m[0x3FC], h.PSW_SP | (7 << 12) | h.PSW_F)
        self.assertEqual((st.isp, sysm.shad, st.pc, st.psw),
                         (0x3F0, 0x3F0, 0x4000, 0))
        self.assertFalse(h.interrupt_accepted(st, 6))   # IPL 0: NMI only
        self.assertTrue(h.interrupt_accepted(st, 0))

    def test_kret_sets_shad_to_new_csp(self):
        ram, sysm, st = machine(psw=0, isp=0x3F0)
        ram.m[0x3F8] = 0x1234
        ram.m[0x3FC] = h.PSW_SP
        code(ram, 0x1000, [0x2C01])
        rec, st = h.step(st)
        self.assertEqual((st.pc, st.psw, st.isp, sysm.shad),
                         (0x1234, h.PSW_SP, 0x400, 0x800))

    def test_cret_fills_the_cache_under_the_new_psw(self):
        # CRET (2c05) into virtual mode: SP/MSP/PC/PSW from the ISP frame,
        # then the CATCH portion fills [SP, MSP) from memory, translated
        # with the restored PSW (p. 3-15).  Virtual 0x400020 is physical
        # 0x30020 through the paged segment.
        ram, sysm, st = machine(psw=0, cache=True,
                                config=h.CONFIG_SE)
        sysm.stb = mmu(ram)
        ram.m[0x400] = 0x400020
        ram.m[0x404] = 0x400040
        ram.m[0x408] = 0x2000
        ram.m[0x40C] = h.PSW_SP | h.PSW_VIRTUAL
        ram.m[0x30024] = 0x77
        isp = 0x400
        st.isp = isp
        code(ram, 0x1000, [0x2C05])
        rec, st = h.step(st)
        self.assertEqual((st.sp, st.msp, st.pc), (0x400020, 0x400040,
                                                  0x2000))
        self.assertEqual(sysm.shad, 0x400020)
        self.assertEqual(h._read_word(st, None, 0x400024), 0x77)
        self.assertEqual(st.cache[(0x400024 >> 2) & 63], 0x77)

    def test_cret_msp_beyond_the_cache(self):
        # 1e's notify() lowers the saved SP by 0x170 and leaves MSP: a
        # CRET frame with MSP - SP > 256, whose stack-cache results p. 1-13
        # calls unpredictable.  Refused by default; with System.cret_clamp
        # (a harness choice) the CATCH portion stops with the cache full
        # (p. 3-10) and MSP = SP + 256.
        for clamp in (False, True):
            ram, sysm, st = machine(psw=0, cache=True, config=h.CONFIG_SE)
            sysm.cret_clamp = clamp
            ram.m[0x400] = 0x2000                  # SP
            ram.m[0x404] = 0x2170                  # MSP: SP + 0x170
            ram.m[0x408] = 0x3000
            ram.m[0x40C] = h.PSW_SP
            ram.m[0x2004] = 0x1234                 # the handler's argument
            ram.m[0x2104] = 0x5678                 # its cache alias
            code(ram, 0x1000, [0x2C05])
            if not clamp:
                with self.assertRaises(h.Unsupported):
                    h.step(st)
                continue
            rec, st = h.step(st)
            self.assertEqual((st.sp, st.msp, st.pc), (0x2000, 0x2100,
                                                      0x3000))
            self.assertEqual(h._read_word(st, None, 0x2004), 0x1234)
            self.assertEqual(sysm.cret_clamps, 1)

    def test_cret_catch_fault_is_exception_8_at_the_restored_pc(self):
        # CRET whose CATCH portion meets an invalid page (p. 3-15): the
        # fill runs under the restored PSW, block by block from SP; the
        # block at 0x402000 (segment 1, page 2, no PTE) is a read fault,
        # exception 8 (p. 3-11), taken with the restored PC and PSW, MSP
        # at the blocks filled and SP the restored SP (SHAD = SP).
        ram, sysm, st = machine(psw=0, cache=True, config=h.CONFIG_SE)
        sysm.stb = mmu(ram)
        ram.m[0x104] = 0x5000                      # *(VB+4)
        ram.m[0x400] = 0x401FF0                    # SP
        ram.m[0x404] = 0x402010                    # MSP
        ram.m[0x408] = 0x2000                      # PC
        psw = h.PSW_SP | h.PSW_VIRTUAL
        ram.m[0x40C] = psw
        code(ram, 0x1000, [0x2C05])
        rec, st = h.step(st)
        self.assertEqual(st.pc, 0x5000)
        self.assertEqual((st.sp, st.msp), (0x401FF0, 0x402000))
        self.assertEqual(st.isp, 0x400)            # +16 by CRET, -16
        self.assertEqual(ram.m[0x404], h.EXC_READ)
        self.assertEqual(ram.m[0x408], 0x2000)
        self.assertEqual(ram.m[0x40C], psw)
        self.assertEqual(sysm.fault, 0x402000)
        self.assertEqual(st.psw, h.PSW_VIRTUAL)

    def test_kcall_from_user_level_uses_the_kernel_stack_and_vector(self):
        # KCALL $7 (0007) at user level: the frame goes to the ISP and the
        # vector is read at VB, both in a kernel-only segment (p. 3-29:
        # a fault there would reset the part, so the accesses are not
        # user-level accesses).
        ram, sysm, st = machine(pc=0x400000,
                                psw=h.PSW_SP | h.PSW_VIRTUAL | h.PSW_USER,
                                sp=0x400800, msp=0x400800)
        sysm.stb = mmu(ram)
        ram.m[0x100] = 0x5000                      # *(VB)
        code(ram, 0x30000, [0x0007])
        rec, st = h.step(st)
        self.assertEqual(rec.trap, 0)
        self.assertEqual(st.pc, 0x5000)
        self.assertEqual(ram.m[0x3F4], 28)
        self.assertEqual(ram.m[0x3F8], 0x400002)
        self.assertEqual(ram.m[0x3FC],
                         h.PSW_SP | h.PSW_VIRTUAL | h.PSW_USER)
        self.assertEqual(st.isp, 0x3F0)
        self.assertEqual(st.psw, h.PSW_VIRTUAL)

    def test_unimplemented_at_user_level_reads_the_vector(self):
        # p. 1-39: *(CSP) = PC (a user-level store, the user stack) and
        # PC = *(VB+12), read whatever the level (the table is in a
        # kernel-only segment here).  1e's trap.c relies on the vector
        # read succeeding (its _vector2/_vector3 fetch-fault case).
        ram, sysm, st = machine(pc=0x400000,
                                psw=h.PSW_SP | h.PSW_VIRTUAL | h.PSW_USER,
                                sp=0x400800, msp=0x400800)
        sysm.stb = mmu(ram)
        ram.m[0x10C] = 0x3000
        code(ram, 0x30000, [0x88DD, 0x0000, 0x0004])
        rec, st = h.step(st)
        self.assertEqual(st.pc, 0x3000)
        self.assertEqual(ram.m[0x30800], 0x400000)

    def test_enter_into_an_invalid_page_is_exception_8_and_restarts(self):
        # ENTER R-16 (0bfc) with SP = 0x403000: the target 0x402FF0 is in
        # segment 1's page 2, which has no PTE, so p. 3-21's store check
        # fails -> exception 8, FAULT = the target, SP unchanged (SHAD =
        # SP, the event's SP = SHAD), PC saved = the ENTER's: it restarts.
        ram, sysm, st = machine(pc=0x1000,
                                psw=h.PSW_SP | h.PSW_VIRTUAL,
                                sp=0x403000, msp=0x403000)
        sysm.stb = mmu(ram)
        sysm.shad = st.sp
        ram.m[0x104] = 0x5000
        code(ram, 0x1000, [0x0BFC])
        rec, st = h.step(st)
        self.assertEqual(rec.trap, 1)
        self.assertEqual(st.pc, 0x5000)
        self.assertEqual(ram.m[0x400 - 12], h.EXC_READ)
        self.assertEqual(ram.m[0x400 - 8], 0x1000)
        self.assertEqual(sysm.fault, 0x402FF0)
        self.assertEqual((st.sp, st.msp), (0x403000, 0x403000))
        # Into a valid page it completes.
        ram, sysm, st = machine(pc=0x1000,
                                psw=h.PSW_SP | h.PSW_VIRTUAL,
                                sp=0x400800, msp=0x400800)
        sysm.stb = mmu(ram)
        code(ram, 0x1000, [0x0BFC])
        rec, st = h.step(st)
        self.assertEqual((rec.trap, st.sp), (0, 0x4007F0))

    def test_stack_cache_disabled_without_config_se(self):
        # Table 1-2 bit 18: with SE = 0 an address in [SP, MSP) is memory.
        ram, sysm, st = machine(sp=0x800, msp=0x840, cache=True)
        ram.m[0x804] = 5
        st.cache[(0x804 >> 2) & 63] = 9
        self.assertEqual(h._read_word(st, None, 0x804), 5)
        sysm.config = h.CONFIG_SE
        self.assertEqual(h._read_word(st, None, 0x804), 9)

    def test_timer1_counts_instructions_and_overflows(self):
        # Table 1-2: bit 22 counts instructions, bit 24 enables the
        # overflow interrupt (0xFFFFFFFF -> 0).
        ram, sysm, st = machine(config=h.CONFIG_T1CI | h.CONFIG_T1IE)
        sysm.timer1 = 0xFFFFFFFF
        code(ram, 0x1000, [0x2C02, 0x2C02])
        rec, st = h.step(st)
        self.assertEqual(sysm.timer1, 0)
        self.assertTrue(sysm.timer1_pending)
        rec, st = h.step(st)
        self.assertEqual(sysm.timer1, 1)


if __name__ == "__main__":
    unittest.main()
