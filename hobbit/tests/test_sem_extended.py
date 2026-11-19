#!/usr/bin/env python3
"""Unit tests for the instructions added to the one-instruction model.

These are not golden traces: they drive ``sem/hobbit_sem.py`` directly and
assert the printed operation and flag rules, including the cases the six
new goldens do not reach (overflow, tagged operands, divide by zero, the
DQM row selection and the kernel transfers).  The page in each assertion
is the manual page the rule comes from.

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
