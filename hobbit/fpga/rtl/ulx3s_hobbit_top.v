// ulx3s_hobbit_top.v -- board pins for the Hobbit SoC (fpga/README.md,
// "The SoC"; constraints fpga/ulx3s_soc.lpf).
//
// 25 MHz board clock = the system clock.  Reset: power-on (an 8-bit
// counter) or BTN1 held.  The core's clock is the system clock through an
// ECP5 DCCA whose CE (hobbit_soc's cpu_ce) changes on the falling edge.
// The SDRAM clock is the system clock forwarded by an ODDRX1F with D0 = 0,
// D1 = 1, so the part's rising edge is the system clock's falling edge;
// DQ is captured in the I/O register on the system clock's rising edge
// (both are the board practice of the Flute tree's Top.v; this file is
// written here, fpga/IP_PROVENANCE.md).
module ulx3s_hobbit_top #(
    parameter [7:0] DEV_RTL = 8'h00     // build_soc.sh: SOC_RTL
) (
    input  wire        CLK,
    input  wire        BTN1,
    output wire [7:0]  led,
    input  wire        ftdi_txd,     // from the FTDI: our receive
    output wire        ftdi_rxd,     // to the FTDI: our transmit
    output wire        wifi_en,
    output wire        sdram_clk,
    output wire        sdram_cke,
    output wire        sdram_cs_n,
    output wire        sdram_ras_n,
    output wire        sdram_cas_n,
    output wire        sdram_we_n,
    output wire [1:0]  sdram_ba,
    output wire [12:0] sdram_a,
    output wire [1:0]  sdram_dqm,
    inout  wire [15:0] sdram_dq,
    // The MCP7940N's I2C, shared with the GPDI DDC: reserved for the RTC
    // (fpga/dev/rtc.md, "The MCP7940N"), open drain, driven by mkRtc
    // when the RTC is RTL (hobbit_soc's DEV_RTL bit 2), released otherwise.
    inout  wire        gpdi_sda,
    inout  wire        gpdi_scl,
    // HDMI (GPDI): the Lcdisp frame store scanned out (fpga/dev/hdmi_lcd.md).
    output wire [3:0]  gpdi_dp,
    // The ESP32 Ethernet relay's link (docs/ulx3s_ethernet.md): GPIO16
    // (L1) FPGA -> ESP32, GPIO17 (N3) ESP32 -> FPGA, GPIO4 (H1) RTS.
    output wire        wifi_gpio0,
    output wire        wifi_gpio16,
    input  wire        wifi_gpio17,
    input  wire        wifi_gpio4
);
    wire scl_low, sda_low;
    assign gpdi_scl = scl_low ? 1'b0 : 1'bz;
    assign gpdi_sda = sda_low ? 1'b0 : 1'bz;
    // The ESP32 runs the relay when the SONIC is RTL (DEV_RTL bit 5), and
    // is held in reset otherwise; GPIO0 high keeps it out of download mode.
    assign wifi_gpio0 = 1'b1;

    // The video PLL of fpga/dev/hdmi_lcd_top.v: 325 MHz shift clock
    // (sclk), 65 MHz pixel clock (pclk), from the 25 MHz board clock.
    wire sclk, pclk, pll_locked;
    (* FREQUENCY_PIN_CLKI="25" *)
    (* FREQUENCY_PIN_CLKOP="325" *)
    (* FREQUENCY_PIN_CLKOS="65" *)
    (* ICP_CURRENT="12" *) (* LPF_RESISTOR="8" *) (* MFG_ENABLE_FILTEROPAMP="1" *) (* MFG_GMCREF_SEL="2" *)
    EHXPLLL #(
        .PLLRST_ENA("DISABLED"), .INTFB_WAKE("DISABLED"), .STDBY_ENABLE("DISABLED"),
        .DPHASE_SOURCE("DISABLED"), .OUTDIVIDER_MUXA("DIVA"), .OUTDIVIDER_MUXB("DIVB"),
        .OUTDIVIDER_MUXC("DIVC"), .OUTDIVIDER_MUXD("DIVD"),
        .CLKI_DIV(1), .CLKFB_DIV(13), .FEEDBK_PATH("CLKOP"),
        .CLKOP_ENABLE("ENABLED"), .CLKOP_DIV(2),  .CLKOP_CPHASE(1), .CLKOP_FPHASE(0),
        .CLKOS_ENABLE("ENABLED"), .CLKOS_DIV(10), .CLKOS_CPHASE(9), .CLKOS_FPHASE(0)
    ) video_pll (
        .RST(1'b0), .STDBY(1'b0), .CLKI(CLK),
        .CLKOP(sclk), .CLKOS(pclk), .CLKFB(sclk),
        .PHASESEL0(1'b0), .PHASESEL1(1'b0), .PHASEDIR(1'b1),
        .PHASESTEP(1'b1), .PHASELOADREG(1'b1), .PLLWAKESYNC(1'b0),
        .ENCLKOP(1'b0), .LOCK(pll_locked)
    );
    wire [17:0] scan_addr;
    wire [7:0]  scan_data;
    wire [9:0]  tmds_r, tmds_g, tmds_b;
    wire        ptog;
    hdmi_scan scan (
        .pclk(pclk), .rd_addr(scan_addr), .rd_data(scan_data),
        .tmds_r(tmds_r), .tmds_g(tmds_g), .tmds_b(tmds_b), .ptog(ptog),
        .dbg_grey(), .dbg_de(), .dbg_hs(), .dbg_vs());
    dvi_ser ser (.sclk(sclk), .ptog(ptog), .tmds_r(tmds_r), .tmds_g(tmds_g),
                 .tmds_b(tmds_b), .gpdi_dp(gpdi_dp));
    assign sdram_cke = 1'b1;

    reg [7:0] por = 8'd0;
    reg       rst = 1'b1;
    always @(posedge CLK) begin
        if (BTN1) por <= 8'd0;
        else if (por != 8'hFF) por <= por + 1'b1;
        rst <= (por != 8'hFF);
    end
    assign wifi_en = DEV_RTL[5] ? !rst : 1'b0;

    wire cpu_ce, gclk;
    DCCA core_clk_gate (.CLKI(CLK), .CE(cpu_ce), .CLKO(gclk));

    ODDRX1F sdram_clk_oddr (.D0(1'b0), .D1(1'b1), .SCLK(CLK), .RST(1'b0),
                            .Q(sdram_clk));

    wire [15:0] dq_out;
    wire        dq_oe;
    (* useioff = 1 *) reg [15:0] dq_iob;
    always @(posedge CLK) dq_iob <= sdram_dq;
    assign sdram_dq = dq_oe ? dq_out : 16'hzzzz;

    hobbit_soc #(.DEV_RTL(DEV_RTL)) soc (
        .clk(CLK), .rst(rst), .gclk(gclk), .cpu_ce(cpu_ce),
        .pclk(pclk), .scan_addr(scan_addr), .scan_data(scan_data),
        .esp_txd(wifi_gpio16), .esp_rxd(wifi_gpio17), .esp_rts(wifi_gpio4),
        .rxd(ftdi_txd), .txd(ftdi_rxd),
        .sd_cs_n(sdram_cs_n), .sd_ras_n(sdram_ras_n), .sd_cas_n(sdram_cas_n),
        .sd_we_n(sdram_we_n), .sd_ba(sdram_ba), .sd_a(sdram_a),
        .sd_dqm(sdram_dqm), .sd_dq_out(dq_out), .sd_dq_oe(dq_oe),
        .sd_dq_in(dq_iob),
        .i2c_scl_low(scl_low), .i2c_sda_low(sda_low),
        .i2c_scl_in(gpdi_scl), .i2c_sda_in(gpdi_sda), .dev_faults(),
        .leds(led), .retired(), .running(), .stopped(), .core_clocks(),
        .hri_valid(), .hri(),
        .arm_en(1'b0), .arm_n(32'd0), .arm_level(3'd0), .arm_rdy(),
        .took_en(1'b0), .took_rdy(), .took_pc());
endmodule
