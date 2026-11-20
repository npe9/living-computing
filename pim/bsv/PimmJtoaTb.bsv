// Lockstep bench: jis_to_ascii:convert_element/2, from the IPL image,
// on the Bluespec core.  It prints the trace ref/pimm/lockstep_jtoa.py
// compares, line for line, with the reference model's:
//
//   goals 0..65535   convert_element(K, Out), every 16-bit key
//   goal  65536      convert_element(atom, Out)
//   goal  65537      convert_element(Unbound, Out): must suspend
//
// Each goal's variables are fresh heap cells, allocated as the
// reference model allocates them; after each goal the bench prints
// "O <the dereferenced second argument>".
package PimmJtoaTb;

import PimmGen::*;
import PimmTypes::*;
import PimmCore::*;

module mkPimmJtoaTb(Empty);
  PimmCore core <- mkPimmCore("generated/pimm_ipl.hex");

  Reg#(Bit#(17)) goal  <- mkReg(0);
  Reg#(Addr)     heap  <- mkReg(fromInteger(lockstepHeap));
  Reg#(Bit#(3))  phase <- mkReg(0);
  Reg#(Cell)     outv  <- mkRegU;

  function Cell refTo(Addr a) = mkCell(tag_REFo, loadAddress | zeroExtend(a));

  Bool unboundGoal = goal == 65537;

  rule arg0 (phase == 0 && goal <= 65537);
    if (unboundGoal) begin
      core.poke(heap, mkCell(tag_UNDF, 0));
      core.setReg(0, refTo(heap));
      heap <= heap + 1;
    end
    else if (goal == 65536) core.setReg(0, mkCell(tag_ATOMo, 5));
    else core.setReg(0, mkCell(tag_INTo, zeroExtend(goal)));
    phase <= 1;
  endrule

  rule arg1 (phase == 1);
    core.poke(heap, mkCell(tag_UNDF, 0));
    core.setReg(1, refTo(heap));
    outv <= refTo(heap);
    heap <= heap + 1;
    phase <= 2;
  endrule

  rule go (phase == 2);
    core.start(fromInteger(pred_jis_to_ascii__convert_element_2));
    phase <= 3;
  endrule

  rule ended (phase == 3);
    let e <- core.finished;
    core.derefReq(outv);
    phase <= 4;
  endrule

  rule result (phase == 4);
    let w <- core.derefResp;
    $display("O %02x%08x", w.tag, w.val);
    goal <= goal + 1;
    phase <= 0;
  endrule

  rule finish (phase == 0 && goal > 65537);
    $finish(0);
  endrule
endmodule

endpackage
