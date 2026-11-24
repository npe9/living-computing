// hobbit_sysregfile.v -- bsc's RegFile with its read ports on the system
// clock, for the gated SoC core (fpga/sysram_filter.py; fpga/README.md,
// "The core's arrays on the system clock").
//
// Same ports and parameters as $BLUESPECDIR/Verilog/RegFile.v plus SYSCLK.
// The write port is the core's: CLK is the gated core clock.  Each read
// port is a block RAM copy of the array (one write port shared by all
// copies, one read port each) whose read register is clocked by SYSCLK,
// the free-running system clock, from the port's current address.  The
// core's state holds between two core edges, so once an address has been
// stable for a system clock the port shows the word bsc's combinational
// RegFile would; hobbit_soc_mem settles for long enough before every core
// edge.  An unused read port (D_OUT_n unconnected) leaves its copy without
// a reader, and synthesis removes it.
//
// HOBBIT_SIM (the Verilator co-simulation): at every core edge each read
// port must equal a combinational read of its array at its current
// address, the RegFile behaviour the core was verified against; a stale
// port prints SYSRAM STALE and stops the run.
module HobbitSysRegFile(SYSCLK, CLK,
                        ADDR_IN, D_IN, WE,
                        ADDR_1, D_OUT_1,
                        ADDR_2, D_OUT_2,
                        ADDR_3, D_OUT_3,
                        ADDR_4, D_OUT_4,
                        ADDR_5, D_OUT_5);
   parameter addr_width = 1;
   parameter data_width = 1;
   parameter lo = 0;
   parameter hi = 1;

   input                       SYSCLK;
   input                       CLK;
   input [addr_width - 1 : 0]  ADDR_IN;
   input [data_width - 1 : 0]  D_IN;
   input                       WE;
   input [addr_width - 1 : 0]  ADDR_1, ADDR_2, ADDR_3, ADDR_4, ADDR_5;
   output [data_width - 1 : 0] D_OUT_1, D_OUT_2, D_OUT_3, D_OUT_4, D_OUT_5;

   (* ram_style = "block" *) reg [data_width - 1 : 0] arr1 [lo:hi];
   (* ram_style = "block" *) reg [data_width - 1 : 0] arr2 [lo:hi];
   (* ram_style = "block" *) reg [data_width - 1 : 0] arr3 [lo:hi];
   (* ram_style = "block" *) reg [data_width - 1 : 0] arr4 [lo:hi];
   (* ram_style = "block" *) reg [data_width - 1 : 0] arr5 [lo:hi];
   reg [data_width - 1 : 0] q1, q2, q3, q4, q5;

`ifdef BSV_NO_INITIAL_BLOCKS
`else
   // synopsys translate_off
   // bsc's RegFile.v starts every word at 0xAA..; so does this.
   initial begin : init_block
      integer i;
      for (i = lo; i <= hi; i = i + 1) begin
         arr1[i] = {((data_width + 1)/2){2'b10}};
         arr2[i] = {((data_width + 1)/2){2'b10}};
         arr3[i] = {((data_width + 1)/2){2'b10}};
         arr4[i] = {((data_width + 1)/2){2'b10}};
         arr5[i] = {((data_width + 1)/2){2'b10}};
      end
      q1 = {((data_width + 1)/2){2'b10}};
      q2 = q1; q3 = q1; q4 = q1; q5 = q1;
   end
   // synopsys translate_on
`endif

   always @(posedge CLK) begin
      if (WE) begin
         arr1[ADDR_IN] <= D_IN;
         arr2[ADDR_IN] <= D_IN;
         arr3[ADDR_IN] <= D_IN;
         arr4[ADDR_IN] <= D_IN;
         arr5[ADDR_IN] <= D_IN;
      end
   end

   always @(posedge SYSCLK) begin
      q1 <= arr1[ADDR_1];
      q2 <= arr2[ADDR_2];
      q3 <= arr3[ADDR_3];
      q4 <= arr4[ADDR_4];
      q5 <= arr5[ADDR_5];
   end

   assign D_OUT_1 = q1;
   assign D_OUT_2 = q2;
   assign D_OUT_3 = q3;
   assign D_OUT_4 = q4;
   assign D_OUT_5 = q5;

`ifdef HOBBIT_SIM
   // sys_n counts system clocks (Verilator's $time stays 0 here), and
   // ce_at is sys_n at the last core edge.  In reset the top gives a core
   // edge on every system clock (hobbit_soc cpu_ce), so the ports cannot
   // settle and are not checked; out of reset two core edges are always
   // further apart (hobbit_soc_mem's write, read, settle and probe states).
   reg [63:0] sys_n = 0;
   reg [63:0] ce_at = 0;
   always @(posedge SYSCLK) sys_n <= sys_n + 1;
   always @(posedge CLK) begin
      ce_at <= sys_n;
      if (sys_n > ce_at + 1 &&
          ((q1 != arr1[ADDR_1]) || (q2 != arr2[ADDR_2]) || (q3 != arr3[ADDR_3]) ||
           (q4 != arr4[ADDR_4]) || (q5 != arr5[ADDR_5]))) begin
         $display("SYSRAM STALE %m at system clock %0d: a %0d/%0d/%0d/%0d/%0d",
                  sys_n, ADDR_1, ADDR_2, ADDR_3, ADDR_4, ADDR_5);
         $finish;
      end
   end
`endif
endmodule
