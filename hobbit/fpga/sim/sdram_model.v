// sdram_model.v -- behavioural model of the ULX3S's W9825G6KH SDR SDRAM
// for Verilator (4 banks x 8192 rows x 512 columns x 16 bits), written for
// fpga/sim.  Not Micron's or Winbond's model (neither is redistributable;
// fpga/IP_PROVENANCE.md).
//
// The part's clock is the system clock forwarded inverted (the board
// top's ODDRX1F D0 = 0, D1 = 1), so the model acts on the system clock's
// falling edge.  The data bus is split: dq_in/dq_in_oe from the
// controller, dq_out/dq_out_oe from the part; the sim top registers
// dq_out on the rising edge as the board's I/O register does.
//
// It checks what the controller is relied on to do and stops the run
// ($fatal) on a violation: the power-up order (200 us, PRECHARGE ALL,
// eight AUTO REFRESH, MODE REGISTER), the mode it programs (BL 2,
// sequential, CL 2), READ/WRITE only to an open bank and row, ACTIVE only
// to a closed bank, tRCD/tRP/tRAS/tRC/tRFC/tWR in clocks for CLK_HZ,
// AUTO REFRESH only with every bank closed, and no gap between refreshes
// longer than tREFI (7.8 us).
module sdram_model #(
    parameter CLK_HZ = 25000000
) (
    input  wire        clk,          // the system clock; the part uses its falling edge
    input  wire        cs_n, ras_n, cas_n, we_n,
    input  wire [1:0]  ba,
    input  wire [12:0] a,
    input  wire [1:0]  dqm,
    input  wire [15:0] dq_in,
    input  wire        dq_in_oe,
    output reg  [15:0] dq_out,
    output reg         dq_out_oe
);
    reg [15:0] mem [0:(1<<24)-1];

    // Clocks for a time in ns, rounded up.
    function integer clks(input integer ns);
        clks = (ns * (CLK_HZ / 1000000) + 999) / 1000;
    endfunction
    localparam integer C_RCD = clks(18) < 1 ? 1 : clks(18);
    localparam integer C_RP  = clks(18) < 1 ? 1 : clks(18);
    localparam integer C_RAS = clks(42);
    localparam integer C_RC  = clks(60);
    localparam integer C_RFC = clks(66);
    localparam integer C_REFI = (CLK_HZ / 1000000) * 7800 / 1000;
    localparam integer C_PWR = (CLK_HZ / 1000000) * 200;

    reg [63:0] t;                 // clocks since start
    reg        open_  [0:3];
    reg [12:0] row    [0:3];
    reg [63:0] t_act  [0:3];
    reg [63:0] t_pre  [0:3];      // when the bank closed (precharge start)
    reg [63:0] t_wr   [0:3];      // last write data clock
    reg        ap_pend[0:3];      // auto-precharge after the burst
    reg [63:0] ap_at  [0:3];
    reg [63:0] t_ref;
    reg [3:0]  init_refs;
    reg        pre_all_seen, mode_set;
    reg [63:0] t_any_ref;

    // Burst state.
    reg [1:0]  rd_left, wr_left;
    reg [1:0]  bb;
    reg [12:0] brow;
    reg [8:0]  bcol;
    reg [2:0]  rd_q_v;            // CL pipeline: data presented at +2, +3
    reg [23:0] rd_q_a0, rd_q_a1, rd_q_a2;

    integer i;
    initial begin
        t = 0; t_ref = 0; init_refs = 0; pre_all_seen = 0; mode_set = 0;
        dq_out = 16'hxxxx; dq_out_oe = 0; rd_left = 0; wr_left = 0; rd_q_v = 0;
        for (i = 0; i < 4; i = i + 1) begin
            open_[i] = 0; row[i] = 0; t_act[i] = 0; t_pre[i] = 0;
            t_wr[i] = 0; ap_pend[i] = 0; ap_at[i] = 0;
        end
    end

    // DPI back door for the harness: load and read words without the bus.
    export "DPI-C" function sdram_poke16;
    export "DPI-C" function sdram_peek16;
    function void sdram_poke16(input int unsigned h, input int unsigned v);
        mem[h[23:0]] = v[15:0];
    endfunction
    function int unsigned sdram_peek16(input int unsigned h);
        sdram_peek16 = {16'd0, mem[h[23:0]]};
    endfunction

    wire [3:0] cmd = {cs_n, ras_n, cas_n, we_n};
    localparam CMD_ACT = 4'b0011, CMD_RD = 4'b0101, CMD_WR = 4'b0100,
               CMD_PRE = 4'b0010, CMD_REF = 4'b0001, CMD_MRS = 4'b0000;

    function [23:0] haddr(input [1:0] b, input [12:0] r, input [8:0] c);
        // The controller's word layout: column = {w[7:0], beat},
        // bank = w[9:8], row = w[22:10]; halfword index = {row, bank, col}.
        haddr = {r, b, c};
    endfunction

    always @(negedge clk) begin
        t <= t + 1;
        // Auto-precharge completes.
        for (i = 0; i < 4; i = i + 1)
            if (ap_pend[i] && t >= ap_at[i]) begin
                ap_pend[i] <= 0; open_[i] <= 0; t_pre[i] <= t;
            end

        // Read pipeline (CL 2): the word for edge t was queued at t-2.
        dq_out_oe <= rd_q_v[1];
        if (rd_q_v[1]) dq_out <= mem[rd_q_a1];
        rd_q_v <= {rd_q_v[1:0], 1'b0};
        rd_q_a2 <= rd_q_a1; rd_q_a1 <= rd_q_a0;

        // Write beat 1.
        if (wr_left == 1) begin
            if (!dq_in_oe) $fatal(1, "sdram: write beat 1 without DQ driven at %0d", t);
            if (!dqm[0]) mem[haddr(bb, brow, bcol)][7:0]  = dq_in[7:0];
            if (!dqm[1]) mem[haddr(bb, brow, bcol)][15:8] = dq_in[15:8];
            t_wr[bb] <= t;
            wr_left <= 0;
            ap_at[bb] <= t + clks(14) + 1;       // tWR then precharge
        end
        if (rd_left == 1) begin
            rd_q_v[0] <= 1; rd_q_a0 <= haddr(bb, brow, bcol);
            rd_left <= 0;
        end

        if (t > 0 && (t - t_ref) > C_REFI && mode_set)
            $fatal(1, "sdram: no refresh for %0d clocks (tREFI %0d) at %0d", t - t_ref, C_REFI, t);

        case (cmd)
        CMD_ACT: begin
            if (!mode_set) $fatal(1, "sdram: ACTIVE before the mode register at %0d", t);
            if (open_[ba] || ap_pend[ba]) $fatal(1, "sdram: ACTIVE to open bank %0d at %0d", ba, t);
            if (t - t_pre[ba] < C_RP) $fatal(1, "sdram: tRP violated, bank %0d at %0d", ba, t);
            if (t_act[ba] != 0 && t - t_act[ba] < C_RC) $fatal(1, "sdram: tRC violated, bank %0d at %0d", ba, t);
            if (t - t_ref < C_RFC) $fatal(1, "sdram: tRFC violated at %0d", t);
            open_[ba] <= 1; row[ba] <= a; t_act[ba] <= t;
        end
        CMD_RD, CMD_WR: begin
            if (!open_[ba]) $fatal(1, "sdram: READ/WRITE to closed bank %0d at %0d", ba, t);
            if (t - t_act[ba] < C_RCD) $fatal(1, "sdram: tRCD violated at %0d", t);
            if (a[0]) $fatal(1, "sdram: odd start column at %0d", t);
            bb <= ba; brow <= row[ba]; bcol <= {a[8:1], 1'b1};
            if (a[10]) begin
                ap_pend[ba] <= 1;
                // READ with AP: precharge starts after the burst and tRAS.
                ap_at[ba] <= (t + 2 > t_act[ba] + C_RAS) ? t + 2 : t_act[ba] + C_RAS;
            end
            if (cmd == CMD_RD) begin
                rd_q_v[0] <= 1; rd_q_a0 <= haddr(ba, row[ba], {a[8:1], 1'b0});
                rd_left <= 1;
            end else begin
                if (!dq_in_oe) $fatal(1, "sdram: write beat 0 without DQ driven at %0d", t);
                if (!dqm[0]) mem[haddr(ba, row[ba], {a[8:1], 1'b0})][7:0]  = dq_in[7:0];
                if (!dqm[1]) mem[haddr(ba, row[ba], {a[8:1], 1'b0})][15:8] = dq_in[15:8];
                wr_left <= 1;
            end
        end
        CMD_PRE: begin
            if (t < C_PWR) $fatal(1, "sdram: command before 200 us at %0d", t);
            if (a[10]) begin
                for (i = 0; i < 4; i = i + 1) begin open_[i] <= 0; t_pre[i] <= t; end
                pre_all_seen <= 1;
            end else begin open_[ba] <= 0; t_pre[ba] <= t; end
        end
        CMD_REF: begin
            if (!pre_all_seen) $fatal(1, "sdram: REFRESH before PRECHARGE ALL at %0d", t);
            for (i = 0; i < 4; i = i + 1)
                if (open_[i] || ap_pend[i]) $fatal(1, "sdram: REFRESH with bank %0d open at %0d", i, t);
            if (t - t_ref < C_RFC && t_ref != 0) $fatal(1, "sdram: tRFC violated (REF) at %0d", t);
            t_ref <= t;
            if (!mode_set) init_refs <= init_refs + 1;
        end
        CMD_MRS: begin
            if (init_refs < 8) $fatal(1, "sdram: MODE REGISTER after %0d refreshes", init_refs);
            if (a != 13'b000_0_00_010_0_001) $fatal(1, "sdram: mode %h, expected BL2 CL2", a);
            mode_set <= 1; t_ref <= t;
        end
        default: ;
        endcase
    end
endmodule
