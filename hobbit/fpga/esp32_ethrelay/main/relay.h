/*
 * The FPGA <-> ESP32 link protocol of the ULX3S Ethernet relay
 * (hobbit/docs/ulx3s_ethernet.md, "The link").  Portable C: the same
 * file is compiled into the ESP-IDF firmware (main.c) and into the host
 * relay (host/relay_host.c) that tests/test_ethrelay.py runs against
 * tools/qemu1e/hub.py.
 *
 * One link packet is
 *
 *     COBS( type[1] | payload[n] | crc32[4], little-endian ) 0x00
 *
 * COBS (Cheshire and Baker, "Consistent Overhead Byte Stuffing", IEEE/ACM
 * ToN 7(2), 1999) removes every 0x00 from the body, so 0x00 delimits
 * packets and a receiver resynchronises at the next 0x00 after any error.
 * The overhead is one byte per 254 body bytes, plus the delimiter.  The
 * CRC is the Ethernet FCS polynomial (reflected 0xEDB88320, init and
 * final xor 0xFFFFFFFF) over type and payload, so the FPGA can reuse an
 * FCS block.
 *
 * Types: RELAY_T_ETH carries one Ethernet frame exactly as hub.py and
 * QEMU's dgram netdev carry it: destination address first, no preamble,
 * no FCS.  RELAY_T_STATUS (ESP32 -> FPGA only) is a status record the
 * FPGA may ignore.  Any other type is counted and dropped.
 */
#ifndef RELAY_H
#define RELAY_H

#include <stddef.h>
#include <stdint.h>

#define RELAY_T_ETH     0x45    /* 'E' */
#define RELAY_T_STATUS  0x53    /* 'S' */

#define RELAY_MIN_FRAME 14      /* an Ethernet header */
#define RELAY_MAX_FRAME 1518    /* 1514 + an 802.1Q tag; no FCS */

/* type + payload + CRC */
#define RELAY_MAX_BODY  (1 + RELAY_MAX_FRAME + 4)
/* COBS: one code byte per 254 body bytes (and one at the start), + 0x00 */
#define RELAY_MAX_WIRE  (RELAY_MAX_BODY + RELAY_MAX_BODY / 254 + 2)

uint32_t relay_crc32(uint32_t crc, const uint8_t *p, size_t n);

/* Encode one packet into out (at least RELAY_MAX_WIRE bytes).  Returns
 * the number of bytes written, the closing 0x00 included, or 0 if n is
 * larger than RELAY_MAX_FRAME. */
size_t relay_encode(uint8_t type, const uint8_t *payload, size_t n,
                    uint8_t *out);

typedef struct {
    uint8_t  wire[RELAY_MAX_WIRE];  /* encoded bytes since the last 0x00 */
    uint8_t  body[RELAY_MAX_BODY];  /* decoded */
    size_t   n;
    int      overflow;              /* this packet exceeded RELAY_MAX_WIRE */
    uint32_t good, bad_crc, bad_cobs, bad_len, overflows, bad_type;
} relay_dec;

void relay_dec_init(relay_dec *d);

/* Feed one received link byte.  Returns the packet type when it completes
 * a good packet (then *payload, *len describe it, valid until the next
 * call), 0 otherwise.  Bad packets are counted in d and dropped;
 * RELAY_T_ETH packets whose length is outside [RELAY_MIN_FRAME,
 * RELAY_MAX_FRAME] count as bad_len. */
int relay_feed(relay_dec *d, uint8_t c, const uint8_t **payload,
               size_t *len);

#endif
