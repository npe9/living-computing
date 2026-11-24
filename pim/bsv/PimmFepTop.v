// PimmFepTop.v -- ULX3S board top for the FEP emulator self-test
// (PimmFepUlx3s.bsv, mkPimmFepUlx3s).  ALL OURS; the reset is Top.v's.
// Pins: ulx3s_fep.lpf.  The microSD slot is used in SPI mode: sd_d3 is
// chip select, sd_cmd is MOSI, sd_d0 is MISO, sd_clk the clock; sd_d1
// and sd_d2 are inputs, never driven.  Nothing here drives a card data
// line, and the design has no write command.  wifi_en is held low so the
// ESP32, which shares the SD pins (and sd_d0 is its GPIO2 strap), stays
// in reset.
module ulx3s_fep_top(
    input  wire       CLK,
    input  wire       BTN1,
    output wire [7:0] led,
    output wire       ftdi_rxd,     // the FPGA transmits on it
    input  wire       ftdi_txd,     // not used
    output wire       wifi_en,
    output wire       sd_clk,
    output wire       sd_cmd,
    input  wire       sd_d0,
    input  wire       sd_d1,        // not used
    input  wire       sd_d2,        // not used
    output wire       sd_d3
);
    // Hold the Bluespec design in reset briefly after configuration, as
    // Top.v does; FIRE1 restarts (and so reinitializes the card).
    reg [7:0] power_on_reset = 8'h00;
    always @(posedge CLK) begin
        if (BTN1)
            power_on_reset <= 8'h00;
        else if (!&power_on_reset)
            power_on_reset <= power_on_reset + 1'b1;
    end
    wire rst_n = (&power_on_reset) & ~BTN1;

    // MISO through a pad register
    (* useioff = 1 *) reg sd_d0_iob = 1'b1;
    always @(posedge CLK)
        sd_d0_iob <= sd_d0;

    mkPimmFepUlx3s fep (
        .CLK(CLK),
        .RST_N(rst_n),
        .led(led),
        .uart_tx(ftdi_rxd),
        .sd_clk(sd_clk),
        .sd_cs_n(sd_d3),
        .sd_mosi(sd_cmd),
        .sd_miso_v(sd_d0_iob)
    );
    assign wifi_en = 1'b0;
endmodule
