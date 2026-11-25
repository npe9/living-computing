/*************************************************************************
*  PDSS modernisation (living-computing): the arena and the foreign	 *
*  table behind PREF (port.h).  ICOT Free Software terms (COPYRIGHT).	 *
*************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "port.h"

/* The arena is one block of the C library's memory, obtained once.  Its
   size is PDSS_ARENA_MB megabytes (default 1024, at most 2047 so that an
   offset is below PREF_FOREIGN); on hosts that cannot give that much the
   request is halved down to 64 MB.  Pages the program never touches are
   never committed on the usual virtual-memory systems, so the default
   costs nothing.  Within it, blocks are handed out by size class (powers
   of two from 16 bytes) and freed blocks are reused within their class:
   PDSS's own pattern is a few large areas (heap, code) allocated at start
   and small buffers. */

unsigned char *pdss_arena_base;
unsigned char *pdss_arena_end;
static unsigned char *arena_next;

#define HDR	16			/* block header: the size class */
#define NCLASS	32
static void *free_list[NCLASS];

int pdss_arena_init(void)
{
    size_t mb = 1024;
    const char *e = getenv("PDSS_ARENA_MB");
    if(pdss_arena_base) return 1;
    if(e && atoi(e) > 0) mb = (size_t)atoi(e);
    if(mb > 2047) mb = 2047;
    for(; mb >= 64; mb /= 2){
	pdss_arena_base = malloc(mb << 20);
	if(pdss_arena_base) break;
    }
    if(!pdss_arena_base){
	fprintf(stderr, "pdss: cannot allocate the arena\n");
	exit(1);
    }
    pdss_arena_end = pdss_arena_base + (mb << 20);
    arena_next = pdss_arena_base + HDR;	/* offset 0 is never a block */
    return 1;
}

static int size_class(size_t n)
{
    int c = 4;				/* 16 bytes */
    while(((size_t)1 << c) < n) c++;
    return c;
}

void *pdss_malloc(size_t n)
{
    int c;
    unsigned char *p;
    if(!pdss_arena_base) pdss_arena_init();
    if(n == 0) n = 1;
    c = size_class(n);
    if(c >= NCLASS) return NULL;
    if(free_list[c]){
	p = free_list[c];
	memcpy(&free_list[c], p, sizeof(void *));
	return p;
    }
    if((size_t)(pdss_arena_end - arena_next) < ((size_t)1 << c) + HDR) return NULL;
    p = arena_next + HDR;
    memcpy(p - HDR, &c, sizeof c);
    arena_next = p + ((size_t)1 << c);
    return p;
}

void *pdss_calloc(size_t n, size_t m)
{
    void *p;
    if(m && n > (size_t)-1 / m) return NULL;
    p = pdss_malloc(n * m);
    if(p) memset(p, 0, n * m);
    return p;
}

void pdss_free(void *p)
{
    int c;
    if(!p) return;
    memcpy(&c, (unsigned char *)p - HDR, sizeof c);
    memcpy(p, &free_list[c], sizeof(void *));
    free_list[c] = p;
}

void *pdss_realloc(void *p, size_t n)
{
    int c;
    void *q;
    if(!p) return pdss_malloc(n);
    memcpy(&c, (unsigned char *)p - HDR, sizeof c);
    if(n <= ((size_t)1 << c)) return p;
    if(!(q = pdss_malloc(n))) return NULL;
    memcpy(q, p, (size_t)1 << c);
    pdss_free(p);
    return q;
}


/* The foreign table: addresses outside the arena that PDSS stores in a
   32-bit place.  An address gets one index for the life of the process
   (an open-addressing hash from address to index finds it again). */

static const void **foreign;
static unsigned int nforeign, maxforeign;
static unsigned int *fhash;		/* index+1, 0 = empty */
static unsigned int fhash_size;

static unsigned int hash_ptr(const void *p)
{
    uintptr_t x = (uintptr_t)p;
    x ^= x >> 17; x *= 0x9E3779B1u; x ^= x >> 13;
    return (unsigned int)x;
}

static void fhash_insert(unsigned int i)
{
    unsigned int h = hash_ptr(foreign[i]) & (fhash_size - 1);
    while(fhash[h]) h = (h + 1) & (fhash_size - 1);
    fhash[h] = i + 1;
}

PREF pdss_foreign_ref(const void *p)
{
    unsigned int h, i;
    if(fhash_size){
	h = hash_ptr(p) & (fhash_size - 1);
	while(fhash[h]){
	    if(foreign[fhash[h] - 1] == p) return PREF_FOREIGN | (fhash[h] - 1);
	    h = (h + 1) & (fhash_size - 1);
	}
    }
    if(nforeign == maxforeign){
	maxforeign = maxforeign ? maxforeign * 2 : 256;
	foreign = realloc((void *)foreign, maxforeign * sizeof *foreign);
	free(fhash);
	fhash_size = maxforeign * 2;
	fhash = calloc(fhash_size, sizeof *fhash);
	if(!foreign || !fhash || maxforeign >= PREF_FOREIGN){
	    fprintf(stderr, "pdss: foreign reference table full\n");
	    exit(1);
	}
	for(i = 0; i < nforeign; i++) fhash_insert(i);
    }
    foreign[nforeign] = p;
    fhash_insert(nforeign);
    if(getenv("PDSS_FOREIGN_TRACE"))
	fprintf(stderr, "pdss: foreign ref %u = %p\n", nforeign, p);
    return PREF_FOREIGN | nforeign++;
}

void *pdss_foreign_ptr(PREF r)
{
    unsigned int i = r & ~PREF_FOREIGN;
    if(i >= nforeign){
	fprintf(stderr, "pdss: bad reference 0x%08x\n", (unsigned)r);
	abort();
    }
    return (void *)foreign[i];
}

unsigned int pdss_foreign_count(void) { return nforeign; }
