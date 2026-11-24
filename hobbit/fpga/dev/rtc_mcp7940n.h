// rtc_mcp7940n.h -- a behavioural MCP7940N (Microchip I2C real-time clock
// with battery-backed SRAM) on a cycle-level I2C bus, for rtc_iic_tb.cpp.
//
// SOURCES.  The data sheet (Microchip DS20005010) is NOT on disk, so no
// page is cited; every statement below is marked by where it comes from:
//   [T]  ~/src/ulx3s-experiments/flute-lx50/test/rtc_test.c, a program
//        written for the chip on this board design (not yet run on the
//        board, its notes say) that cites
//        DS20005010J: address 0x6F; RTCSEC 0x00 bit 7 ST; RTCWKDAY 0x03
//        bit 3 VBATEN (off at the chip's power-on) and bit 4 PWRFAIL
//        (cleared by writing RTCWKDAY); CONTROL 0x07; register-pointer
//        writes then repeated-START reads; weekday 1..7.
//   [I]  inference, from memory of the part's family, NOT checked against
//        the data sheet: RTCWKDAY bit 5 OSCRUN (oscillator running, read
//        only), RTCHOUR bit 6 12/24 and bit 5 AM/PM, RTCMTH bit 5 LPYR
//        (read only), SRAM 0x20..0x5F (64 bytes), the register pointer
//        auto-incrementing over a burst, OSCRUN clearing some time after
//        ST is cleared, and the recommendation to stop the oscillator
//        (ST = 0, wait for OSCRUN = 0) before writing the time.
//   [M]  modelling choices of this file: OSCRUN sets the cycle ST is
//        written 1, and the second starts counting from that cycle; the
//        pointer wraps from 0x5F to 0x00; a read returns the live
//        register (no latching over a burst); the chip never stretches
//        SCL unless asked to (--mcp-stretch).
#include <cstdint>
#include <cstdio>
#include <string>
#include <vector>

struct Mcp7940n {
    // configuration
    bool present = true;           // answers at 0x6F
    uint64_t tick = 100000;        // cycles per second of the chip
    uint64_t stretch = 0;          // hold SCL low after each ACK clock
    uint64_t oscStopDelay = 3000;  // ST 1->0 to OSCRUN 1->0 [I][M]
    bool stuckScl = false;         // hold SCL low for ever
    uint8_t reg[0x60] = {0};

    // time
    uint64_t sub = 0;              // cycles into the current second
    uint64_t stopAt = 0;           // OSCRUN clears at this cycle (0: no)
    uint64_t lastTick = 0, restart = 0;
    bool restarted = false;

    // bus
    enum St { IDLE, RECV, SACK, SEND, MACK } st = IDLE;
    bool prevScl = true, prevSda = true, sdaLow = false;
    uint64_t sclHoldUntil = 0;
    int bits = 0;
    uint8_t shift = 0, out = 0, ptr = 0;
    bool isAddr = false, rw = false, gotPtr = false, mAck = false;

    // checks
    uint64_t lastEdge = 0, minHigh = ~0ull, minLow = ~0ull;
    int violations = 0;
    std::vector<std::string> notes;
    int timeWritesRunning = 0;     // time written while OSCRUN = 1 [I]
    int writes = 0;

    void note(uint64_t c, const char *what) {
        violations++;
        if (notes.size() < 8) {
            char buf[160];
            snprintf(buf, sizeof buf, "%llu:%s", (unsigned long long)c, what);
            notes.push_back(buf);
        }
    }

    static uint8_t bcdInc(uint8_t x) {
        return (x & 15) == 9 ? (uint8_t)((x & 0xF0) + 0x10) : (uint8_t)(x + 1);
    }
    static int bin(uint8_t x) { return (x >> 4) * 10 + (x & 15); }

    bool oscrun() const { return reg[3] & 0x20; }

    void tickSecond(uint64_t c) {
        lastTick = c;
        uint8_t s = reg[0] & 0x7F;
        if (s != 0x59) { reg[0] = (reg[0] & 0x80) | bcdInc(s); return; }
        reg[0] &= 0x80;
        uint8_t m = reg[1] & 0x7F;
        if (m != 0x59) { reg[1] = bcdInc(m); return; }
        reg[1] = 0;
        if (reg[2] & 0x40) { note(c, "model: 12-hour rollover not modelled"); return; }
        uint8_t h = reg[2] & 0x3F;
        if (h != 0x23) { reg[2] = bcdInc(h); return; }
        reg[2] = 0;
        reg[3] = (reg[3] & 0xF8) | ((reg[3] & 7) == 7 ? 1 : (reg[3] & 7) + 1);
        int y = bin(reg[6]), mo = bin(reg[5] & 0x1F), d = bin(reg[4] & 0x3F);
        static const int dim[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
        int last = (mo == 2 && y % 4 == 0) ? 29 : dim[(mo - 1) % 12];
        if (d != last) { reg[4] = bcdInc(reg[4] & 0x3F); return; }
        reg[4] = 1;
        if (mo != 12) { reg[5] = (reg[5] & 0x20) | bcdInc(reg[5] & 0x1F); return; }
        reg[5] = (reg[5] & 0x20) | 1;
        reg[6] = reg[6] == 0x99 ? 0 : bcdInc(reg[6]);
    }

    void fixLpyr() {           // [I] LPYR read only, from the year
        reg[5] = (reg[5] & 0x1F) | ((bin(reg[6]) % 4 == 0) ? 0x20 : 0);
    }

    uint8_t readReg(uint8_t a) { fixLpyr(); return reg[a % 0x60]; }

    void writeReg(uint64_t c, uint8_t a, uint8_t v) {
        a %= 0x60;
        writes++;
        if (a <= 6 && oscrun() && a != 0) timeWritesRunning++;
        if (a == 0) {
            bool was = reg[0] & 0x80, now = v & 0x80;
            if (oscrun() && was && now) timeWritesRunning++;
            reg[0] = v;
            if (was && !now) stopAt = c + oscStopDelay;
            if (!was && now) {                     // [M] start counting
                reg[3] |= 0x20;
                stopAt = 0;
                sub = 0;
                restart = c;
                restarted = true;
            }
        } else if (a == 3) {
            reg[3] = (reg[3] & 0x20) | (v & 0x0F);  // OSCRUN r/o, PWRFAIL cleared
        } else {
            reg[a] = v;
        }
    }

    // One clock edge.  Master pulls: mScl/mSda = 1 means pulled low.
    // Returns the bus levels the master reads back.
    void lines(int mScl, int mSda, int &scl, int &sda, uint64_t c) {
        bool holdScl = stuckScl || c < sclHoldUntil;
        scl = !(mScl || holdScl);
        sda = !(mSda || sdaLow);
    }

    void cycle(int mScl, int mSda, uint64_t c) {
        // time
        if (stopAt && c >= stopAt) { reg[3] &= ~0x20; stopAt = 0; }
        if ((reg[0] & 0x80) && oscrun()) {
            if (++sub >= tick) { sub = 0; tickSecond(c); }
        }
        int scl, sda;
        lines(mScl, mSda, scl, sda, c);
        if (scl != prevScl) {
            uint64_t len = c - lastEdge;
            if (lastEdge && st != IDLE) {
                if (prevScl) { if (len < minHigh) minHigh = len; }
                else if (len < minLow) minLow = len;
            }
            lastEdge = c;
        }
        if (scl && prevScl && sda != prevSda) {
            bool start = !sda;
            if (st == SEND && mSda) note(c, "master drove SDA while the slave sends");
            // A START or STOP comes right after the first SCL rise of
            // what the slave takes for the next byte (bits == 1); any
            // later one is inside a byte.
            else if ((st == RECV && bits > 1) || st == SEND)
                note(c, start ? "START inside a byte" : "STOP inside a byte");
            if (start) {
                st = RECV; isAddr = true; bits = 0; shift = 0; sdaLow = false;
            } else {
                st = IDLE; sdaLow = false;
            }
        } else if (!prevScl && scl) {                  // rising: sample
            if (st == RECV) { shift = (uint8_t)((shift << 1) | sda); bits++; }
            else if (st == MACK) mAck = !sda;
        } else if (prevScl && !scl) {                  // falling: drive
            switch (st) {
            case RECV:
                if (bits == 8) {
                    if (isAddr) {
                        isAddr = false;
                        if (present && (shift >> 1) == 0x6F) {
                            rw = shift & 1;
                            if (!rw) gotPtr = false;
                            sdaLow = true;
                            st = SACK;
                        } else
                            st = IDLE;
                    } else {
                        if (!gotPtr) { ptr = shift; gotPtr = true; }
                        else { writeReg(c, ptr, shift); ptr = (ptr + 1) % 0x60; }
                        sdaLow = true;
                        st = SACK;
                    }
                }
                break;
            case SACK:
                sdaLow = false;
                if (stretch) sclHoldUntil = c + stretch;
                if (rw) {
                    out = readReg(ptr); ptr = (ptr + 1) % 0x60;
                    sdaLow = !(out & 0x80); bits = 1; st = SEND;
                } else { st = RECV; bits = 0; shift = 0; }
                break;
            case SEND:
                if (bits < 8) { sdaLow = !((out >> (7 - bits)) & 1); bits++; }
                else { sdaLow = false; st = MACK; }
                break;
            case MACK:
                if (mAck) {
                    out = readReg(ptr); ptr = (ptr + 1) % 0x60;
                    sdaLow = !(out & 0x80); bits = 1; st = SEND;
                } else st = IDLE;
                break;
            default:
                break;
            }
        }
        prevScl = scl;
        prevSda = sda;
    }
};
