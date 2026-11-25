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
    /* STRETCH_TAPE_TRACE: report every word written, so a bench can read
       back what a program put on the reel (tests/check_bss_mcp_go.py,
       stage 7: MCP's label, records and tape marks on the OUTPT reel). */
    static int trace = -1;
    if (trace < 0) trace = getenv("STRETCH_TAPE_TRACE") != NULL;
    if (trace) fprintf(stderr, "TAPE_WRITE %u %016llx\n", i, (unsigned long long)d);
}

/* THE DISK, for mkDiskSourceFile (StretchDiskSourceFile.bsv).  It lives
   here rather than in a host_disk.c so that every build that already
   links host_tape.c gets it with no change to its link line.  A full
   353, 2^21 words (Reference Manual printed p.157), zero at power-on
   as mkDiskSourceSmall's registers are; 16 MB of host memory.

   THE IMAGE FILE (docs/disk_subsystem.md §9c).  The format is the
   tape's: 8 bytes per word, big-endian (byte 0 is IBM bits 0-7), word
   i at byte 8*i, word i = arc*512 + word-in-arc (DiskIndex).  A saved
   image is always the whole unit, 2^21 * 8 = 16,777,216 bytes.

   STRETCH_DISK=path loads an image the first time the disk is touched.
   A file shorter than the unit is ZERO-FILLED to the end, including the
   missing bytes of a final partial word: the same power-on zero as a
   disk with no image.  A file longer than the unit, or one that cannot
   be opened, stops the run -- a mistyped path must not boot on a blank
   disk and look like a pass.

   STRETCH_DISK_SAVE=path writes the whole unit when the testbench
   finishes (tests/gen_tb.py's finish rule calls host_disk_save).

   With neither set, nothing here reads a file, writes one or prints. */
#define DISK_WORDS (1u << 21)
static uint64_t *g_disk;

static void disk_init(void)
{
    if (g_disk) return;
    g_disk = calloc(DISK_WORDS, sizeof(uint64_t));
    if (!g_disk) { perror("host_disk: calloc"); exit(1); }
    const char *path = getenv("STRETCH_DISK");
    if (!path || !*path) return;
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); fprintf(stderr, "host_disk: STRETCH_DISK cannot be read\n"); exit(1); }
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    if (n < 0 || (unsigned long)n > (unsigned long)DISK_WORDS * 8) {
        fprintf(stderr, "host_disk: %s is %ld bytes, more than a 353's %u\n",
                path, n, DISK_WORDS * 8);
        exit(1);
    }
    /* Every word of the unit goes through the one buffer.  Bytes the
       file does not have are zeroed HERE, explicitly: past the end,
       fread returns short and b would otherwise still hold the previous
       word (tests/run_disk_image_test.sh's injection). */
    unsigned char b[8];
    for (uint32_t i = 0; i < DISK_WORDS; i++) {
        size_t got = fread(b, 1, 8, f);
        if (got < 8) memset(b + got, 0, 8 - got);
        uint64_t w = 0;
        for (int k = 0; k < 8; k++) w = (w << 8) | b[k];
        g_disk[i] = w;
    }
    fclose(f);
    fprintf(stderr, "host_disk: loaded %s, %ld bytes; %u words zero-filled\n",
            path, n, DISK_WORDS - (uint32_t)((n + 7) / 8));
}

uint64_t host_disk_read_word(uint32_t i)
{
    disk_init();
    return i < DISK_WORDS ? g_disk[i] : 0;
}

void host_disk_write_word(uint32_t i, uint64_t d)
{
    disk_init();
    if (i < DISK_WORDS) g_disk[i] = d;
}

void host_disk_save(void)
{
    const char *path = getenv("STRETCH_DISK_SAVE");
    if (!path || !*path) return;
    disk_init();
    FILE *f = fopen(path, "wb");
    if (!f) { perror(path); fprintf(stderr, "host_disk: STRETCH_DISK_SAVE cannot be written\n"); exit(1); }
    uint32_t i;
    for (i = 0; i < DISK_WORDS; i++) {
        unsigned char b[8];
        for (int k = 0; k < 8; k++) b[k] = (unsigned char)(g_disk[i] >> (56 - 8 * k));
        if (fwrite(b, 1, 8, f) != 8) break;
    }
    if (fclose(f) != 0 || i != DISK_WORDS) {
        perror(path);
        fprintf(stderr, "host_disk: save to %s failed at word %u\n", path, i);
        exit(1);
    }
    fprintf(stderr, "host_disk: saved %s, %u words\n", path, DISK_WORDS);
}
