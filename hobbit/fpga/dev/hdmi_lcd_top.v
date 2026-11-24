// hdmi_lcd_top.v: standalone ULX3S test bitstream for ulx3s_plan.md step 4.
// lcd_pattern writes a test pattern through mkLcdisp's register port (the
// same port the SoC will drive) on the 25 MHz board clock; hdmi_scan reads
// the panel RAM on the 65 MHz pixel clock and dvi_ser sends it out of GPDI
// at 325 MHz (DDR, 650 Mb/s a lane) as 1024x768@60 DVI.  hdmi_lcd.lpf has
// the pins; hdmi_lcd_build.sh builds it.  LEDs: [0] pattern done, [1] PLL
// locked, [2] a 1 Hz-ish blink from the pixel clock (vc wraps 60 times a
// second: bit 5 of a frame counter), [7:3] 0.

module hdmi_lcd_top (
    input  wire       clk_25mhz,
    output wire [7:0] led,
    output wire [3:0] gpdi_dp,
    output wire       wifi_gpio0
);
    assign wifi_gpio0 = 1'b1;       // keep the ESP32 from resetting the board

    // ---- clocks, as `ecppll -i 25 -o 325` computes them: CLKI_DIV 1,
    // CLKFB_DIV 13 with the feedback from CLKOP, so CLKOP = 25 * 13 = 325 MHz
    // (the shift clock), VCO = 325 * CLKOP_DIV 2 = 650 MHz (in the
    // 400..800 MHz range), and CLKOS = 650 / 10 = 65 MHz (the pixel clock).
    // CPHASE is counted in VCO periods (1.54 ns): CLKOP's 1 and CLKOS's 9
    // are DIV - 1 each, ecppll's 0-degree setting, and differ by 8 VCO
    // periods = 4 shift-clock periods, so every pixel-clock edge is on a
    // shift-clock edge.  (The source design's 2 and 12, for dividers 5 and
    // 25, differ by 10 = 2 of its shift-clock periods.)  dvi_ser finds the
    // pixel phase from ptog itself; the alignment only sets the margin of
    // the pclk -> sclk path, which nextpnr times (hdmi_lcd.md).
    wire sclk, pclk, locked;
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
        .RST(1'b0), .STDBY(1'b0), .CLKI(clk_25mhz),
        .CLKOP(sclk), .CLKOS(pclk), .CLKFB(sclk),
        .PHASESEL0(1'b0), .PHASESEL1(1'b0), .PHASEDIR(1'b1),
        .PHASESTEP(1'b1), .PHASELOADREG(1'b1), .PLLWAKESYNC(1'b0),
        .ENCLKOP(1'b0), .LOCK(locked)
    );

    // ---- power-on reset on the board clock
    reg [7:0] por = 0;
    always @(posedge clk_25mhz) if (!por[7]) por <= por + 8'd1;
    wire rst_n = por[7];

    // ---- the device and its writer
    wire        req_en, req_rdy, req_write, resp_rdy;
    wire [11:0] req_addr;
    wire [31:0] req_wdata, resp, overruns;
    wire [3:0]  req_be;
    wire [17:0] rd_addr;
    wire [7:0]  rd_data;
    wire        done;

    lcd_pattern pat (
        .clk(clk_25mhz), .rst_n(rst_n),
        .req_en(req_en), .req_rdy(req_rdy), .req_addr(req_addr),
        .req_wdata(req_wdata), .req_be(req_be), .req_write(req_write),
        .done(done));

    mkLcdisp lcd (
        .CLK_pclk(pclk), .CLK(clk_25mhz), .RST_N(rst_n),
        .req_addr(req_addr), .req_wdata(req_wdata), .req_be(req_be),
        .req_write(req_write), .EN_req(req_en), .RDY_req(req_rdy),
        .EN_resp(resp_rdy), .resp(resp), .RDY_resp(resp_rdy),
        .overruns(overruns),
        .scan_read_a(rd_addr), .EN_scan_read(1'b1), .scan_data(rd_data));

    // ---- scan-out and serializer
    wire [9:0] tmds_r, tmds_g, tmds_b;
    wire       ptog, de, hs, vs;
    wire [7:0] grey;
    hdmi_scan scan (
        .pclk(pclk), .rd_addr(rd_addr), .rd_data(rd_data),
        .tmds_r(tmds_r), .tmds_g(tmds_g), .tmds_b(tmds_b), .ptog(ptog),
        .dbg_grey(grey), .dbg_de(de), .dbg_hs(hs), .dbg_vs(vs));

    dvi_ser ser (.sclk(sclk), .ptog(ptog), .tmds_r(tmds_r), .tmds_g(tmds_g),
                 .tmds_b(tmds_b), .gpdi_dp(gpdi_dp));

    // ---- LEDs
    reg       vs_d = 1;
    reg [5:0] frames = 0;
    always @(posedge pclk) begin
        vs_d <= vs;
        if (vs_d && !vs) frames <= frames + 6'd1;
    end
    assign led = { 5'd0, frames[5], locked, done };
endmodule
