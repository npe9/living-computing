// StretchSmoke.bsv
//
// Smoke-test testbench for mkStretchCore. DELIBERATELY NAMED WITHOUT A
// "Tb" SUFFIX, unlike every generated per-program testbench
// (StretchProblem21Tb.bsv, StretchIoTapeTb.bsv, etc.) -- this file has
// twice been accidentally deleted by an ad-hoc `rm -f
// bsv/Stretch*Tb.bsv` cleanup command typed outside run_tests.sh
// (which itself enumerates exact generated filenames and never
// globs). Renaming this file out of the "*Tb.bsv" shape makes that
// class of mistake structurally impossible: no glob matching
// generated testbenches can ever match this one again, no matter how
// it's typed. See strap/README.md's Gotchas for the two prior
// incidents. Hand-assembles a small
// program (no STRAP assembler yet -- see bsv/README.md "Next steps")
// exercising: VFL binary L/+/ST (unsigned, direct addressing),
// immediate VFL add, index arithmetic (LCI), a Count-and-Branch loop,
// and the decode/execute fallback for an unimplemented-but-
// structurally-valid opcode (RNX).
//
// Sequenced with an explicit phase register, one storage write per
// phase: mkRegFileWCF only relaxes read/write conflicts against a
// single write, not write-vs-write -- a rule (or an execute() case
// arm) may call core.mem.writeWord at most once. See bsv/README.md
// "Toolchain" for how this was diagnosed and StretchVFL.fieldCrosses /
// StretchExecute's Transmit case for the same constraint on the
// execute side.
//
// Run: `./build.sh && ./stretch_sim` (see bsv/Makefile / bsv/build.sh).

package StretchSmoke;

import StretchTypes::*;
import StretchStorage::*;
import StretchCore::*;

// ---------------------------------------------------------------------
// Instruction encoders (mnemonic-level -> raw bit pattern), matching
// the field layouts established in StretchDecode.bsv / bsv/README.md.
// ---------------------------------------------------------------------

function Word64 encVflFull(BitAddr addr, Bit#(4) i1, Bit#(3) p, Bit#(6) length,
                            Bit#(3) bs, Bit#(7) offset, Bit#(1) a, Bit#(1) b,
                            Bit#(1) c, Bit#(6) code) =
  { addr, 4'b1000, i1, p, length, bs, offset, a, b, c, code, 4'b0 };

function HalfWord32 encImmIndex(HWordAddr imm, Bit#(4) j, Bit#(4) code) =
  { imm, j, 5'b10000, code };

function HalfWord32 encCountBranch(HWordAddr addr, Bit#(4) j, Bit#(2) v,
                                    Bit#(1) refill, Bit#(1) bz, Bit#(1) idx) =
  { addr, j, v, 4'b1001, refill, bz, idx };

function HalfWord32 encNop() = { 19'b0, 3'b110, 6'b000000, 4'b0 }; // NOP=110

(* synthesize *)
module mkStretchTb(Empty);
  StretchCore core <- mkStretchCore;
  Reg#(Bit#(8))  phase <- mkReg(0);
  Reg#(Bit#(8))  stepCount <- mkReg(0);
  Reg#(Bit#(32)) fails <- mkReg(0);

  function Action check(String label, Word64 got, Word64 expected) =
    action
      if (got == expected)
        $display("PASS %s = %0d", label, got);
      else begin
        $display("FAIL %s = %0d, expected %0d", label, got, expected);
        fails <= fails + 1;
      end
    endaction;

  // One storage write: read-modify-write the containing word to plant
  // a half-word instruction at half-word address `ha`.
  function Action putHW(HWordAddr ha, HalfWord32 v) =
    action
      WordAddr wa = ha[18:1];
      Word64 w <- core.mem.readWord(wa);
      Word64 neww = (ha[0] == 0) ? {v, w[31:0]} : {w[63:32], v};
      core.mem.writeWord(wa, neww);
    endaction;

  // This test program keeps every full-word instruction bit-address-0
  // (word-)aligned, so a full-word instruction is just one whole-word
  // write -- no half-word splitting needed.
  function Action putFull(HWordAddr ha, Word64 v) = core.mem.writeWord(ha[18:1], v);

  // SETUP_PHASES: exactly one storage-writing action per phase value.
  rule setup (phase < 16);
    case (phase)
      0: core.mem.writeWord(40, 5);   // operand A
      1: core.mem.writeWord(41, 7);   // operand B
      2: core.mem.writeWord(42, 0);   // result
      3: core.mem.writeWord(53, 0);   // loop sum accumulator
      // L addr=40 (unsigned, direct) -> acc = mem[40]
      4: putFull(64, encVflFull({18'd40,6'b0}, 0, 0, 0, 0, 0, 1, 0, 0, 6'b000101));
      // + addr=41 (unsigned, direct) -> acc += mem[41]
      5: putFull(66, encVflFull({18'd41,6'b0}, 0, 0, 0, 0, 0, 1, 0, 0, 6'b000001));
      // ST addr=42 -> mem[42] = acc
      6: putFull(68, encVflFull({18'd42,6'b0}, 0, 0, 0, 0, 0, 1, 0, 0, 6'b001101));
      7: putHW(70, encImmIndex(19'd3, 1, 4'b0010)); // LCI X1, 3 (loop trip count)
      8: putHW(71, encNop());                       // realign to even half-word
      // LOOP_TOP = 72: L addr=53 -> acc = sum
      9: putFull(72, encVflFull({18'd53,6'b0}, 0, 0, 0, 0, 0, 1, 0, 0, 6'b000101));
      // + immediate 10, length=8 (unsigned): immediateOperand takes the
      // *leftmost* `length` bits of the address field, so 10 must be
      // left-justified: 10 << (24-8) = 10 << 16.
      10: putFull(74, encVflFull((24'd10 << 16), 0, 4, 8, 0, 0, 1, 0, 0, 6'b000001));
      // ST addr=53 -> sum = acc
      11: putFull(76, encVflFull({18'd53,6'b0}, 0, 0, 0, 0, 0, 1, 0, 0, 6'b001101));
      // CB X1, LOOP_TOP(72), v=00 (unchanged), refill=0, branch-if-nonzero
      12: putHW(78, encCountBranch(19'd72, 1, 2'b00, 0, 0, 0));
      13: putHW(79, encNop());
      14: putHW(90, 32'hFFFF_FFFF); // decodes as DirIndex RNX; execute -> OP invalid
      15: core.setPC(64);
    endcase
    phase <= phase + 1;
  endrule

  rule run (phase == 16 && stepCount < 24);
    let _ <- core.step();
    stepCount <= stepCount + 1;
  endrule

  rule afterRun (phase == 16 && stepCount == 24);
    phase <= 17;
  endrule

  // check() conditionally writes `fails`; two calls in the same rule
  // would be two writes to that one register (same issue as
  // indicators, see bsv/README.md "Toolchain"), so each check gets its
  // own phase.
  rule checkArith1 (phase == 17);
    let v <- core.mem.readWord(42);
    check("mem[42] (5+7)", v, 12);
    phase <= 18;
  endrule

  rule checkArith2 (phase == 18);
    let v <- core.mem.readWord(53);
    check("mem[53] (3*10 via CB loop)", v, 30);
    core.setPC(90);
    phase <= 19;
  endrule

  rule stepRnx (phase == 19);
    let _ <- core.step();
    phase <= 20;
  endrule

  rule checkRnx (phase == 20);
    let v <- core.mem.readWord(11);
    check("indicator OP after RNX (unimplemented)", (v >> 48) & 1, 1);
    phase <= 21;
  endrule

  rule finish (phase == 21);
    if (fails == 0)
      $display("ALL TESTS PASSED");
    else
      $display("%0d TEST(S) FAILED", fails);
    $finish(0);
  endrule

endmodule

endpackage
