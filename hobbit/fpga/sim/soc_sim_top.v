// soc_sim_top.v -- hobbit_soc with the SDRAM model, for Verilator
// (fpga/sim/run_soc.sh).  It stands for the board top: gclk is the system
// clock ANDed with cpu_ce (cpu_ce changes on the falling edge, as the
// DCCA's enable does on the board), and DQ is registered on the rising
// edge as the board's I/O register does.
module soc_sim_top #(
    parameter CPB = 4,
    parameter SD_T_PWR = 5000,
    parameter SD_T_REFI = 180,
    parameter [7:0] DEV_RTL = 8'h00     // run_soc.sh: SOC_RTL
) (
    input  wire        clk,
    input  wire        rst,
    input  wire        rxd,
    output wire        txd,
    output wire [31:0] retired,
    output wire        running,
    output wire        stopped,
    output wire [39:0] core_clocks,
    output wire        cpu_ce,
    input  wire        arm_en,
    input  wire [31:0] arm_n,
    input  wire [2:0]  arm_level,
    output wire        arm_rdy,
    input  wire        took_en,
    output wire        took_rdy,
    output wire [31:0] took_pc,
    // EspLink's pins, bridged by soc_main.cpp (SOC_ESP_PTY) to a host relay
    // (fpga/esp32_ethrelay/host/relay_host) or left idle.
    output wire        esp_txd,
    input  wire        esp_rxd,
    input  wire        esp_rts
);
    wire gclk = clk & cpu_ce;

    wire sd_cs_n, sd_ras_n, sd_cas_n, sd_we_n, sd_dq_oe, m_oe;
    wire [1:0] sd_ba, sd_dqm;
    wire [12:0] sd_a;
    wire [15:0] sd_dq_out, m_dq;
    reg  [15:0] dq_iob;
    always @(posedge clk) dq_iob <= m_oe ? m_dq : 16'hFFFF;

    // The RTC's I2C has no MCP7940N here: the lines float high (the
    // board's pull-ups) and mcpMode 0 keeps the RTC on startBcd.
    wire scl_low, sda_low;
    hobbit_soc #(.CPB(CPB), .SD_T_PWR(SD_T_PWR), .SD_T_REFI(SD_T_REFI),
                 .DEV_RTL(DEV_RTL), .RTC_MCP(2'd0)) soc (
        .clk(clk), .rst(rst), .gclk(gclk), .cpu_ce(cpu_ce),
        .pclk(clk), .scan_addr(18'd0), .scan_data(),
        .esp_txd(esp_txd), .esp_rxd(esp_rxd), .esp_rts(esp_rts),
        .rxd(rxd), .txd(txd),
        .sd_cs_n(sd_cs_n), .sd_ras_n(sd_ras_n), .sd_cas_n(sd_cas_n),
        .sd_we_n(sd_we_n), .sd_ba(sd_ba), .sd_a(sd_a), .sd_dqm(sd_dqm),
        .sd_dq_out(sd_dq_out), .sd_dq_oe(sd_dq_oe), .sd_dq_in(dq_iob),
        .i2c_scl_low(scl_low), .i2c_sda_low(sda_low),
        .i2c_scl_in(!scl_low), .i2c_sda_in(!sda_low), .dev_faults(),
        .leds(), .retired(retired), .running(running), .stopped(stopped),
        .core_clocks(core_clocks), .hri_valid(), .hri(),
        .arm_en(arm_en), .arm_n(arm_n), .arm_level(arm_level),
        .arm_rdy(arm_rdy), .took_en(took_en), .took_rdy(took_rdy),
        .took_pc(took_pc));

    sdram_model #(.CLK_HZ(25000000)) sdram (
        .clk(clk), .cs_n(sd_cs_n), .ras_n(sd_ras_n), .cas_n(sd_cas_n),
        .we_n(sd_we_n), .ba(sd_ba), .a(sd_a), .dqm(sd_dqm),
        .dq_in(sd_dq_out), .dq_in_oe(sd_dq_oe),
        .dq_out(m_dq), .dq_out_oe(m_oe));
endmodule
