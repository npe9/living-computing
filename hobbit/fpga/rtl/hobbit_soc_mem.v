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
// So a core clock costs at least four system clocks plus SETTLE, plus the
// memory's.  The core counts its own clocks, so its cycle counts do not
// change.
//
// SETTLE is how many system clocks the core's logic is given, after the
// last change to its inputs (a core edge, rdData, the window), before the
// probes are sampled.  The core's arrays read on the system clock
// (rtl/hobbit_sysregfile.v), one clock per array a value passes through
// on its way to a probe, so SETTLE must be at least the longest such
// chain.  That bounds zero-delay simulation only: on hardware each stage
// also needs its combinational path to settle, about ceil(t / 40 ns)
// system clocks at 25 MHz, and the post-placement estimate puts the
// core's paths near 200 ns (fpga/README.md, "The core's arrays on the
// system clock"), so a hardware SETTLE is sized from routed timing.
// HOBBIT_SIM checks it at every core edge: a valid probe in RAM
// or ROM that the window does not hold prints PROBE STALE and stops the
// run (fpga/README.md, "The core's arrays on the system clock").
module hobbit_soc_mem #(
    parameter NWIN = 16,
    parameter NPROBE = 26,
    parameter SETTLE = 1
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
    // cpu_memWr's byte enables, and whether cpu_rdReq's word is only the
    // merge word of a byte or half-word store (HobbitSocCpu memWrBe,
    // rdMerge): such a read is not made of a device, whose register reads
    // are side effects; the store's byte-enabled write needs none of it.
    input  wire [3:0]           cpu_memWrBe,
    input  wire                 cpu_rdMerge,
    // cpu_rdReq's read is speculative; cpu_rdNack says, until the next
    // core edge, that this adapter declined it (a device read only).
    input  wire                 cpu_rdSpec,
    output reg                  cpu_rdNack,
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
    input  wire [31:0]          bk_rdata,
    // A DMA write that reached memory (hobbit_soc's SONIC arbiter): the
    // window and rdData are kept equal to memory.
    input  wire                 snoop_valid,
    input  wire [31:0]          snoop_addr,
    input  wire [31:0]          snoop_wdata,
    input  wire [3:0]           snoop_be
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
    reg        rmerge;           // ... and it is a merge word (cpu_rdMerge)
    reg        rspec;            // ... or speculative (cpu_rdSpec)
    reg [3:0]  wbe0;             // the memory write's byte enables
    reg [1:0]  wi;               // write in flight
    reg [NPROBE*33-1:0] pq;      // probes, registered
    reg [3:0]  settle_n;         // system clocks spent in S_SETTLE

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

    function [31:0] merge(input [31:0] old, input [31:0] d, input [3:0] be);
        merge = {be[3] ? d[31:24] : old[31:24], be[2] ? d[23:16] : old[23:16],
                 be[1] ? d[15:8] : old[15:8], be[0] ? d[7:0] : old[7:0]};
    endfunction

    always @(posedge clk) begin
        aux_done <= 1'b0;
        if (!rst && snoop_valid) begin
            for (i = 0; i < NWIN; i = i + 1)
                if (win_v[i] && win_a[i][31:2] == snoop_addr[31:2])
                    win_d[i] <= merge(win_d[i], snoop_wdata, snoop_be);
            if (ra[31:2] == snoop_addr[31:2] && is_mem(ra))
                cpu_rdData <= merge(cpu_rdData, snoop_wdata, snoop_be);
        end
        if (rst) begin
            st <= S_SETTLE; settle_n <= 0;
            fire <= 1'b0; wpend <= 0; rpend <= 0; rnew <= 0; rmerge <= 0;
            rspec <= 0; cpu_rdNack <= 1'b0;
            wbe0 <= 4'hF;
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
                wbe0 <= cpu_memWrBe;
                wa[1] <= cpu_tblWr[63:32]; wd[1] <= cpu_tblWr[31:0];
                wa[2] <= cpu_evWr[63:32];  wd[2] <= cpu_evWr[31:0];
                rpend <= cpu_rdReq;
                rnew <= cpu_rdReq;
                rmerge <= cpu_rdReq && cpu_rdMerge;
                rspec <= cpu_rdReq && cpu_rdSpec;
                cpu_rdNack <= 1'b0;
                if (cpu_rdReq) ra <= cpu_rdAddr;
                st <= S_WR;
            end else case (st)
            S_WR: if (!bk_valid) begin
                if (wpend != 0) begin
                    wi <= wpend[0] ? 2'd0 : wpend[1] ? 2'd1 : 2'd2;
                    // The memory face's write keeps its byte lanes; the
                    // PTE writeback and the event frame are whole words.
                    bk_valid <= 1'b1; bk_we <= 1'b1;
                    bk_be <= wpend[0] ? wbe0 : 4'hF;
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
                else if (rmerge && !is_mem(ra)) begin
                    // A device's merge word is not read: the store that
                    // wants it writes its own lanes only (bk_be), and a
                    // device register read is a side effect.  The core
                    // sees 0 in the other lanes, which nothing it records
                    // or stores depends on (HobbitStackCache memReq).
                    rpend <= 1'b0; rnew <= 1'b0; rmerge <= 1'b0;
                    cpu_rdData <= 32'd0;
                    st <= S_SETTLE;
                end else if (rspec && !is_mem(ra)) begin
                    // A speculative device read is declined, not made:
                    // the core drops the word and asks again when the
                    // instructions ahead of the one that wants it are
                    // done (HobbitStackCache rdNack).
                    rpend <= 1'b0; rnew <= 1'b0; rspec <= 1'b0;
                    cpu_rdNack <= 1'b1;
                    cpu_rdData <= 32'd0;
                    st <= S_SETTLE;
                end else if (!bk_valid) begin
                    bk_valid <= 1'b1; bk_we <= 1'b0; bk_be <= 4'hF;
                    bk_addr <= ra;
                end else if (bk_done) begin
                    bk_valid <= 1'b0; rpend <= 1'b0; rnew <= 1'b0;
                    cpu_rdData <= bk_rdata;
                    st <= S_SETTLE;
                end
            S_SETTLE:                    // the probes settle on the new state
                if (settle_n + 1 >= SETTLE) begin
                    settle_n <= 0;
                    st <= S_PROBE;
                end else settle_n <= settle_n + 1'b1;
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

`ifdef HOBBIT_SIM
    // Probe freshness: on a core edge every valid probe in RAM or ROM must
    // be in the window, as the probes the core shows *now* (not the ones
    // sampled in S_PROBE) -- a probe that moved after the sample, because
    // an array read had not settled, would otherwise be walked as 0.
    // Window uniqueness: HobbitSocCpu's winRead ORs the words of every
    // matching valid entry, which is the priority select only while no
    // two valid entries hold one address (a fill is made on a miss only).
    integer pp, ww, w2;
    reg hit_now;
    // Out of reset two core edges are never in consecutive system clocks
    // (S_WR, S_RD, S_SETTLE, S_PROBE and S_CHECK lie between them), which
    // rtl/hobbit_sysregfile.v's check relies on to tell reset's edges from
    // the run's.
    reg edge_q;
    always @(posedge clk) begin
        edge_q <= !rst && edge_now;
        if (!rst && edge_now && edge_q) begin
            $display("EDGE STALE at core clock %0d: two core edges in consecutive system clocks",
                     core_clocks);
            $finish;
        end
        if (!rst && edge_now) begin
            for (ww = 0; ww < NWIN; ww = ww + 1)
                for (w2 = ww + 1; w2 < NWIN; w2 = w2 + 1)
                    if (win_v[ww] && win_v[w2] && win_a[ww] == win_a[w2]) begin
                        $display("WINDOW DUPLICATE at core clock %0d: entries %0d and %0d both hold %08x",
                                 core_clocks, ww, w2, win_a[ww]);
                        $finish;
                    end
            for (pp = 0; pp < NPROBE; pp = pp + 1) begin
                if (cpu_probes[pp*33 + 32] &&
                    is_mem({cpu_probes[pp*33+2 +: 30], 2'b00})) begin
                    hit_now = 1'b0;
                    for (ww = 0; ww < NWIN; ww = ww + 1)
                        if (win_v[ww] && win_a[ww] == {cpu_probes[pp*33+2 +: 30], 2'b00})
                            hit_now = 1'b1;
                    if (!hit_now) begin
                        $display("PROBE STALE at core clock %0d: probe %0d %08x not in the window",
                                 core_clocks, pp, {cpu_probes[pp*33+2 +: 30], 2'b00});
                        $finish;
                    end
                end
            end
        end
    end
`endif
endmodule
