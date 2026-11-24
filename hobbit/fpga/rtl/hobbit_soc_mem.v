// hobbit_soc_mem.v -- the memory side of the gated Hobbit core
// (bsv/HobbitSocCpu.bsv; fpga/README.md, "The core's clock and its
// memory").
//
// The core runs on a gated copy of the system clock.  This block decides,
// clock by clock, whether the next system-clock edge is also a core edge
// (`fire`; the top turns it into the DCCA's enable on the falling edge, so
// a core edge is exactly the rising edge after a clock with fire = 1).
// Between core edges the core's registers hold, its logic shows what the
// next edge would do, and this block makes that true of memory:
//
//   1. On a core edge it captures the edge's writes (memory face, table
//      walk's R/M writeback, event frame) and the read request.
//   2. It performs the writes in that order, then the read, through the
//      backend (one request at a time: SDRAM, ROM, or I/O).  The read's
//      word is held on rdData until the next read; a later write to the
//      same address updates it, as mkHobbitMem's readData reads the array
//      as it stands (bsv/HobbitTypes.bsv).
//   3. It takes the core's combinational probes (every physical word the
//      walks and the event sequence would read this clock), and fills
//      the window until each probe in RAM or ROM hits; a probe anywhere
//      else is entered as 0 (a device register is never walked).
//   4. Only then does it set fire.
//
// So a core clock costs at least five system clocks, plus the memory's.
// The core counts its own clocks, so its cycle counts do not change.
module hobbit_soc_mem #(
    parameter NWIN = 16,
    parameter NPROBE = 22
) (
    input  wire                 clk,
    input  wire                 rst,
    // The core (mkHobbitSocCpu's ports).
    input  wire                 cpu_rdReq,
    input  wire [31:0]          cpu_rdAddr,
    output reg  [31:0]          cpu_rdData,
    input  wire [64:0]          cpu_memWr,
    input  wire [64:0]          cpu_tblWr,
    input  wire [64:0]          cpu_evWr,
    output wire [NWIN*65-1:0]   cpu_window,
    input  wire [NPROBE*33-1:0] cpu_probes,
    // Gating.
    output reg                  fire,        // the next rising edge is a core edge
    input  wire                 edge_now,    // this rising edge is a core edge
    output reg  [39:0]          core_clocks, // core edges since reset
    // A second master (the host link's loader); served between core clocks.
    input  wire                 aux_valid,
    input  wire                 aux_we,
    input  wire [31:0]          aux_addr,
    input  wire [31:0]          aux_wdata,
    output reg                  aux_done,
    output reg  [31:0]          aux_rdata,
    // The backend: one request at a time, held until bk_done.
    output reg                  bk_valid,
    output reg                  bk_we,
    output reg  [31:0]          bk_addr,
    output reg  [31:0]          bk_wdata,
    output reg  [3:0]           bk_be,
    input  wire                 bk_done,
    input  wire [31:0]          bk_rdata
);
    localparam S_WR = 0, S_RD = 1, S_SETTLE = 2, S_PROBE = 3, S_CHECK = 4,
               S_FILL = 5, S_FIRE = 6, S_AUX = 7;

    reg [2:0]  st;
    reg [2:0]  wpend;            // {ev, tbl, mem}
    reg [31:0] wa [0:2];
    reg [31:0] wd [0:2];
    reg        rpend;
    reg [31:0] ra;               // address of the word on rdData
    reg        rnew;             // a read was captured at this edge
    reg [1:0]  wi;               // write in flight
    reg [NPROBE*33-1:0] pq;      // probes, registered

    reg        win_v [0:NWIN-1];
    reg [31:0] win_a [0:NWIN-1];
    reg [31:0] win_d [0:NWIN-1];
    reg [$clog2(NWIN)-1:0] wptr;
    reg [31:0] fill_a;
    reg [$clog2(NWIN)-1:0] fill_slot;

    genvar g;
    generate for (g = 0; g < NWIN; g = g + 1) begin : wv
        assign cpu_window[g*65 +: 65] = {win_v[g], win_a[g], win_d[g]};
    end endgenerate

    // RAM (SDRAM, 32 MB at 0x80000000) and the ROM block (16 KB at 0):
    // the words a walk or a vector read can come from.
    function is_mem(input [31:0] a);
        is_mem = (a[31:25] == 7'b1000000) || (a[31:14] == 18'd0);
    endfunction

    // The probes are checked one valid probe per clock (a parallel
    // 22 x 16 match cost 26k LUT4, fpga/README.md "Area"): pi is the
    // first probe not yet checked in this pass, k the next valid one at
    // or after it, and k_hit whether the window holds its word.
    reg  [4:0]  pi;
    reg  [NPROBE-1:0] pvalid, pleft;
    reg  [4:0]  k;
    reg         k_any;
    reg  [31:0] k_a;
    reg         k_hit;
    integer p, i;
    always @(*) begin
        k = 0; k_any = 1'b0;
        for (p = 0; p < NPROBE; p = p + 1) begin
            pvalid[p] = pq[p*33 + 32];
            pleft[p] = pvalid[p] && (p >= pi);
        end
        for (p = NPROBE - 1; p >= 0; p = p - 1)
            if (pleft[p]) begin k = p; k_any = 1'b1; end
        k_a = {pq[k*33+2 +: 30], 2'b00};
        k_hit = 1'b0;
        for (i = 0; i < NWIN; i = i + 1)
            if (win_v[i] && win_a[i] == k_a) k_hit = 1'b1;
    end

    task win_write(input [31:0] a, input [31:0] d);
        integer k;
        for (k = 0; k < NWIN; k = k + 1)
            if (win_v[k] && win_a[k] == {a[31:2], 2'b00}) win_d[k] <= d;
    endtask

    always @(posedge clk) begin
        aux_done <= 1'b0;
        if (rst) begin
            st <= S_SETTLE; fire <= 1'b0; wpend <= 0; rpend <= 0; rnew <= 0;
            bk_valid <= 1'b0; core_clocks <= 0; wptr <= 0; ra <= 0;
            cpu_rdData <= 0;
            for (i = 0; i < NWIN; i = i + 1) begin
                win_v[i] <= 1'b0; win_a[i] <= 0; win_d[i] <= 0;
            end
        end else begin
            if (edge_now) begin
                // A core edge: capture what it did.
                core_clocks <= core_clocks + 1;
                fire <= 1'b0;
                wpend <= {cpu_evWr[64], cpu_tblWr[64], cpu_memWr[64]};
                wa[0] <= cpu_memWr[63:32]; wd[0] <= cpu_memWr[31:0];
                wa[1] <= cpu_tblWr[63:32]; wd[1] <= cpu_tblWr[31:0];
                wa[2] <= cpu_evWr[63:32];  wd[2] <= cpu_evWr[31:0];
                rpend <= cpu_rdReq;
                rnew <= cpu_rdReq;
                if (cpu_rdReq) ra <= cpu_rdAddr;
                st <= S_WR;
            end else case (st)
            S_WR: if (!bk_valid) begin
                if (wpend != 0) begin
                    wi <= wpend[0] ? 2'd0 : wpend[1] ? 2'd1 : 2'd2;
                    bk_valid <= 1'b1; bk_we <= 1'b1; bk_be <= 4'hF;
                    bk_addr <= wpend[0] ? wa[0] : wpend[1] ? wa[1] : wa[2];
                    bk_wdata <= wpend[0] ? wd[0] : wpend[1] ? wd[1] : wd[2];
                end else st <= S_RD;
            end else if (bk_done) begin
                bk_valid <= 1'b0;
                wpend[wi] <= 1'b0;
                win_write(bk_addr, bk_wdata);
                // rdData reads the array as it stands (mkHobbitMem).
                if (!rnew && is_mem(bk_addr) && bk_addr[31:2] == ra[31:2])
                    cpu_rdData <= bk_wdata;
            end
            S_RD: if (!rpend) st <= S_SETTLE;
                else if (!bk_valid) begin
                    bk_valid <= 1'b1; bk_we <= 1'b0; bk_be <= 4'hF;
                    bk_addr <= ra;
                end else if (bk_done) begin
                    bk_valid <= 1'b0; rpend <= 1'b0; rnew <= 1'b0;
                    cpu_rdData <= bk_rdata;
                    st <= S_SETTLE;
                end
            S_SETTLE: st <= S_PROBE;     // the probes settle on the new state
            S_PROBE: begin pq <= cpu_probes; pi <= 0; st <= S_CHECK; end
            S_CHECK:
                if (aux_valid) begin
                    bk_valid <= 1'b1; bk_we <= aux_we; bk_be <= 4'hF;
                    bk_addr <= aux_addr; bk_wdata <= aux_wdata;
                    st <= S_AUX;
                end else if (k_any && k_hit) begin
                    pi <= k + 1'b1;          // this probe hits: the next one
                end else if (k_any) begin
                    // A miss: fill the round-robin slot, then start the
                    // pass again from new probes (the fill may have evicted
                    // a word an earlier probe needs, and a probe may
                    // depend on the word just fetched).
                    fill_a <= k_a; fill_slot <= wptr;
                    wptr <= wptr + 1'b1;
                    if (is_mem(k_a)) begin
                        bk_valid <= 1'b1; bk_we <= 1'b0; bk_be <= 4'hF;
                        bk_addr <= k_a;
                        st <= S_FILL;
                    end else begin
                        win_v[wptr] <= 1'b1; win_a[wptr] <= k_a;
                        win_d[wptr] <= 32'd0;
                        st <= S_SETTLE;
                    end
                end else begin
                    fire <= 1'b1;
                    st <= S_FIRE;
                end
            S_FILL: if (bk_done) begin
                bk_valid <= 1'b0;
                win_v[fill_slot] <= 1'b1; win_a[fill_slot] <= fill_a;
                win_d[fill_slot] <= bk_rdata;
                st <= S_SETTLE;
            end
            S_AUX: if (bk_done) begin
                bk_valid <= 1'b0;
                aux_done <= 1'b1; aux_rdata <= bk_rdata;
                if (bk_we) begin
                    win_write(bk_addr, bk_wdata);
                    if (is_mem(bk_addr) && bk_addr[31:2] == ra[31:2])
                        cpu_rdData <= bk_wdata;
                end
                st <= S_SETTLE;
            end
            S_FIRE: ;                    // the edge comes on the next rising edge
            default: st <= S_SETTLE;
            endcase
        end
    end
endmodule
