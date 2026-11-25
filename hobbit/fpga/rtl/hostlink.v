// hostlink.v -- the Hobbit SoC's framed host link on the FTDI UART
// (fpga/README.md, "The host link"; the host side is tools/p9link.py).
//
// One serial line carries three things: the loader (memory reads and
// writes and the start, step 3), the forwarding of every I/O access that
// has no RTL device yet to the Python device models on the host (step 2's
// bring-up mode), and the host's interrupt level for those models.
// Multi-byte fields are big-endian.
//
//   host -> board                         board -> host
//   'P'                  ping             'p' st1 clk5 ret4
//   'W' a4 d4            write word       'w'
//   'R' a4               read word        'r' d4
//   'B' a4 n2 d4*n       write n words    'b'
//   'G' e4               start at entry   'g'
//   'D' d4               answer to 'F'
//   'I' l1               interrupt level (7 none, else 0..6)
//                                         'F' k1 a4 d4 clk5   forwarded access,
//                                              k = 0 read, 1 write; wants 'D'
//                                         'T' clk5            every 2^TBITS core clocks
//
// st1 = {6'b0, stopped, running}; clk5 = core clocks (the core's own
// clock count, model time at the host's clock rate); ret4 = records
// retired.
module hostlink #(
    parameter CPB = 25,
    parameter TBITS = 18
) (
    input  wire        clk,
    input  wire        rst,
    input  wire        rxd,
    output wire        txd,
    // Memory (the adapter's aux master).
    output reg         mem_valid,
    output reg         mem_we,
    output reg  [31:0] mem_addr,
    output reg  [31:0] mem_wdata,
    input  wire        mem_done,
    input  wire [31:0] mem_rdata,
    // Start.
    output reg         go_valid,
    output reg  [31:0] go_entry,
    input  wire        go_taken,
    // Forwarded I/O: a request is held until fwd_done.
    input  wire        fwd_valid,
    input  wire        fwd_we,
    input  wire [31:0] fwd_addr,
    input  wire [31:0] fwd_wdata,
    output reg         fwd_done,
    output reg  [31:0] fwd_rdata,
    output reg  [2:0]  host_il,
    // Status.
    input  wire        running,
    input  wire        stopped,
    input  wire [39:0] core_clocks,
    input  wire [31:0] retired
);
    wire [7:0] rx_b; wire rx_v; wire rx_ferr;
    uart_rx #(.CPB(CPB)) urx (.clk(clk), .rst(rst), .rxd(rxd),
                              .valid(rx_v), .data(rx_b), .ferr(rx_ferr));
    reg  [7:0] tx_b; reg tx_v; wire tx_rdy;
    uart_tx #(.CPB(CPB)) utx (.clk(clk), .rst(rst), .valid(tx_v), .data(tx_b),
                              .ready(tx_rdy), .txd(txd));

    // ---- transmit: one frame at a time from a 15-byte register --------
    reg [119:0] fr;            // byte 0 in bits 119:112
    reg [3:0]   fr_n;          // bytes left
    reg         reply_req;     // a reply frame is waiting in rp
    reg [119:0] rp;
    reg [3:0]   rp_n;
    reg         fwd_sent;      // 'F' for the current request is out
    reg [39:0]  t_next;
    always @(posedge clk) begin
        tx_v <= 1'b0;
        if (rst) begin
            fr_n <= 0; fwd_sent <= 1'b0; t_next <= (40'd1 << TBITS);
        end else begin
            if (!fwd_valid) fwd_sent <= 1'b0;
            if (fr_n != 0) begin
                if (tx_rdy && !tx_v) begin
                    tx_b <= fr[119:112]; tx_v <= 1'b1;
                    fr <= {fr[111:0], 8'h00}; fr_n <= fr_n - 1;
                end
            end else if (reply_req) begin
                fr <= rp; fr_n <= rp_n;
            end else if (fwd_valid && !fwd_sent) begin
                fr <= {8'h46, 7'd0, fwd_we, fwd_addr, fwd_wdata, core_clocks};
                fr_n <= 15; fwd_sent <= 1'b1;
            end else if (core_clocks >= t_next) begin
                fr <= {8'h54, core_clocks, 72'd0};
                fr_n <= 6; t_next <= t_next + (40'd1 << TBITS);
            end
        end
    end

    // ---- receive ------------------------------------------------------
    reg [7:0]  cmd;
    reg [3:0]  need;           // bytes still to collect for the field
    reg [63:0] acc;
    reg [15:0] bn;             // 'B': words left
    reg [2:0]  ph;             // 0 command, 1 field, 2 'B' data, 3 wait memory
    always @(posedge clk) begin
        if (rst) begin
            ph <= 0; reply_req <= 1'b0; mem_valid <= 1'b0; go_valid <= 1'b0;
            fwd_done <= 1'b0; host_il <= 3'd7;
        end else begin
            fwd_done <= 1'b0;
            if (reply_req && fr_n == 0)
                reply_req <= 1'b0;             // taken by the transmitter this clock
            if (go_valid && go_taken) begin
                go_valid <= 1'b0;
            end
            case (ph)
            0: if (rx_v) begin
                cmd <= rx_b; acc <= 0;
                case (rx_b)
                "P": begin
                    rp <= {8'h70, 6'd0, stopped, running, core_clocks, retired, 32'd0};
                    rp_n <= 11; reply_req <= 1'b1;
                end
                "W": begin need <= 8; ph <= 1; end
                "R": begin need <= 4; ph <= 1; end
                "B": begin need <= 6; ph <= 1; end
                "G": begin need <= 4; ph <= 1; end
                "D": begin need <= 4; ph <= 1; end
                "I": begin need <= 1; ph <= 1; end
                default: ;
                endcase
            end
            1: if (rx_v) begin
                acc <= {acc[55:0], rx_b};
                if (need == 1) begin
                    ph <= 0;
                    case (cmd)
                    "W": begin
                        mem_valid <= 1'b1; mem_we <= 1'b1;
                        mem_addr <= acc[55:24]; mem_wdata <= {acc[23:0], rx_b};
                        ph <= 3;
                    end
                    "R": begin
                        mem_valid <= 1'b1; mem_we <= 1'b0;
                        mem_addr <= {acc[23:0], rx_b}; ph <= 3;
                    end
                    "B": begin
                        mem_addr <= acc[39:8]; bn <= {acc[7:0], rx_b};
                        need <= 4; ph <= ({acc[7:0], rx_b} == 16'd0) ? 4 : 2;
                    end
                    "G": begin
                        go_valid <= 1'b1; go_entry <= {acc[23:0], rx_b};
                        rp <= {8'h67, 112'd0}; rp_n <= 1; reply_req <= 1'b1;
                    end
                    "D": begin
                        fwd_rdata <= {acc[23:0], rx_b};
                        fwd_done <= fwd_valid;
                    end
                    "I": host_il <= rx_b[2:0];
                    default: ;
                    endcase
                end else need <= need - 1;
            end
            2: if (rx_v) begin                // 'B' word bytes
                acc <= {acc[55:0], rx_b};
                if (need == 1) begin
                    mem_valid <= 1'b1; mem_we <= 1'b1;
                    mem_wdata <= {acc[23:0], rx_b};
                    ph <= 3;
                end else need <= need - 1;
            end
            3: if (mem_done) begin
                mem_valid <= 1'b0;
                if (cmd == "B") begin
                    mem_addr <= mem_addr + 4; need <= 4;
                    bn <= bn - 1;
                    ph <= (bn == 1) ? 4 : 2;
                end else begin
                    ph <= 0;
                    if (cmd == "W") begin rp <= {8'h77, 112'd0}; rp_n <= 1; end
                    else begin rp <= {8'h72, mem_rdata, 80'd0}; rp_n <= 5; end
                    reply_req <= 1'b1;
                end
            end
            4: begin
                rp <= {8'h62, 112'd0}; rp_n <= 1; reply_req <= 1'b1; ph <= 0;
            end
            default: ph <= 0;
            endcase
        end
    end
endmodule
