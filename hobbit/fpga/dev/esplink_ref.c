/* esplink_ref.c -- the ESP32 relay's own C codec as the reference for the
 * EspLink RTL (esplink_run_tests.sh).  It links
 * hobbit/fpga/esp32_ethrelay/main/relay.c unchanged.
 *
 *   esplink_ref enc   stdin: one frame a line, hex (an empty line is a
 *                     zero-length frame).  stdout: relay_encode(0x45, ...)
 *                     of each, hex on one line, or "TOOLONG" when
 *                     relay_encode refuses it.
 *   esplink_ref dec   stdin: a link byte stream, hex (whitespace ignored).
 *                     stdout: "F <hex>" for each good 0x45 packet's frame,
 *                     "S <hex>" for each good 0x53 packet, then
 *                     "C good bad_crc bad_cobs bad_len overflows bad_type".
 */
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "relay.h"

static int hexval(int c)
{
    if (c >= '0' && c <= '9') return c - '0';
    c = tolower(c);
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return -1;
}

static void puthex(const uint8_t *p, size_t n)
{
    for (size_t i = 0; i < n; i++)
        printf("%02x", p[i]);
}

static int do_enc(void)
{
    static char line[8192];
    static uint8_t frame[4096], out[RELAY_MAX_WIRE];

    while (fgets(line, sizeof line, stdin)) {
        size_t n = 0;
        int hi = -1;
        for (char *s = line; *s; s++) {
            int v = hexval((unsigned char)*s);
            if (v < 0) continue;
            if (hi < 0) hi = v;
            else { frame[n++] = (uint8_t)(hi << 4 | v); hi = -1; }
        }
        size_t m = relay_encode(RELAY_T_ETH, frame, n, out);
        if (m == 0) printf("TOOLONG");
        else puthex(out, m);
        printf("\n");
    }
    return 0;
}

static int do_dec(void)
{
    static relay_dec d;
    int c, hi = -1;

    relay_dec_init(&d);
    while ((c = getchar()) != EOF) {
        int v = hexval(c);
        if (v < 0) continue;
        if (hi < 0) { hi = v; continue; }
        const uint8_t *p;
        size_t len;
        int t = relay_feed(&d, (uint8_t)(hi << 4 | v), &p, &len);
        hi = -1;
        if (t) {
            printf("%c ", t == RELAY_T_ETH ? 'F' : 'S');
            puthex(p, len);
            printf("\n");
        }
    }
    printf("C %u %u %u %u %u %u\n", d.good, d.bad_crc, d.bad_cobs, d.bad_len,
           d.overflows, d.bad_type);
    return 0;
}

int main(int argc, char **argv)
{
    if (argc == 2 && strcmp(argv[1], "enc") == 0) return do_enc();
    if (argc == 2 && strcmp(argv[1], "dec") == 0) return do_dec();
    fprintf(stderr, "usage: esplink_ref enc|dec\n");
    return 2;
}
