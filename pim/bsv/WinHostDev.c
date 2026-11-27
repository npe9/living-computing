/* WinHostDev.c -- the C side of bsv/WinHostDev.bsv (Bluesim only): the
   host's screen, keyboard and mouse for the window hardware in Bluesim
   (docs/simpos/window_hardware_plan.md §4.1, H7s).  ALL OURS.

   Owner, 2026-11-26: "Figure out how to do emulate the mouse, keyboard and
   screen in bluesim."  This file is that emulation's host end:

   THE SCREEN, a virtual monitor on the scan-out's pixel stream (DE, the
   two sync levels, the 8-bit level, before the TMDS encoders): it locks
   on hsync and vsync, checks every line's and every frame's timing
   against ITS OWN mode table (a file made from psi/winscan.py's MODES by
   tools/win_kl0_host.py's `mode`, never from the RTL's winMode), and
   collects the window's dots (level 00 black = a set dot, ff white; 20,
   the border, outside the window) into a frame.
   THE KEYBOARD AND MOUSE: host events become PS/2 bytes for the bench's
   device models (WinInput.bsv mkWinPs2Dev), which drive the receivers'
   pins with the real waveform.  Host keys are USB HID usage IDs (SDL2's
   SDL_Scancode values are the same numbers); HOST[] below is the HID ->
   scan code set 2 table, checked against tools/wininput.py's HOST by
   `wininput.py hostcheck` on this file's `-DWHD_DUMP` build.
   THE HOST LINK: the bench's host UART bytes; the board's up records are
   parsed here (answers counted for flow control: at most 8 frames
   unanswered, WinLink.bsv), its event records (TYPE 3) passed to the kl0
   host, its down frames taken from the kl0 host.
   THE KL0 HOST: the command in WIN_KL0_HOST (tools/win_kl0_host.py) as a
   child on two pipes, lines:  C -> host "E KIND A B C FLAGS T" (hex) per
   event record, "Q T" input quiet (T the receivers' ms), "F T" the script
   is done; host -> C "D HEX..." frames' bytes, then "." ending its answer.
   Blocking: Bluesim waits while kl0 runs (deterministic).

   Two back ends, by environment:
     WIN_HOSTDEV_SCRIPT=FILE   scripted (the suite's): the primitive host
         script of tools/wininput.py expand, one action at a time, each
         after both devices are idle:
           kd U / ku U     key U (hex HID usage) down / up
           m DX DY BTNS    one mouse packet (PS/2 Y up)
           w MS            wait MS receiver milliseconds
           kraw B F / mraw B F   a raw byte with fault F (wininput.py)
           end
         when the script is done, devices idle and the link quiet, "F" to
         the host; when its frames are all answered and the link is quiet,
         the next whole frame is written to WIN_HOSTDEV_PBM (P4) and the
         run finishes.
     WINVIEW_SOCKET=PATH       interactive: a client of tools/winview
         (docs/simpos/winview_protocol.md): each changed frame is sent to
         the viewer, its key and mouse events come back.  Quiet input for
         WIN_QUIET_MS (default 500, longer than the kl0 host's double-click
         time) receiver ms sends "Q" to the host.  With WIN_HOSTDEV_PBM
         set, the viewer's E (a --play file's end) ends the run like the
         script's end: once its input is all sent, the devices idle, the
         link quiet and the kl0 host's last answer drawn, the next whole
         frame is written there and the run finishes.
       THE REAL-TIME DEVICES (interactive only; fixed 2026-11-26 after the
       owner's live run dropped hundreds of mouse bytes: every host motion
       event had become a packet sent back to back, up to ~230 a receiver
       second (a packet is 3 x 11 bits of 12 cycles plus gaps, ~430
       cycles), where the scaled bench's link carries ~150 event records
       up a second (16 bytes of 40 cycles each), so the receivers' 8-byte
       queue overflowed into broken packets):
         - THE CLOCK.  Free-running, mode 3's bench passes ~4,000 receiver
           ms a wall second (run_win_live.sh `speed`: 1.08 M pixel clocks
           a second, 10/27 sys cycles each, 100 a ms), so a person's
           double click (~150 ms) reached the kl0 host's adapter as ~600 ms,
           past its DCLICK_MS.  So each host event gets a receiver time:
           its gap from the one before (the viewer's W timestamps, wall
           ms; capped at ACTIVE_MS) after the one before's, never in the
           past; and while the person is active (within ACTIVE_MS wall of
           the last event, or events are waiting) the bench may not run
           ahead of the wall clock from the last event's time: it sleeps.
           Otherwise (kl0 drawing, idle) it runs free.  Events that came
           in while kl0 blocked the bench keep their gaps.  OURS.
         - THE MOUSE (a PS/2 mouse in stream mode, SECONDARY, as commonly
           published, e.g. A. Chapweske's PS/2 mouse protocol notes;
           CHECK: from memory, not fetched this session, and IBM's PS/2
           Technical Reference is not held; the wire frame and the
           10-16.7 kHz clock are WinInput.bsv's header's, the same grade):
           default sample rate 100 a second, a 3-byte movement packet sent
           at a sample when the mouse moved or a button changed, the
           motion between samples accumulated, 9-bit deltas).  So motion
           is coalesced to one packet a sample (WIN_MOUSE_RATE, default
           100), a delta of at most 255 a packet (the rest at the next
           samples: no overflow bits), and each button change gets its
           own packet once the mouse has reached the button event's
           place, so no click is lost or moved.  The packet's bytes go at
           the wire's speed (mkWinPs2Dev).  Positions are clamped to the
           decoder's 1,280 x 1,024 (WinInput.bsv mkWinMouseDec), so this
           model and the decoder never disagree.
         - THE KEYBOARD: a key's bytes at its receiver time, back to back
           at the wire's speed (a keyboard sends a code's bytes so).
   WIN_HOSTDEV_MODE=FILE: the monitor's mode, one line "ha hf hs hb va vf
   vs vb hpos vpos x0 y0 fw fh half [px py]" (half: the 2:1 view, whose
   viewer coordinates are doubled into the frame's; px py: the scan
   configuration's pan in frame dots, added to them, mode 3's (0, 24):
   without it, 2026-11-26, the person's clicks landed 24 frame rows above
   the dot pointed at).  WIN_HOSTDEV_MAXMS=N: fail after N
   receiver ms (a guard).  WIN_HOSTDEV_RUNFRAMES=N: finish after N whole
   frames (bsv/run_win_live.sh `speed`).  WIN_MOUSE_RATE=N: the mouse's
   samples a second (interactive; default 100).  WHD_TRACE=1: each host
   event's receiver time and each mouse sample on stderr (interactive).

   Prints one summary line at the end: "WinHostDev: ..." with the timing
   errors counted, which bsv/run_win_live.sh requires to be 0.
*/
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

/* ------------------------------------------------------------ HOST table */
/* HID usage -> (e0, set 2 code); 0 code = none.  Pause (0x48) is special. */
static const uint16_t HOST[256] = {
    [0x04] = 0x1c, [0x05] = 0x32, [0x06] = 0x21, [0x07] = 0x23, [0x08] = 0x24,
    [0x09] = 0x2b, [0x0a] = 0x34, [0x0b] = 0x33, [0x0c] = 0x43, [0x0d] = 0x3b,
    [0x0e] = 0x42, [0x0f] = 0x4b, [0x10] = 0x3a, [0x11] = 0x31, [0x12] = 0x44,
    [0x13] = 0x4d, [0x14] = 0x15, [0x15] = 0x2d, [0x16] = 0x1b, [0x17] = 0x2c,
    [0x18] = 0x3c, [0x19] = 0x2a, [0x1a] = 0x1d, [0x1b] = 0x22, [0x1c] = 0x35,
    [0x1d] = 0x1a,
    [0x1e] = 0x16, [0x1f] = 0x1e, [0x20] = 0x26, [0x21] = 0x25, [0x22] = 0x2e,
    [0x23] = 0x36, [0x24] = 0x3d, [0x25] = 0x3e, [0x26] = 0x46, [0x27] = 0x45,
    [0x28] = 0x5a, [0x29] = 0x76, [0x2a] = 0x66, [0x2b] = 0x0d, [0x2c] = 0x29,
    [0x2d] = 0x4e, [0x2e] = 0x55, [0x2f] = 0x54, [0x30] = 0x5b, [0x31] = 0x5d,
    [0x33] = 0x4c, [0x34] = 0x52, [0x35] = 0x0e, [0x36] = 0x41, [0x37] = 0x49,
    [0x38] = 0x4a, [0x39] = 0x58,
    [0x3a] = 0x05, [0x3b] = 0x06, [0x3c] = 0x04, [0x3d] = 0x0c, [0x3e] = 0x03,
    [0x3f] = 0x0b, [0x40] = 0x83, [0x41] = 0x0a, [0x42] = 0x01, [0x43] = 0x09,
    [0x44] = 0x78, [0x45] = 0x07,
    [0x49] = 0x170, [0x4c] = 0x171, [0x4f] = 0x174, [0x50] = 0x16b, [0x51] = 0x172,
    [0x52] = 0x175, [0x58] = 0x15a,
    [0xe0] = 0x14, [0xe1] = 0x12, [0xe2] = 0x11, [0xe4] = 0x114, [0xe5] = 0x59,
    [0xe6] = 0x111,
};
#define PAUSE 0x48

#ifdef WHD_DUMP
int main(void)
{
    for (int u = 0; u < 256; u++)
        if (HOST[u]) printf("%02x %d %02x\n", u, HOST[u] >> 8, HOST[u] & 0xff);
    return 0;
}
#else

/* ------------------------------------------------------------ byte queues */
#define QN (1 << 20)
typedef struct { uint32_t v[QN]; int h, t; } Q;
static int qn(Q *q) { return (q->t - q->h) & (QN - 1); }
static void qput(Q *q, uint32_t v)
{
    if (qn(q) == QN - 1) { fprintf(stderr, "WinHostDev: a queue overflowed\n"); return; }
    q->v[q->t] = v; q->t = (q->t + 1) & (QN - 1);
}
static uint32_t qget(Q *q) { uint32_t v = q->v[q->h]; q->h = (q->h + 1) & (QN - 1); return v; }

static Q kq, mq, downq;
static uint32_t msdiv = 100, now_lo;
static uint64_t now;                     /* sys cycles, from whd_tick */
static int scripted, failed, finished;
static long timing_errs;
static char *why;

static void fail(const char *m)
{
    if (!failed) { failed = 1; why = strdup(m); fprintf(stderr, "WinHostDev: %s\n", m); }
}

static void key_bytes(int usage, int down)
{
    if (usage == PAUSE) {
        static const uint8_t p[8] = {0xe1, 0x14, 0x77, 0xe1, 0xf0, 0x14, 0xf0, 0x77};
        if (down) for (int i = 0; i < 8; i++) qput(&kq, p[i]);
        return;
    }
    uint16_t c = usage >= 0 && usage < 256 ? HOST[usage] : 0;
    if (!c) { fprintf(stderr, "WinHostDev: host key %02x has no PS/2 code; ignored\n", usage); return; }
    if (c & 0x100) qput(&kq, 0xe0);
    if (!down) qput(&kq, 0xf0);
    qput(&kq, c & 0xff);
}

static void mouse_packet(int dx, int dy, int btns)
{
    qput(&mq, 0x08 | (btns & 7) | (dx < 0 ? 0x10 : 0) | (dy < 0 ? 0x20 : 0));
    qput(&mq, dx & 0xff);
    qput(&mq, dy & 0xff);
}

/* ------------------------------------------------------------ the kl0 host */
static FILE *hin, *hout;               /* to the host, from it */
static pid_t hpid;
static int frames_sent, answers;

static void host_start(void)
{
    const char *cmd = getenv("WIN_KL0_HOST");
    if (!cmd || !*cmd) return;
    int a[2], b[2];
    if (pipe(a) || pipe(b)) { fail("pipe failed"); return; }
    hpid = fork();
    if (hpid == 0) {
        dup2(a[0], 0); dup2(b[1], 1);
        close(a[0]); close(a[1]); close(b[0]); close(b[1]);
        execl("/bin/sh", "sh", "-c", cmd, (char *)0);
        _exit(127);
    }
    close(a[0]); close(b[1]);
    hin = fdopen(a[1], "w"); hout = fdopen(b[0], "r");
}

static int hexv(int c) { return c <= '9' ? c - '0' : (c | 0x20) - 'a' + 10; }

static void host_ask(const char *line)
{
    if (!hin) return;
    fprintf(hin, "%s\n", line);
    fflush(hin);
    char buf[1 << 16];
    for (;;) {
        if (!fgets(buf, sizeof buf, hout)) { fail("the kl0 host ended"); return; }
        if (buf[0] == '.') return;
        if (buf[0] == 'X') { fail(buf + 2); return; }
        if (buf[0] == 'D')
            for (char *p = buf + 2; p[0] && p[1] && p[0] != '\n'; p += 2)
                qput(&downq, hexv(p[0]) << 4 | hexv(p[1]));
    }
}

/* ------------------------------------------------------------ up records */
static uint8_t rec[300];
static int rn;
static long nevents, nlinkerr;
static uint32_t last_event_ms;
static int quiet_sent = 1;

static void up_byte(uint8_t b)
{
    if (rn == 0 && b != 0x5a) { fail("an up byte outside a record"); return; }
    rec[rn++] = b;
    if (rn < 4 || rn < rec[3] + 6) return;
    int typ = rec[2], len = rec[3];
    rn = 0;
    if (typ == 0 || typ == 2) answers++;
    if (typ == 2) nlinkerr++;
    if (typ == 0 && rec[4] != 0) {
        char m[64];
        snprintf(m, sizeof m, "command %d answered status %d", rec[1], rec[4]);
        fail(m);
    }
    if (typ == 3 && len == 10) {
        char line[96];
        snprintf(line, sizeof line, "E %d %04x %04x %04x %02x %04x", rec[4],
                 rec[5] << 8 | rec[6], rec[7] << 8 | rec[8], rec[9] << 8 | rec[10], rec[11],
                 rec[12] << 8 | rec[13]);
        nevents++;
        last_event_ms = (uint32_t)(now / msdiv);
        quiet_sent = 0;
        if (hin) { fprintf(hin, "%s\n", line); fflush(hin); }
    }
}

/* ------------------------------------------------------------ the monitor */
typedef struct { int ha, hf, hs, hb, va, vf, vs, vb, hpos, vpos, x0, y0, fw, fh, half, px, py; } Mode;
static Mode M;
static int have_mode;
static uint8_t *img, *last_sent;       /* fw x fh, 1 byte a dot */
static long hcount = -1;               /* pixels since this line's hsync start */
static int prev_hs, prev_vs, prev_de, line_de, line_vs, de_run, lines, vline = -1;
static int vs_lines, active_lines, locked_frames, in_frame_y = -1, first_active = -1;
static long frames;
static int capture, captured;
static void viewer_frame(void);

static void terr(const char *what, long got, long want)
{
    if (locked_frames < 1) return;     /* the first frame after lock-on is not judged */
    timing_errs++;
    if (timing_errs <= 8)
        fprintf(stderr, "WinHostDev monitor: frame %ld line %d: %s %ld, the mode says %ld\n",
                frames, lines, what, got, want);
}

static void frame_end(void)
{
    /* a whole frame since lock-on: judge the vertical counts */
    if (vline >= 0) {
        if (vs_lines != M.vs) terr("vsync lines", vs_lines, M.vs);
        if (active_lines != M.va) terr("active lines", active_lines, M.va);
        if (lines != M.va + M.vf + M.vs + M.vb) terr("lines", lines, M.va + M.vf + M.vs + M.vb);
        /* the back porch: the first active line's place after the vsync's start */
        if (first_active != M.vs + M.vb) terr("first active line", first_active, M.vs + M.vb);
        locked_frames++;
        frames++;
        if (capture == 2) {
            const char *p = getenv("WIN_HOSTDEV_PBM");
            FILE *f = p ? fopen(p, "wb") : 0;
            if (!f) fail("cannot write WIN_HOSTDEV_PBM");
            else {
                fprintf(f, "P4\n%d %d\n", M.fw, M.fh);
                for (int y = 0; y < M.fh; y++)
                    for (int x = 0; x < M.fw; x += 8) {
                        int v = 0;
                        for (int k = 0; k < 8; k++) v = v << 1 | (x + k < M.fw ? img[y * M.fw + x + k] : 0);
                        fputc(v, f);
                    }
                fclose(f);
            }
            capture = 3; captured = 1;
        }
        if (capture == 1) capture = 2;
        static long runframes = -1;
        if (runframes < 0) { const char *x = getenv("WIN_HOSTDEV_RUNFRAMES"); runframes = x ? atol(x) : 0; }
        if (runframes && frames >= runframes) captured = 1;   /* the speed measurement */
        if (!scripted) viewer_frame();
    }
    vline = 0; lines = 0; vs_lines = 0; active_lines = 0; in_frame_y = -1; first_active = -1;
}

/* one pixel clock: v = de << 10 | vs << 9 | hs << 8 | level (sync LEVELS) */
static void pixel(uint32_t v)
{
    if (!have_mode) return;
    int de = v >> 10 & 1, vsl = v >> 9 & 1, hsl = v >> 8 & 1, lev = v & 0xff;
    int hs = hsl == M.hpos, vs = vsl == M.vpos;          /* active */
    long ht = M.ha + M.hf + M.hs + M.hb;
    if (hs && !prev_hs) {
        /* a line ends at its hsync's start */
        if (hcount >= 0) {
            if (hcount != ht) terr("line length", hcount, ht);
            if (line_de && de_run != M.ha) terr("active pixels", de_run, M.ha);
            if (line_de) active_lines++;
            if (line_de && first_active < 0) first_active = lines;
            if (line_vs) vs_lines++;
            lines++;
        }
        hcount = 0; line_de = 0; de_run = 0; line_vs = 0;
    }
    if (hcount < 0) { prev_hs = hs; prev_vs = vs; prev_de = de; return; }
    if (!hs && prev_hs && hcount != M.hs) terr("hsync width", hcount, M.hs);
    if (de && !prev_de && hcount != M.hs + M.hb) terr("active start", hcount, M.hs + M.hb);
    if (vs != prev_vs) {
        if (hcount != M.hs + M.hb) terr("vsync edge at", hcount, M.hs + M.hb);
        if (vs) frame_end();
        else if (vline >= 0) vline = 1;
    }
    if (hcount == M.hs + M.hb && vs) line_vs = 1;
    if (de) {
        if (!line_de && vline >= 0) in_frame_y++;
        line_de = 1;
        int x = de_run, y = in_frame_y;
        de_run++;
        if (vline >= 0 && y >= 0) {
            int u = x - M.x0, w = y - M.y0;
            int inwin = u >= 0 && u < M.fw && w >= 0 && w < M.fh;
            if (inwin) {
                if (lev != 0 && lev != 0xff) terr("a window level", lev, 0);
                img[w * M.fw + u] = lev == 0;
            }
            else if (lev != 0x20) terr("a border level", lev, 0x20);
        }
    }
    hcount++;
    prev_hs = hs; prev_vs = vs; prev_de = de;
}

/* ------------------------------------------------------------ the viewer */
static int vfd = -1;
static int mouse_x = 640, mouse_y = 472, mouse_b;

static int write_all(int fd, const void *p, size_t n)
{
    const uint8_t *b = p;
    while (n) {
        ssize_t k = write(fd, b, n);
        if (k < 0 && (errno == EINTR || errno == EAGAIN)) {
            /* the socket is non-blocking (for reading): wait until it drains */
            struct pollfd pf = {fd, POLLOUT, 0};
            poll(&pf, 1, 100);
            continue;
        }
        if (k <= 0) return -1;
        b += k; n -= (size_t)k;
    }
    return 0;
}

static void msg(char typ, const uint8_t *pay, uint32_t len)
{
    if (vfd < 0) return;
    uint8_t h[5] = {(uint8_t)typ, len >> 24, len >> 16, len >> 8, len};
    if (write_all(vfd, h, 5) || write_all(vfd, pay, len)) { close(vfd); vfd = -1; finished = 1; }
}

static void viewer_open(const char *path)
{
    vfd = socket(AF_UNIX, SOCK_STREAM, 0);
    struct sockaddr_un a;
    memset(&a, 0, sizeof a);
    a.sun_family = AF_UNIX;
    if (strlen(path) >= sizeof a.sun_path) { fail("the WINVIEW_SOCKET path is too long"); return; }
    strncpy(a.sun_path, path, sizeof a.sun_path - 1);
    if (connect(vfd, (struct sockaddr *)&a, sizeof a)) {
        perror(path); close(vfd); vfd = -1; fail("cannot reach the viewer"); return;
    }
    char t[64];
    int n = snprintf(t, sizeof t, "    Bluesim: window hardware");
    t[0] = M.fw >> 8; t[1] = M.fw; t[2] = M.fh >> 8; t[3] = M.fh;
    msg('H', (uint8_t *)t, (uint32_t)n);
    fcntl(vfd, F_SETFL, O_NONBLOCK);
}

static void viewer_frame(void)
{
    if (vfd < 0) return;
    size_t n = (size_t)M.fw * M.fh;
    if (last_sent && !memcmp(last_sent, img, n)) return;
    if (!last_sent) last_sent = malloc(n);
    memcpy(last_sent, img, n);
    int rowb = (M.fw + 7) / 8;
    uint32_t len = 4 + (uint32_t)rowb * M.fh;
    uint8_t *p = calloc(len, 1);
    p[0] = M.fw >> 8; p[1] = M.fw; p[2] = M.fh >> 8; p[3] = M.fh;
    for (int y = 0; y < M.fh; y++)
        for (int x = 0; x < M.fw; x++)
            if (img[y * M.fw + x]) p[4 + y * rowb + x / 8] |= 0x80 >> (x & 7);
    msg('F', p, len);
    free(p);
}

/* --- the real-time devices (the header's THE REAL-TIME DEVICES) --- */
#define ACTIVE_MS 1000
#define HN (1 << 16)
typedef struct { char typ; int a, b, x, y; uint32_t r; } HEv;   /* a host event, its receiver ms */
static HEv hev[HN];
static int hh, ht;                       /* the host events not yet due */
typedef struct { int edge, bit, down, x, y; } MItem;
static MItem mit[HN];
static int mh, mt;                       /* the mouse's motion and button changes, due */
static int tgt_x = 640, tgt_y = 472;     /* where the mouse is to go */
static uint32_t stamp, prev_stamp, prev_r, next_sample;
static int have_stamp, have_prev, viewer_done;
static double anchor_wall, prev_wall;
static uint32_t anchor_r;
static long host_events, mouse_packets, throttle_sleeps;

static double wall_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e3 + ts.tv_nsec / 1e6;
}

static int clampi(int v, int lo, int hi) { return v < lo ? lo : v > hi ? hi : v; }

static int tracing(void)
{
    static int t = -1;
    if (t < 0) t = getenv("WHD_TRACE") != 0;
    return t;
}

/* a host event from the viewer: its receiver time, then the queue */
static void host_event(char typ, int a, int b, int x, int y)
{
    uint32_t now_ms = (uint32_t)(now / msdiv);
    double w = wall_ms();
    uint32_t gap = have_stamp ? stamp - prev_stamp : (uint32_t)(w - prev_wall);
    if (gap > ACTIVE_MS) gap = ACTIVE_MS;
    uint32_t r = have_prev ? prev_r + gap : now_ms;
    if ((int32_t)(r - now_ms) < 0) r = now_ms;
    if (have_stamp) prev_stamp = stamp;
    prev_r = r; prev_wall = w; have_prev = 1; have_stamp = 0;
    anchor_r = r; anchor_wall = w;
    if (((ht + 1) & (HN - 1)) == hh) { fprintf(stderr, "WinHostDev: the host event queue overflowed\n"); return; }
    if (typ != 'K') {
        if (M.half) { x *= 2; y *= 2; }                 /* the viewer shows the 2:1 view (mode 3) */
        x += M.px; y += M.py;                           /* and the frame from the pan on */
    }
    hev[ht] = (HEv){typ, a, b, clampi(x, 0, 1279), clampi(y, 0, 1023), r};
    if (tracing()) fprintf(stderr, "TR ev %c now %u r %u stamp %u gap %u\n", typ, now_ms, r, stamp, gap);
    ht = (ht + 1) & (HN - 1);
    host_events++;
}

static void mitem(int edge, int bit, int down, int x, int y)
{
    if (((mt + 1) & (HN - 1)) == mh) { fprintf(stderr, "WinHostDev: the mouse queue overflowed\n"); return; }
    mit[mt] = (MItem){edge, bit, down, x, y};
    mt = (mt + 1) & (HN - 1);
}

/* the host events now due: keys to the keyboard's bytes, mouse events to
   the mouse's items */
static void release_due(uint32_t now_ms)
{
    while (hh != ht && (int32_t)(hev[hh].r - now_ms) <= 0) {
        HEv *e = &hev[hh];
        if (e->typ == 'K') key_bytes(e->b, e->a);
        else if (e->typ == 'M') mitem(0, 0, 0, e->x, e->y);
        else mitem(1, e->a, e->b, e->x, e->y);
        hh = (hh + 1) & (HN - 1);
    }
}

/* one sample of the mouse: at most one packet, at most one button change */
static void mouse_sample(void)
{
    while (mh != mt && !mit[mh].edge) { tgt_x = mit[mh].x; tgt_y = mit[mh].y; mh = (mh + 1) & (HN - 1); }
    int edge = mh != mt;
    if (edge) { tgt_x = mit[mh].x; tgt_y = mit[mh].y; }
    int dx = clampi(tgt_x - mouse_x, -255, 255), dy = clampi(tgt_y - mouse_y, -255, 255);
    mouse_x += dx; mouse_y += dy;
    int changed = 0;
    if (edge && mouse_x == tgt_x && mouse_y == tgt_y) {
        int bit = 1 << mit[mh].bit;
        mouse_b = mit[mh].down ? mouse_b | bit : mouse_b & ~bit;
        mh = (mh + 1) & (HN - 1);
        changed = 1;
    }
    if (dx || dy || changed) { mouse_packet(dx, -dy, mouse_b); mouse_packets++; }
    if (tracing())
        fprintf(stderr, "TR sample ms %u d %d %d b %d at %d %d\n", (uint32_t)(now / msdiv), dx, dy, mouse_b,
                mouse_x, mouse_y);
}

static int input_pending(void)
{
    return hh != ht || mh != mt || mouse_x != tgt_x || mouse_y != tgt_y;
}

static void viewer_poll(void)
{
    static uint8_t buf[256];
    static int bn;
    if (vfd < 0) return;
    for (;;) {
        ssize_t k = read(vfd, buf + bn, sizeof buf - bn);
        if (k == 0) { finished = 1; return; }
        if (k < 0) return;
        bn += (int)k;
        while (bn >= 5) {
            uint32_t len = (uint32_t)buf[1] << 24 | buf[2] << 16 | buf[3] << 8 | buf[4];
            if (len > sizeof buf - 5) { fail("a viewer message too long"); return; }
            if (bn < 5 + (int)len) break;
            uint8_t *p = buf + 5;
            switch (buf[0]) {
            case 'W':
                if (len == 4) { stamp = (uint32_t)p[0] << 24 | p[1] << 16 | p[2] << 8 | p[3]; have_stamp = 1; }
                break;
            case 'K': if (len == 3) host_event('K', p[0], p[1] << 8 | p[2], 0, 0); break;
            case 'M': if (len == 4) host_event('M', 0, 0, p[0] << 8 | p[1], p[2] << 8 | p[3]); break;
            case 'B': if (len == 6) host_event('B', p[0], p[1], p[2] << 8 | p[3], p[4] << 8 | p[5]); break;
            case 'E': viewer_done = 1; break;
            case 'Q': finished = 1; break;
            }
            memmove(buf, buf + 5 + len, bn - 5 - len);
            bn -= 5 + (int)len;
        }
    }
}

/* while the person is active, the bench may not run ahead of the wall
   clock from the last host event's time */
static void throttle(uint32_t now_ms)
{
    if (!have_prev) return;
    double w = wall_ms();
    if (w - anchor_wall >= ACTIVE_MS && hh == ht) return;
    double ahead = ((double)(int32_t)(now_ms - anchor_r)) - (w - anchor_wall);
    if (ahead > 0.5) {
        usleep((useconds_t)((ahead > 20 ? 20 : ahead) * 1000));
        throttle_sleeps++;
    }
}

/* ------------------------------------------------------------ the script */
static FILE *script;
static int script_done;
static uint64_t wait_until;
static int final_sent;
static long no_progress_frames;

static void script_step(int idle)
{
    if (script_done || !idle || now < wait_until || qn(&kq) || qn(&mq)) return;
    char line[128];
    if (!fgets(line, sizeof line, script)) { script_done = 1; return; }
    unsigned a, f;
    int dx, dy, bt;
    if (sscanf(line, "kd %x", &a) == 1) key_bytes((int)a, 1);
    else if (sscanf(line, "ku %x", &a) == 1) key_bytes((int)a, 0);
    else if (sscanf(line, "m %d %d %d", &dx, &dy, &bt) == 3) mouse_packet(dx, dy, bt);
    else if (sscanf(line, "w %u", &a) == 1) wait_until = now + (uint64_t)a * msdiv;
    else if (sscanf(line, "kraw %x %u", &a, &f) == 2) qput(&kq, f << 8 | a);
    else if (sscanf(line, "mraw %x %u", &a, &f) == 2) qput(&mq, f << 8 | a);
    else if (!strncmp(line, "end", 3)) script_done = 1;
    else fail("a script line it cannot read");
}

/* ------------------------------------------------------------ BDPI */
static int inited;

static void init(void)
{
    if (inited) return;
    inited = 1;
    signal(SIGPIPE, SIG_IGN);
    const char *mf = getenv("WIN_HOSTDEV_MODE");
    FILE *f = mf ? fopen(mf, "r") : 0;
    if (f && fscanf(f, "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d", &M.ha, &M.hf, &M.hs, &M.hb,
                    &M.va, &M.vf, &M.vs, &M.vb, &M.hpos, &M.vpos, &M.x0, &M.y0, &M.fw, &M.fh,
                    &M.half) == 15) {
        if (fscanf(f, "%d %d", &M.px, &M.py) != 2) M.px = M.py = 0;
        have_mode = 1;
        img = calloc((size_t)M.fw * M.fh, 1);
    }
    else fail("no WIN_HOSTDEV_MODE");
    if (f) fclose(f);
    const char *s = getenv("WIN_HOSTDEV_SCRIPT");
    if (s && *s) {
        scripted = 1;
        script = fopen(s, "r");
        if (!script) fail("cannot read WIN_HOSTDEV_SCRIPT");
    }
    host_start();
    const char *v = getenv("WINVIEW_SOCKET");
    if (!scripted && v && *v) viewer_open(v);
    else if (!scripted) fail("neither WIN_HOSTDEV_SCRIPT nor WINVIEW_SOCKET");
    host_ask("Q 0");                      /* the screen before any input */
}

uint32_t whd_init(uint32_t div)
{
    msdiv = div ? div : 1;
    init();
    return scripted ? 1 : 2;
}

/* every few sys cycles.  idle: bit 0 the keyboard model, bit 1 the mouse's,
   bit 2 the link (both UARTs quiet, no byte queued).  Returns bit 0 to
   finish, bit 1 a failure. */
uint32_t whd_tick(uint32_t cyc_lo, uint32_t cyc_hi, uint32_t idle)
{
    init();
    now = (uint64_t)cyc_hi << 32 | cyc_lo;
    now_lo = cyc_lo;
    int dev_idle = (idle & 3) == 3 && !qn(&kq) && !qn(&mq);
    int link_idle = (idle & 4) && !qn(&downq) && answers >= frames_sent;
    uint32_t ms = (uint32_t)(now / msdiv);
    if (scripted) {
        script_step(dev_idle);
        if (script_done && dev_idle && link_idle && !final_sent && ms > last_event_ms + 20) {
            char l[32];
            snprintf(l, sizeof l, "F %x", ms);
            host_ask(l);
            final_sent = 1;
        }
        else if (final_sent && link_idle && !capture && !getenv("WIN_HOSTDEV_RUNFRAMES")) capture = 1;
    }
    else {
        static uint32_t polled, period, last_input_ms;
        if (!period) {
            const char *r = getenv("WIN_MOUSE_RATE");
            int rate = r ? atoi(r) : 100;
            period = rate > 0 && rate <= 1000 ? 1000 / (uint32_t)rate : 10;
        }
        if (cyc_lo - polled > 256) { polled = cyc_lo; viewer_poll(); }
        if (hh != ht && (int32_t)(hev[hh].r - ms) <= 0) { release_due(ms); last_input_ms = ms; }
        if ((idle & 2) && !qn(&mq) && (int32_t)(ms - next_sample) >= 0 &&
            (mh != mt || mouse_x != tgt_x || mouse_y != tgt_y)) {
            mouse_sample();
            next_sample = ms + period;
            last_input_ms = ms;
        }
        throttle(ms);
        const char *q = getenv("WIN_QUIET_MS");
        uint32_t quiet = q ? (uint32_t)atoi(q) : 500;
        if (!quiet_sent && dev_idle && !input_pending() && ms > last_event_ms + quiet) {
            char l[32];
            snprintf(l, sizeof l, "Q %x", ms);
            host_ask(l);
            quiet_sent = 1;
        }
        /* a --play file's end (E): finish as the script's end does */
        if (viewer_done && !capture && getenv("WIN_HOSTDEV_PBM") && quiet_sent && dev_idle && link_idle &&
            !input_pending() && ms > last_input_ms + quiet && ms > last_event_ms + quiet)
            capture = 1;
    }
    static long maxms = -1;
    if (maxms < 0) { const char *x = getenv("WIN_HOSTDEV_MAXMS"); maxms = x ? atol(x) : 0; }
    if (maxms && ms > (uint32_t)maxms) fail("no end within WIN_HOSTDEV_MAXMS");
    if (captured || failed) finished = 1;
    return (finished ? 1 : 0) | (failed ? 2 : 0);
}

/* the next byte for a device: bit 31 a byte, bits 11-8 its fault */
uint32_t whd_kbd(void) { return qn(&kq) ? 0x80000000u | qget(&kq) : 0; }
uint32_t whd_mouse(void) { return qn(&mq) ? 0x80000000u | qget(&mq) : 0; }

/* a byte read on the board's transmit line */
void whd_up(uint32_t b) { up_byte((uint8_t)b); }

/* the next byte to send down: frames of 18 bytes, at most 8 unanswered */
uint32_t whd_down(void)
{
    static int in_frame;
    if (!qn(&downq)) return 0;
    if (in_frame == 0) {
        if (frames_sent >= answers + 8) return 0;
        frames_sent++;
    }
    in_frame = (in_frame + 1) % 18;
    return 0x80000000u | qget(&downq);
}

void whd_px(uint32_t v) { pixel(v); }

void whd_report(void)
{
    if (hin) { fprintf(hin, "X\n"); fflush(hin); fclose(hin); hin = 0; }
    if (hpid > 0) { int st; waitpid(hpid, &st, 0); hpid = 0; }
    char extra[128] = "";
    if (!scripted)
        snprintf(extra, sizeof extra, "; %ld host events, %ld mouse packets, %ld throttle sleeps",
                 host_events, mouse_packets, throttle_sleeps);
    printf("WinHostDev: %s; %ld frames seen, %ld timing errors, %ld input events up, %ld link errors, "
           "%d frames down, %d answers%s%s%s\n", failed ? "FAILED" : "done", frames, timing_errs, nevents,
           nlinkerr, frames_sent, answers, extra, failed ? ": " : "", failed ? why : "");
    fflush(stdout);
}
#endif
