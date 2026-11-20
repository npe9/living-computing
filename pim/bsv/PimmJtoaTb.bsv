// Lockstep bench: jis_to_ascii:convert_element/2, from the IPL image,
// on the Bluespec core.  It prints the trace ref/pimm/lockstep_jtoa.py
// compares, line for line, with the reference model's.  The bench is a
// short script of core operations (the function `script` below); the
// reference side performs the same operations in the same order:
//
//   keys      convert_element(K, Out) for every 16-bit K, then for an
//             atom (goals 0..65536)
//   bound     convert_element(V, Out), V unbound: the goal suspends
//             into a record hooked on V; V is bound to a key; the goal
//             wakes and finishes
//   chain     the same, but V is first bound to another unbound
//             variable W: the goal wakes, reaches W through V (two
//             references), suspends again on W, finishes when W is bound
//   two       two goals waiting on one V: both wake when it is bound
//
// "O <cell>" is a variable, dereferenced, printed by the bench.
package PimmJtoaTb;

import RegFile::*;
import PimmGen::*;
import PimmTypes::*;
import PimmCore::*;

typedef enum { NewVar,     // slot a := a fresh variable
               ArgKey,     // argument a := this goal's key
               ArgSlot,    // argument a := slot b
               Spawn,      // a goal of convert_element/2
               Run,
               Out,        // print slot a dereferenced
               BindKey,    // unify slot a with the integer 0x2341
               BindSlot,   // unify slot a with slot b
               NextKey,    // next goal; back to the start while keys remain
               Finish } Kind deriving (Bits, Eq);

typedef struct { Kind k; Bit#(2) a; Bit#(2) b; } Op deriving (Bits);

function Op op(Kind k, Bit#(2) a, Bit#(2) b) = Op { k: k, a: a, b: b };

function Op script(Bit#(6) i);
  case (i)
    // keys
    0:  return op(NewVar, 1, 0);
    1:  return op(ArgKey, 1, 0);
    2:  return op(ArgSlot, 2, 1);
    3:  return op(Spawn, 0, 0);
    4:  return op(Run, 0, 0);
    5:  return op(Out, 1, 0);
    6:  return op(NextKey, 0, 0);
    // bound
    7:  return op(NewVar, 0, 0);
    8:  return op(NewVar, 1, 0);
    9:  return op(ArgSlot, 1, 0);
    10: return op(ArgSlot, 2, 1);
    11: return op(Spawn, 0, 0);
    12: return op(Run, 0, 0);
    13: return op(Out, 1, 0);
    14: return op(BindKey, 0, 0);
    15: return op(Run, 0, 0);
    16: return op(Out, 1, 0);
    // chain
    17: return op(NewVar, 0, 0);
    18: return op(NewVar, 1, 0);
    19: return op(ArgSlot, 1, 0);
    20: return op(ArgSlot, 2, 1);
    21: return op(Spawn, 0, 0);
    22: return op(Run, 0, 0);
    23: return op(Out, 1, 0);
    24: return op(NewVar, 2, 0);
    25: return op(BindSlot, 0, 2);
    26: return op(Run, 0, 0);
    27: return op(Out, 1, 0);
    28: return op(BindKey, 2, 0);
    29: return op(Run, 0, 0);
    30: return op(Out, 1, 0);
    // two
    31: return op(NewVar, 0, 0);
    32: return op(NewVar, 1, 0);
    33: return op(ArgSlot, 1, 0);
    34: return op(ArgSlot, 2, 1);
    35: return op(Spawn, 0, 0);
    36: return op(NewVar, 2, 0);
    37: return op(ArgSlot, 1, 0);
    38: return op(ArgSlot, 2, 2);
    39: return op(Spawn, 0, 0);
    40: return op(Run, 0, 0);
    41: return op(Out, 1, 0);
    42: return op(BindKey, 0, 0);
    43: return op(Run, 0, 0);
    44: return op(Out, 1, 0);
    45: return op(Out, 2, 0);
    default: return op(Finish, 0, 0);
  endcase
endfunction

module mkPimmJtoaTb(Empty);
  PimmCore core <- mkPimmCore("generated/pimm_ipl.hex");

  Reg#(Bit#(17)) goal <- mkReg(0);
  Reg#(Bit#(6))  ip   <- mkReg(0);
  Reg#(Bool)     awaited <- mkReg(False);    // the operation's answer is awaited
  RegFile#(Bit#(2), Cell) slot <- mkRegFileFull;

  let o = script(ip);
  Cell key = (goal == 65536) ? mkCell(tag_ATOMo, 5) : mkCell(tag_INTo, zeroExtend(goal));
  Cell bindTo = mkCell(tag_INTo, 32'h2341);

  rule request (!awaited);
    Bool answer = False;
    case (o.k)
      NewVar:   begin core.newVar; answer = True; end
      ArgKey:   core.setArg(zeroExtend(o.a), key);
      ArgSlot:  core.setArg(zeroExtend(o.a), slot.sub(o.b));
      Spawn:    core.spawn(fromInteger(pred_jis_to_ascii__convert_element_2), 2);
      Run:      begin core.run; answer = True; end
      Out:      begin core.derefReq(slot.sub(o.a)); answer = True; end
      BindKey:  begin core.unifyReq(slot.sub(o.a), bindTo); answer = True; end
      BindSlot: begin core.unifyReq(slot.sub(o.a), slot.sub(o.b)); answer = True; end
      NextKey:  goal <= goal + 1;
      Finish:   $finish(0);
    endcase
    if (answer) awaited <= True;
    else if (o.k == NextKey) ip <= (goal < 65536) ? 0 : ip + 1;
    else ip <= ip + 1;
  endrule

  rule gotVar (awaited && o.k == NewVar);
    let v <- core.newVarResult;
    slot.upd(o.a, v);
    awaited <= False;
    ip <= ip + 1;
  endrule

  rule ran (awaited && o.k == Run);
    let e <- core.finished;
    awaited <= False;
    ip <= ip + 1;
  endrule

  rule printed (awaited && o.k == Out);
    let w <- core.derefResp;
    $display("O %02x%08x", w.tag, w.val);
    awaited <= False;
    ip <= ip + 1;
  endrule

  rule unified (awaited && (o.k == BindKey || o.k == BindSlot));
    let ok <- core.unifyDone;
    awaited <= False;
    ip <= ip + 1;
  endrule
endmodule

endpackage
