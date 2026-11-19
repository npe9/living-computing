// HobbitCore.bsv -- orchestration of the ATT92010 Hobbit model.
//
// Structure (the idiomatic-Bluespec requirement in AGENTS.md):
//   * HobbitDecode is its own module with a decode() interface;
//   * HobbitStackCache is its own stateful request/response box;
//   * a depth-1 FIFO is the separate decoded-instruction register;
//   * one fetch/decode rule moves a bundle into the FIFO, one execute
//     rule moves it out and writes back PC and architectural state.
//
// Modelled architectural facts:
//   * reset PC = 0 and CONFIG = 0; PSW = 0 selects the interrupt stack
//     pointer as CSP (p. 1-35).  This milestone models CSP = SP only,
//     so the smoke harness starts the core with software-selected
//     SP/MSP; the PRM does not give SP/MSP reset values.
//   * CALL stores the next PC at CSP (R0) (p. 3-9); RETURN reads the
//     new PC at CSP+src and then adds src to CSP (p. 3-39).
//   * the integer accumulator is the word at CSP+4 (p. 1-7).
//   * CMPEQ sets PSW.F; JMPT/JMPF test it, Y/N is only prediction
//     (p. 1-33, p. 3-28).
//   * one-parcel branches fold into a preceding foldable instruction
//     (p. 4-7) and folded branches are not separately retired (p. 1-33).
//   * an unimplemented parcel, the CPU escape, a bad length prefix or
//     an unmodelled addressing mode raises a loud, recorded trap.
//
// Retirement record: one HRI line per retired instruction, in program
// order.  HRI is the Hobbit Retirement Interface, the Hobbit analogue of
// riscv-formal's RVFI; checking is retire-trace comparison against an
// independent one-instruction model, not a yosys formal proof.
// A stack-cache write counts as an architectural write (the accumulator
// at CSP+4 included); cache flush/refill does not, because it creates no
// new architectural value.

package HobbitCore;

import FIFOF::*;
import Vector::*;
import HobbitTypes::*;
import HobbitDecode::*;
import HobbitStackCache::*;

interface HobbitCore;
  method Action start(Word sp, Word msp);

  method Bool halted();
  method Bool atLimit();
  method Bool faulted();
  method Word faultPc();
  method Word pc();

  method Word sp();
  method Word msp();
  method Word acc();
  method Word readMem(Word addr);
  method Word cacheWord(Word addr);
  method Bool cached(Word addr);

  method Bit#(32) folded();
  method Bit#(32) refills();
  method Bit#(32) instrs();
  method Word minSp();
  method Word maxSp();

  method Bool hriValid();
  method Hri hri();
endinterface

typedef struct {
  Bool we;
  Word addr;
  Word data;
} WrInfo deriving (Bits);

module mkHobbitCore#(HobbitMem mem, Word pcLimit)(HobbitCore);

  HobbitDecode dec <- mkHobbitDecode;
  HobbitStackCache sc <- mkHobbitStackCache(mem);

  FIFOF#(DecodedInstr) dq <- mkFIFOF;

  Reg#(Word) pcReg <- mkReg(0);
  Reg#(Bool) running <- mkReg(False);
  Reg#(Bool) faultedR <- mkReg(False);
  Reg#(Word) faultPcR <- mkReg(0);
  Reg#(Bool) pswF <- mkReg(False);
  Reg#(Bit#(32)) ninstr <- mkReg(0);
  Reg#(Bit#(32)) nfold <- mkReg(0);

  // A folded branch retires architecturally as its own instruction after
  // its host, so one execute can leave two HRI records to print.
  Hri nullHri = Hri { valid: False, pc: 0, insn0: 0, insn1: 0,
                      sp_before: 0, sp_after: 0,
                      msp_before: 0, msp_after: 0,
                      mem_we: False, mem_addr: 0, mem_wdata: 0,
                      mem_wmask: 0, trap: False };
  Reg#(Hri) hri0 <- mkReg(nullHri);
  Reg#(Hri) hri1 <- mkReg(nullHri);
  Reg#(Bit#(2)) hriCnt <- mkReg(0);

  // Big-endian parcel split of the shared image format: the parcel at an
  // even address is bits 31:16 of its word (p. 1-21 and the contract).
  function Parcel parcelAt(Word a);
    Word w = mem.read(a & 32'hFFFFFFFC);
    return (a[1] == 1'b0) ? w[31:16] : w[15:0];
  endfunction

  function Word opAddr(Operand o);
    return (o.kind == OK_STACK) ? sc.csp() + o.val : o.val;
  endfunction

  function Word readOp(Operand o);
    return (o.kind == OK_IMM) ? o.val : sc.read(opAddr(o));
  endfunction

  // Signed greater-than for CMPGT (p. 3-13).  Bit#(32) unpacked to Int#(32)
  // gives the two's-complement interpretation; bsc has no $signed task.
  function Bool signedGt(Word a, Word b);
    Int#(32) x = unpack(a);
    Int#(32) y = unpack(b);
    return x > y;
  endfunction

  // The flag a folded branch must test.  A compare folded together with
  // its branch produces the new PSW.F in the same instruction, so the
  // branch sees the compare's result, not the previous flag (p. 3-13,
  // p. 3-28, p. 4-7).
  function Bool flagAfter(DecodedInstr d, Bool oldFlag);
    case (d.op)
      OP_CMPEQ: return readOp(d.src) == readOp(d.dst);
      OP_CMPGT: return signedGt(readOp(d.src), readOp(d.dst));
      default:  return oldFlag;
    endcase
  endfunction

  // The instruction's own destination write, for the HRI record.
  function WrInfo writeInfo(DecodedInstr d, Word base);
    case (d.op)
      OP_MOV: return WrInfo { we: True, addr: opAddr(d.dst),
                              data: readOp(d.src) };
      OP_ADD: return WrInfo { we: True, addr: opAddr(d.dst),
                              data: readOp(d.dst) + readOp(d.src) };
      OP_SUB: return WrInfo { we: True, addr: opAddr(d.dst),
                              data: readOp(d.dst) - readOp(d.src) };
      // ADD3 stores Acc = dst + src at CSP+4 (p. 1-7, p. 3-5); the
      // destination operand itself is unchanged.
      OP_ADD3: return WrInfo { we: True, addr: sc.csp() + 4,
                               data: readOp(d.dst) + readOp(d.src) };
      OP_CALL: return WrInfo { we: True, addr: sc.csp(), data: base };
      default: return WrInfo { we: False, addr: 0, data: 0 };
    endcase
  endfunction

  // --- fetch and decode -------------------------------------------
  rule fetchDecode (running && !faultedR && !dq.notEmpty() &&
                    (pcReg < pcLimit));
    Word pc = pcReg;
    Vector#(6, Parcel) ps = mkParcels(parcelAt(pc),
                                      parcelAt(pc + 2),
                                      parcelAt(pc + 4),
                                      parcelAt(pc + 6),
                                      parcelAt(pc + 8),
                                      parcelAt(pc + 10));
    dq.enq(dec.decode(pc, ps));
  endrule

  // --- execute -----------------------------------------------------
  rule execute (running && !faultedR && dq.notEmpty() &&
                (hriCnt == 0) && !sc.busy() && (pcReg < pcLimit));
    let d = dq.first();
    dq.deq();

    Word base = d.pc + plenBytes(d.plen);
    Word spb = sc.sp();
    Word mspb = sc.msp();

    if (d.tr != TR_NONE) begin
      // Unimplemented-instruction sequence, p. 1-39:
      //   *(CSP) = PC of the unimplemented opcode; PC = *(VB + 12).
      // The vector fetch is out of scope; the store is performed and is
      // this retired instruction's one architectural write.
      faultedR <= True;
      faultPcR <= d.pc;
      sc.write(spb, d.pc);
      $display("TRAP pc=0x%08x: %s", d.pc, trapText(d.tr));
      hri0 <= Hri { valid: True, pc: d.pc,
                    insn0: d.insn0, insn1: d.insn1,
                    sp_before: spb, sp_after: 0,
                    msp_before: mspb, msp_after: 0,
                    mem_we: True, mem_addr: spb, mem_wdata: d.pc,
                    mem_wmask: 8'h0F, trap: True };
      hri1 <= nullHri;
      hriCnt <= 1;
    end else begin
      WrInfo wr = writeInfo(d, base);

      if (isBranchOp(d.op)) begin
        case (d.op)
          OP_CALL: begin
            sc.call(base);
            pcReg <= d.src.val;
          end
          OP_RETURN: begin
            let rp <- sc.returnFrom(d.src.val);
            pcReg <= rp;
          end
          OP_JMP: pcReg <= d.src.val;
          default: pcReg <= branchTaken(d.op, pswF) ? d.src.val : base;
        endcase
      end else begin
        case (d.op)
          OP_MOV:   sc.write(opAddr(d.dst), readOp(d.src));
          OP_ADD:   sc.write(opAddr(d.dst), readOp(d.dst) + readOp(d.src));
          OP_SUB:   sc.write(opAddr(d.dst), readOp(d.dst) - readOp(d.src));
          OP_ADD3:  sc.write(sc.csp() + 4, readOp(d.dst) + readOp(d.src));
          OP_CMPEQ: pswF <= (readOp(d.src) == readOp(d.dst));
          // CMPGT is signed greater-than with src1 in the source field and
          // src2 in the destination field (p. 3-13 and its Notes).
          OP_CMPGT: pswF <= signedGt(readOp(d.src), readOp(d.dst));
          OP_ENTER: sc.enter((d.src.kind == OK_STACK)
                               ? sc.csp() + d.src.val : d.src.val,
                             d.src.kind == OK_STACK);
          OP_CATCH: sc.catchTo((d.src.kind == OK_STACK)
                                 ? sc.csp() + d.src.val : d.src.val);
          OP_POPN:  sc.popn(d.src.val);
          default:  noAction;
        endcase

        if (d.fold) begin
          nfold <= nfold + 1;
          pcReg <= branchTaken(d.foldOp, flagAfter(d, pswF))
                     ? d.foldTarget : d.foldAfter;
        end else
          pcReg <= base;
      end

      ninstr <= ninstr + 1;
      hri0 <= Hri { valid: True, pc: d.pc,
                    insn0: d.insn0, insn1: d.insn1,
                    sp_before: spb, sp_after: 0,
                    msp_before: mspb, msp_after: 0,
                    mem_we: wr.we, mem_addr: wr.addr, mem_wdata: wr.data,
                    mem_wmask: wr.we ? 8'h0F : 8'h00, trap: False };
      if (d.fold) begin
        // A folded branch retires as its own HRI record immediately after
        // its host, with the host's final state; it costs no cycle but is
        // not hidden (p. 4-7; a folded branch is still an instruction,
        // p. 1-33).
        hri1 <= Hri { valid: True, pc: d.foldPc,
                      insn0: d.foldInsn0, insn1: 0,
                      sp_before: spb, sp_after: 0,
                      msp_before: mspb, msp_after: 0,
                      mem_we: False, mem_addr: 0, mem_wdata: 0,
                      mem_wmask: 0, trap: False };
        hriCnt <= 2;
      end else begin
        hri1 <= nullHri;
        hriCnt <= 1;
      end
    end
  endrule

  // --- retire: one HRI line per architectural instruction, in order,
  // after multi-cycle stack-cache work has settled the after values ----
  rule retire ((hriCnt != 0) && !sc.busy());
    let r = hri0;
    Word spa = sc.sp();
    Word mspa = sc.msp();
    $display("HRI pc=%04x insn=%04x%04x sp=%08x>%08x msp=%08x>%08x we=%d addr=%08x data=%08x mask=%02x trap=%d",
             r.pc[15:0], r.insn0, r.insn1,
             r.sp_before, spa, r.msp_before, mspa,
             pack(r.mem_we), r.mem_addr, r.mem_wdata, r.mem_wmask,
             pack(r.trap));
    if (hriCnt == 2) begin
      hri0 <= hri1;
      hriCnt <= 1;
    end else
      hriCnt <= 0;
  endrule

  // --- interface ----------------------------------------------------
  method Action start(Word sp, Word msp);
    sc.reset(sp, msp);
    dq.clear();
    pcReg <= 0;
    running <= True;
    faultedR <= False;
    faultPcR <= 0;
    pswF <= False;
    ninstr <= 0;
    nfold <= 0;
    hri0 <= nullHri;
    hri1 <= nullHri;
    hriCnt <= 0;
  endmethod

  method Bool halted() = faultedR;
  method Bool atLimit() = (pcReg >= pcLimit);
  method Bool faulted() = faultedR;
  method Word faultPc() = faultPcR;
  method Word pc() = pcReg;

  method Word sp() = sc.sp();
  method Word msp() = sc.msp();
  method Word acc() = sc.read(sc.sp() + 4);
  method Word readMem(Word addr) = sc.read(addr);
  method Word cacheWord(Word addr) = sc.cacheWord(addr);
  method Bool cached(Word addr) = sc.cached(addr);

  method Bit#(32) folded() = nfold;
  method Bit#(32) refills() = sc.refills();
  method Bit#(32) instrs() = ninstr;
  method Word minSp() = sc.minSpSeen();
  method Word maxSp() = sc.maxSpSeen();

  method Bool hriValid() = (hriCnt != 0);
  method Hri hri() = hri0;

endmodule

endpackage
