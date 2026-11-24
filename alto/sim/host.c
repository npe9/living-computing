/* Host helpers for the Alto Bluesim: ROMs, Diablo .dsk images, display, keyboard. */

#include "host.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#include "rom_arrays.h"

#define ALTO_W      606
#define ALTO_H      808
#define HDR_OFF     44
#define LBL_OFF     58
#define DAT_OFF     78
#define SEC_WORDS   347
#define HEADER_N    2
#define LABEL_N     8
#define DATA_N      256

static uint64_t g_max_cycles = 2000000;
static uint32_t g_trace = 0;
static const char *g_disk_path = NULL;
static const char *g_frame_path = "alto_frame.pbm";

static uint16_t *g_pack = NULL;      /* packed CHS records, little-endian words */
static int g_cyls = 203, g_heads = 2, g_secs = 12;
static int g_sec_words = 2 + 8 + 256; /* header+label+data (no dummy) */
static int g_has_dummy = 1;
static int g_loaded = 0;

static uint16_t g_slice[SEC_WORDS];
static int g_sel_c, g_sel_h, g_sel_s;
static int g_dirty = 0;

static uint8_t g_fb[ALTO_W * ALTO_H];
static uint32_t g_last_field = 0;

static uint16_t g_kbd[4] = { 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF };
static uint16_t g_mouse = 0xFFFF;
static uint64_t g_task_cyc[16];
static uint32_t g_dump_n;

/* Keyboard words KBDAD..+3 (HW manual §5.1). Idle = 1, down = 0. */
static const char *g_type = NULL;
static uint64_t g_type_at = 55000000;
static uint64_t g_poll_cyc;
static size_t   g_type_i;
static int      g_type_phase;   /* 0 idle, 1 down, 2 gap */
static uint32_t g_type_timer;

static uint32_t g_cram[1024];
static int g_ether_debug;

#define ETH_MAX 512
static uint16_t g_etx[ETH_MAX];
static int      g_etx_n;
static uint16_t g_erx[ETH_MAX];
static int      g_erx_n;
static int      g_erx_i;
/* Built at TX end; copied into g_erx only on EISFCT so OUTGONE/EPFCT
   cannot stuff the FIFO before the receiver is restarted. */
static uint16_t g_erx_pend[ETH_MAX];
static int      g_erx_pend_n;

static uint16_t rd_le(const uint8_t *p)
{
    return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
}

static void wr_le(uint8_t *p, uint16_t w)
{
    p[0] = (uint8_t)w;
    p[1] = (uint8_t)(w >> 8);
}

static uint16_t checksum(const uint16_t *w, int n)
{
    uint16_t c = 0x0151;
    for (int i = 0; i < n; i++)
        c ^= w[i];
    return c;
}

static uint16_t *pack_ptr(int c, int h, int s)
{
    size_t idx = ((size_t)c * (size_t)g_heads + (size_t)h) * (size_t)g_secs + (size_t)s;
    return g_pack + idx * (size_t)g_sec_words;
}

static void rebuild_slice(void)
{
    memset(g_slice, 0, sizeof g_slice);
    g_slice[HDR_OFF] = 1;
    g_slice[LBL_OFF] = 1;
    g_slice[DAT_OFF] = 1;
    if (!g_loaded)
        return;

    uint16_t *rec = pack_ptr(g_sel_c, g_sel_h, g_sel_s);
    uint16_t tmp[256];

    for (int j = 0; j < HEADER_N; j++)
        tmp[j] = rec[j];
    for (int i = 0, j = HEADER_N - 1; i < HEADER_N; i++, j--)
        g_slice[HDR_OFF + 1 + i] = tmp[j];
    g_slice[HDR_OFF + 3] = checksum(&g_slice[HDR_OFF + 1], HEADER_N);

    for (int j = 0; j < LABEL_N; j++)
        tmp[j] = rec[HEADER_N + j];
    for (int i = 0, j = LABEL_N - 1; i < LABEL_N; i++, j--)
        g_slice[LBL_OFF + 1 + i] = tmp[j];
    g_slice[LBL_OFF + 9] = checksum(&g_slice[LBL_OFF + 1], LABEL_N);

    for (int j = 0; j < DATA_N; j++)
        tmp[j] = rec[HEADER_N + LABEL_N + j];
    for (int i = 0, j = DATA_N - 1; i < DATA_N; i++, j--)
        g_slice[DAT_OFF + 1 + i] = tmp[j];
    g_slice[DAT_OFF + 257] = checksum(&g_slice[DAT_OFF + 1], DATA_N);
}

static int load_disk(const char *path)
{
    FILE *f = fopen(path, "rb");
    if (!f) {
        perror(path);
        return -1;
    }
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);

    /* Bitsavers Diablo 31: 203*2*12*(2 + 4+16+512) = 2,603,784 */
    long n31_dummy = 203L * 2 * 12 * 534;
    long n31_raw   = 203L * 2 * 12 * 532;
    long n44_dummy = 406L * 2 * 12 * 534;

    g_heads = 2;
    g_secs = 12;
    g_sec_words = 2 + 8 + 256;
    if (sz == n44_dummy) {
        g_cyls = 406;
        g_has_dummy = 1;
    } else if (sz == n31_dummy || sz == n31_raw) {
        g_cyls = 203;
        g_has_dummy = (sz == n31_dummy);
    } else if (sz > n31_dummy) {
        g_cyls = 406;
        g_has_dummy = 1;
        fprintf(stderr, "host: unusual image size %ld, treating as Diablo 44\n", sz);
    } else {
        g_cyls = 203;
        g_has_dummy = (sz >= n31_dummy - 4096);
        fprintf(stderr, "host: unusual image size %ld, treating as Diablo 31\n", sz);
    }

    size_t nsec = (size_t)g_cyls * g_heads * g_secs;
    g_pack = calloc(nsec, (size_t)g_sec_words * sizeof(uint16_t));
    if (!g_pack) {
        fclose(f);
        return -1;
    }

    int rec_bytes = g_has_dummy ? 534 : 532;
    uint8_t *buf = malloc((size_t)rec_bytes);
    for (size_t i = 0; i < nsec; i++) {
        if (fread(buf, 1, (size_t)rec_bytes, f) != (size_t)rec_bytes)
            break;
        const uint8_t *p = buf + (g_has_dummy ? 2 : 0);
        uint16_t *dst = g_pack + i * (size_t)g_sec_words;
        for (int w = 0; w < g_sec_words; w++)
            dst[w] = rd_le(p + w * 2);
    }
    free(buf);
    fclose(f);
    g_loaded = 1;
    fprintf(stderr, "host: loaded %s (%d cyl, dummy=%d)\n", path, g_cyls, g_has_dummy);
    return 0;
}

static void write_pbm(const char *path)
{
    FILE *f = fopen(path, "w");
    if (!f)
        return;
    fprintf(f, "P1\n# Xerox Alto display field\n%d %d\n", ALTO_W, ALTO_H);
    for (int y = 0; y < ALTO_H; y++) {
        for (int x = 0; x < ALTO_W; x++)
            fputc(g_fb[y * ALTO_W + x] ? '1' : '0', f);
        fputc('\n', f);
    }
    fclose(f);
    fprintf(stderr, "host: wrote %s\n", path);
}

void host_init(uint32_t dummy)
{
    (void)dummy;
    const char *e;
    if ((e = getenv("ALTO_CYCLES")))
        g_max_cycles = strtoull(e, NULL, 0);
    if ((e = getenv("ALTO_TRACE")))
        g_trace = (uint32_t)strtoul(e, NULL, 0);
    if ((e = getenv("ALTO_DISK")))
        g_disk_path = e;
    if ((e = getenv("ALTO_FRAME")))
        g_frame_path = e;
    if ((e = getenv("ALTO_TYPE")))
        g_type = e;
    if ((e = getenv("ALTO_TYPE_AT")))
        g_type_at = strtoull(e, NULL, 0);
    if ((e = getenv("ALTO_ETHER_DEBUG")))
        g_ether_debug = (int)strtol(e, NULL, 0);
    if (g_type && g_type[0])
        fprintf(stderr, "host: will type %zu chars at cycle %llu\n",
                strlen(g_type), (unsigned long long)g_type_at);

    memset(g_fb, 0, sizeof g_fb);
    memset(g_cram, 0, sizeof g_cram);
    if (g_disk_path)
        load_disk(g_disk_path);
    else
        fprintf(stderr, "host: no ALTO_DISK; controller will report not-ready\n");
}

void host_shutdown(uint32_t dummy)
{
    (void)dummy;
    fprintf(stderr, "\nhost: task cycles");
    for (int t = 0; t < 16; t++)
        if (g_task_cyc[t])
            fprintf(stderr, " %d:%llu", t, (unsigned long long)g_task_cyc[t]);
    fprintf(stderr, "\n");
    if (g_loaded && g_pack) {
        host_disk_commit();
        fprintf(stderr, "host: labels serial 161 (Swatee):\n");
        size_t nsec = (size_t)g_cyls * (size_t)g_heads * (size_t)g_secs;
        for (size_t i = 0; i < nsec; i++) {
            uint16_t *rec = g_pack + i * (size_t)g_sec_words;
            if (rec[2 + 7] != 0161 && rec[2 + 5] != 0161)
                continue;
            int cyl = (int)(i / (size_t)(g_heads * g_secs));
            int rem = (int)(i % (size_t)(g_heads * g_secs));
            int hd = rem / g_secs;
            int sec = rem % g_secs;
            fprintf(stderr, "  %d/%d/%d hdr %06o %06o lab",
                    cyl, hd, sec, rec[0], rec[1]);
            for (int k = 0; k < 8; k++)
                fprintf(stderr, " %06o", rec[2 + k]);
            fprintf(stderr, "\n");
        }
    }
    if (g_last_field)
        write_pbm(g_frame_path);
    free(g_pack);
    g_pack = NULL;
}

void host_task_tick(uint32_t taskn)
{
    if (taskn < 16)
        g_task_cyc[taskn]++;
}

void host_dump_mem(uint32_t addr, uint32_t data)
{
    if ((g_dump_n++ % 8) == 0)
        fprintf(stderr, "\nmem %06o:", addr);
    fprintf(stderr, " %06o", data & 0xffff);
}

uint64_t host_max_cycles(void) { return g_max_cycles; }
uint32_t host_trace(void) { return g_trace; }

void host_log(uint64_t cyc, uint32_t taskn, uint32_t mpc,
              uint32_t pc, uint32_t ir, uint32_t waitn, uint32_t fields,
              uint32_t ac0, uint32_t ac1, uint32_t ac2, uint32_t ac3)
{
    fprintf(stderr,
            "cyc=%llu task=%o mpc=%04o pc=%06o ir=%06o wait=%u fields=%u"
            " ac0=%06o ac1=%06o ac2=%06o ac3=%06o\n",
            (unsigned long long)cyc, taskn, mpc, pc, ir, waitn, fields,
            ac0 & 0xffff, ac1 & 0xffff, ac2 & 0xffff, ac3 & 0xffff);
}

uint32_t host_ucode(uint32_t bank, uint32_t addr)
{
    addr &= 1023;
    if (bank == 1)
        return UROM1[addr];
    return UROM0[addr];
}

uint16_t host_constant(uint32_t addr) { return CROM[addr & 255]; }
uint8_t  host_acs(uint32_t addr) { return ACSROM[addr & 255]; }

uint32_t host_cram_word(uint32_t addr)
{
    return g_cram[addr & 1023];
}

uint16_t host_cram_half(uint32_t addr)
{
    uint32_t w = g_cram[addr & 1023] ^ 0x00088400u;
    return (uint16_t)((addr & 0x0400) ? (w >> 16) : w);
}

void host_cram_write(uint32_t addr, uint32_t data)
{
    g_cram[addr & 1023] = data;
}

uint32_t host_disk_loaded(void) { return (uint32_t)g_loaded; }
uint16_t host_disk_cylinders(void) { return (uint16_t)g_cyls; }

uint16_t host_disk_read_word(uint32_t idx)
{
    if (idx >= SEC_WORDS)
        return 0;
    return g_slice[idx];
}

void host_disk_write_word(uint32_t idx, uint16_t data)
{
    if (idx >= SEC_WORDS)
        return;
    /* .dsk records are header + label + data only. Gap/sync words are
       on the platter for timing but are not part of the image format. */
    int in_hdr = idx >= (HDR_OFF + 1) && idx <= (HDR_OFF + 3);
    int in_lbl = idx >= (LBL_OFF + 1) && idx <= (LBL_OFF + 9);
    int in_dat = idx >= (DAT_OFF + 1) && idx <= (DAT_OFF + 257);
    if (!in_hdr && !in_lbl && !in_dat)
        return;
    if (in_lbl && (idx == LBL_OFF + 8 || idx == LBL_OFF + 7) &&
        g_slice[idx] != data)
        fprintf(stderr, "host: label link c/h/s %d/%d/%d wi=%u %06o -> %06o\n",
                g_sel_c, g_sel_h, g_sel_s, idx, g_slice[idx], data);
    g_slice[idx] = data;
    g_dirty = 1;
}

void host_disk_select(uint32_t cyl, uint32_t head, uint32_t sec)
{
    if (g_dirty)
        host_disk_commit();
    if (cyl >= (uint32_t)g_cyls) cyl = 0;
    if (head > 1) head = 0;
    if (sec > 11) sec = 0;
    g_sel_c = (int)cyl;
    g_sel_h = (int)head;
    g_sel_s = (int)sec;
    rebuild_slice();
}

void host_disk_commit(void)
{
    if (!g_loaded || !g_dirty)
        return;
    uint16_t *rec = pack_ptr(g_sel_c, g_sel_h, g_sel_s);
    for (int i = 0, j = HEADER_N - 1; i < HEADER_N; i++, j--)
        rec[j] = g_slice[HDR_OFF + 1 + i];
    for (int i = 0, j = LABEL_N - 1; i < LABEL_N; i++, j--)
        rec[HEADER_N + j] = g_slice[LBL_OFF + 1 + i];
    for (int i = 0, j = DATA_N - 1; i < DATA_N; i++, j--)
        rec[HEADER_N + LABEL_N + j] = g_slice[DAT_OFF + 1 + i];
    g_dirty = 0;
    static const char *dlog;
    static int dlog_init;
    if (!dlog_init) {
        dlog = getenv("ALTO_DISK_LOG");
        dlog_init = 1;
    }
    if (dlog && dlog[0] && dlog[0] != '0') {
        fprintf(stderr, "host: commit %d/%d/%d hdr %06o %06o lab",
                g_sel_c, g_sel_h, g_sel_s, rec[0], rec[1]);
        for (int k = 0; k < 8; k++)
            fprintf(stderr, " %06o", rec[HEADER_N + k]);
        fprintf(stderr, "\n");
    }
}

void host_draw_word(uint32_t line, uint32_t wordn, uint16_t data, uint32_t lowres)
{
    if (line >= ALTO_H)
        return;
    int pix = lowres ? 32 : 16;
    int x0 = (int)wordn * pix;
    for (int b = 0; b < pix && x0 + b < ALTO_W; b++) {
        int bit = lowres ? (15 - (b / 2)) : (15 - b);
        uint8_t on = (uint8_t)((data >> bit) & 1);
        g_fb[line * ALTO_W + x0 + b] = on;
    }
}

void host_draw_cursor(uint32_t line, uint32_t x, uint32_t wob, uint16_t csr)
{
    if (line >= ALTO_H)
        return;
    for (int b = 0; b < 16; b++) {
        int xx = (int)x + b;
        if (xx < 0 || xx >= ALTO_W)
            continue;
        uint8_t on = (uint8_t)((csr >> (15 - b)) & 1);
        if (on)
            g_fb[line * ALTO_W + xx] = wob ? 1 : 0;
    }
}

void host_render_field(uint32_t fieldn)
{
    g_last_field = fieldn;
    if ((fieldn & 15) == 0)
        fprintf(stderr, "host: field %u\n", fieldn);
    /* Keep a snapshot when the bitmap is no longer a blank+cursor field. */
    if ((fieldn & 31) == 0 && fieldn != 0) {
        unsigned offs = 0;
        for (unsigned i = 0; i < sizeof g_fb; i++)
            if (!g_fb[i])
                offs++;
        if (offs > 200) {
            char path[64];
            snprintf(path, sizeof path, "alto_frame_f%u.pbm", fieldn);
            write_pbm(path);
        }
    }
}

uint16_t host_kb_read(uint16_t addr)
{
    if (addr >= 0xFE1C && addr <= 0xFE1F)
        return g_kbd[addr - 0xFE1C];
    if (addr >= 0xFE18 && addr <= 0xFE1B)
        return g_mouse;
    return 0xFFFF;
}

uint16_t host_mouse_bits(void)
{
    return 0x0000; /* no motion; CPU ORs with 0xFFF0 */
}

/* Microswitch keyboard, Alto bit 0 = MSB (HW manual §5.1 Figure 6). */
static int key_lookup(int c, int *word, uint16_t *mask, int *need_shift)
{
    *need_shift = 0;
    int u = c;
    if (c >= 'a' && c <= 'z')
        u = c - 32;
    struct { int ch; int w; uint16_t m; int sh; } map[] = {
        {'5',0,0x8000,0}, {'4',0,0x4000,0}, {'6',0,0x2000,0}, {'E',0,0x1000,0},
        {'7',0,0x0800,0}, {'D',0,0x0400,0}, {'U',0,0x0200,0}, {'V',0,0x0100,0},
        {'0',0,0x0080,0}, {'K',0,0x0040,0}, {'-',0,0x0020,0}, {'P',0,0x0010,0},
        {'/',0,0x0008,0}, {'\\',0,0x0004,0},
        {'3',1,0x8000,0}, {'2',1,0x4000,0}, {'W',1,0x2000,0}, {'Q',1,0x1000,0},
        {'S',1,0x0800,0}, {'A',1,0x0400,0}, {'9',1,0x0200,0}, {'I',1,0x0100,0},
        {'X',1,0x0080,0}, {'O',1,0x0040,0}, {'L',1,0x0020,0}, {',',1,0x0010,0},
        {'\'',1,0x0008,0}, {']',1,0x0004,0},
        {'1',2,0x8000,0}, {'F',2,0x1000,0}, {'C',2,0x0400,0}, {'J',2,0x0200,0},
        {'B',2,0x0100,0}, {'Z',2,0x0080,0}, {'.',2,0x0020,0}, {';',2,0x0010,0},
        {'R',3,0x8000,0}, {'T',3,0x4000,0}, {'G',3,0x2000,0}, {'Y',3,0x1000,0},
        {'H',3,0x0800,0}, {'8',3,0x0400,0}, {'N',3,0x0200,0}, {'M',3,0x0100,0},
        {' ',3,0x0040,0}, {'[',3,0x0020,0}, {'=',3,0x0010,0},
        {'\n',2,0x0008,0}, {'\r',2,0x0008,0}, {'\t',2,0x2000,0},
        {'\b',0,0x0001,0}, {27,2,0x4000,0},
        {'?',0,0x0008,1}, {':',2,0x0010,1}, {'+',3,0x0010,1},
        {'_',0,0x0020,1}, {'"',1,0x0008,1}, {'<',1,0x0010,1}, {'>',2,0x0020,1},
    };
    for (size_t i = 0; i < sizeof map / sizeof map[0]; i++) {
        if (map[i].ch == u || map[i].ch == c) {
            *word = map[i].w;
            *mask = map[i].m;
            *need_shift = map[i].sh;
            return 0;
        }
    }
    return -1;
}

static void kbd_clear(void)
{
    g_kbd[0] = g_kbd[1] = g_kbd[2] = g_kbd[3] = 0xFFFF;
}

static void kbd_down(int word, uint16_t mask, int shift)
{
    kbd_clear();
    if (shift)
        g_kbd[2] &= (uint16_t)~0x0040; /* LSHIFT */
    g_kbd[word] &= (uint16_t)~mask;
}

void host_poll_input(void)
{
    g_poll_cyc++;
    if (!g_type || g_type[g_type_i] == '\0')
        return;
    if (g_poll_cyc < g_type_at)
        return;

    if (g_type_phase == 0) {
        int w, sh;
        uint16_t m;
        unsigned char c = (unsigned char)g_type[g_type_i];
        if (key_lookup(c, &w, &m, &sh) != 0) {
            fprintf(stderr, "host: skip unknown key 0x%02x\n", c);
            g_type_i++;
            return;
        }
        kbd_down(w, m, sh);
        g_type_phase = 1;
        g_type_timer = 500000;  /* ~85 ms at 170 ns */
    } else if (g_type_phase == 1) {
        if (--g_type_timer == 0) {
            kbd_clear();
            g_type_phase = 2;
            g_type_timer = 200000;  /* ~34 ms gap */
        }
    } else if (--g_type_timer == 0) {
        g_type_i++;
        g_type_phase = 0;
        if (g_type[g_type_i] == '\0')
            fprintf(stderr, "host: finished typing\n");
    }
}

/* 3 Mbit Ethernet + Pup time (HW manual §7, Pup types 206B/207B). */
#define PUP_TYPE     0x0200   /* 1000B */

static int ether_debug(void)
{
    return g_ether_debug;
}

#define PT_TIME_REQ  0x86     /* 206B */
#define PT_TIME_REP  0x87     /* 207B */
#define ETH_HOST     66       /* 102B, this Alto (RSNF) */
#define ETH_SERVER   1        /* gateway / time server (must not be us) */

static uint32_t xerox_seconds(void)
{
    const char *e = getenv("ALTO_TIME");
    if (e && e[0])
        return (uint32_t)strtoul(e, NULL, 0);
    /* Executive MAKETIMELINE only prints a date for years 1983–1990
       (local, after zone/DST). 1985-06-16 20:00 GMT is 13:00 PDT. */
    return 2665252800u;
}

static void queue_time_reply(const uint16_t *req, int n)
{
    if (n < 12)
        return;
    /* req[0] dest<<8|src, [1] type, [2..] Pup */
    uint8_t src = (uint8_t)(req[0] & 0xff);
    uint16_t tctl_type = req[3];
    uint8_t ptype = (uint8_t)(tctl_type & 0xff);
    if ((req[1] != PUP_TYPE && req[1] != 0x0200) || ptype != PT_TIME_REQ)
        return;

    uint32_t secs = xerox_seconds();
    int i = 0;
    g_erx_pend[i++] = (uint16_t)((src << 8) | ETH_SERVER);
    g_erx_pend[i++] = PUP_TYPE;
    g_erx_pend[i++] = 32;                         /* pupOvBytes+10 */
    g_erx_pend[i++] = (tctl_type & 0xff00) | PT_TIME_REP;
    g_erx_pend[i++] = req[4];                     /* id hi */
    g_erx_pend[i++] = req[5];                     /* id lo */
    g_erx_pend[i++] = req[9];
    g_erx_pend[i++] = req[10];
    g_erx_pend[i++] = req[11];
    g_erx_pend[i++] = (uint16_t)ETH_SERVER;
    g_erx_pend[i++] = 0;
    g_erx_pend[i++] = 4;
    g_erx_pend[i++] = (uint16_t)(secs >> 16);
    g_erx_pend[i++] = (uint16_t)(secs & 0xffff);
    g_erx_pend[i++] = 0x0800;                     /* west, 8h PST */
    g_erx_pend[i++] = 121;                        /* beginDST (1 May-ish) */
    g_erx_pend[i++] = 305;                        /* endDST (1 Nov-ish) */
    g_erx_pend[i++] = 0xFFFF;                     /* checksum unused */
    g_erx_pend[i++] = 0;                          /* 3 Mbit CRC */
    g_erx_pend_n = i;
    if (ether_debug()) {
        fprintf(stderr, "host: ether time reply pending (%u sec)", secs);
        for (int k = 0; k < i; k++)
            fprintf(stderr, " %06o", g_erx_pend[k]);
        fprintf(stderr, "\n");
    }
}

void host_ether_tx_word(uint16_t w)
{
    if (g_etx_n < ETH_MAX)
        g_etx[g_etx_n++] = w;
}

void host_ether_tx_end(void)
{
    if (g_etx_n > 0) {
        if (ether_debug()) {
            fprintf(stderr, "host: ether tx %d words", g_etx_n);
            for (int i = 0; i < g_etx_n; i++)
                fprintf(stderr, " %06o", g_etx[i]);
            fprintf(stderr, "\n");
        }
        queue_time_reply(g_etx, g_etx_n);
    }
    g_etx_n = 0;
}

uint32_t host_ether_rx_count(void)
{
    return (uint32_t)(g_erx_n - g_erx_i);
}

void host_ether_reset(void)
{
    g_etx_n = 0;
    g_erx_n = 0;
    g_erx_i = 0;
    g_erx_pend_n = 0;
}

void host_ether_post(uint16_t status)
{
    if (ether_debug())
        fprintf(stderr, "host: ether post ep=%06o rxleft=%d\n",
                status, g_erx_n - g_erx_i);
}

void host_ether_pkt(uint16_t ebloc, uint16_t eip,
                    uint16_t w0, uint16_t w1, uint16_t w2, uint16_t w3)
{
    if (ether_debug())
        fprintf(stderr, "host: ether ESIDON ebloc=%06o eip=%06o  %06o %06o %06o %06o\n",
                ebloc, eip, w0, w1, w2, w3);
}

void host_ether_look(uint16_t peek, uint16_t bus)
{
    if (ether_debug())
        fprintf(stderr, "host: ether look peek=%06o bus=%06o\n", peek, bus);
}

void host_ether_ebfct(uint32_t cmd, uint32_t done, uint32_t late, uint32_t coll)
{
    if (ether_debug() && (cmd | done | late | coll))
        fprintf(stderr, "host: ether EBFCT cmd=%o done=%u late=%u coll=%u\n",
                cmd, done, late, coll);
}


void host_ether_rx_release(void)
{
    if (g_erx_pend_n == 0)
        return;
    memcpy(g_erx, g_erx_pend, (size_t)g_erx_pend_n * sizeof g_erx[0]);
    g_erx_n = g_erx_pend_n;
    g_erx_i = 0;
    g_erx_pend_n = 0;
    if (ether_debug())
        fprintf(stderr, "host: ether rx release %d words\n", g_erx_n);
}

void host_ether_rx_rewind(void)
{
    /* EPFCT while a packet was only partly consumed: put it back
       pending so the next EISFCT can try again. */
    if (g_erx_n == 0)
        return;
    if (g_erx_i == g_erx_n) {
        g_erx_n = 0;
        g_erx_i = 0;
        return;
    }
    if (g_erx_pend_n == 0) {
        memcpy(g_erx_pend, g_erx, (size_t)g_erx_n * sizeof g_erx[0]);
        g_erx_pend_n = g_erx_n;
    }
    if (ether_debug())
        fprintf(stderr, "host: ether rewind (was %d/%d)\n", g_erx_i, g_erx_n);
    g_erx_n = 0;
    g_erx_i = 0;
}

void host_ether_note(uint32_t ev)
{
    static unsigned n;
    if (ev == 1)
        fprintf(stderr, "host: ether EOSFCT\n");
    else if (ev == 2)
        fprintf(stderr, "host: ether EISFCT rxleft=%d\n", g_erx_n - g_erx_i);
    else if ((++n % 100) == 0)
        fprintf(stderr, "host: ether note %u n=%u\n", ev, n);
}

uint16_t host_ether_rx_word(void)
{
    if (g_erx_i >= g_erx_n)
        return 0;
    uint16_t w = g_erx[g_erx_i++];
    if (ether_debug() && (g_erx_i == 1 || g_erx_i == g_erx_n))
        fprintf(stderr, "host: ether rx %d/%d %06o\n", g_erx_i, g_erx_n, w);
    return w;
}
