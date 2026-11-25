/*************************************************************************
*  PDSS modernisation (living-computing): the representation layer.	 *
*  Not part of the 1992 sources; see ../README.md, "How the cell stays	 *
*  32 bits".  ICOT Free Software terms apply to the whole (COPYRIGHT).	 *
*************************************************************************/

#ifndef PDSS_PORT_H
#define PDSS_PORT_H

#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <limits.h>

/* PDSS's KL1-B cell is 8 bytes on every host: a 16-bit tag, a 16-bit MRB
   word and a 32-bit value (cell.h).  The original kept C pointers in the
   value.  Here a pointer is kept as a PREF, a 32-bit reference:

     0                      NULL
     1 .. 0x7FFFFFFF        byte offset into the arena (arena.c), where
                            every PDSS allocation lives: heap, code area,
                            records, modules, buffers
     0x80000000 | i         entry i of the foreign table: an address
                            outside the arena (a static variable, a C
                            function, a FILE), registered on first use

   so offsets preserve the arena's address order and differences, as the
   original's pointers did inside its 32-bit address space, and every
   record keeps its 32-bit size (record.h), which the heap accounting,
   and therefore the GC schedule, depend on. */

typedef uint32_t PREF;

#define PREF_FOREIGN 0x80000000u

extern unsigned char *pdss_arena_base;	/* first byte (offset 0 is NULL) */
extern unsigned char *pdss_arena_end;	/* one past the last byte */

PREF  pdss_foreign_ref(const void *p);
void *pdss_foreign_ptr(PREF r);

static inline PREF pdss_ref(const void *p)
{
    const unsigned char *q = (const unsigned char *)p;
    if(q == NULL) return 0;
    if(q >= pdss_arena_base && q <= pdss_arena_end)
	return (PREF)(q - pdss_arena_base);
    return pdss_foreign_ref(p);
}

static inline void *pdss_ptr(PREF r)
{
    if(r == 0) return NULL;
    if(!(r & PREF_FOREIGN)) return pdss_arena_base + r;
    return pdss_foreign_ptr(r);
}

/* Native (C-coded) predicates are entered by putting the function's
   address where a code address goes (goal records, PC): PDSS tells them
   apart with InCode().  Converting between function and object pointers
   is not ISO C, but POSIX requires it (dlsym) and every target here
   supports it; these two macros are the only places it happens. */
typedef int (*PDSS_FUNC)(void);
#define CodeOfFunction(f)  ((OBJ *)(void *)(f))
#define FunctionOfCode(p)  ((PDSS_FUNC)(void *)(p))

/* A cell value from an integer or a pointer, for SetAll and friends,
   which the original used for both: integers are stored as their 32
   low bits, pointers as a PREF. */
/* The 32-bit two's-complement value of the low 32 bits, by arithmetic
   (a cast of an out-of-range value to int32_t is implementation-defined). */
static inline int32_t pdss_s32(uint32_t v)
{
    return v <= (uint32_t)INT32_MAX ? (int32_t)v : (int32_t)(v - 0x80000000u) - INT32_MAX - 1;
}
static inline int32_t pdss_v_int(long long v)   { return pdss_s32((uint32_t)(unsigned long long)v); }
static inline int32_t pdss_v_uint(unsigned long long v) { return pdss_s32((uint32_t)v); }
static inline int32_t pdss_v_ptr(const void *p) { return (int32_t)pdss_ref(p); }
#define CellValue(V) _Generic((V),				\
    _Bool: pdss_v_int, char: pdss_v_int, signed char: pdss_v_int,	\
    unsigned char: pdss_v_uint, short: pdss_v_int,		\
    unsigned short: pdss_v_uint, int: pdss_v_int,		\
    unsigned int: pdss_v_uint, long: pdss_v_int,		\
    unsigned long: pdss_v_uint, long long: pdss_v_int,		\
    unsigned long long: pdss_v_uint,				\
    default: pdss_v_ptr)(V)

/* KL1-B code is a byte string (klb.h).  Multi-byte fields are read and
   written with memcpy in the host's byte order: code never leaves memory
   as raw bytes (save files are written field by field, big-endian, by
   saveload.c), and memcpy is alignment-safe. */
static inline int32_t pdss_get32(const void *p)  { int32_t x; memcpy(&x, p, 4); return x; }
static inline uint32_t pdss_getu32(const void *p) { uint32_t x; memcpy(&x, p, 4); return x; }
static inline int16_t pdss_get16(const void *p)  { int16_t x; memcpy(&x, p, 2); return x; }
static inline uint16_t pdss_getu16(const void *p) { uint16_t x; memcpy(&x, p, 2); return x; }
static inline void pdss_put32(void *p, uint32_t x) { memcpy(p, &x, 4); }
static inline void pdss_put16(void *p, uint16_t x) { memcpy(p, &x, 2); }

/* A float kept in a cell's 32-bit value (single precision, as on the
   original), without aliasing an int as a float. */
static inline float pdss_float_of(const int32_t *v) { float f; memcpy(&f, v, 4); return f; }
static inline void pdss_set_float(int32_t *v, float f) { memcpy(v, &f, 4); }

/* The arena and the C library's allocator. */
int   pdss_arena_init(void);
void *pdss_malloc(size_t n);
void *pdss_calloc(size_t n, size_t m);
void *pdss_realloc(void *p, size_t n);
void  pdss_free(void *p);

/* Layout check (not a supported configuration): -DPDSS_LP64_RECORDS pads
   every PREF field of the records (record.h, cell.h) to 8 bytes, giving them the sizes the
   reference port (pointers in records, x86_64) had, so that the modern
   source can be compared with that port's golden transcripts including
   their GC schedule.  See ../../README.md, "Record sizes". */
#ifdef PDSS_LP64_RECORDS
#define PREF_PAD(n) uint32_t pad_##n;
#else
#define PREF_PAD(n)
#endif

/* Assumptions checked at compile time. */
_Static_assert(CHAR_BIT == 8, "PDSS needs 8-bit bytes");
_Static_assert(sizeof(int) == 4, "PDSS needs a 32-bit int");
_Static_assert(sizeof(float) == 4, "PDSS keeps floats in 32 bits");

#endif
