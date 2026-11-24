/* The link protocol of the ULX3S Ethernet relay; see relay.h. */
#include "relay.h"

#include <string.h>

uint32_t relay_crc32(uint32_t crc, const uint8_t *p, size_t n)
{
    /* Bitwise, reflected 0xEDB88320: small, and fast enough at UART rates
     * (a 1518-byte frame is ~12k shift steps). */
    crc = ~crc;
    while (n--) {
        crc ^= *p++;
        for (int k = 0; k < 8; k++)
            crc = (crc >> 1) ^ (0xEDB88320u & (0u - (crc & 1u)));
    }
    return ~crc;
}

/* A push-style COBS encoder, so the body need not be copied. */
typedef struct {
    uint8_t *out;
    size_t   ci;    /* index of the pending code byte */
    size_t   o;     /* next output index */
    uint8_t  code;
} cobs_enc;

static void enc_start(cobs_enc *e, uint8_t *out)
{
    e->out = out;
    e->ci = 0;
    e->o = 1;
    e->code = 1;
}

static void enc_byte(cobs_enc *e, uint8_t b)
{
    if (b == 0) {
        e->out[e->ci] = e->code;
        e->ci = e->o++;
        e->code = 1;
    } else {
        e->out[e->o++] = b;
        if (++e->code == 0xFF) {
            e->out[e->ci] = e->code;
            e->ci = e->o++;
            e->code = 1;
        }
    }
}

static size_t enc_end(cobs_enc *e)
{
    e->out[e->ci] = e->code;
    e->out[e->o++] = 0x00;          /* the delimiter */
    return e->o;
}

size_t relay_encode(uint8_t type, const uint8_t *payload, size_t n,
                    uint8_t *out)
{
    cobs_enc e;
    uint32_t crc;
    size_t i;

    if (n > RELAY_MAX_FRAME)
        return 0;
    crc = relay_crc32(0, &type, 1);
    crc = relay_crc32(crc, payload, n);
    enc_start(&e, out);
    enc_byte(&e, type);
    for (i = 0; i < n; i++)
        enc_byte(&e, payload[i]);
    for (i = 0; i < 4; i++)
        enc_byte(&e, (uint8_t)(crc >> (8 * i)));
    return enc_end(&e);
}

void relay_dec_init(relay_dec *d)
{
    memset(d, 0, sizeof *d);
}

/* Decode d->wire[0..d->n) into d->body; returns the body length or -1. */
static long cobs_decode(relay_dec *d)
{
    size_t i = 0, o = 0;

    while (i < d->n) {
        uint8_t code = d->wire[i++];
        if (code == 0)
            return -1;
        for (uint8_t k = 1; k < code; k++) {
            if (i >= d->n || o >= sizeof d->body)
                return -1;
            d->body[o++] = d->wire[i++];
        }
        if (code != 0xFF && i < d->n) {
            if (o >= sizeof d->body)
                return -1;
            d->body[o++] = 0;
        }
    }
    return (long)o;
}

int relay_feed(relay_dec *d, uint8_t c, const uint8_t **payload,
               size_t *len)
{
    long m;
    uint32_t want, got;
    int type;

    if (c != 0x00) {
        if (d->n < sizeof d->wire)
            d->wire[d->n++] = c;
        else
            d->overflow = 1;
        return 0;
    }
    /* the delimiter: a packet ends (an empty one is idle fill) */
    if (d->n == 0 && !d->overflow)
        return 0;
    if (d->overflow) {
        d->overflows++;
        d->n = 0;
        d->overflow = 0;
        return 0;
    }
    m = cobs_decode(d);
    d->n = 0;
    if (m < 0) {
        d->bad_cobs++;
        return 0;
    }
    if (m < 5) {
        d->bad_len++;
        return 0;
    }
    want = relay_crc32(0, d->body, (size_t)m - 4);
    got = (uint32_t)d->body[m - 4] | (uint32_t)d->body[m - 3] << 8
        | (uint32_t)d->body[m - 2] << 16 | (uint32_t)d->body[m - 1] << 24;
    if (want != got) {
        d->bad_crc++;
        return 0;
    }
    type = d->body[0];
    m -= 5;
    if (type == RELAY_T_ETH) {
        if (m < RELAY_MIN_FRAME || m > RELAY_MAX_FRAME) {
            d->bad_len++;
            return 0;
        }
    } else if (type != RELAY_T_STATUS) {
        d->bad_type++;
        return 0;
    }
    d->good++;
    *payload = d->body + 1;
    *len = (size_t)m;
    return type;
}
