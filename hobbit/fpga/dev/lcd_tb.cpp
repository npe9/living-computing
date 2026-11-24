// lcd_tb.cpp: Verilator bench for the Lcdisp device and its HDMI scan-out
// (lcd_sim_top.v = mkLcdisp + hdmi_scan + lcd_pattern).  Driven by
// lcd_test.py, which owns the comparisons with p9term.LcdPanel.
//
//   lcd_tb [--writes FILE] [--pattern] [--dump-at N,N,...] [--frames K] OUT
//
// --writes FILE  8-byte records, in order, each one register-port request:
//                  u16 addr[11:0] | write << 15, u8 byte enables, u8 0,
//                  u32 wdata (all little-endian)
//                one request a device clock while RDY_req is high.
// --pattern      instead, let lcd_pattern (the test bitstream's writer)
//                drive the port until it says done.
// --dump-at      after request N (1-based) has been issued, read the whole
//                panel RAM back through its pixel-clock port (196,608 bytes)
//                into OUT/buf_N.bin; the end state always goes to
//                OUT/buf_end.bin.
// --frames K     then run the scan-out on the pixel clock for K + 1 frames
//                and decode the TMDS words of all three lanes (DVI 1.0
//                3.2.3, decoded here independently of the encoder): check the
//                raster (1344 x 806 totals, 136-clock HSYNC and 6-line VSYNC,
//                both active low, porches) on every frame, red = green =
//                blue, and write the first whole frame as 1024 x 768 grey
//                bytes to OUT/frame.bin.
//
// Prints "requests R responses S overruns O" and the raster checks; exits 1
// on any failed check.

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>
#include <set>
#include "Vlcd_sim_top.h"
#include "verilated.h"

static Vlcd_sim_top *top;
static int fails = 0;
#define CHECK(c, ...) do { if (!(c)) { if (++fails < 20) { printf("FAIL: " __VA_ARGS__); printf("\n"); } } } while (0)

static void tick_sys() {
    top->CLK = 0; top->eval();
    top->CLK = 1; top->eval();
}
static void tick_pix() {
    top->CLK_pclk = 0; top->eval();
    top->CLK_pclk = 1; top->eval();
}

static uint64_t responses = 0;
static void sys_cycle() {
    // a response is taken on this edge when RDY_resp is high before it
    top->CLK = 0; top->eval();
    if (top->resp_valid) {
        responses++;
        if (top->resp != 0) { fails++; printf("FAIL: response %08x, not 0\n", top->resp); }
    }
    top->CLK = 1; top->eval();
}

static void dump(const std::string &path) {
    std::vector<uint8_t> buf(196608);
    top->dump_sel = 1;
    for (uint32_t a = 0; a < buf.size(); a++) {
        top->dump_addr = a;
        tick_pix();
        tick_pix();
        buf[a] = top->scan_data;
    }
    top->dump_sel = 0;
    FILE *f = fopen(path.c_str(), "wb");
    fwrite(buf.data(), 1, buf.size(), f);
    fclose(f);
}

// TMDS decode, DVI 1.0 3.2.3; -1..-4 for the control tokens (C1C0 = 0..3)
static int tmds_decode(uint32_t q) {
    switch (q) {
    case 0x354: return -1;          // 1101010100: C1C0 = 00
    case 0x0AB: return -2;          // 0010101011: 01
    case 0x154: return -3;          // 0101010100: 10
    case 0x2AB: return -4;          // 1010101011: 11
    }
    uint32_t d = (q & 0x200) ? (~q & 0xFF) : (q & 0xFF);
    uint32_t o = d & 1;
    for (int i = 1; i < 8; i++) {
        uint32_t b = ((d >> i) ^ (d >> (i - 1))) & 1;
        if (!(q & 0x100)) b ^= 1;
        o |= b << i;
    }
    return (int)o;
}

// TMDS encode, DVI 1.0 3.2.3 (its encoding flowchart), a second model
// written from the specification, not from tmds_enc: the bench re-encodes
// what it decoded and expects the RTL's exact word, so the
// transition-minimizing choice and the DC balance are checked too.  cnt is
// the whole disparity (tmds_enc keeps half of it).
struct TmdsRef {
    int cnt = 0;
    uint32_t enc(bool de, int ctrl, uint32_t d) {
        static const uint32_t tok[4] = { 0x354, 0x0AB, 0x154, 0x2AB };
        if (!de) { cnt = 0; return tok[ctrl & 3]; }
        int n1 = __builtin_popcount(d & 0xFF);
        bool xnor = n1 > 4 || (n1 == 4 && !(d & 1));
        uint32_t qm = d & 1;
        for (int i = 1; i < 8; i++) {
            uint32_t b = ((qm >> (i - 1)) ^ (d >> i)) & 1;
            if (xnor) b ^= 1;
            qm |= b << i;
        }
        if (!xnor) qm |= 0x100;
        int q8 = (qm >> 8) & 1;
        int n1q = __builtin_popcount(qm & 0xFF), n0q = 8 - n1q;
        uint32_t q;
        if (cnt == 0 || n1q == n0q) {
            q = q8 ? (qm & 0x1FF) : (0x200 | (~qm & 0xFF));
            cnt += q8 ? n1q - n0q : n0q - n1q;
        } else if ((cnt > 0 && n1q > n0q) || (cnt < 0 && n0q > n1q)) {
            q = 0x200 | (qm & 0x100) | (~qm & 0xFF);
            cnt += 2 * q8 + (n0q - n1q);
        } else {
            q = qm & 0x1FF;
            cnt += -2 * (q8 ^ 1) + (n1q - n0q);
        }
        return q;
    }
};

int main(int argc, char **argv) {
    Verilated::commandArgs(argc, argv);
    std::string writes, out;
    bool pattern = false;
    int frames = 0;
    std::set<uint64_t> dump_at;
    for (int i = 1; i < argc; i++) {
        std::string a = argv[i];
        if (a == "--writes") writes = argv[++i];
        else if (a == "--pattern") pattern = true;
        else if (a == "--frames") frames = atoi(argv[++i]);
        else if (a == "--dump-at") {
            char *s = argv[++i];
            for (char *t = strtok(s, ","); t; t = strtok(NULL, ","))
                dump_at.insert(strtoull(t, NULL, 10));
        } else if (a[0] != '+') out = a;
    }
    top = new Vlcd_sim_top;
    top->RST_N = 0; top->pat_sel = 0; top->dump_sel = 0; top->tb_en = 0;
    for (int i = 0; i < 4; i++) { tick_sys(); tick_pix(); }
    top->RST_N = 1;
    for (int i = 0; i < 2; i++) tick_sys();

    uint64_t requests = 0;
    if (pattern) {
        top->pat_sel = 1;
        uint64_t n = 0;
        while (!top->pat_done && n < 10000000) {
            top->CLK = 0; top->eval();
            if (top->pat_req) requests++;
            if (top->resp_valid) responses++;
            top->CLK = 1; top->eval();
            n++;
        }
        top->pat_sel = 0;
        for (int i = 0; i < 4; i++) sys_cycle();
    } else if (!writes.empty()) {
        FILE *f = fopen(writes.c_str(), "rb");
        if (!f) { perror(writes.c_str()); return 2; }
        uint8_t r[8];
        while (fread(r, 1, 8, f) == 8) {
            uint16_t aw = r[0] | (r[1] << 8);
            top->tb_addr = aw & 0xFFF;
            top->tb_write = (aw >> 15) & 1;
            top->tb_be = r[2] & 0xF;
            top->tb_wdata = r[4] | (r[5] << 8) | (r[6] << 16) | ((uint32_t)r[7] << 24);
            top->tb_en = 1;
            top->CLK = 0; top->eval();
            while (!top->req_rdy) { top->tb_en = 0; sys_cycle(); top->tb_en = 1; top->CLK = 0; top->eval(); }
            sys_cycle();
            top->tb_en = 0;
            requests++;
            if (dump_at.count(requests))
                dump(out + "/buf_" + std::to_string(requests) + ".bin");
        }
        fclose(f);
        for (int i = 0; i < 4; i++) sys_cycle();
    }
    dump(out + "/buf_end.bin");
    printf("requests %llu responses %llu overruns %u\n",
           (unsigned long long)requests, (unsigned long long)responses, top->overruns);
    CHECK(requests == responses, "one response per request: %llu requests, %llu responses",
              (unsigned long long)requests, (unsigned long long)responses);

    if (frames > 0) {
        const int HT = 1344, VT = 806, HA = 1024, VA = 768;
        const int HFP = 24, HS = 136, VFP = 3, VS = 6;
        uint64_t total = (uint64_t)HT * VT * (frames + 1) + 64;
        std::vector<int> de(total), hs(total), vs(total), gr(total);
        TmdsRef ref_r, ref_g, ref_b;
        bool synced = false;        // the reference starts at a blanking word
        for (uint64_t t = 0; t < total; t++) {
            tick_pix();
            int b = tmds_decode(top->tmds_b), g = tmds_decode(top->tmds_g),
                r = tmds_decode(top->tmds_r);
            synced = synced || b < 0;
            if (synced) {
                bool d = b >= 0;
                uint32_t eb = ref_b.enc(d, d ? 0 : -b - 1, d ? b : 0),
                         eg = ref_g.enc(d, 0, d ? g : 0),
                         er = ref_r.enc(d, 0, d ? r : 0);
                if (eb != top->tmds_b || eg != top->tmds_g || er != top->tmds_r) {
                    fails++;
                    if (fails < 10) printf("FAIL: clock %llu: TMDS words %03x %03x %03x, the "
                                           "reference encoder gives %03x %03x %03x\n",
                                           (unsigned long long)t, top->tmds_r, top->tmds_g,
                                           top->tmds_b, er, eg, eb);
                }
            }
            if (b >= 0) {
                de[t] = 1; gr[t] = b;
                hs[t] = vs[t] = 1;     // syncs are only sent in blanking
                if (!(g == b && r == b)) {
                    fails++;
                    if (fails < 10) printf("FAIL: clock %llu: r %d g %d b %d differ\n",
                                           (unsigned long long)t, r, g, b);
                }
            } else {
                int c = -b - 1;
                de[t] = 0; gr[t] = 0;
                hs[t] = c & 1; vs[t] = (c >> 1) & 1;
                if (g != -1 || r != -1) {
                    fails++;
                    if (fails < 10) printf("FAIL: clock %llu: blanking r %d g %d not C=00\n",
                                           (unsigned long long)t, r, g);
                }
            }
        }
        // vertical: VSYNC falls every HT*VT clocks, low for VS lines
        std::vector<uint64_t> vfall, hfall, derise;
        for (uint64_t t = 1; t < total; t++) {
            if (vs[t - 1] && !vs[t]) vfall.push_back(t);
            if (hs[t - 1] && !hs[t]) hfall.push_back(t);
            if (!de[t - 1] && de[t]) derise.push_back(t);
        }
        CHECK(vfall.size() >= (size_t)frames, "VSYNC edges: %zu", vfall.size());
        for (size_t k = 0; k + 1 < vfall.size(); k++)
            CHECK(vfall[k + 1] - vfall[k] == (uint64_t)HT * VT, "VSYNC period %llu",
                  (unsigned long long)(vfall[k + 1] - vfall[k]));
        for (uint64_t v : vfall) {
            uint64_t n = 0;
            while (v + n < total && !vs[v + n]) n++;
            if (v + n < total) CHECK(n == (uint64_t)VS * HT, "VSYNC low %llu clocks", (unsigned long long)n);
        }
        for (size_t k = 0; k + 1 < hfall.size(); k++)
            CHECK(hfall[k + 1] - hfall[k] == (uint64_t)HT, "HSYNC period %llu at %llu",
                  (unsigned long long)(hfall[k + 1] - hfall[k]), (unsigned long long)hfall[k]);
        for (uint64_t h : hfall) {
            uint64_t n = 0;
            while (h + n < total && !hs[h + n]) n++;
            if (h + n < total) CHECK(n == (uint64_t)HS, "HSYNC low %llu clocks", (unsigned long long)n);
        }
        // active video: every DE run is HA long, HFP clocks before HSYNC
        // falls; a frame's first line starts (VT - VA - VFP) lines after
        // VSYNC falls, and the frame has VA lines
        std::vector<uint8_t> frame((size_t)HA * VA);
        bool got = false;
        for (size_t k = 0; k < vfall.size(); k++) {
            uint64_t start = vfall[k] + (uint64_t)(VT - VA - VFP) * HT;
            if (start + (uint64_t)VA * HT > total) break;
            for (int y = 0; y < VA; y++) {
                uint64_t s = start + (uint64_t)y * HT;
                CHECK(de[s] && !de[s - 1], "frame %zu line %d: DE does not rise at %llu", k, y,
                      (unsigned long long)s);
                for (int x = 0; x < HA; x++) {
                    if (!de[s + x]) { CHECK(0, "frame %zu line %d: DE low at x %d", k, y, x); break; }
                    if (!got) frame[(size_t)y * HA + x] = gr[s + x];
                }
                CHECK(!de[s + HA], "frame %zu line %d: DE run longer than %d", k, y, HA);
                CHECK(hs[s + HA + HFP - 1] && !hs[s + HA + HFP],
                      "frame %zu line %d: HSYNC does not fall %d clocks after DE", k, y, HFP);
            }
            // no DE in vertical blanking
            for (uint64_t t = start + (uint64_t)VA * HT; t < start + (uint64_t)VT * HT && t < total; t++)
                if (de[t]) { CHECK(0, "frame %zu: DE in vertical blanking at %llu", k, (unsigned long long)t); break; }
            if (!got) {
                FILE *f = fopen((out + "/frame.bin").c_str(), "wb");
                fwrite(frame.data(), 1, frame.size(), f);
                fclose(f);
                got = true;
            }
        }
        CHECK(got, "no whole frame captured");
        printf("raster: %zu VSYNC, %zu HSYNC, %zu DE runs checked\n",
               vfall.size(), hfall.size(), derise.size());
    }
    printf("%s (%d failed checks)\n", fails ? "FAIL" : "ok", fails);
    delete top;
    return fails ? 1 : 0;
}
