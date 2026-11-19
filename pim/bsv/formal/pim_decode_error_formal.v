// pim_decode_error_formal.v -- formal check of the decode-error path.
//
// The image formal_images/decode_error_program.hex is
//
//   pc 0: 0x0f_00000000   undefined opcode (decode entry 0x0f has valid=0)
//   pc 1: halt            must never be reached
//
// PimE.cycle's empty-E branch sees !dec.valid and latches errorSeen; the
// top-level fault rule turns that into `error`.  The documented loud
// failure is checked two ways: the machine must report `error` inside
// the BMC window, and it must not report success (`halted`) instead.

`default_nettype none

module pim_decode_error_formal (input wire CLK);

  reg [3:0] rst_cnt = 4'd0;
  wire RST_N = (rst_cnt >= 4'd2);
  always @(posedge CLK)
    if (rst_cnt != 4'd15) rst_cnt <= rst_cnt + 4'd1;

  reg [7:0] cyc = 8'd0;
  always @(posedge CLK)
    if (cyc != 8'd255) cyc <= cyc + 8'd1;

  wire [39:0] readReg;
  wire [15:0] pc;
  wire        halted;
  wire        error;

  mkPimPUFormal dut (
    .CLK(CLK),
    .RST_N(RST_N),
    .EN_start(1'b1),
    .RDY_start(),
    .halted(halted),
    .RDY_halted(),
    .error(error),
    .RDY_error(),
    .readReg_r(6'd0),
    .readReg(readReg),
    .RDY_readReg(),
    .readMem_a(16'd0),
    .readMem(),
    .RDY_readMem(),
    .pc(pc),
    .RDY_pc()
  );

  always @(posedge CLK) begin
    if (RST_N == 1'b1) begin
      assert (!halted);              // the undefined opcode must not retire
      if (cyc == 8'd20) assert (error);
    end
  end

endmodule

`default_nettype wire
