/* winview -- a standalone SDL2 viewer for the SIMPOS window system's
   screen, keyboard and mouse (OURS, 2026-11-26).

   Owner, 2026-11-26: "Figure out how to do emulate the mouse, keyboard and
   screen in bluesim." and "It's okay to make an emulator to go with this
   so we can test look and feel".  The viewer is the emulated monitor,
   keyboard and mouse.  It is a separate program, so that both the Bluesim
   window hardware (bsv/WinHostDev.c, a client) and the fast software
   window stack (kl0 and psi/windev.py, a later client) can drive it.  The
   protocol is docs/simpos/winview_protocol.md; tools/winview_client.py is
   a stdlib Python client of it.

   It listens on a Unix socket and serves one client at a time:
     in   H (size, title), F (a whole 1-bit frame), R (a rectangle), T (title)
     out  K (a key, by USB HID usage = SDL_Scancode), M (the mouse moved),
          B (a button), Q (the window was closed)
   A dot of 1 is black on white paper (the PSI's, TM-115 p74-76).

   Use:  winview SOCKET [--scale N] [--dump FILE.pbm] [--fake-events]
                        [--frames N] [--events FILE] [--linger MS] [--no-fit]
     --scale N      each dot N x N pixels (default 1; 2 for 640 x 480); a
                    window larger than the display's usable area is made
                    smaller to fit (unless --no-fit or the dummy driver),
                    and it can be resized: the mouse is always reported in
                    dots, by the window's real size (2026-11-26, M11)
     --dump FILE    write each frame received as a P4 PBM (for checks),
                    through FILE.tmp and a rename, so it is never half written
     --fake-events  after the first frame, push a key A press and release,
                    a mouse motion to (10, 20) and a left click there into
                    SDL's own queue, so they go out through the same code
                    as a user's (the headless self-check: SDL_VIDEODRIVER=dummy)
     --frames N     exit after N frames received
     --events FILE  (window M11, OURS) after the first frame, push the
                    file's events into SDL's queue at their times (the
                    first one at once): tools/simpos_live.py's event lines
                    `MS K DOWN USAGE`, `MS M X Y`, `MS B BUTTON DOWN X Y`
                    (X, Y in dots; other lines ignored), so a scripted
                    session goes out through the same code as a user's
     --linger MS    with --events: once all are pushed and no frame has
                    come for MS ms (default 3000), close (Q) and exit
   K, M and B end with a 4-byte time stamp, the event's SDL time in ms
   (window M11: clicks are classified by when they were made, not when the
   client read them; a client that reads fields by offset ignores it).
   Build: tools/winview/build.sh (cc, pkg-config sdl2).
*/
#include <SDL.h>
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

static int lfd = -1, cfd = -1;
static SDL_Window *win;
static SDL_Renderer *ren;
static SDL_Texture *tex;
static int W = 640, H = 480, scale = 1;
static uint32_t *pix;                 /* W x H ARGB */
static const char *dump;
static long nframes, maxframes;
static int fake, faked;
static const char *events_path;
static long linger = 3000;
static int nofit;
static uint32_t last_frame;            /* SDL ms of the last frame received */

static int write_all(int fd, const void *p, size_t n)
{
    const uint8_t *b = p;
    while (n) {
        ssize_t k = write(fd, b, n);
        if (k < 0 && (errno == EINTR || errno == EAGAIN)) continue;
        if (k <= 0) return -1;
        b += k; n -= (size_t)k;
    }
    return 0;
}

static void send_msg(char typ, const uint8_t *p, uint32_t len)
{
    if (cfd < 0) return;
    uint8_t h[5] = {(uint8_t)typ, len >> 24, len >> 16, len >> 8, len};
    if (write_all(cfd, h, 5) || write_all(cfd, p, len)) { close(cfd); cfd = -1; }
}

static void resize(int w, int h)
{
    W = w; H = h;
    free(pix);
    pix = malloc((size_t)W * H * 4);
    for (int i = 0; i < W * H; i++) pix[i] = 0xffffffff;
    if (tex) SDL_DestroyTexture(tex);
    int ww = W * scale, wh = H * scale;
    SDL_Rect r;
    const char *drv = SDL_GetCurrentVideoDriver();
    if (!nofit && !(drv && !strcmp(drv, "dummy")) && !SDL_GetDisplayUsableBounds(0, &r)
        && r.w > 0 && r.h > 60 && (ww > r.w || wh > r.h - 30)) {
        /* fit the usable area (less a title bar), keeping the aspect */
        double k = (double)r.w / ww, k2 = (double)(r.h - 30) / wh;
        if (k2 < k) k = k2;
        ww = (int)(ww * k); wh = (int)(wh * k);
        fprintf(stderr, "winview: the window is made %d x %d to fit the display\n", ww, wh);
    }
    SDL_SetWindowSize(win, ww, wh);
    tex = SDL_CreateTexture(ren, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STREAMING, W, H);
}

static void present(void)
{
    SDL_UpdateTexture(tex, NULL, pix, W * 4);
    SDL_RenderClear(ren);
    SDL_RenderCopy(ren, tex, NULL, NULL);
    SDL_RenderPresent(ren);
}

static void write_dump(void)
{
    if (!dump) return;
    char tmp[1024];
    snprintf(tmp, sizeof tmp, "%s.tmp", dump);
    FILE *f = fopen(tmp, "wb");
    if (!f) { perror(tmp); return; }
    fprintf(f, "P4\n%d %d\n", W, H);
    for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x += 8) {
            int v = 0;
            for (int k = 0; k < 8; k++)
                v = v << 1 | (x + k < W && pix[y * W + x + k] == 0xff000000u);
            fputc(v, f);
        }
    fclose(f);
    if (rename(tmp, dump)) perror(dump);
}

/* a rectangle of 1-bit rows (MSB first, rows padded to a byte) at (x, y) */
static void blit(int x0, int y0, int w, int h, const uint8_t *rows)
{
    int rb = (w + 7) / 8;
    for (int y = 0; y < h; y++)
        for (int x = 0; x < w; x++) {
            int X = x0 + x, Y = y0 + y;
            if (X < 0 || Y < 0 || X >= W || Y >= H) continue;
            int on = rows[y * rb + x / 8] >> (7 - (x & 7)) & 1;
            pix[Y * W + X] = on ? 0xff000000u : 0xffffffffu;
        }
}

static uint8_t *ibuf;
static size_t ibn, icap;

static void handle(char typ, const uint8_t *p, uint32_t len)
{
    switch (typ) {
    case 'H':
        if (len >= 4) {
            resize(p[0] << 8 | p[1], p[2] << 8 | p[3]);
            char t[128];
            int n = len - 4 < sizeof t - 1 ? (int)len - 4 : (int)sizeof t - 1;
            memcpy(t, p + 4, n); t[n] = 0;
            SDL_SetWindowTitle(win, n ? t : "winview");
        }
        break;
    case 'T': {
        char t[128];
        int n = len < sizeof t - 1 ? (int)len : (int)sizeof t - 1;
        memcpy(t, p, n); t[n] = 0;
        SDL_SetWindowTitle(win, t);
        break; }
    case 'F':
        if (len >= 4) {
            int w = p[0] << 8 | p[1], h = p[2] << 8 | p[3];
            if (w != W || h != H) resize(w, h);
            if (len >= 4 + (uint32_t)((w + 7) / 8) * h) blit(0, 0, w, h, p + 4);
            nframes++;
            last_frame = SDL_GetTicks();
            write_dump();
            present();
        }
        break;
    case 'R':
        if (len >= 8) {
            int x = p[0] << 8 | p[1], y = p[2] << 8 | p[3], w = p[4] << 8 | p[5], h = p[6] << 8 | p[7];
            if (len >= 8 + (uint32_t)((w + 7) / 8) * h) blit(x, y, w, h, p + 8);
            nframes++;
            last_frame = SDL_GetTicks();
            write_dump();
            present();
        }
        break;
    }
}

static void read_client(void)
{
    for (;;) {
        if (icap - ibn < 65536) { icap = icap * 2 + 65536; ibuf = realloc(ibuf, icap); }
        ssize_t k = read(cfd, ibuf + ibn, icap - ibn);
        if (k == 0) { close(cfd); cfd = -1; ibn = 0; fprintf(stderr, "winview: the client left\n"); return; }
        if (k < 0) return;
        ibn += (size_t)k;
        size_t o = 0;
        while (ibn - o >= 5) {
            uint32_t len = (uint32_t)ibuf[o + 1] << 24 | ibuf[o + 2] << 16 | ibuf[o + 3] << 8 | ibuf[o + 4];
            if (ibn - o < 5 + (size_t)len) break;
            handle((char)ibuf[o], ibuf + o + 5, len);
            o += 5 + len;
        }
        memmove(ibuf, ibuf + o, ibn - o);
        ibn -= o;
    }
}

static void put16(uint8_t *p, int v) { p[0] = (uint8_t)(v >> 8); p[1] = (uint8_t)v; }
static void put32(uint8_t *p, uint32_t v) { put16(p, (int)(v >> 16)); put16(p + 2, (int)(v & 0xffff)); }

/* a window position in dots, by the window's real size (it may have been
   fitted to the display or resized), clamped to the screen */
static int dot_of(int v, int dots, int horizontal)
{
    int ww, wh;
    SDL_GetWindowSize(win, &ww, &wh);
    int n = horizontal ? ww : wh;
    long d = n > 0 ? (long)v * dots / n : v / scale;
    return d < 0 ? 0 : d >= dots ? dots - 1 : (int)d;
}

/* a dot's window position (the inverse of dot_of, rounded up so that it
   maps back to the same dot) */
static int win_of(int d, int dots, int horizontal)
{
    int ww, wh;
    SDL_GetWindowSize(win, &ww, &wh);
    long n = horizontal ? ww : wh;
    return n > 0 ? (int)(((long)d * n + dots - 1) / dots) : d * scale;
}

/* --events: the file's events, pushed at their times after the first frame */
struct ev { long ms; char typ; int a[4]; };
static struct ev *evs;
static int nevs, evi;
static uint32_t ev_t0;

static void load_events(void)
{
    FILE *f = fopen(events_path, "r");
    if (!f) { perror(events_path); exit(1); }
    char ln[256];
    int cap = 0;
    while (fgets(ln, sizeof ln, f)) {
        struct ev e;
        char t[4];
        int ok = 0;
        memset(&e, 0, sizeof e);
        if (ln[0] == '#' || sscanf(ln, "%ld %3s", &e.ms, t) != 2) continue;
        e.typ = t[0];
        if (e.typ == 'K') ok = sscanf(ln, "%*d %*s %d %x", &e.a[0], &e.a[1]) == 2;
        else if (e.typ == 'M') ok = sscanf(ln, "%*d %*s %d %d", &e.a[0], &e.a[1]) == 2;
        else if (e.typ == 'B') ok = sscanf(ln, "%*d %*s %d %d %d %d", &e.a[0], &e.a[1], &e.a[2], &e.a[3]) == 4;
        if (!ok) continue;
        if (nevs == cap) { cap = cap * 2 + 64; evs = realloc(evs, cap * sizeof *evs); }
        evs[nevs++] = e;
    }
    fclose(f);
    fprintf(stderr, "winview: %d events from %s\n", nevs, events_path);
}

static void push_events(void)
{
    uint32_t now = SDL_GetTicks();
    if (!ev_t0) ev_t0 = now ? now : 1;
    while (evi < nevs && (long)(now - ev_t0) >= evs[evi].ms - evs[0].ms) {
        struct ev *v = &evs[evi++];
        SDL_Event e;
        memset(&e, 0, sizeof e);
        if (v->typ == 'K') {
            e.type = v->a[0] ? SDL_KEYDOWN : SDL_KEYUP;
            e.key.keysym.scancode = (SDL_Scancode)v->a[1];
        } else if (v->typ == 'M') {
            e.type = SDL_MOUSEMOTION;
            e.motion.x = win_of(v->a[0], W, 1); e.motion.y = win_of(v->a[1], H, 0);
        } else {
            e.type = v->a[1] ? SDL_MOUSEBUTTONDOWN : SDL_MOUSEBUTTONUP;
            e.button.button = v->a[0] == 0 ? SDL_BUTTON_LEFT : v->a[0] == 1 ? SDL_BUTTON_MIDDLE : SDL_BUTTON_RIGHT;
            e.button.x = win_of(v->a[2], W, 1); e.button.y = win_of(v->a[3], H, 0);
        }
        SDL_PushEvent(&e);
    }
}

static void push_fake(void)
{
    SDL_Event e;
    memset(&e, 0, sizeof e);
    e.type = SDL_KEYDOWN; e.key.keysym.scancode = SDL_SCANCODE_A; SDL_PushEvent(&e);
    e.type = SDL_KEYUP; SDL_PushEvent(&e);
    memset(&e, 0, sizeof e);
    e.type = SDL_MOUSEMOTION; e.motion.x = 10 * scale; e.motion.y = 20 * scale; SDL_PushEvent(&e);
    memset(&e, 0, sizeof e);
    e.type = SDL_MOUSEBUTTONDOWN; e.button.button = SDL_BUTTON_LEFT;
    e.button.x = 10 * scale; e.button.y = 20 * scale; SDL_PushEvent(&e);
    e.type = SDL_MOUSEBUTTONUP; SDL_PushEvent(&e);
}

int main(int argc, char **argv)
{
    if (argc < 2) { fprintf(stderr, "use: winview SOCKET [--scale N] [--dump F] [--fake-events] [--frames N] [--events F] [--linger MS] [--no-fit]\n"); return 2; }
    const char *path = argv[1];
    for (int i = 2; i < argc; i++) {
        if (!strcmp(argv[i], "--scale") && i + 1 < argc) scale = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--dump") && i + 1 < argc) dump = argv[++i];
        else if (!strcmp(argv[i], "--fake-events")) fake = 1;
        else if (!strcmp(argv[i], "--frames") && i + 1 < argc) maxframes = atol(argv[++i]);
        else if (!strcmp(argv[i], "--events") && i + 1 < argc) events_path = argv[++i];
        else if (!strcmp(argv[i], "--linger") && i + 1 < argc) linger = atol(argv[++i]);
        else if (!strcmp(argv[i], "--no-fit")) nofit = 1;
    }
    if (scale < 1) scale = 1;
    if (SDL_Init(SDL_INIT_VIDEO)) { fprintf(stderr, "winview: SDL_Init: %s\n", SDL_GetError()); return 1; }
    win = SDL_CreateWindow("winview", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, W * scale, H * scale, SDL_WINDOW_RESIZABLE);
    ren = win ? SDL_CreateRenderer(win, -1, SDL_RENDERER_SOFTWARE) : NULL;
    if (!ren) { fprintf(stderr, "winview: SDL window: %s\n", SDL_GetError()); return 1; }
    resize(W, H);
    present();
    if (events_path) load_events();

    lfd = socket(AF_UNIX, SOCK_STREAM, 0);
    struct sockaddr_un a;
    memset(&a, 0, sizeof a);
    a.sun_family = AF_UNIX;
    if (strlen(path) >= sizeof a.sun_path) {
        fprintf(stderr, "winview: the socket path is longer than %zu bytes: use a shorter one\n",
                sizeof a.sun_path - 1);
        return 1;
    }
    strncpy(a.sun_path, path, sizeof a.sun_path - 1);
    unlink(path);
    if (bind(lfd, (struct sockaddr *)&a, sizeof a) || listen(lfd, 1)) { perror(path); return 1; }
    fcntl(lfd, F_SETFL, O_NONBLOCK);
    fprintf(stderr, "winview: listening on %s\n", path);

    int running = 1, bstate = 0;
    while (running) {
        if (cfd < 0) {
            cfd = accept(lfd, NULL, NULL);
            if (cfd >= 0) { fcntl(cfd, F_SETFL, O_NONBLOCK); fprintf(stderr, "winview: a client\n"); }
        }
        if (cfd >= 0) read_client();
        if (fake && !faked && nframes > 0) { push_fake(); faked = 1; }
        if (events_path && nframes > 0) {
            push_events();
            if (evi == nevs && SDL_GetTicks() - last_frame > (uint32_t)linger) {
                uint8_t q[1];
                send_msg('Q', q, 0);
                running = 0;
            }
        }
        SDL_Event e;
        while (SDL_PollEvent(&e)) {
            uint8_t p[12];
            switch (e.type) {
            case SDL_QUIT: send_msg('Q', p, 0); running = 0; break;
            case SDL_KEYDOWN: case SDL_KEYUP:
                p[0] = e.type == SDL_KEYDOWN; put16(p + 1, e.key.keysym.scancode);
                put32(p + 3, e.key.timestamp);
                send_msg('K', p, 7);
                break;
            case SDL_MOUSEMOTION:
                put16(p, dot_of(e.motion.x, W, 1)); put16(p + 2, dot_of(e.motion.y, H, 0));
                put32(p + 4, e.motion.timestamp);
                send_msg('M', p, 8);
                break;
            case SDL_MOUSEBUTTONDOWN: case SDL_MOUSEBUTTONUP: {
                int b = e.button.button == SDL_BUTTON_LEFT ? 0 : e.button.button == SDL_BUTTON_MIDDLE ? 1
                      : e.button.button == SDL_BUTTON_RIGHT ? 2 : -1;
                if (b < 0) break;
                int down = e.type == SDL_MOUSEBUTTONDOWN;
                bstate = down ? bstate | 1 << b : bstate & ~(1 << b);
                p[0] = (uint8_t)b; p[1] = (uint8_t)down;
                put16(p + 2, dot_of(e.button.x, W, 1)); put16(p + 4, dot_of(e.button.y, H, 0));
                put32(p + 6, e.button.timestamp);
                send_msg('B', p, 10);
                break; }
            }
        }
        if (maxframes && nframes >= maxframes) running = 0;
        SDL_Delay(5);
    }
    if (cfd >= 0) close(cfd);
    unlink(path);
    SDL_Quit();
    fprintf(stderr, "winview: %ld frames\n", nframes);
    return 0;
}
