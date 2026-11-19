// PimKL1BSwitchTb.bsv -- KL1-B type-dispatch switches.
//
// The PIMOS encodings are `r_c16_i`: opcode 0x28/0x29/0x2a in bits
// 31-24, the tested register in bits 23-16, and the resolved label in
// bits 15-0 (klb_opr.kl1 lines 317-332).  The semantics are the
// mnemonic's: "switch on non-<type>" means "jump to the label when the
// dereferenced value is NOT that type; otherwise fall through."  The
// complement form is the clause-indexing test: a clause whose argument
// is not its type fails and control moves to the next clause group.
//
// Program (11 words):
//   0x00 set_value 5, r1                 ; r1 = INT 5
//   0x01 switch_on_non_integer r1, 0x04  ; INT -> NOT taken -> 0x02
//   0x02 put_integer 1, r2               ; r2 = INT 1   (marker A)
//   0x03 switch_on_non_atom r1, 0x06     ; INT -> taken -> 0x06
//   0x04 put_integer 2, r2               ; must NOT run
//   0x05 halt                            ; must NOT run
//   0x06 switch_on_non_list r1, 0x09     ; INT -> taken -> 0x09
//   0x07 put_integer 3, r2               ; must NOT run
//   0x08 halt                            ; must NOT run
//   0x09 put_integer 7, r3               ; r3 = INT 7   (marker B)
//   0x0a halt
//
// Pass: r2 == INT 1 and r3 == INT 7.  Marker A proves the non-integer
// test fell through; marker B proves both the non-atom and non-list
// tests branched to their labels.
//
// Observed failure set (2026-11-19), each injection reverting clean:
//   - non_integer condition changed from != to ==: r2 == INT 2 and
//     r3 == INT 7, because 0x01 branches to 0x04 and put_integer 2 runs.
//   - non_atom condition changed from != to ==: r2 == INT 2 and
//     r3 == INT 7, because 0x03 falls through to 0x04.
//   - non_list condition changed from != to ==: r2 == INT 3 and
//     r3 == INT 7, because 0x06 falls through to 0x07.
// Each injection makes only this testbench print FAIL; the other
// fifteen KL1-B testbenches stay green.
package PimKL1BSwitchTb;

import PimKL1B::*;

(* synthesize *)
module mkPimKL1BSwitchTb(Empty);

  PimKL1B pu <- mkPimKL1B;
  Reg#(Bit#(4)) idx <- mkReg(0);
  Reg#(Bool) started <- mkReg(False);

  function Word prog(Bit#(4) i);
    case (i)
      0:  return 40'h23_14_05_01_00;  // set_value 5, r1
      1:  return 40'h23_28_01_00_04;  // switch_on_non_integer r1, 0x04
      2:  return 40'h23_31_02_00_01;  // put_integer 1, r2
      3:  return 40'h23_29_01_00_06;  // switch_on_non_atom r1, 0x06
      4:  return 40'h23_31_02_00_02;  // put_integer 2, r2 (must not run)
      5:  return 40'h23_71_00_00_00;  // halt (must not run)
      6:  return 40'h23_2a_01_00_09;  // switch_on_non_list r1, 0x09
      7:  return 40'h23_31_02_00_03;  // put_integer 3, r2 (must not run)
      8:  return 40'h23_71_00_00_00;  // halt (must not run)
      9:  return 40'h23_31_03_00_07;  // put_integer 7, r3
      default: return 40'h23_71_00_00_00;  // halt
    endcase
  endfunction

  rule load if (idx < 11);
    pu.load(zeroExtend(idx), prog(idx));
    idx <= idx + 1;
  endrule

  rule start if (idx == 11 && !started);
    pu.start(0);
    started <= True;
  endrule

  rule run if (started && !pu.halted());
    pu.step();
  endrule

  rule check if (pu.halted());
    Word r2 = pu.readReg(2);
    Word r3 = pu.readReg(3);
    $display("switch case: r2=%h r3=%h", r2, r3);
    if (r2 == 40'h02_00_00_00_01 && r3 == 40'h02_00_00_00_07)
      $display("PimKL1BSwitchTb: PASS");
    else
      $display("PimKL1BSwitchTb: FAIL");
    $finish;
  endrule

endmodule

endpackage
