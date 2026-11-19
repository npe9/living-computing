// pim_fault_formal.v -- formal check of the top-level fault path.
//
// The image formal_images/fault_program.hex is
//
//   pc 0: jmp a6      (microcode at uBase 0x0d, from fault_wcs.hex)
//   pc 1: halt
//
// The jmp microinstruction writes rselPc (41).  PimRegFile::write does
// not accept PC as a destination; it sets badW, and PimPU's `fault`
// rule latches `error`.  The write itself is dropped, so the machine's
// PC is not corrupted.
//
// Note the model's current scope: the `fault` rule raises `error` but
// the `pipe` rule only checks estage.stopped() (haltSeen/errorSeen), so
// this fault does not freeze the pipe.  The program therefore reaches
// its halt too.  The property checked here is the documented loud
// failure, `error`; `halted` is deliberately not constrained.

`default_nettype none

module pim_fault_formal (input wire CLK);

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
    if (RST_N == 1'b1 && cyc == 8'd20) assert (error);
  end

endmodule

`default_nettype wire
