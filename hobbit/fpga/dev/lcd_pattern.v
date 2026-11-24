// lcd_pattern.v: a test pattern written through the Lcdisp register port
// exactly as s9term's screenupdate writes the panel: for each group of four
// rows y = 4q .. 4q+3, ctl = y >> 8, ctl = (y >> 2) & 0x3f, then 768 data
// words, word x holding cell (x, y + r) in bits 2r+1..2r.  Once the whole
// panel is written it stops (done = 1).  lcd_pattern.py is the same pattern
// in Python, fed to p9term.LcdPanel by lcd_test.py.
//
// Cell level (3 white, 0 black), first rule that applies:
//   border 8 cells wide on every edge            0
//   y < 256: four vertical bars                  x / 192  (0, 1, 2, 3)
//   y >= 768: 32 x 32 checkerboard               ((x>>5) ^ (y>>5)) & 1 ? 3 : 1
//   ((x + y) & 63) < 4: diagonal stripes         0
//   otherwise                                    3
//
// The port is driven one request at a time (req when RDY_req), and every
// response is taken (EN_resp = RDY_resp) as the contract requires.

module lcd_pattern (
    input  wire        clk,
    input  wire        rst_n,
    output wire        req_en,
    input  wire        req_rdy,
    output wire [11:0] req_addr,
    output wire [31:0] req_wdata,
    output wire [3:0]  req_be,
    output wire        req_write,
    output reg         done = 0
);
    function [1:0] pcell (input [9:0] x, input [9:0] y);
        begin
            if (x < 8 || x >= 760 || y < 8 || y >= 1016)
                pcell = 2'd0;
            else if (y < 256)
                pcell = (x < 192) ? 2'd0 : (x < 384) ? 2'd1 : (x < 576) ? 2'd2 : 2'd3;
            else if (y >= 768)
                pcell = (x[5] ^ y[5]) ? 2'd3 : 2'd1;
            else if (((x + y) & 10'd63) < 4)
                pcell = 2'd0;
            else
                pcell = 2'd3;
        end
    endfunction

    reg [7:0] q = 0;        // row group
    reg [1:0] ph = 0;       // 0: ctl hi, 1: ctl lo, 2: data
    reg [9:0] x = 0;
    wire [9:0] y = { q, 2'b00 };
    wire [7:0] word = { pcell(x, y + 10'd3), pcell(x, y + 10'd2), pcell(x, y + 10'd1), pcell(x, y) };

    assign req_en    = rst_n && !done && req_rdy;
    assign req_write = 1'b1;
    assign req_be    = 4'hF;
    assign req_addr  = (ph == 2'd2) ? 12'h004 : 12'h000;
    assign req_wdata = (ph == 2'd0) ? { 30'd0, y[9:8] } :
                       (ph == 2'd1) ? { 26'd0, y[7:2] } : { 24'd0, word };

    always @(posedge clk) begin
        if (!rst_n) begin
            q <= 0; ph <= 0; x <= 0; done <= 0;
        end else if (req_en) begin
            if (ph != 2'd2)
                ph <= ph + 2'd1;
            else if (x != 10'd767)
                x <= x + 10'd1;
            else begin
                x <= 0;
                ph <= 0;
                q <= q + 8'd1;
                if (q == 8'd255) done <= 1;
            end
        end
    end
endmodule
