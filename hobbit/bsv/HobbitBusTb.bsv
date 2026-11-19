// HobbitBusTb.bsv -- PASS/FAIL checks for the Appendix A bus face.
//
// Evidence: January 1993 PRM Appendix A (pp. A-1..A-8) and the December
// 1992 data sheet Table 1:
//   A.1/A.2  BGRANT/BREQ/BGACK ownership and surrender   pp. A-1/A-2
//   A.3      START begins, DTACK ends, IOC = 0 ends a block p. A-4
//   A.3.1    text reads are double-word; data single/double/quad
//   A.3.4    block beats increment HA[3:2], decrement IOC[1:0] p. A-6
//   A.4.1    RETRY masks DTACK and reruns the transaction   p. A-6
//   A.4.2    BERR with DTACK ends the transaction in error  p. A-6
//   data sheet p. 10: BE0..BE3 -> HD[7:0]..HD[31:24], byte/half
//   replication on HD; pp. 1-3/1-4: big-endian byte 0 = HD[31:24],
//   little-endian byte 0 = HD[7:0], text is big-endian.
//
// The testbench has one always-on clock counter (`tick`) and one action
// rule that fires only on cycles where a bus method is called.  A single
// always-firing case rule would conflict with the bus engine every cycle
// and starve it; the guard keeps the engine free on the intervening
// clocks.

package HobbitBusTb;

import Vector::*;
import HobbitTypes::*;
import HobbitBus::*;
import HobbitBusTbMem::*;

(* synthesize *)
module mkHobbitBusTb(Empty);
  HobbitBusTbMem mem <- mkHobbitBusTbMem;

  Reg#(Bit#(16)) t <- mkReg(0);
  function Vector#(4, Word) v4(Word a, Word b, Word c, Word d);
    Vector#(4, Word) v = replicate(0);
    v = update(v, 0, a);
    v = update(v, 1, b);
    v = update(v, 2, c);
    return update(v, 3, d);
  endfunction

  // Call sites pass the compared expression, the label, the expression
  // to print, and the expected value.
  function Action chk(Word got, String label, Word shown, Word want) =
    action
      if (got == want) $display("PASS %s = 0x%08x", label, shown);
      else $display("FAIL %s = 0x%08x, want 0x%08x", label, shown, want);
    endaction;

  function Action chkb(Bool ok, String label) =
    action
      if (ok) $display("PASS %s", label);
      else    $display("FAIL %s", label);
    endaction;

  rule tick;
    t <= t + 1;
  endrule

  // Cycles on which a bus method is called.
  function Bool isAction(Bit#(16) x);
    case (x)
      16'd0, 16'd1, 16'd2, 16'd3, 16'd4, 16'd5, 16'd6,
      16'd8, 16'd9, 16'd10,
      16'd12, 16'd13, 16'd14, 16'd15, 16'd16, 16'd17, 16'd18, 16'd19,
      16'd20, 16'd21, 16'd22, 16'd23, 16'd24, 16'd25, 16'd26,
      16'd27, 16'd28, 16'd29, 16'd30,
      16'd33, 16'd34, 16'd35, 16'd36, 16'd37,
      16'd42, 16'd43, 16'd44, 16'd47,
      16'd50, 16'd51, 16'd52, 16'd53, 16'd54, 16'd55, 16'd56,
      16'd58, 16'd59, 16'd60, 16'd61, 16'd62, 16'd64, 16'd65,
      16'd66, 16'd67, 16'd69, 16'd71, 16'd72, 16'd74, 16'd75,
      16'd77, 16'd78, 16'd79, 16'd80, 16'd81, 16'd82, 16'd83,
      16'd84, 16'd85:
        return True;
      default: return False;
    endcase
  endfunction

  rule act (isAction(t));
    case (t)
      // ---- reset and a word write/read -----------------------------
      16'd0: mem.master.resetBus();
      16'd1: mem.master.writeWord(32'h00000100, 32'h11223344);
      16'd2: begin
        // A.3 p. A-4: START begins the transfer; a word is BE = 1111,
        // IOC = 0, D/T high (data), no LOCK.
        chkb(mem.writePins().start, "word_write_start");
        chk(mem.writePins().ha, "word_write_ha",
            mem.writePins().ha, 32'h100);
        chk(zeroExtend(mem.writePins().be), "word_write_be",
            zeroExtend(mem.writePins().be), 32'h0000000F);
        chk(zeroExtend(mem.writePins().ioc), "word_write_ioc",
            zeroExtend(mem.writePins().ioc), 0);
        chkb(mem.writePins().dtri, "word_write_dtri_data");
        mem.master.readDataWord(32'h00000100);
      end
      16'd3: begin
        chk(mem.master.readData(), "word_read_data",
            mem.master.readData(), 32'h11223344);
        chk(zeroExtend(mem.pins().be), "word_read_be",
            zeroExtend(mem.pins().be), 32'h0000000F);
        chkb(mem.pins().read, "word_read_rd");
        // big-endian byte 0 is HD[31:24] -> BE3.
        mem.master.writeSub(32'h00000104, 32'h000000AA, BUS_BYTE);
      end
      16'd4: begin
        chk(zeroExtend(mem.writePins().be), "byte_be_write_be",
            zeroExtend(mem.writePins().be), 32'h00000008);
        chk(mem.writePins().hd, "byte_be_write_hd_replicated",
            mem.writePins().hd, 32'hAAAAAAAA);
        mem.master.readSub(32'h00000104, BUS_BYTE);
      end
      16'd5: begin
        chk(extractSub(mem.master.readData(), 32'h104, BUS_BYTE, False),
            "byte_be_read_value",
            extractSub(mem.master.readData(), 32'h104, BUS_BYTE, False),
            32'hAA);
        chk(zeroExtend(mem.pins().be), "byte_be_read_be",
            zeroExtend(mem.pins().be), 32'h00000008);
        mem.master.writeSub(32'h00000106, 32'h000000BB, BUS_BYTE);
      end
      16'd6: begin
        chk(zeroExtend(mem.writePins().be), "byte_be_lane2_be",
            zeroExtend(mem.writePins().be), 32'h00000002);
        mem.master.readDataWord(32'h00000104);
      end
      16'd7: chk(mem.master.readData(), "byte_be_merge",
                 mem.master.readData(), 32'hAA00BB00);
      16'd8: mem.master.writeSub(32'h00000108, 32'h0000BEEF, BUS_HALF);
      16'd9: begin
        chk(zeroExtend(mem.writePins().be), "half_be_write_be",
            zeroExtend(mem.writePins().be), 32'h0000000C);
        chk(mem.writePins().hd, "half_be_write_hd_replicated",
            mem.writePins().hd, 32'hBEEFBEEF);
        mem.master.readSub(32'h00000108, BUS_HALF);
      end
      16'd10: begin
        chk(extractSub(mem.master.readData(), 32'h108, BUS_HALF, False),
            "half_be_read_value",
            extractSub(mem.master.readData(), 32'h108, BUS_HALF, False),
            32'hBEEF);
        mem.master.setEndian(True);
      end
      // ---- little-endian (the setter applies one clock later) ------
      16'd12: mem.master.writeSub(32'h0000010C, 32'h000000CC, BUS_BYTE);
      16'd13: begin
        chk(zeroExtend(mem.writePins().be), "byte_le_write_be",
            zeroExtend(mem.writePins().be), 32'h00000001);
        chk(mem.writePins().hd, "byte_le_write_hd_replicated",
            mem.writePins().hd, 32'hCCCCCCCC);
        mem.master.readSub(32'h0000010C, BUS_BYTE);
      end
      16'd14: begin
        chk(extractSub(mem.master.readData(), 32'h10C, BUS_BYTE, True),
            "byte_le_read_value",
            extractSub(mem.master.readData(), 32'h10C, BUS_BYTE, True),
            32'hCC);
        mem.master.writeSub(32'h0000010E, 32'h00001234, BUS_HALF);
      end
      16'd15: begin
        chk(zeroExtend(mem.writePins().be), "half_le_write_be",
            zeroExtend(mem.writePins().be), 32'h0000000C);
        chk(mem.writePins().hd, "half_le_write_hd_replicated",
            mem.writePins().hd, 32'h12341234);
        mem.master.readDataWord(32'h0000010C);
      end
      16'd16: begin
        chk(mem.master.readData(), "le_word_value",
            mem.master.readData(), 32'h123400CC);
        mem.master.readSub(32'h0000010C, BUS_BYTE);
      end
      16'd17: begin
        chk(extractSub(mem.master.readData(), 32'h10C, BUS_BYTE, True),
            "le_word_byte0",
            extractSub(mem.master.readData(), 32'h10C, BUS_BYTE, True),
            32'hCC);
        mem.master.readSub(32'h0000010E, BUS_HALF);
      end
      16'd18: begin
        chk(extractSub(mem.master.readData(), 32'h10E, BUS_HALF, True),
            "le_word_half",
            extractSub(mem.master.readData(), 32'h10E, BUS_HALF, True),
            32'h1234);
        mem.master.setEndian(False);
      end
      16'd19: mem.master.writeWord(32'h00000110, 32'h01020304);
      // pp. 1-3/1-4: big-endian byte 0 = HD[31:24] = 0x01.
      16'd20: mem.master.readSub(32'h00000110, BUS_BYTE);
      16'd21: begin
        chk(extractSub(mem.master.readData(), 32'h110, BUS_BYTE, False),
            "be_byte0",
            extractSub(mem.master.readData(), 32'h110, BUS_BYTE, False),
            32'h01);
        mem.master.readSub(32'h00000111, BUS_BYTE);
      end
      16'd22: begin
        chk(extractSub(mem.master.readData(), 32'h111, BUS_BYTE, False),
            "be_byte1",
            extractSub(mem.master.readData(), 32'h111, BUS_BYTE, False),
            32'h02);
        mem.master.readSub(32'h00000112, BUS_BYTE);
        mem.master.setEndian(True);
      end
      16'd23: begin
        chk(extractSub(mem.master.readData(), 32'h112, BUS_BYTE, False),
            "be_byte2",
            extractSub(mem.master.readData(), 32'h112, BUS_BYTE, False),
            32'h03);
        mem.master.readSub(32'h00000113, BUS_BYTE);
      end
      16'd24: begin
        chk(extractSub(mem.master.readData(), 32'h113, BUS_BYTE, False),
            "be_byte3",
            extractSub(mem.master.readData(), 32'h113, BUS_BYTE, False),
            32'h04);
        mem.master.readSub(32'h00000110, BUS_BYTE);
      end
      16'd25: begin
        chk(extractSub(mem.master.readData(), 32'h110, BUS_BYTE, True),
            "le_byte0",
            extractSub(mem.master.readData(), 32'h110, BUS_BYTE, True),
            32'h04);
        mem.master.readSub(32'h00000111, BUS_BYTE);
      end
      16'd26: begin
        chk(extractSub(mem.master.readData(), 32'h111, BUS_BYTE, True),
            "le_byte1",
            extractSub(mem.master.readData(), 32'h111, BUS_BYTE, True),
            32'h03);
        mem.master.readSub(32'h00000112, BUS_BYTE);
      end
      16'd27: begin
        chk(extractSub(mem.master.readData(), 32'h112, BUS_BYTE, True),
            "le_byte2",
            extractSub(mem.master.readData(), 32'h112, BUS_BYTE, True),
            32'h02);
        mem.master.readSub(32'h00000113, BUS_BYTE);
      end
      16'd28: begin
        chk(extractSub(mem.master.readData(), 32'h113, BUS_BYTE, True),
            "le_byte3",
            extractSub(mem.master.readData(), 32'h113, BUS_BYTE, True),
            32'h01);
        mem.master.setEndian(False);
        mem.master.writeWord(32'h00000200, 32'hDEADBEEF);
      end
      16'd29: mem.master.writeWord(32'h00000204, 32'hCAFEF00D);
      // ---- double-word data block read -----------------------------
      16'd30: mem.master.readBlock(32'h00000200, BUS_DOUBLE, False);
      16'd31: noAction;   // engine issues beat 0
      16'd32: begin
        chk(mem.master.blockBeat(), "block_double_beat0",
            mem.master.blockBeat(), 32'hDEADBEEF);
        chk(zeroExtend(mem.blockPins().ioc), "block_double_ioc0",
            zeroExtend(mem.blockPins().ioc), 1);
        chk(mem.blockPins().ha, "block_double_ha0",
            mem.blockPins().ha, 32'h200);
        chkb(mem.blockPins().start, "block_double_start0");
        // engine issues beat 1
      end
      16'd33: begin
        chk(mem.master.blockBeat(), "block_double_beat1",
            mem.master.blockBeat(), 32'hCAFEF00D);
        chk(zeroExtend(mem.blockPins().ioc), "block_double_ioc1",
            zeroExtend(mem.blockPins().ioc), 0);
        chk(mem.blockPins().ha, "block_double_ha1",
            mem.blockPins().ha, 32'h204);
        chkb(mem.master.blockDone(), "block_double_done");
        mem.master.writeWord(32'h00000210, 32'h11111111);
      end
      16'd34: mem.master.writeWord(32'h00000214, 32'h22222222);
      16'd35: mem.master.writeWord(32'h00000218, 32'h33333333);
      16'd36: mem.master.writeWord(32'h0000021C, 32'h44444444);
      // ---- quad-word data block read -------------------------------
      16'd37: mem.master.readBlock(32'h00000210, BUS_QUAD, False);
      16'd38: noAction;
      16'd39: begin
        chk(mem.master.blockBeat(), "block_quad_beat0",
            mem.master.blockBeat(), 32'h11111111);
        chk(zeroExtend(mem.blockPins().ioc), "block_quad_ioc3",
            zeroExtend(mem.blockPins().ioc), 3);
      end
      16'd40: begin
        chk(mem.master.blockBeat(), "block_quad_beat1",
            mem.master.blockBeat(), 32'h22222222);
        chk(zeroExtend(mem.blockPins().ioc), "block_quad_ioc2",
            zeroExtend(mem.blockPins().ioc), 2);
      end
      16'd41: begin
        chk(mem.master.blockBeat(), "block_quad_beat2",
            mem.master.blockBeat(), 32'h33333333);
        chk(zeroExtend(mem.blockPins().ioc), "block_quad_ioc1",
            zeroExtend(mem.blockPins().ioc), 1);
      end
      16'd42: begin
        chk(mem.master.blockBeat(), "block_quad_beat3",
            mem.master.blockBeat(), 32'h44444444);
        chk(zeroExtend(mem.blockPins().ioc), "block_quad_ioc0",
            zeroExtend(mem.blockPins().ioc), 0);
        chkb(mem.master.blockDone(), "block_quad_done");
        mem.master.writeWord(32'h00000220, 32'h00112233);
      end
      // ---- text double-word block ----------------------------------
      16'd43: mem.master.writeWord(32'h00000224, 32'h44556677);
      16'd44: mem.master.readTextLine(32'h00000220);
      16'd45: noAction;
      16'd46: begin
        chk(mem.master.blockBeat(), "text_block_beat0",
            mem.master.blockBeat(), 32'h00112233);
        chkb(!mem.blockPins().dtri, "text_block_dtri_text");
        chk(zeroExtend(mem.blockPins().ioc), "text_block_ioc1",
            zeroExtend(mem.blockPins().ioc), 1);
      end
      16'd47: begin
        chk(mem.master.blockBeat(), "text_block_beat1",
            mem.master.blockBeat(), 32'h44556677);
        chk(zeroExtend(mem.blockPins().ioc), "text_block_ioc0",
            zeroExtend(mem.blockPins().ioc), 0);
        chkb(mem.master.blockDone(), "text_block_done");
        mem.master.writeBlock(32'h00000230, BUS_DOUBLE,
                              v4(32'h11111111, 32'h22222222,
                                 32'h0, 32'h0));
      end
      // ---- double-word block write ---------------------------------
      16'd50: mem.master.readDataWord(32'h00000230);
      16'd51: begin
        chk(mem.master.readData(), "block_write_word0",
            mem.master.readData(), 32'h11111111);
        mem.master.readDataWord(32'h00000234);
      end
      16'd52: begin
        chk(mem.master.readData(), "block_write_word1",
            mem.master.readData(), 32'h22222222);
        mem.setRetry(True);
      end
      // ---- RETRY ---------------------------------------------------
      16'd53: mem.master.readDataWord(32'h00000100);
      16'd54: begin
        chkb(mem.retried(), "retry_seen");
        mem.setRetry(False);
      end
      16'd55: mem.master.readDataWord(32'h00000100);
      16'd56: begin
        chkb(!mem.retried(), "retry_cleared");
        chk(mem.master.readData(), "retry_rerun_data",
            mem.master.readData(), 32'h11223344);
        mem.setBerr(True);
      end
      // ---- BERR ----------------------------------------------------
      16'd57: noAction;
      16'd58: mem.master.writeWord(32'h00000100, 32'hBAD0BAD0);
      16'd59: begin
        chkb(mem.busError(), "bus_error_seen");
        mem.setBerr(False);
      end
      16'd60: mem.master.readDataWord(32'h00000100);
      16'd61: begin
        chkb(mem.master.readData() != 32'hBAD0BAD0, "bus_error_no_write");
        mem.setHold(True);
      end
      // ---- HOLD ----------------------------------------------------
      16'd62: mem.master.writeWord(32'h00000240, 32'h00000055);
      16'd63: noAction;
      16'd64: mem.setHold(False);
      16'd65: mem.master.readDataWord(32'h00000240);
      16'd66: begin
        chk(mem.master.readData(), "hold_no_write",
            mem.master.readData(), 0);
        mem.master.writeWord(32'h00000240, 32'h00000055);
      end
      16'd67: mem.master.readDataWord(32'h00000240);
      16'd68: noAction;
      // ---- BGRANT / BGACK / BREQ -----------------------------------
      16'd69: mem.setBgrant(False);
      16'd70: noAction;
      16'd71: begin
        chkb(!mem.granted(), "bgack_released");
        mem.master.writeWord(32'h00000244, 32'h00000066);
      end
      16'd72: begin
        chkb(!mem.writePins().start, "no_start_without_bgrant");
        chkb(mem.breq(), "breq_while_waiting");
        mem.setBgrant(True);
      end
      16'd73: noAction;
      16'd74: begin
        chkb(mem.granted(), "bgack_regranted");
        mem.master.writeWord(32'h00000244, 32'h00000066);
      end
      16'd75: mem.master.readDataWord(32'h00000244);
      16'd76: noAction;
      // ---- NCACHE --------------------------------------------------
      16'd77: mem.master.setNcache(False);
      16'd78: mem.master.readDataWord(32'h00000100);
      16'd79: begin
        chkb(!mem.pins().ncache, "ncache_deasserted");
        mem.master.setNcache(True);
      end
      16'd80: mem.master.readDataWord(32'h00000100);
      16'd81: begin
        chkb(mem.pins().ncache, "ncache_asserted");
        mem.master.setLock(True);
      end
      // ---- LOCK (interlocked read-modify-write) --------------------
      16'd82: mem.master.readDataWord(32'h00000100);
      16'd83: begin
        chkb(mem.pins().lock, "lock_read_asserted");
        mem.master.writeWord(32'h00000100, 32'h11223344);
      end
      16'd84: begin
        chkb(mem.writePins().lock, "lock_write_asserted");
        mem.master.setLock(False);
      end
      16'd85: begin
        chkb(!mem.overrun(), "no_queue_overrun");
        $display("SUMMARY bus: done");
        $finish;
      end
      default: noAction;
    endcase
  endrule

  // Check-only cycles: no bus method is called, so this rule cannot
  // starve the block engine.
  function Bool isCheck(Bit#(16) x);
    case (x)
      16'd7, 16'd32, 16'd39, 16'd40, 16'd41, 16'd46,
      16'd63, 16'd68, 16'd76:
        return True;
      default: return False;
    endcase
  endfunction

  rule check (isCheck(t));
    case (t)
      16'd7: chk(mem.master.readData(), "byte_be_merge",
                 mem.master.readData(), 32'hAA00BB00);
      16'd32: begin
        chk(mem.master.blockBeat(), "block_double_beat0",
            mem.master.blockBeat(), 32'hDEADBEEF);
        chk(zeroExtend(mem.blockPins().ioc), "block_double_ioc0",
            zeroExtend(mem.blockPins().ioc), 1);
        chk(mem.blockPins().ha, "block_double_ha0",
            mem.blockPins().ha, 32'h200);
        chkb(mem.blockPins().start, "block_double_start0");
      end
      16'd39: begin
        chk(mem.master.blockBeat(), "block_quad_beat0",
            mem.master.blockBeat(), 32'h11111111);
        chk(zeroExtend(mem.blockPins().ioc), "block_quad_ioc3",
            zeroExtend(mem.blockPins().ioc), 3);
      end
      16'd40: begin
        chk(mem.master.blockBeat(), "block_quad_beat1",
            mem.master.blockBeat(), 32'h22222222);
        chk(zeroExtend(mem.blockPins().ioc), "block_quad_ioc2",
            zeroExtend(mem.blockPins().ioc), 2);
      end
      16'd41: begin
        chk(mem.master.blockBeat(), "block_quad_beat2",
            mem.master.blockBeat(), 32'h33333333);
        chk(zeroExtend(mem.blockPins().ioc), "block_quad_ioc1",
            zeroExtend(mem.blockPins().ioc), 1);
      end
      16'd46: begin
        chk(mem.master.blockBeat(), "text_block_beat0",
            mem.master.blockBeat(), 32'h00112233);
        chkb(!mem.blockPins().dtri, "text_block_dtri_text");
        chk(zeroExtend(mem.blockPins().ioc), "text_block_ioc1",
            zeroExtend(mem.blockPins().ioc), 1);
      end
      16'd63: chkb(!mem.writePins().start, "hold_no_start");
      16'd68: chk(mem.master.readData(), "hold_released_write",
                 mem.master.readData(), 32'h55);
      16'd76: chk(mem.master.readData(), "write_after_regrant",
                 mem.master.readData(), 32'h66);
      default: noAction;
    endcase
  endrule

endmodule

endpackage
