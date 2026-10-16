/* host_tape.c -- the Bluesim side of mkTapeSourceFile, modelled on
   ~/src/alto-bluespec/sim/host.c (load_disk / host_disk_read_word).
   The image path comes from the environment, as ALTO_DISK does there. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static uint64_t *g_img;
static uint32_t  g_words;
static int       g_loaded;

static void load(void)
{
    static int tried;
    if (tried) return;
    tried = 1;
    const char *path = getenv("STRETCH_TAPE");
    if (!path || !*path) {
        fprintf(stderr, "host_tape: no STRETCH_TAPE; tape reports no media\n");
        return;
    }
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); return; }
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    g_words = (uint32_t)(n / 8);
    g_img = calloc(g_words ? g_words : 1, sizeof(uint64_t));
    for (uint32_t i = 0; i < g_words; i++) {
        unsigned char b[8];
        if (fread(b, 1, 8, f) != 8) { g_words = i; break; }
        /* Big-endian: byte 0 of the record is IBM bits 0-7, the
           leftmost byte of the word. */
        uint64_t w = 0;
        for (int k = 0; k < 8; k++) w = (w << 8) | b[k];
        g_img[i] = w;
    }
    fclose(f);
    g_loaded = 1;
    fprintf(stderr, "host_tape: mounted %s, %u words\n", path, g_words);
}

uint32_t host_tape_loaded(void)            { load(); return (uint32_t)g_loaded; }
uint32_t host_tape_words(void)             { load(); return g_words; }
uint64_t host_tape_read_word(uint32_t i)   { load(); return i < g_words ? g_img[i] : 0; }
void     host_tape_write_word(uint32_t i, uint64_t d)
{
    load();
    if (i < g_words) g_img[i] = d;   /* write-back to the file is a
                                        separate commit, as in
                                        host_disk_commit() */
}
