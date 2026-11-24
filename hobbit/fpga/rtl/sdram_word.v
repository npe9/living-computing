// sdram_word.v -- one-word-at-a-time controller for the ULX3S SDRAM
// (Winbond W9825G6KH-6: 4 banks x 8192 rows x 512 columns x 16 bits, 32 MB).
//
// Written for the Hobbit SoC (fpga/README.md, "The SoC").  It is not a
// copy of the Flute tree's mkSdram_Controller (no licence is stated in
// that tree, fpga/IP_PROVENANCE.md); it follows that design's board
// facts, which are the board's, not the code's: the SDRAM clock is the
// system clock forwarded through an ODDRX1F with D0 = 0, D1 = 1 (so the
// part samples on the system clock's falling edge), DQ is captured in
// the I/O register on the system clock's rising edge, CL 2, eight
// AUTO REFRESH at power-up, and a refresh that falls due during an
// access is held, never dropped.
//
// One request is one 32-bit word, two 16-bit beats (BL 2, sequential),
// with its own ACTIVE and an auto-precharge READ or WRITE, so every bank
// is closed between requests and a refresh can go in at any request
// boundary.  Slow, simple, and enough for a core that waits for memory
// anyway (the core's clock is gated, fpga/README.md).
//
// Address: word w = addr[24:2]; column = {w[7:0], beat}, bank = w[9:8],
// row = w[22:10].  Beat 0 is the low halfword (bits 15:0); byte enable
// be[i] enables byte i (bits 8i+7:8i), DQM is its inverse.
//
// Timing in system clocks (parameters; the defaults are 25 MHz):
//   ACTIVE -> READ/WRITE 1 clock (tRCD 18 ns), CL 2, one access every
//   T_ACC clocks at most (covers tRAS 42 ns + tRP 18 ns, tRC 60 ns,
//   tWR 2 clocks), tRFC T_RFC, refresh every T_REFI (<= 7.8 us),
//   power-up wait T_PWR (>= 200 us).
module sdram_word #(
    parameter T_PWR  = 5000,     // 200 us at 25 MHz
    parameter T_REFI = 180,      // 7.2 us at 25 MHz (tREFI 7.8 us)
    parameter T_RFC  = 3,        // 120 ns at 25 MHz (>= 66 ns)
    parameter T_ACC  = 6         // clocks from ACTIVE to the next ACTIVE
) (
    input  wire        clk,
    input  wire        rst,            // synchronous, active high

    input  wire        req_valid,
    output wire        req_ready,
    input  wire        req_we,
    input  wire [24:2] req_addr,
    input  wire [31:0] req_wdata,
    input  wire [3:0]  req_be,
    output reg         rsp_valid,      // one clock: read data, or write done
    output reg  [31:0] rsp_rdata,
    output reg         init_done,

    // Pins (registered).  dq_in is the I/O-register capture of DQ.
    output reg         sd_cs_n,
    output reg         sd_ras_n,
    output reg         sd_cas_n,
    output reg         sd_we_n,
    output reg  [1:0]  sd_ba,
    output reg  [12:0] sd_a,
    output reg  [1:0]  sd_dqm,
    output reg  [15:0] sd_dq_out,
    output reg         sd_dq_oe,
    input  wire [15:0] sd_dq_in
);
    // {cs_n, ras_n, cas_n, we_n}
    localparam CMD_NOP = 4'b0111, CMD_ACT = 4'b0011, CMD_RD = 4'b0101,
               CMD_WR = 4'b0100, CMD_PRE = 4'b0010, CMD_REF = 4'b0001,
               CMD_MRS = 4'b0000;
    // Mode register: burst length 2, sequential, CL 2, burst writes.
    localparam [12:0] MODE = 13'b000_0_00_010_0_001;

    localparam S_PWR = 0, S_PRE = 1, S_IREF = 2, S_MRS = 3, S_IDLE = 4,
               S_RW = 5, S_WB1 = 6, S_DONE = 7, S_WAIT = 8;

    reg [3:0]  st;
    reg [15:0] cnt;          // general wait
    reg [3:0]  nref;         // init refreshes left
    reg [15:0] refc;         // clocks to the next refresh
    reg        ref_due;
    reg        we_l;
    reg [24:2] addr_l;
    reg [31:0] wdata_l;
    reg [3:0]  be_l;
    reg [4:0]  rd_pipe;      // READ at clock r: bit 3 at r+4 (beat 0), bit 4 at r+5
    reg        rd_got;
    reg [15:0] lo;

    assign req_ready = (st == S_IDLE) && !ref_due && init_done;

    always @(posedge clk) begin
        rsp_valid <= 1'b0;
        {sd_cs_n, sd_ras_n, sd_cas_n, sd_we_n} <= CMD_NOP;
        if (rst) begin
            st <= S_PWR; cnt <= T_PWR; init_done <= 1'b0;
            sd_dqm <= 2'b11; sd_dq_oe <= 1'b0; sd_ba <= 0; sd_a <= 0;
            sd_dq_out <= 0;
            refc <= T_REFI; ref_due <= 1'b0; rd_pipe <= 0; nref <= 0;
            rd_got <= 1'b0;
        end else begin
            // Refresh timer: expiry holds `ref_due` until IDLE serves it.
            if (refc != 0) refc <= refc - 1;
            else ref_due <= 1'b1;

            // Read beats: READ issued at clock r; the part drives beat 0
            // after its edge at r+2.5, the I/O register takes it at r+3, so
            // this logic sees beat 0 in sd_dq_in at r+4 and beat 1 at r+5.
            rd_pipe <= {rd_pipe[3:0], 1'b0};
            if (rd_pipe[3]) lo <= sd_dq_in;
            if (rd_pipe[4]) begin
                rsp_rdata <= {sd_dq_in, lo};
                rsp_valid <= 1'b1;
                rd_got <= 1'b1;
            end

            case (st)
            S_PWR: if (cnt == 0) st <= S_PRE; else cnt <= cnt - 1;
            S_PRE: begin
                {sd_cs_n, sd_ras_n, sd_cas_n, sd_we_n} <= CMD_PRE;
                sd_a <= 13'h0400;                  // A10: all banks
                cnt <= T_RFC; nref <= 8; st <= S_IREF;
            end
            S_IREF: if (cnt != 0) cnt <= cnt - 1;
                else if (nref != 0) begin
                    {sd_cs_n, sd_ras_n, sd_cas_n, sd_we_n} <= CMD_REF;
                    nref <= nref - 1; cnt <= T_RFC;
                end else st <= S_MRS;
            S_MRS: begin
                {sd_cs_n, sd_ras_n, sd_cas_n, sd_we_n} <= CMD_MRS;
                sd_a <= MODE; sd_ba <= 0;
                cnt <= 3; st <= S_WAIT;
                refc <= T_REFI; ref_due <= 1'b0;
            end
            S_IDLE: begin
                sd_dq_oe <= 1'b0; sd_dqm <= 2'b11;
                if (ref_due) begin
                    {sd_cs_n, sd_ras_n, sd_cas_n, sd_we_n} <= CMD_REF;
                    refc <= T_REFI; ref_due <= 1'b0;
                    cnt <= T_RFC; st <= S_WAIT;
                end else if (req_valid && init_done) begin
                    we_l <= req_we; addr_l <= req_addr;
                    wdata_l <= req_wdata; be_l <= req_be;
                    {sd_cs_n, sd_ras_n, sd_cas_n, sd_we_n} <= CMD_ACT;
                    sd_ba <= req_addr[11:10];
                    sd_a  <= req_addr[24:12];
                    st <= S_RW;
                end
            end
            S_RW: begin
                sd_ba <= addr_l[11:10];
                // A10 = 1: auto-precharge; A8:0 = the column.
                sd_a  <= {2'b00, 1'b1, 1'b0, addr_l[9:2], 1'b0};
                rd_got <= 1'b0;
                if (we_l) begin
                    {sd_cs_n, sd_ras_n, sd_cas_n, sd_we_n} <= CMD_WR;
                    sd_dq_out <= wdata_l[15:0];
                    sd_dqm <= ~be_l[1:0];
                    sd_dq_oe <= 1'b1;
                    st <= S_WB1;
                end else begin
                    {sd_cs_n, sd_ras_n, sd_cas_n, sd_we_n} <= CMD_RD;
                    sd_dqm <= 2'b00;
                    rd_pipe <= 5'b00001;
                    st <= S_DONE;
                end
                cnt <= T_ACC - 2;
            end
            S_WB1: begin                           // write beat 1
                sd_dq_out <= wdata_l[31:16];
                sd_dqm <= ~be_l[3:2];
                st <= S_DONE;
            end
            S_DONE: begin
                if (we_l) begin
                    sd_dq_oe <= 1'b0; sd_dqm <= 2'b11;
                end
                if (cnt != 0) cnt <= cnt - 1;
                else if (we_l) begin
                    rsp_valid <= 1'b1; st <= S_IDLE;
                end else if (rd_got || rd_pipe[4]) st <= S_IDLE;
            end
            S_WAIT: if (cnt != 0) cnt <= cnt - 1;
                else begin
                    st <= S_IDLE;
                    if (!init_done) init_done <= 1'b1;
                end
            default: st <= S_IDLE;
            endcase
        end
    end
endmodule
