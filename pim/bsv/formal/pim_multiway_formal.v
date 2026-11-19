// pim_multiway_formal.v -- formal check of the E-stage multi-way tag jump.
//
// The image is formal_images/multiway_program.hex.  It loads two words
// whose tags are the same type/data except for the MRB bit:
//
//   mem[100] = 0x01_0000002a   (type int, MRB set)
//   mem[101] = 0xff_0000002a   (type 0x7f, MRB set)
//
// and executes a condMultiway jmp_tag on each (the microprogram is in
// multiway_wcs.hex).  The jump table is the model's 256-entry,
// 8-bit-indexed table; the base is the micro-PC of the multiway
// microinstruction, 0x0e:
//
//   jump[0x01] = 0x30 -> target 0x3e, writes a1 = a6 = 0x101   (correct)
//   jump[0x00] = 0x40 -> target 0x4e, writes a1 = a5 = 0x100   (decoy)
//   jump[0xff] = 0x50 -> target 0x5e, writes a2 = a7 = 0x1ff   (correct)
//   jump[0x7f] = 0x60 -> target 0x6e, writes a2 = a4 = 0x17f   (decoy)
//
// An index that drops MRB (the old 7-bit tagType lookup) lands on the
// decoy and fails the post-state assertion.  The case tag 0xff is the
// top entry of the 256-entry table, so it also shows the top of the
// 8-bit index range is reachable; a 7-bit index cannot reach it.
//
// The jump-table read address itself is internal to the generated
// netlist and is not an interface port.  Yosys does not resolve the
// dotted reference to it from this wrapper, so the property is checked
// end-to-end through the target microprograms instead of by asserting
// the internal address wire.

`default_nettype none

module pim_multiway_formal (input wire CLK);

  // Reset sequencer: two cycles of RST_N low, as in the smoke wrapper.
  reg [3:0] rst_cnt = 4'd0;
  wire RST_N = (rst_cnt >= 4'd2);
  always @(posedge CLK)
    if (rst_cnt != 4'd15) rst_cnt <= rst_cnt + 4'd1;

  // Free-running cycle counter for the bounded-liveness check.
  reg [7:0] cyc = 8'd0;
  always @(posedge CLK)
    if (cyc != 8'd255) cyc <= cyc + 8'd1;

  wire [39:0] readReg;
  wire [15:0] pc;
  wire        halted;
  wire        error;
  wire [5:0]  readReg_r;

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
    .readMem_a(16'd0),
    .readMem(),
    .RDY_readMem(),
    .pc(pc),
    .RDY_pc()
  );

  // Post-halt scan of a1 then a2.  The halt state is frozen.
  localparam [1:0] S_A1   = 2'd0;
  localparam [1:0] S_A2   = 2'd1;
  localparam [1:0] S_DONE = 2'd2;

  reg [1:0] scan = S_A1;
  always @(posedge CLK)
    if (RST_N == 1'b0)           scan <= S_A1;
    else if (!halted)            scan <= S_A1;
    else if (scan != S_DONE)     scan <= scan + 2'd1;

  assign readReg_r = (scan == S_A2) ? 6'd2 : 6'd1;

  always @(posedge CLK) begin
    if (RST_N == 1'b1 && halted) begin
      if (scan == S_A1) assert (readReg == 40'h00_0000_0101);
      if (scan == S_A2) assert (readReg == 40'h00_0000_01ff);
      assert (!error);
    end
  end

  // Bounded liveness: the ten-instruction program must halt in the
  // BMC window.  The Bluesim smoke retires twelve instructions in 48
  // steps; 70 cycles leaves margin for the two three-cycle tag jumps.
  always @(posedge CLK) begin
    if (cyc == 8'd70) assert (halted);
  end

endmodule

`default_nettype wire
