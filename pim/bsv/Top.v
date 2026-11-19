module ulx3s_top(
    input  wire        CLK,
    input  wire        BTN1,
    output wire [7:0]  led,
    output wire        ftdi_rxd,
    input  wire        ftdi_txd,
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
    inout  wire [15:0] sdram_dq
);
    // Hold the Bluespec design in reset briefly after configuration.
    // BSC's generated registers need an explicit reset; FIRE1 restarts.
    reg [7:0] power_on_reset = 8'h00;
    always @(posedge CLK) begin
        if (BTN1)
            power_on_reset <= 8'h00;
        else if (!&power_on_reset)
            power_on_reset <= power_on_reset + 1'b1;
    end

    // `rst_n` is the explicit module argument that gates the start rule;
    // `RST_N` is the implicit Bluespec reset.  Both must be driven.
    wire rst_n = (&power_on_reset) & ~BTN1;

    // SDRAM clock: forward the 25 MHz board clock through an ECP5 DDR
    // output cell, as the Flute ULX3S design does.
    ODDRX1F sdram_clk_oddr (
        .D0  (1'b0),
        .D1  (1'b1),
        .SCLK(CLK),
        .RST (1'b0),
        .Q   (sdram_clk)
    );

    // Register DQ at the pad so all 16 bits sample on the same edge.
    (* useioff = 1 *) reg [15:0] sdram_dq_iob;
    always @(posedge CLK)
        sdram_dq_iob <= sdram_dq;

    wire [15:0] sdram_dq_out;
    wire        sdram_dq_oe;
    assign sdram_dq = sdram_dq_oe ? sdram_dq_out : 16'hZZZZ;

    mkPimUlx3s pim (
        .CLK(CLK),
        .RST_N(rst_n),
        .rst_n(rst_n),
        .led(led),
        .sdram_init_done(),
        .sdram_cke(sdram_cke),
        .sdram_cs_n(sdram_cs_n),
        .sdram_ras_n(sdram_ras_n),
        .sdram_cas_n(sdram_cas_n),
        .sdram_we_n(sdram_we_n),
        .sdram_ba(sdram_ba),
        .sdram_a(sdram_a),
        .sdram_dqm(sdram_dqm),
        .sdram_dq_out(sdram_dq_out),
        .sdram_dq_oe(sdram_dq_oe),
        .sdram_dq_in_v(sdram_dq_iob),
        .EN_sdram_dq_in(1'b1)
    );
    assign ftdi_rxd = 1'b1;
    assign wifi_en = 1'b0;
endmodule
