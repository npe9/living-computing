// hobbit_soc.v -- the Hobbit SoC for the ULX3S (fpga/README.md, "The SoC").
//
//   mkHobbitSocCpu (bsv/HobbitSocCpu.bsv)  the privileged machine, on gclk
//   hobbit_soc_mem                         gating, write/read/probe service
//   backend router                         RAM -> sdram_word, ROM -> block RAM,
//                                          everything else -> the I/O bus
//   I/O bus                                device windows (the device bus
//                                          contract, docs/ulx3s_plan.md); a
//                                          window with no RTL device, and any
//                                          unmapped address, is forwarded
//                                          over the host link
//   hostlink                               loader, start, forwarding, host IL
//
// Physical map (tools/p9boot.py, which follows io.h):
//   0x00000000-0x00003FFF  ROM block RAM (16 KB of PROMBASE's 512 KB; the
//                          fpi image is 13 KB); the rest of PROMBASE forwards
//   0x80000000-0x81FFFFFF  SDRAM (32 MB; the kernel is told 8 MB, PPage0)
//   0xB0000000 + ...       IOACK: incon +0x000, iic +0x080, quart +0x100,
//                          lcd +0x3000
//   0xB8000000 + ...       IONAK: ioctl +0x000, irq +0x080, scsi +0x100,
//                          rtc +0x2000..0x3FFF
//   0xA4400000             SONIC
//
// The core's clock: gclk is the system clock gated by `cpu_ce`, which this
// module changes on the falling edge only (the ECP5 DCCA in the board top,
// an AND in simulation).  `cpu_ce` is high throughout reset so the core's
// synchronous reset sees edges.
module hobbit_soc #(
    parameter CPB = 25,              // host link: 25 MHz / 1 Mbaud
    parameter SD_T_PWR = 5000,
    parameter SD_T_REFI = 180
) (
    input  wire        clk,
    input  wire        rst,          // synchronous, active high
    input  wire        gclk,
    output reg         cpu_ce,
    // Host link.
    input  wire        rxd,
    output wire        txd,
    // SDRAM pins (registered in sdram_word).
    output wire        sd_cs_n, sd_ras_n, sd_cas_n, sd_we_n,
    output wire [1:0]  sd_ba,
    output wire [12:0] sd_a,
    output wire [1:0]  sd_dqm,
    output wire [15:0] sd_dq_out,
    output wire        sd_dq_oe,
    input  wire [15:0] sd_dq_in,
    // State.
    output wire [7:0]  leds,
    output wire [31:0] retired,
    output wire        running,
    output wire        stopped,
    output wire [39:0] core_clocks,
    output wire        hri_valid,
    output wire [298:0] hri,
    // A replayed run's interrupts (fpga/sim; the board ties them off):
    // HobbitSocCpu armInterrupt / takenInterrupt, enables sampled on a
    // core edge.
    input  wire        arm_en,
    input  wire [31:0] arm_n,
    input  wire [2:0]  arm_level,
    output wire        arm_rdy,
    input  wire        took_en,
    output wire        took_rdy,
    output wire [31:0] took_pc
);
    // ---- the core ------------------------------------------------------
    wire        c_rdReq;
    wire [31:0] c_rdAddr;
    wire [31:0] c_rdData;
    wire [64:0] c_memWr, c_tblWr, c_evWr;
    wire [1039:0] c_window;
    wire [725:0] c_probes;
    wire        c_rdy_go;
    wire [31:0] c_pc;
    wire        go_valid;
    wire [31:0] go_entry;
    wire [2:0]  host_il;
    wire        fire;

    mkHobbitSocCpu cpu (
        .CLK(gclk), .RST_N(~rst),
        .rdReq(c_rdReq), .rdAddr(c_rdAddr), .rdData_d(c_rdData),
        .memWr(c_memWr), .tblWr(c_tblWr), .evWr(c_evWr),
        .window_w(c_window), .probes(c_probes),
        .go_entry(go_entry), .EN_go(go_valid && c_rdy_go), .RDY_go(c_rdy_go),
        .running(running),
        .il_level(host_il),
        .armInterrupt_n(arm_n), .armInterrupt_level(arm_level),
        .EN_armInterrupt(arm_en && arm_rdy), .RDY_armInterrupt(arm_rdy),
        .irqArmable(),
        .EN_takenInterrupt(took_en && took_rdy), .takenInterrupt(took_pc),
        .RDY_takenInterrupt(took_rdy),
        .retired(retired), .stopped(stopped), .pc(c_pc),
        .hriValid(hri_valid), .hri(hri));

    always @(negedge clk) cpu_ce <= rst | fire;
    wire edge_now = cpu_ce;

    // A start offered on an edge is taken by it.
    wire go_taken = edge_now && go_valid && c_rdy_go;

    // ---- memory adapter ------------------------------------------------
    wire        aux_valid, aux_we, aux_done;
    wire [31:0] aux_addr, aux_wdata, aux_rdata;
    wire        bk_valid, bk_we;
    wire [31:0] bk_addr, bk_wdata;
    wire [3:0]  bk_be;
    reg         bk_done;
    reg  [31:0] bk_rdata;

    hobbit_soc_mem mem (
        .clk(clk), .rst(rst),
        .cpu_rdReq(c_rdReq), .cpu_rdAddr(c_rdAddr), .cpu_rdData(c_rdData),
        .cpu_memWr(c_memWr), .cpu_tblWr(c_tblWr), .cpu_evWr(c_evWr),
        .cpu_window(c_window), .cpu_probes(c_probes),
        .fire(fire), .edge_now(edge_now && !rst), .core_clocks(core_clocks),
        .aux_valid(aux_valid), .aux_we(aux_we), .aux_addr(aux_addr),
        .aux_wdata(aux_wdata), .aux_done(aux_done), .aux_rdata(aux_rdata),
        .bk_valid(bk_valid), .bk_we(bk_we), .bk_addr(bk_addr),
        .bk_wdata(bk_wdata), .bk_be(bk_be), .bk_done(bk_done),
        .bk_rdata(bk_rdata));

    // ---- backend router ------------------------------------------------
    wire is_ram = (bk_addr[31:25] == 7'b1000000);
    wire is_rom = (bk_addr[31:14] == 18'd0);

    wire        sd_ready, sd_rsp_valid, sd_init;
    wire [31:0] sd_rdata;
    reg         sd_issued;
    sdram_word #(.T_PWR(SD_T_PWR), .T_REFI(SD_T_REFI)) sdram (
        .clk(clk), .rst(rst),
        .req_valid(bk_valid && is_ram && !sd_issued), .req_ready(sd_ready),
        .req_we(bk_we), .req_addr(bk_addr[24:2]), .req_wdata(bk_wdata),
        .req_be(bk_be), .rsp_valid(sd_rsp_valid), .rsp_rdata(sd_rdata),
        .init_done(sd_init),
        .sd_cs_n(sd_cs_n), .sd_ras_n(sd_ras_n), .sd_cas_n(sd_cas_n),
        .sd_we_n(sd_we_n), .sd_ba(sd_ba), .sd_a(sd_a), .sd_dqm(sd_dqm),
        .sd_dq_out(sd_dq_out), .sd_dq_oe(sd_dq_oe), .sd_dq_in(sd_dq_in));

    // ROM: 4096 words of block RAM, written by the loader.
    reg [31:0] rom [0:4095];
    reg [31:0] rom_q;
    reg        rom_busy;
`ifdef HOBBIT_SIM
    // The co-simulation's back door (fpga/sim/soc_main.cpp).
    export "DPI-C" function soc_rom_poke;
    function void soc_rom_poke(input int unsigned a, input int unsigned v);
        rom[a[13:2]] = v;
    endfunction
`endif

    // I/O: a request is held until io_done.
    wire        io_done;
    wire [31:0] io_rdata;
    reg         io_issued;

    always @(posedge clk) begin
        bk_done <= 1'b0;
        if (rst) begin
            sd_issued <= 1'b0; rom_busy <= 1'b0; io_issued <= 1'b0;
        end else if (bk_valid && !bk_done) begin
            if (is_ram) begin
                if (!sd_issued && sd_ready) sd_issued <= 1'b1;
                if (sd_issued && sd_rsp_valid) begin
                    bk_done <= 1'b1; bk_rdata <= sd_rdata; sd_issued <= 1'b0;
                end
            end else if (is_rom) begin
                if (!rom_busy) begin
                    rom_busy <= 1'b1;
                    if (bk_we) rom[bk_addr[13:2]] <= bk_wdata;
                    rom_q <= rom[bk_addr[13:2]];
                end else begin
                    rom_busy <= 1'b0; bk_done <= 1'b1; bk_rdata <= rom_q;
                end
            end else begin
                if (!io_issued) io_issued <= 1'b1;
                if (io_issued && io_done) begin
                    bk_done <= 1'b1; bk_rdata <= io_rdata; io_issued <= 1'b0;
                end
            end
        end
    end

    // ---- I/O bus: every window forwards until its device lands ---------
    wire        fwd_done;
    wire [31:0] fwd_rdata;
    assign io_done = fwd_done;
    assign io_rdata = fwd_rdata;

    hostlink #(.CPB(CPB)) link (
        .clk(clk), .rst(rst), .rxd(rxd), .txd(txd),
        .mem_valid(aux_valid), .mem_we(aux_we), .mem_addr(aux_addr),
        .mem_wdata(aux_wdata), .mem_done(aux_done), .mem_rdata(aux_rdata),
        .go_valid(go_valid), .go_entry(go_entry), .go_taken(go_taken),
        .fwd_valid(bk_valid && !is_ram && !is_rom && io_issued),
        .fwd_we(bk_we), .fwd_addr(bk_addr), .fwd_wdata(bk_wdata),
        .fwd_done(fwd_done), .fwd_rdata(fwd_rdata), .host_il(host_il),
        .running(running), .stopped(stopped), .core_clocks(core_clocks),
        .retired(retired));

    assign leds = {stopped, running, sd_init, c_pc[6:2]};
endmodule
