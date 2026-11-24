/* PimmFepEmuTb.c -- the vector file for PimmFepEmuTb.bsv (Bluesim only).
   ALL OURS.  Reads PIMM_FEP_VECTORS (whitespace-separated hex words,
   written by bsv/fepemu_check.py) once; a word past the end reads 0. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static uint32_t *v;
static uint32_t nv;

static void load(void)
{
    static int tried;
    if (tried) return;
    tried = 1;
    const char *path = getenv("PIMM_FEP_VECTORS");
    if (!path || !*path) { fprintf(stderr, "PimmFepEmuTb: no PIMM_FEP_VECTORS\n"); return; }
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); return; }
    uint32_t cap = 1024, x;
    v = malloc(cap * sizeof *v);
    while (fscanf(f, "%x", &x) == 1) {
        if (nv == cap) v = realloc(v, (cap *= 2) * sizeof *v);
        v[nv++] = x;
    }
    fclose(f);
}

uint32_t fept_word(uint32_t i)
{
    load();
    return i < nv ? v[i] : 0;
}
