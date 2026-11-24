/* PimmSdBlockFile.c -- the C side of mkPimmSdBlockFile (Bluesim only).
   ALL OURS.  Opens the image named by PIMM_SD_IMAGE read-only, once, and
   answers bytes of 512-byte blocks.  Nothing here writes a file.
   The pattern is stretch/bsv/sd_reference/host_tape.c. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static unsigned char *img;
static uint32_t nblocks;

static void load(void)
{
    static int tried;
    if (tried) return;
    tried = 1;
    const char *path = getenv("PIMM_SD_IMAGE");
    if (!path || !*path) {
        fprintf(stderr, "PimmSdBlockFile: no PIMM_SD_IMAGE; the card has no blocks\n");
        return;
    }
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); return; }
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    nblocks = (uint32_t)(n / 512);
    img = malloc(nblocks ? (size_t)nblocks * 512 : 1);
    if (fread(img, 1, (size_t)nblocks * 512, f) != (size_t)nblocks * 512) nblocks = 0;
    fclose(f);
}

uint32_t pimm_sd_blocks(void) { load(); return nblocks; }

uint8_t pimm_sd_byte(uint32_t block, uint32_t ix)
{
    load();
    if (block >= nblocks || ix >= 512) return 0;
    return img[(size_t)block * 512 + ix];
}
