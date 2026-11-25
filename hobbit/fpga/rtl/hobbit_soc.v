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
`ifndef HOBBIT_SOC_SETTLE
`define HOBBIT_SOC_SETTLE 1
`endif
module hobbit_soc #(
    parameter CPB = 25,              // host link: 25 MHz / 1 Mbaud
    parameter SD_T_PWR = 5000,
    parameter SD_T_REFI = 180,
    // Which devices are RTL (fpga/socdev/HobbitSocDevs.bsv's `rtl` bits:
    // 0 incon/ioctl/irq, 1 Quart, 2 RTC, 3 IIC, 4 Lcdisp, 5 SONIC); the
    // rest forward.
    parameter [7:0]  DEV_RTL = 8'h00,
    parameter [31:0] RTC_TICKS = 25000000,
    parameter [55:0] RTC_START = 56'h93010301120000,
    parameter [1:0]  RTC_MCP = 2'd3,
    parameter [15:0] RTC_I2CQ = 16'd63,
    parameter QUART_CPB = 1302,                 // the console tunnel's rate
    // hobbit_soc_mem's SETTLE; the board and the co-simulation use the
    // same default (run_soc.sh can override it for the injection test).
    parameter SOC_SETTLE = `HOBBIT_SOC_SETTLE
) (
    input  wire        clk,
    input  wire        rst,          // synchronous, active high
    input  wire        gclk,
    output reg         cpu_ce,
    // Lcdisp's scan port (pixel clock domain), for the HDMI path.
    input  wire        pclk,
    input  wire [17:0] scan_addr,
    output wire [7:0]  scan_data,
    // EspLink: the ESP32's GPIO16 (txd), GPIO17 (rxd) and GPIO4 (RTS).
    output wire        esp_txd,
    input  wire        esp_rxd,
    input  wire        esp_rts,
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
    // The RTC's MCP7940N I2C (open drain: *_low = 1 pulls the line low).
    output wire        i2c_scl_low,
    output wire        i2c_sda_low,
    input  wire        i2c_scl_in,
    input  wire        i2c_sda_in,
    output wire [7:0]  dev_faults,
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
    wire [3:0]  c_memWrBe;
    wire        c_rdMerge, c_rdSpec, c_rdNack;
    wire [1039:0] c_window;
    wire [857:0] c_probes;          // 26 probes of 33 bits
    wire        c_rdy_go;
    wire [31:0] c_pc;
    wire        go_valid;
    wire [31:0] go_entry;
    wire [2:0]  host_il;
    wire        dev_il6;
    wire        fire;

    // SYSCLK: the core's arrays read on the free-running clock between
    // core edges (fpga/sysram_filter.py, rtl/hobbit_sysregfile.v).
    mkHobbitSocCpu cpu (
        .SYSCLK(clk), .CLK(gclk), .RST_N(~rst),
        .rdReq(c_rdReq), .rdAddr(c_rdAddr), .rdData_d(c_rdData),
        .memWr(c_memWr), .tblWr(c_tblWr), .evWr(c_evWr),
        .memWrBe(c_memWrBe), .rdMerge(c_rdMerge),
        .rdSpec(c_rdSpec), .rdNack_n(c_rdNack),
        .window_w(c_window), .probes(c_probes),
        .go_entry(go_entry), .EN_go(go_valid && c_rdy_go), .RDY_go(c_rdy_go),
        .running(running),
        .il_level(dev_il6 && host_il > 3'd6 ? 3'd6 : host_il),
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

    // SETTLE: the longest chain of core arrays a probe depends on
    // (rtl/hobbit_soc_mem.v).
    hobbit_soc_mem #(.NPROBE(26), .SETTLE(SOC_SETTLE)) mem (
        .clk(clk), .rst(rst),
        .cpu_rdReq(c_rdReq), .cpu_rdAddr(c_rdAddr), .cpu_rdData(c_rdData),
        .cpu_memWr(c_memWr), .cpu_tblWr(c_tblWr), .cpu_evWr(c_evWr),
        .cpu_memWrBe(c_memWrBe), .cpu_rdMerge(c_rdMerge),
        .cpu_rdSpec(c_rdSpec), .cpu_rdNack(c_rdNack),
        .cpu_window(c_window), .cpu_probes(c_probes),
        .fire(fire), .edge_now(edge_now && !rst), .core_clocks(core_clocks),
        .aux_valid(aux_valid), .aux_we(aux_we), .aux_addr(aux_addr),
        .aux_wdata(aux_wdata), .aux_done(aux_done), .aux_rdata(aux_rdata),
        .bk_valid(bk_valid), .bk_we(bk_we), .bk_addr(bk_addr),
        .bk_wdata(bk_wdata), .bk_be(bk_be), .bk_done(bk_done),
        .bk_rdata(bk_rdata),
        .snoop_valid(dma_wr_done), .snoop_addr(snoop_a),
        .snoop_wdata(snoop_d), .snoop_be(snoop_be_r));

    // ---- backend router ------------------------------------------------
    wire is_ram = (bk_addr[31:25] == 7'b1000000);
    wire is_rom = (bk_addr[31:14] == 18'd0);

    wire        sd_ready, sd_rsp_valid, sd_init;
    wire [31:0] sd_rdata;
    reg         sd_issued;

    // ---- SDRAM arbiter: the core's memory service and the SONIC's DMA ----
    // One request at a time; the core's side goes first when both wait.
    // A DMA word outside RAM is not sent to the SDRAM: a read of it is
    // answered 0 and a write dropped (dma_bad counts them).
    wire        dma_rdy;                 // a DMA request is offered
    wire [68:0] dma_req;                 // SonicDmaReq: addr, write, wdata, be
    wire        dma_rd_rdy;
    reg         dma_get, dma_put;
    reg  [31:0] dma_put_d;
    wire [31:0] dma_addr  = dma_req[68:37];
    wire        dma_write = dma_req[36];
    wire [31:0] dma_wdata = dma_req[35:4];
    wire [3:0]  dma_be    = dma_req[3:0];
    wire        dma_in_ram = (dma_addr[31:25] == 7'b1000000);
    reg         sd_busy, sd_dma, sd_dma_we;
    reg  [15:0] dma_bad;
    reg         dma_wr_done;             // a DMA write reached the SDRAM
    wire bk_wants  = bk_valid && !bk_done && is_ram && !sd_issued;
    wire dma_wants = dma_rdy && !dma_get && !dma_put;
    wire sd_req_valid = !sd_busy && (bk_wants || (dma_wants && dma_in_ram));
    wire grant_bk = bk_wants;
    wire sd_go = sd_req_valid && sd_ready;
    sdram_word #(.T_PWR(SD_T_PWR), .T_REFI(SD_T_REFI)) sdram (
        .clk(clk), .rst(rst),
        .req_valid(sd_req_valid), .req_ready(sd_ready),
        .req_we(grant_bk ? bk_we : dma_write),
        .req_addr(grant_bk ? bk_addr[24:2] : dma_addr[24:2]),
        .req_wdata(grant_bk ? bk_wdata : dma_wdata),
        .req_be(grant_bk ? bk_be : dma_be),
        .rsp_valid(sd_rsp_valid), .rsp_rdata(sd_rdata),
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

    // The DMA side: the request is taken (EN_dmaReq_get) when its SDRAM
    // access is issued, or at once when it is outside RAM; a read's word
    // is put back (EN_dmaRdata_put) when the SDRAM answers.  dma_addr and
    // its fields stay valid until the take, which is the clock of issue.
    always @(posedge clk) begin
        dma_get <= 1'b0; dma_put <= 1'b0;
        if (rst) begin
            sd_busy <= 1'b0; sd_dma <= 1'b0; dma_bad <= 0;
        end else begin
            if (sd_go) begin
                sd_busy <= 1'b1; sd_dma <= !grant_bk;
                sd_dma_we <= !grant_bk && dma_write;
            end
            if (sd_busy && sd_rsp_valid) begin
                sd_busy <= 1'b0;
                if (sd_dma && !sd_dma_we) begin dma_put <= 1'b1; dma_put_d <= sd_rdata; end
            end
            if (!grant_bk && dma_wants && !dma_in_ram && !sd_busy) begin
                dma_bad <= dma_bad + 1;
                if (!dma_write) begin dma_put <= 1'b1; dma_put_d <= 32'd0; end
            end
        end
    end
    // dmaReq_get is taken on the clock its SDRAM request is issued (or
    // refused); the write's snoop data are its fields that clock, held.
    reg [31:0] snoop_a, snoop_d; reg [3:0] snoop_be_r; reg snoop_pend;
    wire dma_take = (sd_go && !grant_bk) ||
                    (!grant_bk && dma_wants && !dma_in_ram && !sd_busy);
    always @(posedge clk) begin
        dma_wr_done <= 1'b0;
        if (rst) snoop_pend <= 1'b0;
        else if (sd_go && !grant_bk && dma_write) begin
            snoop_pend <= 1'b1; snoop_a <= dma_addr; snoop_d <= dma_wdata;
            snoop_be_r <= dma_be;
        end else if (snoop_pend && sd_busy && sd_rsp_valid) begin
            snoop_pend <= 1'b0; dma_wr_done <= 1'b1;
        end
    end
`ifdef VERILATOR
    // Simulation only: how much SONIC DMA the run did (run_soc.sh prints it).
    reg [31:0] dma_nrd = 0, dma_nwr = 0;
    always @(posedge clk)
        if (sd_go && !grant_bk) begin
            if (dma_write) dma_nwr <= dma_nwr + 1; else dma_nrd <= dma_nrd + 1;
        end
    final $display("SOC sonic dma: %0d reads, %0d writes reached the SDRAM, %0d refused",
                   dma_nrd, dma_nwr, dma_bad);
`endif

    always @(posedge clk) begin
        bk_done <= 1'b0;
        if (rst) begin
            sd_issued <= 1'b0; rom_busy <= 1'b0; io_issued <= 1'b0;
        end else if (bk_valid && !bk_done) begin
            if (is_ram) begin
                if (!sd_issued && sd_go && grant_bk) sd_issued <= 1'b1;
                if (sd_issued && sd_rsp_valid) begin
                    bk_done <= 1'b1; bk_rdata <= sd_rdata; sd_issued <= 1'b0;
                end
            end else if (is_rom) begin
                if (!rom_busy) begin
                    rom_busy <= 1'b1;
                    // Byte lanes, as the SDRAM's DQM.
                    if (bk_we && bk_be[0]) rom[bk_addr[13:2]][7:0]   <= bk_wdata[7:0];
                    if (bk_we && bk_be[1]) rom[bk_addr[13:2]][15:8]  <= bk_wdata[15:8];
                    if (bk_we && bk_be[2]) rom[bk_addr[13:2]][23:16] <= bk_wdata[23:16];
                    if (bk_we && bk_be[3]) rom[bk_addr[13:2]][31:24] <= bk_wdata[31:24];
                    rom_q <= rom[bk_addr[13:2]];
                end else begin
                    rom_busy <= 1'b0; bk_done <= 1'b1; bk_rdata <= rom_q;
                end
            end else if (dev_claims) begin
                if (!io_issued && dev_rdy_req) io_issued <= 1'b1;
                if (io_issued && dev_rdy_resp) begin
                    bk_done <= 1'b1; bk_rdata <= dev_resp; io_issued <= 1'b0;
                end
            end else begin
                if (!io_issued) io_issued <= 1'b1;
                if (io_issued && io_done) begin
                    bk_done <= 1'b1; bk_rdata <= io_rdata; io_issued <= 1'b0;
                end
            end
        end
    end

    // ---- RTL devices (fpga/socdev/HobbitSocDevs.bsv) -----------------------
    // A claimed access is sent once (EN_req on the clock io_issued rises)
    // and completes with the device's one response.
    wire        dev_claims, dev_rdy_req, dev_rdy_resp;
    wire [31:0] dev_resp;
    wire [15:0] host_src;
    wire        q_txd;
    reg         q_rxd;
    wire        dev_take_req = bk_valid && !bk_done && !is_ram && !is_rom &&
                               dev_claims && !io_issued && dev_rdy_req;
    wire        dev_take_resp = bk_valid && !bk_done && !is_ram && !is_rom &&
                                dev_claims && io_issued && dev_rdy_resp;
    mkHobbitSocDevs #(.rtl(DEV_RTL), .ticksPerSec(RTC_TICKS),
                      .startBcd(RTC_START), .mcpMode(RTC_MCP),
                      .i2cQuarter(RTC_I2CQ)) devs (
        .CLK(clk), .RST_N(!rst), .CLK_pclk(pclk),
        .EN_dmaReq_get(dma_take), .dmaReq_get(dma_req), .RDY_dmaReq_get(dma_rdy),
        .dmaRdata_put(dma_put_d), .EN_dmaRdata_put(dma_put), .RDY_dmaRdata_put(dma_rd_rdy),
        .espTxd(esp_txd), .espPins_rxd(esp_rxd), .espPins_rts(esp_rts),
        .scan_read_a(scan_addr), .EN_scan_read(1'b1), .scan_data(scan_data),
        .claims_pa(bk_addr), .claims(dev_claims),
        .req_pa(bk_addr), .req_wdata(bk_wdata), .req_be(bk_be),
        .req_write(bk_we), .EN_req(dev_take_req), .RDY_req(dev_rdy_req),
        .EN_resp(dev_take_resp), .resp(dev_resp), .RDY_resp(dev_rdy_resp),
        .hostSources_s(host_src), .il6(dev_il6),
        .quartTxd(q_txd), .quartRxd_v(q_rxd),
        .i2cSclLow(i2c_scl_low), .i2cSdaLow(i2c_sda_low),
        .i2cPins_scl(i2c_scl_in), .i2cPins_sda(i2c_sda_in),
        .faults(dev_faults), .iicLed());

    // The RTL Quart's channel 0 is the console: its serial line is turned
    // into bytes and carried by the host link ('C' out, 'K' in), because
    // the FTDI port is the host link.
    wire [7:0] con_rx_b; wire con_rx_v; wire con_rx_ferr;
    uart_rx #(.CPB(QUART_CPB)) con_rx (.clk(clk), .rst(rst), .rxd(q_txd),
        .valid(con_rx_v), .data(con_rx_b), .ferr(con_rx_ferr));
    reg        con_valid;
    reg  [7:0] con_byte;
    wire       con_taken;
    always @(posedge clk) begin
        if (rst) con_valid <= 1'b0;
        else if (con_rx_v) begin con_valid <= 1'b1; con_byte <= con_rx_b; end
        else if (con_taken) con_valid <= 1'b0;
    end
    wire       key_valid;
    wire [7:0] key_byte;
    wire       key_ready;
    wire       key_txd;
    uart_tx #(.CPB(QUART_CPB)) con_tx (.clk(clk), .rst(rst),
        .valid(key_valid), .data(key_byte), .ready(key_ready), .txd(key_txd));
    always @(posedge clk) q_rxd <= rst ? 1'b1 : key_txd;

    // ---- I/O bus: an unclaimed window forwards ---------------------------
    wire        fwd_done;
    wire [31:0] fwd_rdata;
    assign io_done = fwd_done;
    assign io_rdata = fwd_rdata;

    hostlink #(.CPB(CPB)) link (
        .clk(clk), .rst(rst), .rxd(rxd), .txd(txd),
        .mem_valid(aux_valid), .mem_we(aux_we), .mem_addr(aux_addr),
        .mem_wdata(aux_wdata), .mem_done(aux_done), .mem_rdata(aux_rdata),
        .go_valid(go_valid), .go_entry(go_entry), .go_taken(go_taken),
        .fwd_valid(bk_valid && !is_ram && !is_rom && !dev_claims && io_issued),
        .fwd_we(bk_we), .fwd_be(bk_be), .fwd_addr(bk_addr), .fwd_wdata(bk_wdata),
        .fwd_done(fwd_done), .fwd_rdata(fwd_rdata), .host_il(host_il),
        .host_src(host_src),
        .con_valid(con_valid), .con_byte(con_byte), .con_taken(con_taken),
        .key_valid(key_valid), .key_byte(key_byte),
        .running(running), .stopped(stopped), .core_clocks(core_clocks),
        .retired(retired));

    assign leds = {stopped, running, sd_init, c_pc[6:2]};
endmodule
