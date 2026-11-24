// rtc_iic_tb.cpp -- Verilator replay harness for mkRtc / mkIic (bsc
// Verilog).  Built twice by rtc_iic_check.py: -DDEV_IIC for mkIic,
// otherwise mkRtc.
//
// stdin, one access per line:   CYCLE OP ADDR DATA BE
//   CYCLE  earliest cycle to issue it (decimal; cycle 0 is the first
//          clock edge after reset is released)
//   OP     R or W;  ADDR, DATA, BE in hex
// stdout, one line per access:  ACCEPT RDATA FAULT LED LEDN
//   ACCEPT the cycle whose edge took the request (the time the model is
//          evaluated at); RDATA the response (0 for a write); FAULT the
//          sticky fault code after the access; LED/LEDN the latch byte
//          and its write count (0 for the RTC).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "verilated.h"
#ifdef DEV_IIC
#include "VmkIic.h"
typedef VmkIic Top;
#else
#include "VmkRtc.h"
typedef VmkRtc Top;
#endif

static Top *top;
static unsigned long long cyc;

static void edge() {
    top->CLK = 0;
    top->eval();
    top->CLK = 1;
    top->eval();
}

static void tick() {            // one cycle with the current inputs
    edge();
    cyc++;
}

int main(int argc, char **argv) {
    Verilated::commandArgs(argc, argv);
    top = new Top;
    top->EN_request = 0;
    top->EN_response = 0;
    top->RST_N = 0;
    for (int i = 0; i < 4; i++)
        edge();
    top->RST_N = 1;
    top->CLK = 0;
    top->eval();
    cyc = 0;

    char line[256];
    while (fgets(line, sizeof line, stdin)) {
        unsigned long long when;
        char op;
        unsigned addr, data, be;
        if (line[0] == '#' || line[0] == '\n')
            continue;
        if (sscanf(line, "%llu %c %x %x %x", &when, &op, &addr, &data,
                   &be) != 5) {
            fprintf(stderr, "tb: bad line: %s", line);
            return 2;
        }
        while (cyc < when)
            tick();
        top->CLK = 0;
        top->eval();
        while (!top->RDY_request) {
            tick();
            top->CLK = 0;
            top->eval();
        }
        top->request_addr = addr;
        top->request_wdata = data;
        top->request_be = be;
        top->request_write = (op == 'W');
        top->EN_request = 1;
        unsigned long long accept = cyc;
        tick();
        top->EN_request = 0;
        top->CLK = 0;
        top->eval();
        unsigned long guard = 0;
        while (!top->RDY_response) {
            tick();
            top->CLK = 0;
            top->eval();
            if (++guard > 1000) {
                fprintf(stderr, "tb: no response at cycle %llu\n", cyc);
                return 3;
            }
        }
        unsigned rdata = top->response;
        top->EN_response = 1;
        tick();
        top->EN_response = 0;
        top->CLK = 0;
        top->eval();
#ifdef DEV_IIC
        unsigned led = top->led, ledn = top->ledWrites;
#else
        unsigned led = 0, ledn = 0;
#endif
        printf("%llu %08x %02x %02x %02x\n", accept, rdata,
               (unsigned)top->fault, led, ledn);
    }
    top->final();
    delete top;
    return 0;
}
