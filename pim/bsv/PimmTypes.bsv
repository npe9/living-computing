// PIM/m core, real-binary track: shared types.
//
// This is the model that executes the PIMOS binaries' own cells (40-bit
// tagged words, the machine's tags, relative labels), built beside the
// bench model PimKL1B.bsv and following ref/pimm/pimm.py instruction
// for instruction (docs/pimm_semantics.md).  Tags, opcodes and the
// memory size come from PimmGen.bsv, written by asm/gen_pimm_bsv.py.
package PimmTypes;

import PimmGen::*;

typedef Bit#(AddrBits) Addr;

typedef struct {
  Bit#(8)  tag;
  Bit#(32) val;
} Cell deriving (Bits, Eq, FShow);

function Cell mkCell(Bit#(8) t, Bit#(32) v) = Cell { tag: t, val: v };

// The low tag bit is the o/x suffix of tagtbl.kl1; types ignore it.
function Bool isRef(Cell c)  = (c.tag | 1) == tag_REFx;
function Bool isInt(Cell c)  = (c.tag | 1) == tag_INTx;
function Bool isAtom(Cell c) = (c.tag | 1) == tag_ATOMx;
function Bool isHook(Cell c) = (c.tag | 1) == tag_HOOKx;
function Bool isStrg(Cell c) = (c.tag | 1) == tag_STRGx;

// What an unbound variable's cell holds: UNDF, or HOOK when goals wait.
function Bool isUnboundCell(Cell c) = c.tag == tag_UNDF || isHook(c);

// A pointer's memory index is its value less the load address, which
// has no bits inside the modelled memory.
function Addr cellAddr(Cell c) = truncate(c.val);
function Bit#(32) absAddr(Addr a) = loadAddress | zeroExtend(a);
function Bool inMemory(Bit#(32) v) =
  (v >> valueOf(AddrBits)) == (loadAddress >> valueOf(AddrBits));

// A label is relative to the instruction: here + 2 + c16.
function Addr labelOf(Addr here, Bit#(16) c16) = here + 2 + signExtend(c16);

function Cell intCell(Bit#(16) c16) = mkCell(tag_INTo, signExtend(c16));
function Cell intC(Bit#(32) v) = mkCell(tag_INTo, v);

typedef struct {
  Addr pc;
  Cell word;
  Cell next;       // the cell after it: the second word of a two-word instruction
} Fetched deriving (Bits, FShow);

// How a reduction ends.  Unimp and Error are the model failing loud:
// an instruction or case it does not implement, or a state the
// reference model treats as a machine error.  Idle is the machine,
// not a reduction: the ready queue is empty.
typedef enum { EndDone, EndFail, EndSusp, EndUnimp, EndError, EndIdle } End
  deriving (Bits, Eq, FShow);

typedef union tagged {
  Addr Next;
  End  Stop;
} Step deriving (Bits, FShow);

// A state neither model continues from: stop the simulation loud.
function Action fatal(String why);
  action
    $display("E error: %s", why);
    $finish(1);
  endaction
endfunction

// The lockstep trace, one line per event, the same text
// ref/pimm/pimm.py writes (docs/pimm_semantics.md "Trace").
function Action traceI(Addr pc, Cell c) =
  $display("I %0d %02x%08x", pc, c.tag, c.val);
function Action traceR(Bit#(8) r, Cell c) =
  $display("R %0d %02x%08x", r, c.tag, c.val);
function Action traceA(Bit#(8) r, Cell c) =
  $display("A %0d %02x%08x", r, c.tag, c.val);
function Action traceM(Addr a, Cell c) =
  $display("M %0d %02x%08x", a, c.tag, c.val);

endpackage
