// rtc_iic_tb.cpp -- Verilator replay harness for mkRtc / mkIic (bsc
// Verilog).  Built by rtc_iic_check.py: -DDEV_IIC for mkIic, otherwise
// mkRtc, whose I2C pins go to the behavioural MCP7940N in
// rtc_mcp7940n.h (open drain: a line is low when either side pulls it).
//
// stdin, one access per line:   CYCLE OP ADDR DATA BE
//   CYCLE  earliest cycle to issue it (decimal; cycle 0 is the first
//          clock edge after reset is released)
//   OP     R or W;  ADDR, DATA, BE in hex
//   OP N   no access: run until CYCLE, print nothing
// stdout, one line per access:  ACCEPT RDATA FAULT LED LEDN
//   ACCEPT the cycle whose edge took the request (the time the model is
//          evaluated at); RDATA the response (0 for a write); FAULT the
//          sticky fault code after the access; LED/LEDN the latch byte
//          and its write count (0 for the RTC).
// mkRtc only, after the accesses, one line
//   MCP seed=S seedcyc=L snap=R0..R6 lasttick=T writes=W regs=R0..R6
//       restart=C viol=V twr=N minhigh=H minlow=L drove=D notes...
// (snap: the chip's seven time registers on the seed's load cycle;
// lasttick: the chip's last second before it; regs: at the end; drove:
// cycles the RTL pulled either line low).
//
// mkRtc options:
//   --mcp-absent            no ACK at 0x6F
//   --mcp-regs=HEX14        RTCSEC..RTCYEAR at power-on (default
//                           80 00 12 23 03 01 93 with OSCRUN set)
//   --mcp-tick=N            chip cycles per second (default 100000)
//   --mcp-phase=N           cycles into its first second at reset
//   --mcp-stretch=N         hold SCL low N cycles after each ACK clock
//   --mcp-stuck             hold SCL low for ever
//   --mcp-oscstop=N         ST cleared -> OSCRUN cleared after N cycles
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include "verilated.h"
#ifdef DEV_IIC
#include "VmkIic.h"
typedef VmkIic Top;
#else
#include "VmkRtc.h"
#include "rtc_mcp7940n.h"
typedef VmkRtc Top;
static Mcp7940n mcp;
static unsigned long long seedCyc, drove;
static unsigned seedSeen;
static uint8_t snap[7];
static uint64_t snapLastTick;
#endif

static Top *top;
static unsigned long long cyc;

static void edge() {
    top->CLK = 0;
    top->eval();
#ifndef DEV_IIC
    int scl, sda;
    int ms = top->i2cSclLow, md = top->i2cSdaLow;
    if (ms || md) drove++;
    mcp.lines(ms, md, scl, sda, cyc);
    top->i2cPins_scl = scl;
    top->i2cPins_sda = sda;
    top->eval();
    mcp.cycle(ms, md, cyc);
    unsigned before = top->mcpSeed;
    for (int k = 0; k < 7; k++) snap[k] = mcp.reg[k];
    uint64_t lt = mcp.lastTick;
#endif
    top->CLK = 1;
    top->eval();
#ifndef DEV_IIC
    if (!seedSeen && top->mcpSeed != before && top->RST_N) {
        seedSeen = top->mcpSeed;
        seedCyc = cyc;
        snapLastTick = lt;
    }
#endif
}

static uint8_t seedSnap[7];

static void tick() {            // one cycle with the current inputs
#ifndef DEV_IIC
    unsigned had = seedSeen;
#endif
    edge();
#ifndef DEV_IIC
    if (!had && seedSeen) memcpy(seedSnap, snap, 7);
#endif
    cyc++;
}

static void settle() {
    top->CLK = 0;
    top->eval();
}

int main(int argc, char **argv) {
#ifndef DEV_IIC
    const uint8_t dflt[7] = {0x80, 0x00, 0x12, 0x23, 0x03, 0x01, 0x93};
    memcpy(mcp.reg, dflt, 7);
    mcp.reg[3] |= 0x20;
    for (int i = 1; i < argc; i++) {
        const char *a = argv[i];
        if (!strcmp(a, "--mcp-absent")) mcp.present = false;
        else if (!strcmp(a, "--mcp-stuck")) mcp.stuckScl = true;
        else if (!strncmp(a, "--mcp-regs=", 11)) {
            for (int k = 0; k < 7; k++) {
                unsigned v;
                sscanf(a + 11 + 2 * k, "%2x", &v);
                mcp.reg[k] = v;
            }
        } else if (!strncmp(a, "--mcp-tick=", 11)) mcp.tick = strtoull(a + 11, 0, 0);
        else if (!strncmp(a, "--mcp-phase=", 12)) mcp.sub = strtoull(a + 12, 0, 0);
        else if (!strncmp(a, "--mcp-stretch=", 14)) mcp.stretch = strtoull(a + 14, 0, 0);
        else if (!strncmp(a, "--mcp-oscstop=", 14)) mcp.oscStopDelay = strtoull(a + 14, 0, 0);
    }
#endif
    Verilated::commandArgs(argc, argv);
    top = new Top;
    top->EN_request = 0;
    top->EN_response = 0;
    top->RST_N = 0;
    for (int i = 0; i < 4; i++)
        edge();
    top->RST_N = 1;
    settle();
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
        settle();
        if (op == 'N')
            continue;
        unsigned long long guard = 0;
        while (!top->RDY_request) {
            tick();
            settle();
            if (++guard > 50000000ull) {
                fprintf(stderr, "tb: request never ready at %llu\n", cyc);
                return 3;
            }
        }
        top->request_addr = addr;
        top->request_wdata = data;
        top->request_be = be;
        top->request_write = (op == 'W');
        top->EN_request = 1;
        unsigned long long accept = cyc;
        tick();
        top->EN_request = 0;
        settle();
        guard = 0;
        while (!top->RDY_response) {
            tick();
            settle();
            if (++guard > 1000) {
                fprintf(stderr, "tb: no response at cycle %llu\n", cyc);
                return 3;
            }
        }
        unsigned rdata = top->response;
        top->EN_response = 1;
        tick();
        top->EN_response = 0;
        settle();
#ifdef DEV_IIC
        unsigned led = top->led, ledn = top->ledWrites;
#else
        unsigned led = 0, ledn = 0;
#endif
        printf("%llu %08x %02x %02x %02x\n", accept, rdata,
               (unsigned)top->fault, led, ledn);
    }
#ifndef DEV_IIC
    printf("MCP seed=%u seedcyc=%llu snap=", (unsigned)top->mcpSeed,
           seedSeen ? seedCyc : 0ull);
    for (int k = 0; k < 7; k++) printf("%02x", seedSnap[k]);
    printf(" lasttick=%llu writes=%u regs=", (unsigned long long)snapLastTick,
           (unsigned)top->mcpWrites);
    mcp.fixLpyr();
    for (int k = 0; k < 7; k++) printf("%02x", mcp.reg[k]);
    printf(" restart=%llu viol=%d twr=%d minhigh=%llu minlow=%llu drove=%llu"
           " fault=%02x end=%llu",
           mcp.restarted ? (unsigned long long)mcp.restart : 0ull,
           mcp.violations, mcp.timeWritesRunning,
           (unsigned long long)mcp.minHigh, (unsigned long long)mcp.minLow,
           drove, (unsigned)top->fault, cyc);
    for (auto &n : mcp.notes) printf(" note=%s", n.c_str());
    printf("\n");
#endif
    top->final();
    delete top;
    return 0;
}
