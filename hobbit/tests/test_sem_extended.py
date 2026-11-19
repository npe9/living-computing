#!/usr/bin/env python3
"""Unit tests for the instructions added to the one-instruction model.

These are not golden traces: they drive ``sem/hobbit_sem.py`` directly and
assert the printed operation and flag rules, including the cases the
new goldens do not reach (overflow, tagged operands, divide by zero, the
DQM row selection, the kernel transfers and the one-parcel row-11
shifts).  The page in each assertion is the manual page the rule comes
from.

Discriminating check, observed 2026-11-19: dropping DIV's sign
application (``quotient = -quotient`` replaced by a no-op) made this file
fail 2 of its 27 tests, and ``tests/hri_check.py`` on golden 008 reported
``line 2 field DATA: dut=0x00000003 spec=0xfffffffd pc=0x0002`` --
the predicted signed-quotient failure and nothing else in that trace.
The injection was reverted by the reverse edit; the suite was green
before and after.

Second injection, same day: moving KCALL's source-word store from
``ISP-12`` to ``ISP-16`` (both forms) made exactly one test fail --
``test_kcall_frame_and_isp`` with ``KeyError: 52`` on ``memory[0x34]``,
the printed ``*(ISP-12) = src`` of p. 3-29 -- and nothing else.  Also
reverted by the reverse edit.

Third injection, same day: setting ``PSW.F`` from carry instead of
overflow in TADD/TSUB made exactly
``test_tadd_sets_carry_and_overflow_then_flag_from_overflow`` and
``test_tsub_borrow_and_overflow`` fail (2 of 30), and nothing else.
Reverted; ``sem/hobbit_sem.py`` is byte-identical to HEAD.

Fourth injection, same day: replacing SHL3's left shift with SHR3's
arithmetic right shift (the wrong direction, one line in
``hobbit_sem.py``) made exactly two of the 35 tests fail --
``test_shl3_accumulator_destination`` (``wdata 0xffffffff`` where the
trace has ``0xfffffff0``) and ``test_shift_count_is_low_five_bits``
(``0`` where ``1 << 31`` is ``0x80000000``) -- and nothing else.
``tests/hri_check.py`` on golden 013 reported exactly ``line 2 field
DATA: dut=0xffffffff spec=0xfffffff0 pc=0x0002`` (2 instructions
compared, FAIL); the core was untouched and still matched.  Reverted by
the reverse edit.

Indirect-mode injections, 2026-11-19, each reverted by the reverse edit
and each run through this file and the golden 014/015 traces:
(a) dropping the three/five-parcel 0xE indirection (using the slot as
the address) failed exactly the four 0xE tests
(``test_word_indirect_source``,
``test_word_indirect_destination_address_is_pointer_value``,
``test_indirect_target_must_meet_its_width_alignment``,
``test_indirect_pointer_word_is_read_from_the_stack_slot``, the last as
an error) and both goldens;
(b) dropping the one-parcel ``_istk5`` indirection failed exactly
``test_mov_is_one_parcel`` (fail) and ``test_mov_ii_one_parcel`` /
``test_mov_si_one_parcel`` (errors), and golden 014 only;
(c) making mode 0x8 unsigned failed exactly
``test_indirect_byte_signed_and_unsigned`` and golden 014 only;
(d) making mode 0xA unsigned failed exactly
``test_indirect_half_signed_and_unsigned`` and golden 014 only;
(e) removing the 0xE offset's ``off & 3`` check (p. 1-27) failed exactly
``test_indirect_offset_must_be_word_aligned`` and neither golden;
(f) removing ``_load``'s word ``ea & 3`` check (p. 1-4) failed exactly
``test_indirect_target_must_meet_its_width_alignment`` and neither
golden;
(g) forcing a byte store's mask to 0xF failed exactly
``test_indirect_byte_store_marks_and_merge`` and golden 015 only;
(h) in the core, replacing EU_S2's pointed-to read with zero failed
exactly the load lines of both goldens (014 L07/L08/L13/L15, 015
L09/L10/L11) and nothing else; the stores' own records were unchanged
because a word store has no merge and a byte/half store's merge is not a
field of the record.
"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "sem"))

import hobbit_sem as h  # noqa: E402


def run(words, memory=None, **kwargs):
    """Execute one instruction at PC 0 from the reference pre-state."""
    psw = kwargs.pop("psw", h.PSW_SP)
    state = h.State(pc=0, sp=0x100, msp=0x180, psw=psw, **kwargs)
    state.memory.update(words)
    if memory:
        state.memory.update(memory)
    return h.step(state, None)


class ArithmeticTest(unittest.TestCase):
    def test_mul_product_and_flags(self):
        # MUL 7 * 6 at R8: p0 0xa6fd, src 0x0006, dst 0x0008 (p. 3-34).
        record, state = run({0: 0xA6FD0006, 4: 0x00080000},
                            {0x108: 7})
        self.assertEqual(state.memory[0x108], 42)
        self.assertFalse(state.psw & h.PSW_C)
        self.assertFalse(state.psw & h.PSW_V)
        self.assertEqual(record.cyc, 20)

    def test_mul_unsigned_overflow_only(self):
        # -1 * 2 = -2 signed (no V), but 0xffffffff * 2 overflows 32 bits (C).
        record, state = run({0: 0xA6FD0002, 4: 0x00080000},
                            {0x108: 0xFFFFFFFF})
        self.assertEqual(state.memory[0x108], 0xFFFFFFFE)
        self.assertTrue(state.psw & h.PSW_C)
        self.assertFalse(state.psw & h.PSW_V)

    def test_div_truncates_toward_zero(self):
        # p. 3-17: two's complement division; README choice 25.
        for dividend, divisor, quotient in (
                (-7, 2, -3), (7, -2, -3), (-7, -2, 3)):
            record, state = run(
                {0: 0xA7FD0000 | (divisor & 0xFFFF),
                 4: 0x00080000},
                {0x108: dividend & 0xFFFFFFFF})
            self.assertEqual(state.memory[0x108],
                             quotient & 0xFFFFFFFF, (dividend, divisor))

    def test_rem_follows_dividend_sign(self):
        for dividend, divisor, remainder in (
                (-7, 2, -1), (7, -2, 1), (-7, -2, -1)):
            record, state = run(
                {0: 0xA5FD0000 | (divisor & 0xFFFF),
                 4: 0x00080000},
                {0x108: dividend & 0xFFFFFFFF})
            self.assertEqual(state.memory[0x108],
                             remainder & 0xFFFFFFFF, (dividend, divisor))
            self.assertFalse(state.psw & h.PSW_V)

    def test_div_overflow_case(self):
        # p. 3-17: 0x80000000 / -1 sets V and returns 0x80000000.
        record, state = run({0: 0xA7FDFFFF, 4: 0x00080000},
                            {0x108: 0x80000000})
        self.assertEqual(state.memory[0x108], 0x80000000)
        self.assertTrue(state.psw & h.PSW_V)
        self.assertFalse(state.psw & h.PSW_C)

    def test_udiv_and_urem_clear_carry(self):
        record, state = run({0: 0xAFFD0002, 4: 0x00080000},
                            {0x108: 0xFFFFFFF9, 0x100: 0},
                            psw=h.PSW_SP | h.PSW_C | h.PSW_V)
        self.assertEqual(state.memory[0x108], 0x7FFFFFFC)
        self.assertFalse(state.psw & h.PSW_C)
        self.assertTrue(state.psw & h.PSW_V)

        record, state = run({0: 0x85FD0002, 4: 0x00080000},
                            {0x108: 0xFFFFFFF9},
                            psw=h.PSW_SP | h.PSW_C)
        self.assertEqual(state.memory[0x108], 1)
        self.assertFalse(state.psw & h.PSW_C)

    def test_divide_by_zero_is_refused(self):
        with self.assertRaises(h.Refusal):
            run({0: 0xA7FD0000, 4: 0x00080000})

    def test_mul3_writes_accumulator(self):
        # MUL3 4 * 6 -> 24 at CSP+4 (p. 1-7, p. 3-34).
        record, state = run({0: 0xB6FD0004, 4: 0x00080000},
                            {0x108: 6})
        self.assertEqual(state.memory[0x104], 24)
        self.assertEqual(record.mem_addr, 0x104)


class InterlockedAndTaggedTest(unittest.TestCase):
    def test_addi_writes_dst_and_old_acc(self):
        # ADDI $3,R8: hidden=dst; dst+=src; Acc=hidden (p. 3-6).
        record, state = run({0: 0x83FD0003, 4: 0x00080000},
                            {0x108: 5})
        self.assertEqual(state.memory[0x108], 8)
        self.assertEqual(state.memory[0x104], 5)

    def test_addi_does_not_touch_carry_or_overflow(self):
        record, state = run({0: 0x83FD0003, 4: 0x00080000},
                            {0x108: 0xFFFFFFFF},
                            psw=h.PSW_SP | h.PSW_C)
        self.assertTrue(state.psw & h.PSW_C)
        self.assertFalse(state.psw & h.PSW_V)

    def test_addi_to_r4_is_a_no_op(self):
        # p. 3-6 note: R4 destination ends as its previous value.
        record, state = run({0: 0x83FD0003, 4: 0x00040000},
                            {0x104: 0x55})
        self.assertEqual(state.memory[0x104], 0x55)
        self.assertEqual(record.mem_addr, 0x104)

    def test_andi_and_ori(self):
        record, state = run({0: 0x82FD000F, 4: 0x00080000},
                            {0x108: 0x33})
        self.assertEqual(state.memory[0x108], 0x03)
        self.assertEqual(state.memory[0x104], 0x33)

        record, state = run({0: 0x81FD000F, 4: 0x00080000},
                            {0x108: 0x30})
        self.assertEqual(state.memory[0x108], 0x3F)
        self.assertEqual(state.memory[0x104], 0x30)

    def test_tadd_untagged_stores_and_tagged_does_not(self):
        record, state = run({0: 0x8CFD0004, 4: 0x00080000},
                            {0x108: 4})
        self.assertEqual(state.memory[0x108], 8)
        self.assertFalse(state.psw & h.PSW_F)

        record, state = run({0: 0x8CFD0002, 4: 0x00080000},
                            {0x108: 4})
        self.assertEqual(record.mem_we, 0)
        self.assertEqual(state.memory[0x108], 4)
        self.assertTrue(state.psw & h.PSW_F)

    def test_tsub_untagged(self):
        record, state = run({0: 0x8DFD0004, 4: 0x00080000},
                            {0x108: 4})
        self.assertEqual(state.memory[0x108], 0)

    def test_tadd_sets_carry_and_overflow_then_flag_from_overflow(self):
        # p. 3-44 operation block: C on unsigned overflow, V on signed
        # overflow, then PSW.F = PSW.V, and the store happens only when
        # F = 0.
        # src and dst both have low 2 bits 0, so neither is tagged.
        record, state = run({0: 0x8CFD0004, 4: 0x00080000},
                            {0x108: 0xFFFFFFFC})
        self.assertEqual(state.memory[0x108], 0)
        self.assertTrue(state.psw & h.PSW_C)
        self.assertFalse(state.psw & h.PSW_V)
        self.assertFalse(state.psw & h.PSW_F)

        record, state = run({0: 0x8CFD0004, 4: 0x00080000},
                            {0x108: 0x7FFFFFFC})
        self.assertEqual(record.mem_we, 0)
        self.assertEqual(state.memory[0x108], 0x7FFFFFFC)
        self.assertFalse(state.psw & h.PSW_C)
        self.assertTrue(state.psw & h.PSW_V)
        self.assertTrue(state.psw & h.PSW_F)

    def test_tagged_tadd_leaves_carry_and_overflow(self):
        # Tagged operand: F = 1 and C/V as they were (p. 3-44).
        record, state = run({0: 0x8CFD0002, 4: 0x00080000},
                            {0x108: 4},
                            psw=h.PSW_SP | h.PSW_C | h.PSW_V)
        self.assertTrue(state.psw & h.PSW_F)
        self.assertTrue(state.psw & h.PSW_C)
        self.assertTrue(state.psw & h.PSW_V)
        self.assertEqual(state.memory[0x108], 4)
        self.assertEqual(record.mem_we, 0)

    def test_tsub_borrow_and_overflow(self):
        # p. 3-47: C on unsigned borrow, V on signed overflow.
        record, state = run({0: 0x8DFD0004, 4: 0x00080000},
                            {0x108: 0})
        self.assertEqual(state.memory[0x108], 0xFFFFFFFC)
        self.assertTrue(state.psw & h.PSW_C)
        self.assertFalse(state.psw & h.PSW_V)
        self.assertFalse(state.psw & h.PSW_F)

        record, state = run({0: 0x8DFD0004, 4: 0x00080000},
                            {0x108: 0x80000000})
        self.assertEqual(record.mem_we, 0)
        self.assertTrue(state.psw & h.PSW_V)
        self.assertTrue(state.psw & h.PSW_F)


class MoveAndOtherTest(unittest.TestCase):
    def test_clre_clears_enter_guard(self):
        record, state = run({0: 0x2C0A0000},
                            psw=h.PSW_SP | h.PSW_E)
        self.assertFalse(state.psw & h.PSW_E)
        self.assertEqual(record.cyc, 1)

    def test_mova_one_parcel_is_address_of_source(self):
        # MOVA R16,R8 -> SP+16 (p. 3-33).
        record, state = run({0: 0x74820000})
        self.assertEqual(state.memory[0x108], 0x110)

    def test_mova_three_parcel_rejects_immediate(self):
        with self.assertRaises(h.IllegalInstruction):
            run({0: 0x84FD0010, 4: 0x00080000})

    def test_ldraa_absolute_flow32(self):
        # LDRAA *$0x100 -> accumulator = 0x100 (p. 3-31).
        record, state = run({0: 0x80FA0000, 4: 0x01000000})
        self.assertEqual(state.memory[0x104], 0x100)


class OneParcelRow11Test(unittest.TestCase):
    """Table 1-15 row 11 (p. 1-22): the one-parcel 0x18..0x1F forms."""

    def test_shl3_accumulator_destination(self):
        # SHL3 $4,R12 = 0x7883: opcode 0x1E, uimm5 4, stk5 3 (p. 3-41).
        # The destination word 0xffffffff is shifted left, zeros fill,
        # and only the accumulator at CSP+4 is written; the destination
        # word is unchanged (p. 3-41, p. 1-7).
        record, state = run({0: 0x78830000}, {0x10C: 0xFFFFFFFF},
                            psw=h.PSW_SP | h.PSW_C | h.PSW_V | h.PSW_F)
        self.assertEqual(record.mem_we, 1)
        self.assertEqual(record.mem_addr, 0x104)
        self.assertEqual(record.mem_wdata, 0xFFFFFFF0)
        self.assertEqual(record.mem_wmask, 0x0F)
        self.assertEqual(state.memory[0x10C], 0xFFFFFFFF)
        self.assertEqual(state.memory[0x104], 0xFFFFFFF0)
        # pp. 3-41/3-42 state no C/V/F effect.
        self.assertTrue(state.psw & h.PSW_C)
        self.assertTrue(state.psw & h.PSW_V)
        self.assertTrue(state.psw & h.PSW_F)
        self.assertEqual(record.cyc, 1)          # Table 4-32, p. 4-3

    def test_shr3_is_arithmetic(self):
        # SHR3 $4,R12 = 0x7c83: the sign bit is copied as bits move right
        # (p. 3-42).  0x80000000 >> 4 is 0xf8000000, not 0x08000000.
        record, state = run({0: 0x7C830000}, {0x10C: 0x80000000})
        self.assertEqual(record.mem_addr, 0x104)
        self.assertEqual(state.memory[0x104], 0xF8000000)
        self.assertEqual(state.memory[0x10C], 0x80000000)
        self.assertEqual(record.cyc, 1)

    def test_shift_count_is_low_five_bits(self):
        # uimm5 = 31: SHL3 $31,R12 = 0x7be3.  1 << 31 = 0x80000000.
        record, state = run({0: 0x7BE30000}, {0x10C: 1})
        self.assertEqual(state.memory[0x104], 0x80000000)
        self.assertEqual(record.cyc, 1)

    def test_mov_cs_immediate(self):
        # MOV $-1,R12 = 0x73e3 (opcode 0x1C): imm5 sign-extends (p. 3-32).
        record, state = run({0: 0x73E30000})
        self.assertEqual(record.mem_addr, 0x10C)
        self.assertEqual(record.mem_wdata, 0xFFFFFFFF)
        self.assertEqual(record.cyc, 1)

    def test_three_parcel_shifts_write_their_destination(self):
        # Table 1-18 (p. 1-24) three-parcel shifts: source in parcel 1,
        # destination in parcel 2.  A 16-bit Roffset field is a byte
        # offset -- p. 1-21 scales only five-bit and ten-bit values, and
        # one-parcel stk5 is a word index scaled by four, so `SHL R12,R8`
        # encodes 0x000C/0x0008 against SP=0x100 and names 0x10C/0x108.
        # p. 3-41 SHL: "dst <<= Unsigned(src)"; p. 3-42 SHR copies the
        # sign bit into the vacated bits; p. 3-50 USHR fills with zeros.
        # Unlike the `[3]` forms, the plain forms write the destination
        # and leave the accumulator alone; all three take one cycle
        # (Table 4-32, p. 4-3).
        record, state = run({0: 0xAEDD000C, 4: 0x00082C02},
                            {0x10C: 3, 0x108: 0x0F})
        self.assertEqual(state.memory[0x108], 0x78)
        self.assertEqual(record.mem_addr, 0x108)
        self.assertEqual(record.cyc, 1)
        self.assertNotIn(0x104, state.memory)

        _, state = run({0: 0xACDD000C, 4: 0x00082C02},
                       {0x10C: 4, 0x108: 0xFFFFFF00})
        self.assertEqual(state.memory[0x108], 0xFFFFFFF0)

        _, state = run({0: 0xADDD000C, 4: 0x00082C02},
                       {0x10C: 4, 0x108: 0xFFFFFF00})
        self.assertEqual(state.memory[0x108], 0x0FFFFFF0)


class DqmTest(unittest.TestCase):
    def test_constant_to_sc_double_word(self):
        # 5-parcel DQM $0x11223344,R8: two words, cyc 3 (p. 3-18, p. 4-4).
        record, state = run({0: 0xC7F41122, 4: 0x33440000,
                             8: 0x00080000})
        self.assertEqual(state.memory[0x108], 0x11223344)
        self.assertEqual(state.memory[0x10C], 0x11223344)
        self.assertEqual(record.cyc, 3)
        self.assertEqual(record.mem_addr, 0x108)

    def test_memory_to_memory_double_word(self):
        record, state = run({0: 0x87C00200, 4: 0x03000000},
                            {0x200: 0x11, 0x204: 0x22})
        self.assertEqual(state.memory[0x300], 0x11)
        self.assertEqual(state.memory[0x304], 0x22)
        self.assertEqual(record.cyc, 4)

    def test_memory_to_memory_quad_word_refuses_undefined_s(self):
        with self.assertRaises(h.Refusal):
            run({0: 0x87CC0200, 4: 0x03000000})


class KernelTransferTest(unittest.TestCase):
    def test_kcall_frame_and_isp(self):
        record, state = run({0: 0x00010000},
                            {0x200: 0x40}, vb=0x200)
        self.assertEqual(state.isp, 0x30)
        self.assertEqual(state.memory[0x34], 4)       # src = 1*4
        self.assertEqual(state.memory[0x38], 0x0002)  # return PC
        self.assertEqual(state.memory[0x3C], h.PSW_SP)
        self.assertEqual(state.pc, 0x40)              # *(VB+0)
        self.assertFalse(state.psw & h.PSW_SP)        # PSW &= 0xffff0000
        self.assertEqual(record.cyc, 11)

    def test_kret_restores_pc_and_psw(self):
        record, state = run({0: 0x2C010000},
                            {0x48: 0x20, 0x4C: 0x200})
        self.assertEqual(state.pc, 0x20)
        self.assertEqual(state.psw, 0x200)
        self.assertEqual(state.isp, 0x50)
        self.assertEqual(record.mem_we, 0)
        self.assertEqual(record.cyc, 12)

    def test_cret_restores_stack_pc_and_psw(self):
        record, state = run({0: 0x2C050000},
                            {0x40: 0x100, 0x44: 0x180,
                             0x48: 0x20, 0x4C: 0x200})
        self.assertEqual(state.sp, 0x100)
        self.assertEqual(state.msp, 0x180)
        self.assertEqual(state.pc, 0x20)
        self.assertEqual(state.psw, 0x200)
        self.assertEqual(state.isp, 0x50)
        self.assertEqual(record.cyc, 15)

    def test_kret_is_privileged(self):
        with self.assertRaises(h.Refusal):
            run({0: 0x2C010000}, psw=h.PSW_SP | h.PSW_USER)


class IndirectOperandTest(unittest.TestCase):
    """Table 1-21's stack-offset-indirect modes 0x8-0xB and 0xE (p. 1-25).

    p. 1-27: "Stack Offset Indirect - addressing adds a constant offset in
    the instruction to the address of the current stack pointer (CSP). The
    word at this address is fetched and then used as an address to obtain
    the data operand. The offset must be word aligned. An alignment fault
    (0x4) is executed if the offset is not word aligned."  The width,
    sign and byte-mark rules are p. 1-4's; the offset is a byte offset,
    unscaled (sem/README.md, "Stack fields are measured in two units").
    """

    def test_word_indirect_source(self):
        # MOV *R8,R12 (mode 0xE, three parcels): pointer at SP+8 = 0x108.
        record, state = run({0: 0x86ED0008, 4: 0x000C0000},
                            {0x108: 0x110, 0x110: 0xCAFEBABE})
        self.assertEqual(state.memory[0x10C], 0xCAFEBABE)
        self.assertEqual(record.mem_addr, 0x10C)
        self.assertEqual(record.mem_wdata, 0xCAFEBABE)
        self.assertEqual(record.mem_wmask, 0x0F)
        self.assertEqual(record.cyc, 1)          # Table 4-32, p. 4-3

    def test_word_indirect_destination_address_is_pointer_value(self):
        # MOV $0x1234,*R8: the write's address is the pointer's value
        # (p. 1-27), not the stack slot that holds the pointer.
        record, state = run({0: 0x86FE1234, 4: 0x00080000},
                            {0x108: 0x114})
        self.assertEqual(state.memory[0x114], 0x1234)
        self.assertEqual(record.mem_addr, 0x114)
        self.assertEqual(record.mem_wdata, 0x1234)
        self.assertEqual(record.mem_wmask, 0x0F)
        self.assertEqual(record.cyc, 1)

    def test_mov_is_one_parcel(self):
        # MOV.IS R4,R8 = 0x6422 (opcode 0x19): istk5 1 -> *0x104, stk5 2
        # -> 0x108; the one-parcel field is scaled by four (p. 1-21).
        record, state = run({0: 0x64220000},
                            {0x104: 0x114, 0x114: 0x11223344})
        self.assertEqual(state.memory[0x108], 0x11223344)
        self.assertEqual(record.mem_addr, 0x108)
        self.assertEqual(record.cyc, 1)

    def test_mov_si_one_parcel(self):
        # MOV.SI R4,R8 = 0x6822 (opcode 0x1A): source 0x104, pointer 0x108.
        record, state = run({0: 0x68220000},
                            {0x104: 0x000000AA, 0x108: 0x114})
        self.assertEqual(state.memory[0x114], 0xAA)
        self.assertEqual(record.mem_addr, 0x114)
        self.assertEqual(record.mem_wmask, 0x0F)

    def test_mov_ii_one_parcel(self):
        # MOV.II R4,R8 = 0x6C22 (opcode 0x1B): both slots hold pointers.
        record, state = run({0: 0x6C220000},
                            {0x104: 0x114, 0x108: 0x118,
                             0x114: 0x00000055})
        self.assertEqual(state.memory[0x118], 0x55)
        self.assertEqual(record.mem_addr, 0x118)
        self.assertEqual(record.cyc, 1)

    def test_indirect_byte_signed_and_unsigned(self):
        # MOV *R4:B,R8 = 0x868D / *R4:UB = 0x869D.  The byte at 0x111 is
        # bits 23:16 of the word at 0x110 (big-endian, p. 1-4).
        record, state = run({0: 0x868D0004, 4: 0x00080000},
                            {0x104: 0x111, 0x110: 0x00AB0000})
        self.assertEqual(state.memory[0x108], 0xFFFFFFAB)
        self.assertEqual(record.mem_wdata, 0xFFFFFFAB)

        record, state = run({0: 0x869D0004, 4: 0x00080000},
                            {0x104: 0x111, 0x110: 0x00AB0000})
        self.assertEqual(state.memory[0x108], 0x000000AB)

    def test_indirect_half_signed_and_unsigned(self):
        # MOV *R4:H,R8 = 0x86AD / *R4:UH = 0x86BD at 0x112.
        record, state = run({0: 0x86AD0004, 4: 0x00080000},
                            {0x104: 0x112, 0x110: 0x00008000})
        self.assertEqual(state.memory[0x108], 0xFFFF8000)

        record, state = run({0: 0x86BD0004, 4: 0x00080000},
                            {0x104: 0x112, 0x110: 0x00008000})
        self.assertEqual(state.memory[0x108], 0x00008000)

    def test_indirect_byte_store_marks_and_merge(self):
        # MOV R16:B,*R8 = 0x86D8: a byte store at 0x121 keeps the other
        # three bytes of the word at 0x120 (p. 1-4's byte marks).
        record, state = run({0: 0x86D80010, 4: 0x00080000},
                            {0x110: 0x000000AB, 0x108: 0x121,
                             0x120: 0x11223344})
        self.assertEqual(state.memory[0x120], 0x11AB3344)
        self.assertEqual(record.mem_addr, 0x120)
        self.assertEqual(record.mem_wdata, 0x00AB0000)
        self.assertEqual(record.mem_wmask, 0x04)

    def test_indirect_offset_must_be_word_aligned(self):
        # p. 1-27: the *offset* must be word-aligned; offset 0x6 is not.
        for first in (0x86ED, 0x868D, 0x86AD):
            with self.assertRaises(h.AlignmentFault):
                run({0: first << 16 | 0x0006, 4: 0x00080000},
                    {0x106: 0x110, 0x110: 0x0})

    def test_indirect_target_must_meet_its_width_alignment(self):
        # p. 1-4: the pointed-to address obeys the width's rule.  A word
        # at 0x111 and a half-word at 0x111 are both misaligned; a byte
        # there is not (test_indirect_byte_signed_and_unsigned).
        for first in (0x86ED, 0x86AD):
            with self.assertRaises(h.AlignmentFault):
                run({0: first << 16 | 0x0004, 4: 0x00080000},
                    {0x104: 0x111, 0x110: 0x0})

    def test_indirect_pointer_word_is_read_from_the_stack_slot(self):
        # The pointer word comes from CSP+offset; a byte offset is not
        # scaled (p. 1-21 scales only the five- and ten-bit fields).
        record, state = run({0: 0x86ED0008, 4: 0x000C0000},
                            {0x108: 0x120, 0x120: 0x77})
        self.assertEqual(state.memory[0x10C], 0x77)


class FiveParcelTest(unittest.TestCase):
    def test_five_parcel_mul(self):
        # 5-parcel MUL $6,R8: p0 0xe6fd, src 0x00000006, dst 0x00000008.
        record, state = run({0: 0xE6FD0000, 4: 0x00060000,
                             8: 0x00080000},
                            {0x108: 7})
        self.assertEqual(state.memory[0x108], 42)
        self.assertEqual(record.cyc, 20)

    def test_five_parcel_addi(self):
        record, state = run({0: 0xC3FD0000, 4: 0x00030000,
                             8: 0x00080000},
                            {0x108: 5})
        self.assertEqual(state.memory[0x108], 8)
        self.assertEqual(record.cyc, 2)


if __name__ == "__main__":
    unittest.main()
