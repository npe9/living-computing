// soc_main.cpp -- Verilator driver for fpga/sim/soc_sim_top.v: the Hobbit
// SoC (gated core, memory adapter, SDRAM controller and model, host link)
// booting the shipped kernel against the reference boot's recording, the
// way bsv/P9KernTb.bsv does on the bare core (fpga/sim/run_soc.sh).
//
// What this checks is that the SoC's memory system is invisible to the
// core: every retirement record (written by the core's own $display) must
// equal the reference boot's, which run_soc.sh compares with
// tools/p9coreboot.py exactly as bsv/run_p9kern.sh does.
//
// The driver plays the host's side of the host link at the UART pins
// (rtl/hostlink.v's protocol, CPB clocks per bit): it starts the core with
// 'G', and answers every forwarded I/O access ('F') from bsv/p9kern.c --
// a read with the recorded device value, a write checked against the
// recording.  RAM is loaded through the SDRAM model's back door, the ROM
// block with the fpi image (tools/p9boot.py's Rom), and the recorded
// interrupts are handed to the core's queue (armInterrupt) as
// P9KernTb does.
#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <cstring>
#include <deque>
#include <vector>
#include "verilated.h"
#include "Vsoc_sim_top.h"
#include "svdpi.h"

extern "C" {
uint32_t pk_start(void);
uint32_t pk_end(void);
uint32_t pk_fetch(uint32_t addr, uint32_t fresh);
void pk_write(uint32_t addr, uint32_t v);
uint32_t pk_peek(uint32_t addr);
void pk_retired(uint32_t n);
uint32_t pk_failed(void);
void pk_report(void);
uint32_t pk_irq_at(void);
uint32_t pk_irq_level(void);
uint32_t pk_irq_pc(void);
void pk_irq_taken(uint32_t pc);
void sdram_poke16(unsigned h, unsigned v);
unsigned sdram_peek16(unsigned h);
void soc_rom_poke(unsigned a, unsigned v);
}

#ifndef CPB
#define CPB 4
#endif

static Vsoc_sim_top *top;
static uint64_t clocks;

// ---- host side of the UART -------------------------------------------
static std::deque<uint8_t> txq;      // host -> board
static int tx_bit = -1, tx_cnt = 0;
static uint16_t tx_sh;
static int rx_state = 0, rx_cnt = 0, rx_n = 0;
static uint8_t rx_sh;
static std::vector<uint8_t> rxbuf;   // board -> host

static void uart_step(void) {
    // Transmit to rxd.
    if (tx_bit < 0 && !txq.empty()) {
        tx_sh = (uint16_t)(0x200 | (txq.front() << 1));
        txq.pop_front();
        tx_bit = 0; tx_cnt = CPB;
    }
    if (tx_bit >= 0) {
        top->rxd = (tx_sh >> tx_bit) & 1;
        if (--tx_cnt == 0) { tx_cnt = CPB; if (++tx_bit == 10) tx_bit = -1; }
    } else top->rxd = 1;
    // Receive from txd (mid-bit).
    int b = top->txd;
    switch (rx_state) {
    case 0: if (!b) { rx_state = 1; rx_cnt = CPB / 2; } break;
    case 1:
        if (--rx_cnt == 0) {
            if (b) rx_state = 0; else { rx_state = 2; rx_cnt = CPB; rx_n = 0; rx_sh = 0; }
        }
        break;
    case 2:
        if (--rx_cnt == 0) {
            rx_cnt = CPB;
            if (rx_n < 8) { rx_sh |= (uint8_t)(b << rx_n); rx_n++; }
            else {
                if (!b) { fprintf(stderr, "SOC FAIL: framing error at %llu\n", (unsigned long long)clocks); exit(1); }
                rxbuf.push_back(rx_sh); rx_state = 0;
            }
        }
        break;
    }
}

static void put32(uint32_t v) {
    for (int i = 3; i >= 0; i--) txq.push_back((uint8_t)(v >> (8 * i)));
}
static uint32_t get32(const uint8_t *p) {
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) | ((uint32_t)p[2] << 8) | p[3];
}

static unsigned long fwd_reads, fwd_writes;
// $SOC_IOLOG: every forwarded access, "R|W addr value retired".
static FILE *iolog;

// Consume complete frames from the board.
static bool frames(void) {
    while (!rxbuf.empty()) {
        uint8_t c = rxbuf[0];
        size_t need = c == 'F' ? 15 : c == 'T' ? 6 : c == 'p' ? 11 :
                      c == 'r' ? 5 : 1;
        if (rxbuf.size() < need) return true;
        if (c == 'F') {
            int we = rxbuf[1] & 1;
            uint32_t a = get32(&rxbuf[2]), d = get32(&rxbuf[6]);
            uint32_t v = 0;
            if (we) { pk_write(a, d); fwd_writes++; }
            else { v = pk_fetch(a, 1); fwd_reads++; }
            if (iolog)
                fprintf(iolog, "%c %08x %08x %u\n", we ? 'W' : 'R', a,
                        we ? d : v, (unsigned)top->retired);
            txq.push_back('D'); put32(v);
        } else if (c != 'T' && c != 'g' && c != 'w' && c != 'b' && c != 'p' && c != 'r') {
            fprintf(stderr, "SOC FAIL: unexpected byte %02x from the board\n", c);
            exit(1);
        }
        rxbuf.erase(rxbuf.begin(), rxbuf.begin() + need);
    }
    return true;
}

static void tick(void) {
    top->clk = 0; top->eval();
    top->clk = 1; top->eval();
    clocks++;
}

static void load_rom(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f) { fprintf(stderr, "soc: no %s\n", path); exit(1); }
    std::vector<uint8_t> b(1 << 20);
    size_t n = fread(b.data(), 1, b.size(), f);
    fclose(f);
    uint32_t text = get32(&b[4]), entry = get32(&b[20]);
    uint32_t base = entry - 0xC0000000u;
    for (uint32_t i = 0; i < text / 4 && 32 + 4 * i + 3 < n; i++) {
        uint32_t w = b[32 + 4 * i] | (b[33 + 4 * i] << 8) | (b[34 + 4 * i] << 16) |
                     ((uint32_t)b[35 + 4 * i] << 24);
        uint32_t a = base + 4 * i;
        if (a < 0x4000) soc_rom_poke(a, w);
    }
    printf("SOC rom: fpi image, %u bytes at %08x\n", text, base);
}

int main(int argc, char **argv) {
    Verilated::commandArgs(argc, argv);
    top = new Vsoc_sim_top;
    if (getenv("SOC_IOLOG")) iolog = fopen(getenv("SOC_IOLOG"), "w");
    top->rxd = 1; top->rst = 1; top->arm_en = 0; top->took_en = 0;
    for (int i = 0; i < 20; i++) tick();
    top->rst = 0;

    svSetScope(svGetScopeFromName("TOP.soc_sim_top.sdram"));
    uint32_t entry = pk_start();
    uint32_t endN = pk_end();
    unsigned long words = 0;
    for (uint32_t a = 0x80000000u; a < 0x80800000u; a += 4) {
        uint32_t v = pk_peek(a);
        if (!v) continue;
        uint32_t w = (a - 0x80000000u) >> 2;
        sdram_poke16(2 * w, v & 0xFFFF);
        sdram_poke16(2 * w + 1, v >> 16);
        words++;
    }
    printf("SOC ram: %lu nonzero words loaded\n", words);
    const char *rom = getenv("SOC_ROM");
    if (rom && *rom) {
        svSetScope(svGetScopeFromName("TOP.soc_sim_top.soc"));
        load_rom(rom);
    }
    txq.push_back('G'); put32(entry);
    printf("SOC start pc=%08x, the reference has %u records\n", entry, endN);

    uint64_t limit = strtoull(getenv("SOC_CLOCKS") ? getenv("SOC_CLOCKS") : "4000000000", 0, 0);
    uint32_t last_ret = 0; uint64_t last_change = 0;
    bool armed = false, arming = false, taking = false;
    int why = 0;
    while (clocks < limit) {
        uart_step();
        // The replayed interrupts: one in the queue at a time.
        uint32_t n = pk_irq_at();
        top->arm_en = 0;
        if (!armed && n != 0xFFFFFFFFu && n < endN && top->arm_rdy) {
            top->arm_en = 1; top->arm_n = n; top->arm_level = pk_irq_level();
            arming = true;
        }
        top->took_en = top->took_rdy ? 1 : 0;
        taking = top->took_en;
        uint32_t tpc = top->took_pc;
        top->clk = 0; top->eval();
        bool edge = top->cpu_ce;      // the coming rising edge is a core edge
        top->clk = 1; top->eval();
        clocks++;
        if (edge && arming && top->arm_en) armed = true;
        if (edge && taking) {
            uint32_t want = pk_irq_pc();
            pk_irq_taken(tpc);
            armed = false;
            if (want != tpc) {
                printf("SOC FAIL: interrupt saved pc %08x, the reference %08x\n", tpc, want);
                why = 1; break;
            }
        }
        arming = false;
        uint32_t r = top->retired;
        pk_retired(r);
        frames();
        if (r != last_ret) { last_ret = r; last_change = clocks; }
        if (r >= endN) { why = 0; break; }
        if (pk_failed()) { why = 1; break; }
        if (top->stopped) { why = 2; break; }
        if (clocks - last_change > 20000000ull) { why = 3; break; }
    }
    // Drain: let the last records print.
    for (int i = 0; i < 4000; i++) { uart_step(); tick(); pk_retired(top->retired); frames(); }
    static const char *whys[] = {"the reference's last record", "a failed check", "the core stopped", "a stall or the clock limit"};
    printf("SOC end: %s; %u records, %llu core clocks, %llu system clocks "
           "(%.2f per core clock), %lu forwarded reads, %lu forwarded writes\n",
           clocks >= limit ? whys[3] : whys[why], top->retired,
           (unsigned long long)top->core_clocks, (unsigned long long)clocks,
           top->core_clocks ? (double)clocks / (double)top->core_clocks : 0.0,
           fwd_reads, fwd_writes);
    pk_report();
    top->final();
    delete top;
    return (why == 0 && clocks < limit) ? 0 : 1;
}
