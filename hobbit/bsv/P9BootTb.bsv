// Boot a 1st Edition Plan 9 `z` image on the model, with the A1 syscall
// shim.
//
// The image is produced by tools/p9exec.py: the whole file mapped at
// UTZERO (0x1000) as the 1e kernel's sysproc.c does, so the Exec header
// occupies 0x1000..0x101f, text begins at 0x1020 and data at the
// program's own bdata.
//
// What this testbench does is the loader's job plus the kernel side of
// the syscall:
//
//   * it places the shim stub (tools/p9shim.py, assembled by
//     asm/hobbit_asm.py) in the boot window's Exec header, the 32 bytes
//     below the text that the loader owns, and zero-fills the rest of
//     memory;
//   * it supplies the vector page (emem[VB] = stub) and watches the
//     doorbell: the KCALL's own frame write at ISP-12 is the word the
//     host polls and clears (PRM p. 3-29, *(ISP-12) = src);
//   * on the doorbell it decodes the id and the arguments from the
//     user's stack (SP+4/+8/+12, the 1e libc stub's convention), does
//     the syscall against a host file, and hands the result back
//     through two memory words the stub reads: RES, then RDY;
//   * when the stub has returned it does what KRET would: PSW from the
//     frame's ISP-4 word, ISP back up by the frame's 16 bytes;
//   * `exits` stops the run with a status.
//
// The machine does every instruction and every frame itself; only the
// kernel's work between KCALL and the return is the host's.
//
// Known limit: the host reads and writes the user's buffer in memory.
// A buffer word that is also inside the stack cache window [SP, MSP)
// has its current value in the cache, not in memory, so a program that
// touched such words itself would disagree with the host.  cat hands
// its buffer to read and write untouched, so this run does not depend
// on it; a kernel entry that flushes the cache is the real answer.
package P9BootTb;

import HobbitTypes::*;
import RegFile::*;
import HobbitCore::*;
import P9Image::*;
import P9Entry::*;
import P9Shim::*;

// A 64 Kbyte memory: text at 0x1020, data at bdata (0x3000 here), the
// user stack at 0x8000 and the shim's devices at 0x0c00..0x0d00.
interface P9Mem;
  interface HobbitMem bus;
  method Word peek(Word a);
  method Action poke(Word a, Word v);
  method Bool pokeIdle();
endinterface

module mkP9Mem(P9Mem);
  // bsc gives mkRegFileFull five read ports and counts one per distinct
  // address expression, not per source line.  The readers here are the
  // bus's registered read (the machine's only read: an operand outside
  // the stack cache is fetched through it, HobbitCore "Memory operands")
  // and the testbench's own probes.  A register vector has no port cap
  // but elaborates to a 46 Mbyte model and minutes of C++ per build --
  // the wrong price for a testbench.
  RegFile#(Bit#(14), Word) m <- mkRegFileFull;
  Reg#(Word) raddr <- mkReg(0);
  // The machine's write and the host's write share the one write port.
  // Both arrive on wires and one rule owns the port: the machine's write
  // goes straight through, and the host's waits one register for a clock
  // the machine does not write in (the host asks only while that
  // register is empty, `pokeIdle`).  When the two shared one wire, the
  // host's rule and the stack-cache box's rule conflicted, the box's rule
  // lost the clock, and the command it carried (an architectural write,
  // a pointer update) was dropped without a trace.  Wires in, one owner:
  // every host rule reads (`sub`) before this rule writes (`upd`), and
  // nothing here schedules against the machine.
  Wire#(Maybe#(Tuple2#(Word, Word))) busW <- mkDWire(tagged Invalid);
  Wire#(Maybe#(Tuple2#(Word, Word))) pokeW <- mkDWire(tagged Invalid);
  Reg#(Maybe#(Tuple2#(Word, Word))) pend <- mkReg(tagged Invalid);
  function Bit#(14) idx(Word a) = truncate(a >> 2);
  function Word readAt(Word a) = m.sub(idx(a));
  rule commitWr;
    Maybe#(Tuple2#(Word, Word)) w = tagged Invalid;
    if (isValid(busW)) begin
      w = busW;
      if (isValid(pokeW)) pend <= pokeW;
    end else if (isValid(pend)) begin
      w = pend;
      pend <= pokeW;
    end else
      w = pokeW;
    if (w matches tagged Valid {.a, .v}) m.upd(idx(a), v);
  endrule
  interface HobbitMem bus;
    method Action readReq(Word a); raddr <= a; endmethod
    method Word readData() = readAt(raddr);
    method Action write(Word a, Word v);
      busW <= tagged Valid tuple2(a, v);
    endmethod
    method Word peek(Word a) = readAt(a);
  endinterface
  method Word peek(Word a) = readAt(a);
  method Action poke(Word a, Word v);
    pokeW <= tagged Valid tuple2(a, v);
  endmethod
  method Bool pokeIdle() = !isValid(pend);
endmodule

typedef enum { SH_IDLE,      // waiting for a KCALL's frame
               SH_LATCH,     // the id is in the frame: decode the call
               SH_READ,      // copying the file into the user's buffer
               SH_WRITE,     // copying the user's buffer to the console
               SH_CLEAR,     // clear the doorbell
               SH_RESULT,    // write RES
               SH_READY,     // write RDY: the stub may go
               SH_RETURN     // waiting for the stub to return to the program
             } ShimState deriving (Bits, Eq);

(* synthesize *)
module mkP9BootTb(Empty);

  Word sp0  = shimSp0();        // 0x8000
  Word msp0 = shimMsp0();       // 0x8100
  Word psw0 = shimPsw0();       // PSW_S|PSW_X: CSP = SP, user level
  Word isp0 = shimIsp0();       // interrupt stack top
  // The whole run's clock budget.  cat over the 7,532-byte raml.s is two
  // host copies of a byte every clock or two plus a few thousand machine
  // clocks; this is several times that and still a log of megabytes.
  Bit#(32) shimClockLimit = 200000;

  P9Mem pm <- mkP9Mem;
  MemCycles mcyc = defaultMemCycles();
  HobbitCore core <- mkHobbitCore(pm.bus, 32'hFFFFFFFF, mcyc);

  Reg#(Bit#(16)) li <- mkReg(0);
  Reg#(Bool) loaded <- mkReg(False);
  Reg#(Bit#(2)) boot <- mkReg(0);
  Reg#(Bit#(32)) clocks <- mkReg(0);
  Reg#(File) con <- mkReg(InvalidFile);

  Reg#(Bool) ispSet <- mkReg(False);
  Reg#(ShimState) shState <- mkReg(SH_IDLE);
  Reg#(Word) shId <- mkReg(0);
  Reg#(Word) shResult <- mkReg(0);
  Reg#(Word) shAddr <- mkReg(0);      // byte address in the user buffer
  Reg#(Bit#(32)) shOff <- mkReg(0);   // byte offset in the host file
  Reg#(Bit#(32)) shLeft <- mkReg(0);  // bytes left to move
  Reg#(Bit#(32)) shFileOff <- mkReg(0);  // the open file's offset
  Reg#(Bool) shOpened <- mkReg(False);   // fd 3 has been opened
  Reg#(Bit#(32)) shWrites <- mkReg(0);
  Reg#(Bit#(32)) shReads <- mkReg(0);

  // ---- the loader ----------------------------------------------------
  // One poke per clock over the whole 64 Kbyte: the image, the stub over
  // the image's Exec header, and zero everywhere else (the RegFile has
  // no reset value, and the model's memory is zero-filled).
  rule load (!loaded && pm.pokeIdle);
    Word a = zeroExtend(li) << 2;
    Bool inCode = (a >= shimBase()) &&
                  (a < shimBase() + (shimCodeLength() << 2));
    Bool inImage = zeroExtend(li) < imageLength();
    Word v = inCode ? shimCodeWord(truncate((a - shimBase()) >> 2))
           : inImage ? imageWord(li)
           : 0;
    pm.poke(a, v);
    if (li == 16383) loaded <= True;
    else li <= li + 1;
  endrule

  rule ask (loaded && boot == 0 && pm.pokeIdle);
    core.setVb(shimVb());
    core.prefetchImageAt(p9fillbase());
    boot <= 1;
  endrule

  rule start ((boot == 1) && core.prefetchReady());
    // The vector page is the testbench's: its +0 word is the stub.
    // startAt installs ISP = SHAD = SP; shim_isp moves the ISP to the
    // shim's interrupt stack before the first KCALL.
    core.eventMemWrite(shimVb(), shimStub());
    core.startAt(shimBoot(), sp0, msp0, psw0);
    let f <- $fopen("p9.console", "w");
    con <= f;
    boot <= 2;
    $display("P9SHIM boot pc=%08x sp=%08x msp=%08x isp=%08x psw=%08x",
             shimBoot(), sp0, msp0, isp0, psw0);
  endrule

  // ---- helpers -------------------------------------------------------
  // A user stack word.  The three argument words are inside [SP, MSP)
  // whenever a KCALL can happen, so the cache is where the program put
  // them.
  function Word userWord(Word a);
    return core.cacheWord(a);
  endfunction

  function Bool inShim(Word pc);
    return (pc >= shimBase()) && (pc < shimBase() + 32);
  endfunction

  // ---- the host side of the syscall ----------------------------------
  // The interrupt stack is the kernel's job in a real boot (raml.s:16);
  // one write after the start is enough for the shim's own frames.
  rule shim_isp (boot == 2 && !ispSet);
    core.setIsp(isp0);
    core.setShad(isp0);
    ispSet <= True;
  endrule

  // The KCALL writes the id to ISP-12 first (p. 3-29).
  rule shim_door (boot == 2 && shState == SH_IDLE);
    let id = pm.peek(isp0 - 12);
    if (id != 0) begin
      shId <= id;
      shState <= SH_LATCH;
    end
  endrule

  rule shim_latch (boot == 2 && shState == SH_LATCH);
    let id = shId;
    Word sp = core.sp();
    Word a0 = userWord(sp + 4);
    Word a1 = userWord(sp + 8);
    Word a2 = userWord(sp + 12);
    let len = shimFileLength();
    if (id == 1) begin
      // errstr(buf, n): no error text to copy.
      shResult <= 0;
      shState <= SH_CLEAR;
      $display("P9SHIM syscall=%0d errstr buf=%08x n=%0d -> 0", id, a0, a1);
    end else if (id == 4) begin
      if (a0 == shimFileFd()) shOpened <= False;
      shResult <= 0;
      shState <= SH_CLEAR;
      $display("P9SHIM syscall=%0d close fd=%0d -> 0", id, a0);
    end else if (id == 8) begin
      $display("P9SHIM syscall=%0d exits msg=%08x reads=%0d writes=%0d",
               id, a0, shReads, shWrites);
      // 1e's exits(nil) is success; a message is a failure.
      $display("P9SHIM EXIT status=%0d", (a0 == 0) ? 0 : 1);
      $fclose(con);
      $finish;
    end else if (id == 14) begin
      // The shim serves one host file whatever the path names.
      shOpened <= True;
      shFileOff <= 0;
      shResult <= shimFileFd();
      shState <= SH_CLEAR;
      $display("P9SHIM syscall=%0d open path=%08x mode=%0d -> fd %0d (the shim's one file)",
               id, a0, a1, shimFileFd());
    end else if (id == 15) begin
      Bit#(32) off = shFileOff;
      Bit#(32) avail = (off < len) ? (len - off) : 0;
      Bit#(32) take = (a2 < avail) ? a2 : avail;
      if ((a0 != 0) && !((a0 == shimFileFd()) && shOpened)) begin
        $display("P9SHIM REFUSED read fd=%0d: only stdin (0) and this shim's file (fd %0d, once opened) exist",
                 a0, shimFileFd());
        $finish;
      end else begin
        shResult <= take;
        shAddr <= a1;
        shOff <= off;
        shLeft <= take;
        shFileOff <= off + take;
        shState <= (take == 0) ? SH_CLEAR : SH_READ;
        shReads <= shReads + 1;
        $display("P9SHIM syscall=%0d read fd=%0d buf=%08x n=%0d -> %0d",
                 id, a0, a1, a2, take);
      end
    end else if (id == 20) begin
      if ((a0 != 1) && (a0 != 2)) begin
        $display("P9SHIM REFUSED write fd=%0d: only the console (1,2) is writable", a0);
        $finish;
      end else begin
        shResult <= a2;
        shAddr <= a1;
        shLeft <= a2;
        shState <= (a2 == 0) ? SH_CLEAR : SH_WRITE;
        shWrites <= shWrites + 1;
        $display("P9SHIM syscall=%0d write fd=%0d buf=%08x n=%0d -> %0d",
                 id, a0, a1, a2, a2);
      end
    end else begin
      // Loud refusal: the number and where the set is defined.
      $display("P9SHIM REFUSED syscall %0d: not in the 1e syscall table (%s)",
               id, "hobbit/bin/cat stubs; hobbit/lib/libc.a members; raml.s _vectors");
      $finish;
    end
  endrule

  // read: one byte per step from the host file into the user's buffer,
  // merged into its word with big-endian lanes (the byte at a word
  // address is bits 31:24, PRM Figure 1-2).  1e itself runs little-endian
  // (PSW_UL, machine.h:77); cat cannot tell, because the same lanes are
  // used on the way in and on the way out and cat never reads a byte --
  // see tools/p9shim.py's Mem and tools/p9run.py.  Each step waits for the
  // previous poke to land, because the next byte may share its word.
  rule shim_read (boot == 2 && shState == SH_READ && pm.pokeIdle);
    let a = shAddr;
    let w = pm.peek(a);
    Bit#(32) shift = (3 - zeroExtend(a[1:0])) << 3;
    Word mask = 32'h0000_00FF << shift;
    Bit#(8) b = shimFileByte(truncate(shOff));
    pm.poke(a, (w & ~mask) | (zeroExtend(b) << shift));
    shAddr <= a + 1;
    shOff <= shOff + 1;
    shLeft <= shLeft - 1;
    if (shLeft == 1) shState <= SH_CLEAR;
  endrule

  // write: one byte per clock from the user's buffer to the console.
  rule shim_write (boot == 2 && shState == SH_WRITE);
    let a = shAddr;
    let w = pm.peek(a);
    Bit#(32) shift = (3 - zeroExtend(a[1:0])) << 3;
    Bit#(8) b = truncate(w >> shift);
    $fwrite(con, "%c", b);
    shAddr <= a + 1;
    shLeft <= shLeft - 1;
    if (shLeft == 1) shState <= SH_CLEAR;
  endrule

  // The answer, in the order the stub needs it: the doorbell cleared
  // (so the host cannot take this call twice), the result, then RDY.
  rule shim_clear (boot == 2 && shState == SH_CLEAR && pm.pokeIdle);
    pm.poke(isp0 - 12, 0);
    shState <= SH_RESULT;
  endrule

  rule shim_result (boot == 2 && shState == SH_RESULT && pm.pokeIdle);
    pm.poke(shimRes(), shResult);
    shState <= SH_READY;
  endrule

  rule shim_ready (boot == 2 && shState == SH_READY && pm.pokeIdle);
    pm.poke(shimRdy(), 1);
    shState <= SH_RETURN;
    $display("P9SHIM result=%08x", shResult);
  endrule

  // The stub's RETURN has redirected the PC back into the program.  The
  // host now does the rest of KRET: the PSW the KCALL saved at ISP-4
  // (its PSW &= 0xFFFF0000 and the stub's own compare are the writers
  // since), and the frame's 16 bytes back on the interrupt stack (p. 3-29
  // moved ISP down by 16) -- otherwise the next KCALL's doorbell lands
  // 16 bytes below the word the host polls.  RDY is cleared for the next
  // call.
  rule shim_return (boot == 2 && shState == SH_RETURN && pm.pokeIdle &&
                    !inShim(core.pc()));
    core.setPsw(pm.peek(isp0 - 4));
    core.setIsp(isp0);
    pm.poke(shimRdy(), 0);
    shState <= SH_IDLE;
    $display("P9SHIM return pc=%08x", core.pc());
  endrule

  // ---- observation ----------------------------------------------------
  // The watchdog writes nothing the shim rules read (`$finish` alone
  // ends the run), so it fires every clock.  When it also set a `done`
  // flag it conflicted with every shim rule, lost to `shim_door` on
  // urgency, and the clock count stood still: a run that went wrong then
  // spun in the stub and wrote HRI lines until the disk filled (5 Gbyte,
  // twice).
  rule observe (boot == 2);
    clocks <= clocks + 1;
    if (core.faulted()) begin
      $display("P9SHIM FAULT pc=%08x clocks=%0d", core.faultPc(), clocks);
      $fclose(con);
      $finish;
    end else if (clocks > shimClockLimit) begin
      $display("P9SHIM STOP clocks=%0d pc=%08x state=%0d psw=%08x", clocks,
               core.pc(), pack(shState), core.psw());
      $fclose(con);
      $finish;
    end
  endrule

endmodule
endpackage
