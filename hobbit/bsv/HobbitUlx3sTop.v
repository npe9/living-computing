// HobbitUlx3sTop.v -- ULX3S pin wrapper for the ATT92010 Hobbit board top.
//
// board boundary follows Flute (Bluespec, Inc., Apache-2.0) — see docs/bluespec_architecture.md
//
// Mirrors pim/bsv/Top.v: the Bluespec module mkHobbitUlx3s is synthesized
// and this wrapper maps the board pins and generates the power-on reset
// from the active-high reset button BTN1 (pin R1).
//
// BTN1 is active high: pressing it holds the design in reset and restarts
// the power-on counter.  When BTN1 is released, an 8-bit counter fills
// with ones (256 clocks at 25 MHz = 10.24 us) and only then does RST_N
// rise.  RST_N is bsc's implicit reset; rst_n is the explicit argument of
// mkHobbitUlx3s that gates its start rule.  Both must be driven.
//
// ftdi_rxd is the FPGA's UART output and is driven by the board top's
// HRI writer (idle high comes from the UART transmitter's reset state).
// ftdi_txd (the board's UART input) and wifi_en are constrained but not
// otherwise used: wifi_en is tied low to keep the WiFi module powered down.

module ulx3s_top(
    input  wire       CLK,
    input  wire       BTN1,
    output wire [7:0] led,
    output wire       ftdi_rxd,
    input  wire       ftdi_txd,
    output wire       wifi_en
);
    reg [7:0] power_on_reset = 8'h00;
    always @(posedge CLK) begin
        if (BTN1)
            power_on_reset <= 8'h00;
        else if (!&power_on_reset)
            power_on_reset <= power_on_reset + 1'b1;
    end

    wire rst_n = (&power_on_reset) & ~BTN1;

    // ftdi_txd is an input on this board; keep it referenced so no tool
    // warns about an unused port.
    wire unused_uart_in = ftdi_txd;

    wire led_rdy;
    wire txd_rdy;

    mkHobbitUlx3s hobbit (
        .CLK       (CLK),
        .RST_N     (rst_n),
        .rst_n     (rst_n),
        .led       (led),
        .RDY_led   (led_rdy),
        .txd       (ftdi_rxd),
        .RDY_txd   (txd_rdy)
    );

    assign wifi_en = 1'b0;
endmodule
