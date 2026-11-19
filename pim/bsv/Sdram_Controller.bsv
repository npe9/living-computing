// ================================================================
// Sdram_Controller: bridge between Flute's "raw memory" port
// (256-bit words, byte-enables, fire-and-forget writes, one
// outstanding request) and the ULX3S's 32 MB Winbond W9825G6KH-6
// 16-bit SDR SDRAM, running from the 25 MHz board clock.
//
// Raw-memory address r is a 32-byte granule number:
//   byte  = r << 5,  halfword = r << 4
//   bank  = r[6:5],  row = r[19:7],  col base = {r[4:0], 4'b0}
// A 256-bit request is two BL8 bursts (burst 0 at col, burst 1 at
// col+8), with auto-precharge, so all banks are closed between
// requests and refresh can be inserted at request boundaries.
//
// Timing constants are in system clock cycles (25 MHz = 40 ns; the PLL
// build runs at 32.14 MHz = 31.1 ns): tRCD 1 (>=18 ns), CL 2, tRFC and the
// init gaps derived from clk_hz (>=66 ns, at least 2), refresh every 98
// cycles (<= 7.8 us at any clock >= 12.5 MHz), power-up wait 200 us.
// ================================================================

package Sdram_Controller;

export Sdram_Controller_IFC (..), mkSdram_Controller;

import Vector      :: *;
import FIFOF       :: *;
import GetPut      :: *;
import ClientServer :: *;
import Memory      :: *;    // MemoryRequest, MemoryResponse, MemoryServer

import Mem_Controller :: *;    // Bits_per_Raw_Mem_Addr/WWord

// ================================================================

// JEDEC command encoding {cs_n, ras_n, cas_n, we_n}
Bit #(4) cmd_nop     = 4'b0111;
Bit #(4) cmd_act     = 4'b0011;
Bit #(4) cmd_read    = 4'b0101;
Bit #(4) cmd_write   = 4'b0100;
Bit #(4) cmd_pre     = 4'b0010;
Bit #(4) cmd_ref     = 4'b0001;
Bit #(4) cmd_mrs     = 4'b0000;

// Mode register: CL2, BL8, sequential burst, write bursts enabled
Bit #(13) mode_reg_value = 13'h0023;

Integer t_rcd         = 1;     // ACT -> READ/WRITE
Integer t_cas_first   = 3;     // IOB reg + BSV input reg pipeline (sim-validated)
Integer refresh_div   = 98;     // 7.8 us at 12.5 MHz (80 ns/cycle)

// ================================================================

typedef enum {ST_PWR_WAIT,
              ST_PRE_ALL, ST_PRE_ALL_WAIT,
              ST_INIT_REF1, ST_INIT_REF1_WAIT,
              ST_INIT_REF2, ST_INIT_REF2_WAIT,
              ST_MRS, ST_MRS_WAIT,
              ST_IDLE,
              ST_ACT, ST_RCD_WAIT,
              ST_RD, ST_RD_CAP,
              ST_GAP,
              ST_WR, ST_WR_DATA, ST_WR_END,
              ST_REF, ST_REF_WAIT } State
deriving (Bits, Eq, FShow);

// ================================================================

interface Sdram_Controller_IFC;
   interface MemoryServer #(Bits_per_Raw_Mem_Addr, Bits_per_Raw_Mem_Word)  mem_server;

   (* always_ready *) method Bool     init_done;

   (* always_ready *) method Bit #(1)  sdram_cke;
   (* always_ready *) method Bit #(1)  sdram_cs_n;
   (* always_ready *) method Bit #(1)  sdram_ras_n;
   (* always_ready *) method Bit #(1)  sdram_cas_n;
   (* always_ready *) method Bit #(1)  sdram_we_n;
   (* always_ready *) method Bit #(2)  sdram_ba;
   (* always_ready *) method Bit #(13) sdram_a;
   (* always_ready *) method Bit #(2)  sdram_dqm;
   (* always_ready *) method Bit #(16) sdram_dq_out;
   (* always_ready *) method Bit #(1)  sdram_dq_oe;
   (* always_enabled *) method Action sdram_dq_in (Bit #(16) v);
endinterface

// ================================================================

function Bit #(2)  fn_bank (Bit #(64) a); return a [6:5];   endfunction
function Bit #(13) fn_row  (Bit #(64) a); return a [19:7];  endfunction
function Bit #(9)  fn_col  (Bit #(64) a, Bool second_burst);
   return { a [4:0], 4'b0 } + (second_burst ? 9'd8 : 9'd0);
endfunction

// ================================================================

module mkSdram_Controller #(Integer clk_hz) (Sdram_Controller_IFC);

   Integer t_powerup = clk_hz / 5000;    // 200 us
   // tRFC >= 66 ns (and the init gaps tRP/tRFC/tMRD, which it covers), in
   // clocks, at least 2: 2 at 25 MHz (80 ns), 3 at the 32.14 MHz PLL clock
   // (2 would be 62 ns).  Refresh interval refresh_div (98 clocks) stays
   // well under tREFI 7.8 us at any clock >= 12.5 MHz.
   Integer ns_x_hz   = 66 * clk_hz;
   Integer t_rfc_c   = (ns_x_hz + 999_999_999) / 1_000_000_000;
   Integer t_rfc     = max (2, t_rfc_c);
   Integer t_init_gap = t_rfc;

   Reg #(State)     rg_state     <- mkReg (ST_PWR_WAIT);
   Reg #(Bit #(16)) rg_wait      <- mkReg (0);
   Reg #(Bit #(16)) rg_pwrcnt    <- mkReg (fromInteger (t_powerup));
   Reg #(Bit #(16)) rg_ref_cnt   <- mkReg (fromInteger (refresh_div));

   // Latched current request
   Reg #(Bool)      rg_req_write  <- mkReg (False);
   Reg #(Bit #(64)) rg_req_addr   <- mkReg (0);
   Reg #(Bit #(256)) rg_req_data  <- mkReg (0);
   Reg #(Bit #(32)) rg_req_byteen <- mkReg (0);
   Reg #(Bool)      rg_phase      <- mkReg (False);    // second burst
   Reg #(Bit #(4))  rg_beat       <- mkReg (0);

   // Read-data assembly (16 halfword beats)
   Vector #(16, Reg #(Bit #(16))) rg_rdata <- replicateM (mkReg (16'h0));

   // Pin registers
   Reg #(Bit #(4))  rg_cmd      <- mkReg (cmd_nop);    // command output (updated by state rules)
   Reg #(Bit #(13)) rg_a        <- mkReg (0);
   Reg #(Bit #(2))  rg_ba       <- mkReg (0);
   Reg #(Bit #(2))  rg_dqm      <- mkReg (2'b11);
   Reg #(Bit #(16)) rg_dq_out   <- mkReg (0);
   Reg #(Bit #(1))  rg_dq_oe    <- mkReg (0);
   Reg #(Bit #(16)) rg_dq_in    <- mkReg (0);

   Reg #(Bool) rg_inited     <- mkReg (False);
   Reg #(Bool) rg_cmd_valid  <- mkReg (False);
   Reg #(Bool) rg_clear_cmd  <- mkReg (False);

   FIFOF #(MemoryRequest  #(Bits_per_Raw_Mem_Addr, Bits_per_Raw_Mem_Word)) f_reqs <- mkSizedFIFOF (4);
   FIFOF #(MemoryResponse #(Bits_per_Raw_Mem_Word))                        f_rsps <- mkSizedFIFOF (2);

   // Issue rules assert rg_cmd_valid for exactly one cycle; this rule
   // clears it the following cycle.  Kept separate from data-burst rules
   // so the behavioral model can sample command pins without a cycle.
   rule rl_clear_cmd_valid (rg_clear_cmd);
      rg_cmd_valid  <= False;
      rg_clear_cmd  <= False;
   endrule

   // ----------------------------------------------------------------
   // Power-up initialization: 200 us stable clock with CKE low,
   // PRECHARGE ALL, 2x AUTO REFRESH, LOAD MODE REGISTER (CL2, BL8).

   rule rl_pwr_wait (rg_state == ST_PWR_WAIT);
      if (rg_pwrcnt == 1)
         rg_state <= ST_PRE_ALL;
      else
         rg_pwrcnt <= rg_pwrcnt - 1;
   endrule

   rule rl_pre_all (rg_state == ST_PRE_ALL);
      rg_cmd      <= cmd_pre;
      rg_cmd_valid <= True;
      rg_clear_cmd <= True;
      rg_a        <= 13'h0400;    // A10 = 1: precharge all banks
      rg_ba       <= 0;
      rg_wait     <= fromInteger (t_init_gap);
      rg_state    <= ST_PRE_ALL_WAIT;
   endrule

   rule rl_pre_all_wait (rg_state == ST_PRE_ALL_WAIT);
      if (rg_wait == 0)
         rg_state <= ST_INIT_REF1;
      else
         rg_wait <= rg_wait - 1;
   endrule

   rule rl_init_ref1 (rg_state == ST_INIT_REF1);
      rg_cmd      <= cmd_ref;
      rg_cmd_valid <= True;
      rg_clear_cmd <= True;
      rg_wait     <= fromInteger (t_init_gap);
      rg_state    <= ST_INIT_REF1_WAIT;
   endrule

   rule rl_init_ref1_wait (rg_state == ST_INIT_REF1_WAIT);
      if (rg_wait == 0)
         rg_state <= ST_INIT_REF2;
      else
         rg_wait <= rg_wait - 1;
   endrule

   rule rl_init_ref2 (rg_state == ST_INIT_REF2);
      rg_cmd      <= cmd_ref;
      rg_cmd_valid <= True;
      rg_clear_cmd <= True;
      rg_wait     <= fromInteger (t_init_gap);
      rg_state    <= ST_INIT_REF2_WAIT;
   endrule

   rule rl_init_ref2_wait (rg_state == ST_INIT_REF2_WAIT);
      if (rg_wait == 0)
         rg_state <= ST_MRS;
      else
         rg_wait <= rg_wait - 1;
   endrule

   rule rl_mrs (rg_state == ST_MRS);
      rg_cmd      <= cmd_mrs;
      rg_cmd_valid <= True;
      rg_clear_cmd <= True;
      rg_a        <= mode_reg_value;
      rg_ba       <= 0;
      rg_wait     <= fromInteger (t_init_gap);
      rg_state    <= ST_MRS_WAIT;
   endrule

   rule rl_mrs_wait (rg_state == ST_MRS_WAIT);
      if (rg_wait == 0) begin
         rg_state  <= ST_IDLE;
         rg_inited <= True;
      end
      else
         rg_wait <= rg_wait - 1;
   endrule

   // ----------------------------------------------------------------
   // Refresh countdown.  When it expires the IDLE rule issues a
   // refresh before starting any new request, and the counter has
   // already restarted, so refreshes stay tREFI apart.

   rule rl_refresh_tick;
      if (rg_ref_cnt <= 1)
         rg_ref_cnt <= fromInteger (refresh_div);
      else
         rg_ref_cnt <= rg_ref_cnt - 1;
   endrule

   rule rl_ref (rg_state == ST_REF);
      rg_cmd      <= cmd_ref;
      rg_cmd_valid <= True;
      rg_clear_cmd <= True;
      rg_wait     <= fromInteger (t_rfc);
      rg_state    <= ST_REF_WAIT;
   endrule

   rule rl_ref_wait (rg_state == ST_REF_WAIT);
      if (rg_wait == 0)
         rg_state <= ST_IDLE;
      else
         rg_wait <= rg_wait - 1;
   endrule

   // ----------------------------------------------------------------
   // IDLE: serve refresh first, then latch the next request.

   rule rl_idle (rg_state == ST_IDLE);
      rg_dq_oe     <= 1'b0;
      rg_dqm       <= 2'b11;
      if (rg_ref_cnt <= 1)
         rg_state <= ST_REF;
      else if (f_reqs.notEmpty) begin
         let req = f_reqs.first;
         f_reqs.deq;
         rg_req_write  <= req.write;
         rg_req_addr   <= req.address;
         rg_req_data   <= req.data;
         rg_req_byteen <= req.byteen;
         rg_phase      <= False;
         rg_state      <= ST_ACT;
`ifdef SDCAP_PROBES
         // granule 0 only (req.address == 0): keeps REPL-boot logs small
         if (req.address == 0)
            $display ("%0d SDREQ %s addr=%0h (byte %0h) byteen=%0h",
                      0, req.write ? "WR" : "RD", req.address,
                      req.address << 5, req.byteen);
`endif
      end
   endrule

   // ----------------------------------------------------------------
   // Shared row activation

   rule rl_act (rg_state == ST_ACT);
      rg_cmd      <= cmd_act;
      rg_cmd_valid <= True;
      rg_clear_cmd <= True;
      rg_a        <= fn_row (rg_req_addr);
      rg_ba       <= fn_bank (rg_req_addr);
      rg_wait     <= fromInteger (t_rcd);
      rg_state    <= ST_RCD_WAIT;
   endrule

   rule rl_rcd_wait (rg_state == ST_RCD_WAIT);
      if (rg_wait == 0)
         rg_state <= (rg_req_write ? ST_WR : ST_RD);
      else
         rg_wait <= rg_wait - 1;
   endrule

   // ----------------------------------------------------------------
   // Read: two BL8 bursts, capture 16 halfwords, return 256-bit word

   rule rl_rd (rg_state == ST_RD);
      rg_cmd      <= cmd_read;
      rg_cmd_valid <= True;
      rg_clear_cmd <= True;
      // Auto-precharge only on the second burst, so the row stays open
      // across the two bursts of one raw-memory request.
      rg_a        <= { 4'b0, fn_col (rg_req_addr, rg_phase) } | (rg_phase ? 13'h0400 : 13'h0);
      rg_ba       <= fn_bank (rg_req_addr);
      rg_dqm      <= 2'b00;    // unmask read data for the entire burst
      rg_beat     <= 0;
      rg_wait     <= fromInteger (t_cas_first);
      rg_state    <= ST_RD_CAP;
   endrule

   rule rl_rd_cap (rg_state == ST_RD_CAP);
      if (rg_wait != 0)
         rg_wait <= rg_wait - 1;
      else if ((rg_beat == 7) && rg_phase) begin
         // Final beat of the request: assemble and return the word
         Vector #(16, Bit #(16)) v = readVReg (rg_rdata);
         v [15] = rg_dq_in;
         f_rsps.enq (MemoryResponse {data: pack (v)});
         // SIM PROBE: log returned read data (granule 0 only)
`ifdef SDCAP_PROBES
         if (rg_req_addr == 0)
            $display ("%0d SDRSP addr=%0h data=%0h", 0, rg_req_addr, pack (v));
`endif
         rg_state <= ST_IDLE;
      end
      else begin
         Bit #(4) idx = (rg_phase ? 4'd8 : 4'd0) + rg_beat;
         rg_rdata [idx] <= rg_dq_in;
`ifdef SDCAP_PROBES
         if (rg_req_addr == 0)
            $display ("%0d SDCAP phase=%0d beat=%0d idx=%0d dq_in=%0h",
                      0, rg_phase, rg_beat, idx, rg_dq_in);
`endif
         if (rg_beat == 7) begin    // first burst complete
            rg_phase <= True;
            rg_state <= ST_GAP;
         end
         else
            rg_beat <= rg_beat + 1;
      end
   endrule

   // One idle cycle between the two bursts of a request (tCCD)
   rule rl_gap_rd (rg_state == ST_GAP && ! rg_req_write);
      rg_state    <= ST_RD;
   endrule

   rule rl_gap_wr (rg_state == ST_GAP && rg_req_write);
      rg_state    <= ST_WR;
   endrule

   // ----------------------------------------------------------------
   // Write: two BL8 bursts, zero write latency (first beat driven
   // with the WRITE command), per-byte DQM masking.

   rule rl_wr (rg_state == ST_WR);
      Vector #(16, Bit #(16)) v_wdata = unpack (rg_req_data);
      Vector #(32, Bit #(1))  v_be    = unpack (rg_req_byteen);
      Bit #(4) idx     = rg_phase ? 4'd8 : 4'd0;
      Bit #(5) be_idx  = { idx, 1'b0 };
      rg_cmd      <= cmd_write;
      rg_cmd_valid <= True;
      rg_clear_cmd <= True;
      // Auto-precharge only on the second burst, so the row stays open
      // across the two bursts of one raw-memory request.
      rg_a        <= { 4'b0, fn_col (rg_req_addr, rg_phase) } | (rg_phase ? 13'h0400 : 13'h0);
      rg_ba       <= fn_bank (rg_req_addr);
      rg_dq_oe    <= 1'b1;
      rg_dq_out   <= v_wdata [idx];
      rg_dqm      <= { ~ v_be [be_idx + 1], ~ v_be [be_idx] };
      rg_beat     <= 1;
      rg_state    <= ST_WR_DATA;
`ifdef SDCAP_PROBES
      if (rg_req_addr == 0)
         $display ("%0d SDWRB0 addr=%0h idx=%0d dq=%0h dqm=%0b",
                   0, rg_req_addr, idx, v_wdata [idx], { ~ v_be [be_idx + 1], ~ v_be [be_idx] });
`endif
   endrule

   rule rl_wr_data (rg_state == ST_WR_DATA);
      Vector #(16, Bit #(16)) v_wdata = unpack (rg_req_data);
      Vector #(32, Bit #(1))  v_be    = unpack (rg_req_byteen);
      Bit #(4) idx     = (rg_phase ? 4'd8 : 4'd0) + rg_beat;
      Bit #(5) be_idx  = { idx, 1'b0 };
      rg_dq_out <= v_wdata [idx];
      rg_dqm    <= { ~ v_be [be_idx + 1], ~ v_be [be_idx] };
`ifdef SDCAP_PROBES
      if (rg_req_addr == 0)
         $display ("%0d SDWRB%0d addr=%0h idx=%0d dq=%0h dqm=%0b",
                   0, rg_beat, rg_req_addr, idx, v_wdata [idx], { ~ v_be [be_idx + 1], ~ v_be [be_idx] });
`endif
      if (rg_beat == 7)
         rg_state <= ST_WR_END;
      else
         rg_beat <= rg_beat + 1;
   endrule

   rule rl_wr_end (rg_state == ST_WR_END);
      rg_dq_oe    <= 1'b0;
      rg_dqm      <= 2'b11;
      if (! rg_phase) begin
         rg_phase <= True;
         rg_state <= ST_GAP;
      end
      else
         rg_state <= ST_IDLE;
   endrule

   // ----------------------------------------------------------------
   // INTERFACE

   // The command is driven only during the single-cycle issue states.
   // During waits, data bursts, gaps and idle the bus is held at NOP.
   function Bit #(4) fn_cmd_out ();
      return rg_cmd_valid ? rg_cmd : cmd_nop;
   endfunction

   interface MemoryServer mem_server = toGPServer (f_reqs, f_rsps);

   method Bool init_done = rg_inited;

   method Bit #(1) sdram_cke   = pack (rg_state != ST_PWR_WAIT);
   method Bit #(1) sdram_cs_n  = fn_cmd_out () [3];
   method Bit #(1) sdram_ras_n = fn_cmd_out () [2];
   method Bit #(1) sdram_cas_n = fn_cmd_out () [1];
   method Bit #(1) sdram_we_n  = fn_cmd_out () [0];
   method Bit #(2) sdram_ba    = rg_ba;
   method Bit #(13) sdram_a    = rg_a;
   method Bit #(2) sdram_dqm   = rg_dqm;
   method Bit #(16) sdram_dq_out = rg_dq_out;
   method Bit #(1) sdram_dq_oe = rg_dq_oe;
   method Action sdram_dq_in (Bit #(16) v);
      rg_dq_in <= v;
   endmethod
endmodule

endpackage
