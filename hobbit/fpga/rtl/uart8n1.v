// uart8n1.v -- 8N1 UART transmitter and receiver for the Hobbit SoC's
// host link on the ULX3S FTDI port (fpga/README.md, "The host link").
// Written here; the receiver samples mid-bit, as the Flute tree's
// mkUART_Pins does (a design choice, not its code).
//
// CPB is clocks per bit (25 MHz / 115200 = 217; the default host link
// runs at 25 MHz / 1,000,000 = 25, which the FT231X supports).

module uart_tx #(parameter CPB = 25) (
    input  wire       clk,
    input  wire       rst,
    input  wire       valid,
    input  wire [7:0] data,
    output wire       ready,
    output reg        txd
);
    reg [9:0]  sh;
    reg [3:0]  n;
    reg [15:0] c;
    assign ready = (n == 0);
    always @(posedge clk) begin
        if (rst) begin
            txd <= 1'b1; n <= 0; c <= 0; sh <= 10'h3FF;
        end else if (n == 0) begin
            txd <= 1'b1;
            if (valid) begin
                sh <= {1'b1, data, 1'b0};
                n <= 10; c <= CPB - 1;
                txd <= 1'b0;
            end
        end else if (c != 0) begin
            c <= c - 1;
        end else begin
            sh <= {1'b1, sh[9:1]};
            txd <= sh[1];
            c <= CPB - 1;
            n <= n - 1;
            if (n == 1) txd <= 1'b1;
        end
    end
endmodule

module uart_rx #(parameter CPB = 25) (
    input  wire       clk,
    input  wire       rst,
    input  wire       rxd,
    output reg        valid,      // one clock per byte
    output reg  [7:0] data,
    output reg        ferr        // one clock: a stop bit read low
);
    reg [1:0]  sync;
    reg [3:0]  n;                 // 0 idle; 1 start; 2..9 data; 10 stop
    reg [15:0] c;
    reg [7:0]  sh;
    wire       r = sync[1];
    always @(posedge clk) begin
        sync <= {sync[0], rxd};
        valid <= 1'b0;
        ferr <= 1'b0;
        if (rst) begin
            n <= 0; sync <= 2'b11; c <= 0;
        end else if (n == 0) begin
            if (!r) begin n <= 1; c <= CPB / 2; end
        end else if (c != 0) begin
            c <= c - 1;
        end else begin
            c <= CPB - 1;
            if (n == 1) begin
                if (r) n <= 0;            // a glitch, not a start bit
                else n <= 2;
            end else if (n <= 9) begin
                sh <= {r, sh[7:1]};
                n <= n + 1;
            end else begin
                if (r) begin valid <= 1'b1; data <= sh; end
                else ferr <= 1'b1;
                n <= 0;
            end
        end
    end
endmodule
