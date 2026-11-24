// hdmi_tmds.v: TMDS encoder and 10:1 DVI serializer for the ULX3S GPDI port.
//
// COPIED VERBATIM (lines 380-481: modules tmds_enc and dvi_ser, no edits) from
//   ~/src/ulx3s-experiments/flute-lx50/src/Video_DVI.v
//   repository github.com/npe9/flute-ulx3s, branch lx50, commit
//   8aaf3603f9716c39ac607f3531f180f2e02b3d74
//   sha256 of the whole source file
//   88ad876db6ecf37e124ddc3cabace67345dfc47fe89ea8aae2a6888ff82d5b0c
// The source file carries no licence header; it is the repository owner's own
// code (not Bluespec's Flute, whose Apache-2.0 LICENSE covers Flute/ in that
// tree).  See hobbit/fpga/IP_PROVENANCE.md.
//
// Used here at 1024x768@60: pclk 65 MHz, sclk 325 MHz (5x, two bits a shift
// clock through ODDRX1F).  The comments below are the source's and speak of
// its 640x480 build (25/125 MHz).

// ----------------------------------------------------------------
// TMDS encoder (DVI 1.0 section 3.2.3), one registered output word per pixel clock.

module tmds_enc (
    input  wire       clk,
    input  wire       de,
    input  wire [1:0] ctrl,     // { C1, C0 }
    input  wire [7:0] d,
    output reg  [9:0] q
);
    function [3:0] ones8 (input [7:0] x);
        integer k;
        begin
            ones8 = 0;
            for (k = 0; k < 8; k = k + 1) ones8 = ones8 + x[k];
        end
    endfunction

    wire [3:0] n1d = ones8(d);
    wire       xn  = (n1d > 4) || (n1d == 4 && !d[0]);
    // transition-minimizing stage, as a function: a per-bit assign chain on one vector reads
    // as circular logic to the simulator (UNOPTFLAT)
    function [8:0] tmds_qm (input [7:0] x, input use_xnor);
        integer k;
        begin
            tmds_qm[0] = x[0];
            for (k = 1; k < 8; k = k + 1)
                tmds_qm[k] = use_xnor ? ~(tmds_qm[k-1] ^ x[k]) : (tmds_qm[k-1] ^ x[k]);
            tmds_qm[8] = ~use_xnor;
        end
    endfunction
    wire [8:0] qm = tmds_qm(d, xn);

    wire [3:0]        n1q  = ones8(qm[7:0]);
    wire signed [4:0] diff = $signed({ 1'b0, n1q }) - $signed(5'd4);   // (n1 - n0) / 2
    reg  signed [4:0] cnt = 0;                                          // disparity / 2

    always @(posedge clk) begin
        if (!de) begin
            cnt <= 0;
            case (ctrl)
                2'b00: q <= 10'b1101010100;
                2'b01: q <= 10'b0010101011;
                2'b10: q <= 10'b0101010100;
                default: q <= 10'b1010101011;
            endcase
        end else if (cnt == 0 || diff == 0) begin
            q   <= { ~qm[8], qm[8], qm[8] ? qm[7:0] : ~qm[7:0] };
            cnt <= qm[8] ? cnt + diff : cnt - diff;
        end else if ((cnt > 0 && diff > 0) || (cnt < 0 && diff < 0)) begin
            q   <= { 1'b1, qm[8], ~qm[7:0] };
            cnt <= cnt + $signed({ 4'b0, qm[8] }) - diff;
        end else begin
            q   <= { 1'b0, qm[8], qm[7:0] };
            cnt <= cnt - $signed({ 4'b0, ~qm[8] }) + diff;
        end
    end
endmodule

// ----------------------------------------------------------------
// DVI serializer: 10:1 at 5x the pixel clock through ODDRX1F (2 bits per shift clock).
// The shift-clock domain finds the pixel-clock phase from ptog (a pixel-domain toggle) and
// loads the words two shift clocks after it sees the toggle, so the words have been stable
// for over two shift clocks and stay stable for one more.

module dvi_ser (
    input  wire       sclk,         // 5x pixel clock (125 MHz), same PLL as the pixel clock
    input  wire       ptog,
    input  wire [9:0] tmds_r,
    input  wire [9:0] tmds_g,
    input  wire [9:0] tmds_b,
    output wire [3:0] gpdi_dp       // [0] blue, [1] green, [2] red, [3] clock
);
    // One load flag per lane, set a shift clock early from ph's next value: each lane's load
    // select is then a local flop.  One shared (ph == 1) decode fanned out to the four lanes'
    // shift registers across the die (x 23..117) and routed at 122 MHz (lx49 seeds 3 and 7).
    // keep: yosys would otherwise merge the four equal flops back into one.
    // Equal to the shared-decode version cycle for cycle (formal/dvi_ser/equiv.ys).
    reg       t1 = 0, t2 = 0;
    reg [2:0] ph = 0;
    (* keep *) reg ld_r = 0;
    (* keep *) reg ld_g = 0;
    (* keep *) reg ld_b = 0;
    (* keep *) reg ld_c = 0;
    reg [9:0] sr = 0, sg = 0, sb = 0, sc = 0;
    wire [2:0] ph_n = (t1 != t2) ? 3'd0 : ph + 3'd1;
    always @(posedge sclk) begin
        t1 <= ptog;
        t2 <= t1;
        ph <= ph_n;
        ld_r <= (ph_n == 3'd1); ld_g <= (ph_n == 3'd1);
        ld_b <= (ph_n == 3'd1); ld_c <= (ph_n == 3'd1);
        sr <= ld_r ? tmds_r : sr >> 2;
        sg <= ld_g ? tmds_g : sg >> 2;
        sb <= ld_b ? tmds_b : sb >> 2;
        sc <= ld_c ? 10'b0000011111 : sc >> 2;
    end
    ODDRX1F ddr_b (.D0(sb[0]), .D1(sb[1]), .SCLK(sclk), .RST(1'b0), .Q(gpdi_dp[0]));
    ODDRX1F ddr_g (.D0(sg[0]), .D1(sg[1]), .SCLK(sclk), .RST(1'b0), .Q(gpdi_dp[1]));
    ODDRX1F ddr_r (.D0(sr[0]), .D1(sr[1]), .SCLK(sclk), .RST(1'b0), .Q(gpdi_dp[2]));
    ODDRX1F ddr_c (.D0(sc[0]), .D1(sc[1]), .SCLK(sclk), .RST(1'b0), .Q(gpdi_dp[3]));
endmodule
