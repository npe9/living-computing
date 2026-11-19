// pim_smoke_formal.v -- riscv-formal style post-state check for the PIM/m PU.
//
// The DUT is the Verilog produced by
//   bsc -verilog -g mkPimPUFormal -p .:$BLUESPECDIR/Libraries -u PimPUFormal.bsv
// and is the same machine the Bluesim smoke test drives.  The wrapper
// supplies reset and start, runs the machine freely, and once the E
// stage reports halted/error it checks the architectural post-state
// against the value the ISA model requires for the diagnostic program:
//
//   a2        = 42           (wordInt 42)
//   a4        = 42, MRB on   (tag 0x01)
//   a5        = 42, MRB on
//   a7        = 0            (the tag-jump taken path skips the write)
//   mem[100]  = 42
//   pc        = 17
//
// The PU is a multi-cycle machine, so "one cycle" here means one cycle
// after the last instruction retires: the halt state freezes every
// architectural register and memory, so the five read-port samples
// below all observe the same final state.  If the machine does not
// halt by cycle 70 the bounded-liveness assertion fails, so a PASS is
// not vacuous.

`default_nettype none

module pim_smoke_formal (input wire CLK);

  // Reset sequencer.  The DUT reset is active low and the generated
  // registers have no initial values, so two cycles of RST_N low put
  // the machine in its defined reset state.
  reg [3:0] rst_cnt = 4'd0;
  wire RST_N = (rst_cnt >= 4'd2);   // active low: held 0 for the first two cycles
  always @(posedge CLK)
    if (rst_cnt != 4'd15) rst_cnt <= rst_cnt + 4'd1;

  // Free-running cycle counter for the bounded-liveness check.
  reg [7:0] cyc = 8'd0;
  always @(posedge CLK)
    if (cyc != 8'd255) cyc <= cyc + 8'd1;

  wire [39:0] readReg;
  wire [39:0] readMem;
  wire [15:0] pc;
  wire        halted;
  wire        error;
  wire [5:0]  readReg_r;
  wire [15:0] readMem_a;

  mkPimPUFormal dut (
    .CLK(CLK),
    .RST_N(RST_N),
    .EN_start(1'b1),
    .RDY_start(),
    .halted(halted),
    .RDY_halted(),
    .error(error),
    .RDY_error(),
    .readReg_r(readReg_r),
    .readReg(readReg),
    .RDY_readReg(),
    .readMem_a(readMem_a),
    .readMem(readMem),
    .RDY_readMem(),
    .pc(pc),
    .RDY_pc()
  );

  // Post-halt read scan.  The interface has one register read port, so
  // walk the five architectural locations one per cycle; the halted
  // state does not change, so each sample is the final value.
  localparam [2:0] S_A2   = 3'd0;
  localparam [2:0] S_A4   = 3'd1;
  localparam [2:0] S_A5   = 3'd2;
  localparam [2:0] S_A7   = 3'd3;
  localparam [2:0] S_PC   = 3'd4;
  localparam [2:0] S_DONE = 3'd5;

  reg [2:0] scan = S_A2;
  always @(posedge CLK)
    if (RST_N == 1'b0)           scan <= S_A2;
    else if (!halted)            scan <= S_A2;
    else if (scan != S_DONE)     scan <= scan + 3'd1;

  assign readReg_r = (scan == S_A4) ? 6'd4 :
                     (scan == S_A5) ? 6'd5 :
                     (scan == S_A7) ? 6'd7 : 6'd2;
  assign readMem_a = 16'd100;

  // Architectural post-state assertions.  40'hxx_xxxxxxxx is
  // {8-bit tag, 32-bit data}; tag 0x01 is tagInt with MRB set.
  always @(posedge CLK) begin
    if (RST_N == 1'b1 && halted) begin
      if (scan == S_A2) assert (readReg == 40'h00_0000_002a);
      if (scan == S_A4) assert (readReg == 40'h01_0000_002a);
      if (scan == S_A5) assert (readReg == 40'h01_0000_002a);
      if (scan == S_A7) assert (readReg == 40'h00_0000_0000);
      if (scan == S_PC) assert (pc == 16'd17);
      assert (readMem == 40'h00_0000_002a);
      assert (!error);
    end
  end

  // Bounded liveness: the diagnostic must halt.  The Bluesim run
  // retires in 48 steps; 70 cycles leaves margin for the formal reset.
  always @(posedge CLK) begin
    if (cyc == 8'd70) assert (halted);
  end

endmodule

`default_nettype wire
