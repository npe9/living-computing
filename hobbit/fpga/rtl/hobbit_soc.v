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
    parameter SD_T_REFI = 180,
    // Which devices are RTL (fpga/socdev/HobbitSocDevs.bsv's `rtl` bits:
    // 0 incon/ioctl/irq, 1 Quart, 2 RTC, 3 IIC, 4 Lcdisp); the rest forward.
    parameter [7:0]  DEV_RTL = 8'h00,
    parameter [31:0] RTC_TICKS = 25000000,
    parameter [55:0] RTC_START = 56'h93010301120000,
    parameter [1:0]  RTC_MCP = 2'd3,
    parameter [15:0] RTC_I2CQ = 16'd63,
    parameter QUART_CPB = 1302                  // the console tunnel's rate
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
    wire [1039:0] c_window;
    wire [725:0] c_probes;
    wire        c_rdy_go;
    wire [31:0] c_pc;
    wire        go_valid;
    wire [31:0] go_entry;
    wire [2:0]  host_il;
    wire        dev_il6;
    wire        fire;

    mkHobbitSocCpu cpu (
        .CLK(gclk), .RST_N(~rst),
        .rdReq(c_rdReq), .rdAddr(c_rdAddr), .rdData_d(c_rdData),
        .memWr(c_memWr), .tblWr(c_tblWr), .evWr(c_evWr),
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
        .CLK(clk), .RST_N(!rst),
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
        .fwd_we(bk_we), .fwd_addr(bk_addr), .fwd_wdata(bk_wdata),
        .fwd_done(fwd_done), .fwd_rdata(fwd_rdata), .host_il(host_il),
        .host_src(host_src),
        .con_valid(con_valid), .con_byte(con_byte), .con_taken(con_taken),
        .key_valid(key_valid), .key_byte(key_byte),
        .running(running), .stopped(stopped), .core_clocks(core_clocks),
        .retired(retired));

    assign leds = {stopped, running, sd_init, c_pc[6:2]};
endmodule
