// hdmi_scan.v: scan-out of the Lcdisp panel (LcdLcdisp.bsv) as 1024x768@60
// DVI on the ULX3S GPDI port, the portrait panel turned a quarter turn.
//
// Mode: VESA DMT 1024x768 at 60 Hz, 65.000 MHz pixel clock, 1344 x 806 total
// (h: 1024 active, 24 front porch, 136 sync, 160 back porch; v: 768, 3, 6,
// 29), both syncs active low; 65e6 / (1344 * 806) = 60.004 Hz.  The TMDS
// bit rate is 650 Mb/s a lane, so the serializer (hdmi_tmds.v dvi_ser, two
// bits a clock through ODDRX1F) runs at 325 MHz.  See hdmi_lcd.md for why
// this mode and not the panel letterboxed in 1280x1024.
//
// Rotation: display pixel (X, Y), 0 <= X < 1024, 0 <= Y < 768, shows panel
// cell (x, y) = (767 - Y, X).  The panel's top row is the display's left
// column and its left column the display's bottom row, so a monitor pivoted
// a quarter turn clockwise (its left edge up) shows the panel upright.  In
// the panel RAM (one byte per (quad, col): cell (x, y) is bits
// 2(y&3)+1..2(y&3) of byte (y>>2)*768 + x) a display line walks y, so one
// byte gives four consecutive display pixels.
//
// Shade: s9term's getcolor (0x80026aa0) maps bitmap pixel 0 to white and the
// kernel sends ~pixel to the panel, so panel level 3 is white and 0 black;
// levels 1 and 2 are drawn as greys, grey = 85 * level, as p9term.LcdPanel
// .grey() and p9boot's dumps draw them (TERM_CHOICES 'lcd', 'framebuffer').
// Cells never written are level 0, black, as in the model.
//
// Pipeline (all on pclk):  stage 0 the counters hc, vc, and the RAM address
// (combinational from them) into the RAM;  the RAM's own register and its
// output register (BRAMCore hasOutputRegister) are stages 1 and 2, so the
// byte for stage 0's pixel is on rd_data in stage 2;  stage 3 the grey and
// the syncs;  stage 4 the TMDS words (tmds_enc's register).  de/hs/vs and
// the cell index ride the same pipeline.

module hdmi_scan #(
    parameter H_ACT = 1024, H_FP = 24, H_SYNC = 136, H_BP = 160,
    parameter V_ACT = 768,  V_FP = 3,  V_SYNC = 6,   V_BP = 29
) (
    input  wire        pclk,
    output wire [17:0] rd_addr,     // to LcdScan.read, every pixel clock
    input  wire [7:0]  rd_data,     // LcdScan.data, two pixel clocks later
    output wire [9:0]  tmds_r,
    output wire [9:0]  tmds_g,
    output wire [9:0]  tmds_b,
    output reg         ptog = 0,    // pixel-clock toggle for dvi_ser
    // stage-3 taps (the encoder's inputs), for benches
    output reg  [7:0]  dbg_grey = 0,
    output reg         dbg_de = 0,
    output reg         dbg_hs = 1,
    output reg         dbg_vs = 1
);
    localparam H_TOT = H_ACT + H_FP + H_SYNC + H_BP;
    localparam V_TOT = V_ACT + V_FP + V_SYNC + V_BP;

    reg [10:0] hc = 0;
    reg [9:0]  vc = 0;
    always @(posedge pclk) begin
        ptog <= ~ptog;
        if (hc == H_TOT - 1) begin
            hc <= 0;
            vc <= (vc == V_TOT - 1) ? 10'd0 : vc + 10'd1;
        end else
            hc <= hc + 11'd1;
    end

    // stage 0: panel x = 767 - Y, quad = X >> 2; byte = quad * 768 + x
    wire [7:0]  quad = hc[9:2];
    wire [9:0]  px   = 10'd767 - vc;
    assign rd_addr = ({ 10'd0, quad } << 9) + ({ 10'd0, quad } << 8) + { 8'd0, px };

    wire de0 = (hc < H_ACT) && (vc < V_ACT);
    wire hs0 = !((hc >= H_ACT + H_FP) && (hc < H_ACT + H_FP + H_SYNC));
    wire vs0 = !((vc >= V_ACT + V_FP) && (vc < V_ACT + V_FP + V_SYNC));

    // stages 1, 2: wait for the RAM
    reg [1:0] r1 = 0, r2 = 0;
    reg       de1 = 0, de2 = 0, hs1 = 1, hs2 = 1, vs1 = 1, vs2 = 1;
    always @(posedge pclk) begin
        r1 <= hc[1:0];  r2 <= r1;
        de1 <= de0;     de2 <= de1;
        hs1 <= hs0;     hs2 <= hs1;
        vs1 <= vs0;     vs2 <= vs1;
    end

    // stage 3: the cell (row r of the byte's four) and its grey
    wire [1:0] level = rd_data[2 * r2 +: 2];
    always @(posedge pclk) begin
        dbg_grey <= de2 ? { level, level, level, level } : 8'd0;   // 85 * level
        dbg_de   <= de2;
        dbg_hs   <= hs2;
        dbg_vs   <= vs2;
    end

    // stage 4: TMDS (blue carries the syncs: C0 = HSYNC, C1 = VSYNC)
    tmds_enc enc_b (.clk(pclk), .de(dbg_de), .ctrl({ dbg_vs, dbg_hs }), .d(dbg_grey), .q(tmds_b));
    tmds_enc enc_g (.clk(pclk), .de(dbg_de), .ctrl(2'b00),              .d(dbg_grey), .q(tmds_g));
    tmds_enc enc_r (.clk(pclk), .de(dbg_de), .ctrl(2'b00),              .d(dbg_grey), .q(tmds_r));
endmodule
