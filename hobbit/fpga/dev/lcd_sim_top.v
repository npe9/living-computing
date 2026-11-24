// lcd_sim_top.v: Verilator harness top for lcd_tb.cpp (not synthesized).
// The device (mkLcdisp) with its register port driven either by the bench
// (pat_sel = 0) or by the test bitstream's pattern writer lcd_pattern
// (pat_sel = 1), and its scan port read either by hdmi_scan (dump_sel = 0)
// or by the bench, to read the whole panel back through the RAM's real
// pixel-clock port (dump_sel = 1).

module lcd_sim_top (
    input  wire        CLK,         // device clock
    input  wire        CLK_pclk,    // pixel clock
    input  wire        RST_N,
    // bench register port
    input  wire        tb_en,
    input  wire [11:0] tb_addr,
    input  wire [31:0] tb_wdata,
    input  wire [3:0]  tb_be,
    input  wire        tb_write,
    output wire        req_rdy,
    output wire        resp_valid,  // a response was taken this clock
    output wire [31:0] resp,
    output wire [31:0] overruns,
    input  wire        pat_sel,
    output wire        pat_done,
    output wire        pat_req,     // lcd_pattern issues a request this clock
    // bench scan port
    input  wire        dump_sel,
    input  wire [17:0] dump_addr,
    output wire [7:0]  scan_data,
    // video
    output wire [9:0]  tmds_r,
    output wire [9:0]  tmds_g,
    output wire [9:0]  tmds_b,
    output wire [7:0]  dbg_grey,
    output wire        dbg_de,
    output wire        dbg_hs,
    output wire        dbg_vs
);
    wire        p_en, p_write;
    wire [11:0] p_addr;
    wire [31:0] p_wdata;
    wire [3:0]  p_be;
    lcd_pattern pat (.clk(CLK), .rst_n(RST_N && pat_sel), .req_en(p_en),
                     .req_rdy(req_rdy), .req_addr(p_addr), .req_wdata(p_wdata),
                     .req_be(p_be), .req_write(p_write), .done(pat_done));

    wire        en = pat_sel ? p_en : (tb_en && req_rdy);
    wire        resp_rdy;
    wire [17:0] scan_addr;
    wire        ptog;
    assign resp_valid = resp_rdy;
    assign pat_req = p_en;

    mkLcdisp lcd (
        .CLK_pclk(CLK_pclk), .CLK(CLK), .RST_N(RST_N),
        .req_addr(pat_sel ? p_addr : tb_addr),
        .req_wdata(pat_sel ? p_wdata : tb_wdata),
        .req_be(pat_sel ? p_be : tb_be),
        .req_write(pat_sel ? p_write : tb_write),
        .EN_req(en), .RDY_req(req_rdy),
        .EN_resp(resp_rdy), .resp(resp), .RDY_resp(resp_rdy),
        .overruns(overruns),
        .scan_read_a(dump_sel ? dump_addr : scan_addr), .EN_scan_read(1'b1),
        .scan_data(scan_data));

    hdmi_scan scan (
        .pclk(CLK_pclk), .rd_addr(scan_addr), .rd_data(scan_data),
        .tmds_r(tmds_r), .tmds_g(tmds_g), .tmds_b(tmds_b), .ptog(ptog),
        .dbg_grey(dbg_grey), .dbg_de(dbg_de), .dbg_hs(dbg_hs), .dbg_vs(dbg_vs));
endmodule
