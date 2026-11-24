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
module ulx3s_hobbit_top (
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
    // (fpga/dev/rtc.md, "The MCP7940N").  Released (open drain, not
    // driven) until mkRtc's i2cPins are wired here.
    inout  wire        gpdi_sda,
    inout  wire        gpdi_scl
);
    assign gpdi_sda = 1'bz;
    assign gpdi_scl = 1'bz;
    assign wifi_en = 1'b0;           // the ESP32 stays in reset
    assign sdram_cke = 1'b1;

    reg [7:0] por = 8'd0;
    reg       rst = 1'b1;
    always @(posedge CLK) begin
        if (BTN1) por <= 8'd0;
        else if (por != 8'hFF) por <= por + 1'b1;
        rst <= (por != 8'hFF);
    end

    wire cpu_ce, gclk;
    DCCA core_clk_gate (.CLKI(CLK), .CE(cpu_ce), .CLKO(gclk));

    ODDRX1F sdram_clk_oddr (.D0(1'b0), .D1(1'b1), .SCLK(CLK), .RST(1'b0),
                            .Q(sdram_clk));

    wire [15:0] dq_out;
    wire        dq_oe;
    (* useioff = 1 *) reg [15:0] dq_iob;
    always @(posedge CLK) dq_iob <= sdram_dq;
    assign sdram_dq = dq_oe ? dq_out : 16'hzzzz;

    hobbit_soc soc (
        .clk(CLK), .rst(rst), .gclk(gclk), .cpu_ce(cpu_ce),
        .rxd(ftdi_txd), .txd(ftdi_rxd),
        .sd_cs_n(sdram_cs_n), .sd_ras_n(sdram_ras_n), .sd_cas_n(sdram_cas_n),
        .sd_we_n(sdram_we_n), .sd_ba(sdram_ba), .sd_a(sdram_a),
        .sd_dqm(sdram_dqm), .sd_dq_out(dq_out), .sd_dq_oe(dq_oe),
        .sd_dq_in(dq_iob),
        .leds(led), .retired(), .running(), .stopped(), .core_clocks(),
        .hri_valid(), .hri(),
        .arm_en(1'b0), .arm_n(32'd0), .arm_level(3'd0), .arm_rdy(),
        .took_en(1'b0), .took_rdy(), .took_pc());
endmodule
