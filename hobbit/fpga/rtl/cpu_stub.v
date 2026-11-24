// cpu_stub.v -- a stand-in for bsc's mkHobbitSocCpu with the same ports,
// used only by `build_soc.sh stub` to place and time the SoC's periphery
// (adapter, SDRAM controller, host link, ROM block, DCCA) while the
// privileged core does not fit the LFE5U-85F (fpga/README.md, "Area").
//
// Every input is folded into a shift register on the core's clock and every
// output is taken from it, so synthesis keeps all of the adapter's logic
// (the 16-entry window, the 22 probes, the three write ports) and the
// gated-clock crossings.  It computes nothing; it is never simulated.
module mkHobbitSocCpu(
  input          CLK,
  input          RST_N,
  output         rdReq,
  output [31:0]  rdAddr,
  input  [31:0]  rdData_d,
  output [64:0]  memWr,
  output [64:0]  tblWr,
  output [64:0]  evWr,
  input  [1039:0] window_w,
  output [725:0] probes,
  input  [31:0]  go_entry,
  input          EN_go,
  output         RDY_go,
  output         running,
  input  [2:0]   il_level,
  input  [31:0]  armInterrupt_n,
  input  [2:0]   armInterrupt_level,
  input          EN_armInterrupt,
  output         RDY_armInterrupt,
  output         irqArmable,
  input          EN_takenInterrupt,
  output [31:0]  takenInterrupt,
  output         RDY_takenInterrupt,
  output [31:0]  retired,
  output         stopped,
  output [31:0]  pc,
  output         hriValid,
  output [298:0] hri);

  // Fold the 1040-bit window into 32 bits (each bit of every entry used).
  reg [31:0] fold;
  integer i;
  always @* begin
    fold = rdData_d ^ go_entry ^ armInterrupt_n;
    for (i = 0; i < 32; i = i + 1)
      fold = fold ^ window_w[32 * i +: 32];
    fold[16:0] = fold[16:0] ^ window_w[1039:1024];
    fold[2:0] = fold[2:0] ^ il_level ^ armInterrupt_level;
    fold[3] = fold[3] ^ EN_go ^ EN_armInterrupt ^ EN_takenInterrupt;
  end

  reg [767:0] s;
  always @(posedge CLK)
    if (!RST_N) s <= 768'b0;
    else s <= {s[735:0], fold} ^ {s[31:0], 736'b0} ^ {24{fold}};

  assign rdReq = s[0];
  assign rdAddr = s[63:32];
  assign memWr = s[200:136];
  assign tblWr = s[300:236];
  assign evWr = s[400:336];
  assign probes = s[725:0];
  assign RDY_go = s[1];
  assign running = s[2];
  assign RDY_armInterrupt = s[3];
  assign irqArmable = s[4];
  assign takenInterrupt = s[95:64];
  assign RDY_takenInterrupt = s[5];
  assign retired = s[127:96];
  assign stopped = s[6];
  assign pc = s[159:128];
  assign hriValid = s[7];
  assign hri = s[766:468];
endmodule
