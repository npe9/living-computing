/*
 * The ESP32 Ethernet relay, built for the host (hobbit/docs/ulx3s_ethernet.md).
 *
 * The firmware's protocol code (main/relay.c) with POSIX in place of
 * ESP-IDF: the UART to the FPGA is stdin (FPGA -> relay) and stdout
 * (relay -> FPGA), paced at the UART's byte rate, and WiFi is a UDP socket
 * to tools/qemu1e/hub.py.  tests/test_ethrelay.py drives it.
 *
 *   relay_host --hub HOST:PORT --local PORT [--baud N] [--queue N]
 *
 * --baud N paces both link directions at N/10 bytes/s (8N1); 0 (the
 * default) is unpaced.  --queue N bounds the frames waiting for the link
 * towards the FPGA (default 64); a frame arriving to a full queue is
 * dropped and counted, as the firmware's bounded UART buffer does.
 * At end of stdin the queue is drained and one JSON line of counters is
 * written to stderr.
 */
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

#include "../main/relay.h"

#define QMAX 1024

static uint8_t q[QMAX][RELAY_MAX_WIRE];
static size_t qlen[QMAX];

static double now(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

/* Pacing: *tl is when the link is next free.  While a direction stays
 * busy, a transfer catches up on the time poll() overslept (it sleeps in
 * whole milliseconds) and may run 1 ms ahead, as a UART FIFO would, so
 * the average rate is exact; after the direction has gone idle no
 * credit is banked (busy == 0: the transfer starts from now). */
static size_t credit(double tl, double t, double rate, size_t cap, int busy)
{
    double base = busy ? tl : (tl > t ? tl : t);
    double k = (t - base) * rate + rate * 0.001;
    if (k < 1)
        k = 1;
    return k < cap ? (size_t)k : cap;
}

static double advance(double tl, double t, double rate, size_t n, int busy)
{
    double base = busy ? tl : (tl > t ? tl : t);
    return base + n / rate;
}

static void usage(void)
{
    fprintf(stderr, "usage: relay_host --hub HOST:PORT --local PORT "
            "[--baud N] [--queue N]\n");
    exit(2);
}

int main(int argc, char **argv)
{
    const char *hub = NULL;
    int local = -1, qcap = 64;
    long baud = 0;
    struct sockaddr_in peer, me;
    int s, i;

    for (i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--hub") && i + 1 < argc)
            hub = argv[++i];
        else if (!strcmp(argv[i], "--local") && i + 1 < argc)
            local = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--baud") && i + 1 < argc)
            baud = atol(argv[++i]);
        else if (!strcmp(argv[i], "--queue") && i + 1 < argc)
            qcap = atoi(argv[++i]);
        else
            usage();
    }
    if (!hub || local < 0 || qcap < 1 || qcap > QMAX)
        usage();
    {
        char host[64];
        const char *c = strrchr(hub, ':');
        if (!c || (size_t)(c - hub) >= sizeof host)
            usage();
        memcpy(host, hub, c - hub);
        host[c - hub] = 0;
        memset(&peer, 0, sizeof peer);
        peer.sin_family = AF_INET;
        peer.sin_port = htons(atoi(c + 1));
        if (inet_pton(AF_INET, host, &peer.sin_addr) != 1)
            usage();
    }
    s = socket(AF_INET, SOCK_DGRAM, 0);
    memset(&me, 0, sizeof me);
    me.sin_family = AF_INET;
    me.sin_port = htons(local);
    me.sin_addr.s_addr = htonl(0x7F000001u);
    if (s < 0 || bind(s, (struct sockaddr *)&me, sizeof me) < 0) {
        perror("relay_host: bind");
        return 1;
    }
    {
        int big = 1 << 20;
        setsockopt(s, SOL_SOCKET, SO_RCVBUF, &big, sizeof big);
    }

    double rate = baud > 0 ? baud / 10.0 : 0;   /* bytes per second */
    double t_in = now(), t_out = t_in;
    relay_dec dec;
    relay_dec_init(&dec);
    size_t qh = 0, qt = 0, qn = 0, qoff = 0, qmaxdepth = 0;
    unsigned long link_in = 0, net_in = 0, link_out = 0, dropped = 0,
                  oversize = 0, udp_err = 0;
    int eof = 0, in_busy = 0, out_busy = 0;
    uint8_t buf[2048];

    for (;;) {
        double t = now();
        int want_in = !eof && (rate == 0 || t >= t_in);
        int want_out = qn > 0 && (rate == 0 || t >= t_out);
        struct pollfd p[3];
        int np = 0, ix_in = -1, ix_out = -1, ix_net;
        double wake = 1.0;

        if (eof && qn == 0)
            break;
        if (want_in) {
            p[np].fd = 0;
            p[np].events = POLLIN;
            ix_in = np++;
        } else if (!eof && t_in - t < wake)
            wake = t_in - t;
        if (want_out) {
            p[np].fd = 1;
            p[np].events = POLLOUT;
            ix_out = np++;
        } else if (qn > 0 && t_out - t < wake)
            wake = t_out - t;
        p[np].fd = s;
        p[np].events = POLLIN;
        ix_net = np++;
        if (poll(p, np, (int)(wake * 1000) + 1) < 0) {
            if (errno == EINTR)
                continue;
            perror("relay_host: poll");
            return 1;
        }

        if (ix_in >= 0 && (p[ix_in].revents & (POLLIN | POLLHUP))) {
            size_t lim = sizeof buf;
            if (rate > 0)
                lim = credit(t_in, t, rate, lim, in_busy);
            ssize_t k = read(0, buf, lim);
            if (k <= 0)
                eof = 1;
            else {
                if (rate > 0)
                    t_in = advance(t_in, t, rate, (size_t)k, in_busy);
                in_busy = (size_t)k == lim;
                for (ssize_t j = 0; j < k; j++) {
                    const uint8_t *pl;
                    size_t n;
                    int ty = relay_feed(&dec, buf[j], &pl, &n);
                    if (ty == RELAY_T_ETH) {
                        link_in++;
                        if (sendto(s, pl, n, 0, (struct sockaddr *)&peer,
                                   sizeof peer) < 0)
                            udp_err++;
                    }
                }
            }
        }

        if (p[ix_net].revents & POLLIN) {
            ssize_t k = recv(s, buf, sizeof buf, 0);
            if (k > 0) {
                net_in++;
                if (k < RELAY_MIN_FRAME || k > RELAY_MAX_FRAME)
                    oversize++;
                else if (qn == (size_t)qcap)
                    dropped++;
                else {
                    qlen[qt] = relay_encode(RELAY_T_ETH, buf, (size_t)k, q[qt]);
                    qt = (qt + 1) % QMAX;
                    if (++qn > qmaxdepth)
                        qmaxdepth = qn;
                }
            }
        }

        if (ix_out >= 0 && (p[ix_out].revents & POLLOUT)) {
            size_t k = qlen[qh] - qoff;
            if (rate > 0)
                k = credit(t_out, t, rate, k, out_busy);
            ssize_t w = write(1, q[qh] + qoff, k);
            if (w < 0) {
                perror("relay_host: write");
                return 1;
            }
            if (rate > 0)
                t_out = advance(t_out, t, rate, (size_t)w, out_busy);
            qoff += (size_t)w;
            if (qoff == qlen[qh]) {
                qoff = 0;
                qh = (qh + 1) % QMAX;
                qn--;
                link_out++;
            }
            out_busy = qn > 0;
        }
    }
    fprintf(stderr,
            "{\"link_in\": %lu, \"net_in\": %lu, \"link_out\": %lu, "
            "\"dropped\": %lu, \"oversize\": %lu, \"udp_err\": %lu, "
            "\"max_queue\": %zu, \"good\": %u, \"bad_crc\": %u, "
            "\"bad_cobs\": %u, \"bad_len\": %u, \"overflows\": %u, "
            "\"bad_type\": %u}\n",
            link_in, net_in, link_out, dropped, oversize, udp_err, qmaxdepth,
            dec.good, dec.bad_crc, dec.bad_cobs, dec.bad_len, dec.overflows,
            dec.bad_type);
    return 0;
}
