/*
 * p9host.c -- the host side of bsv/P9HostTb.bsv (Bluesim BDPI).
 *
 * Two things live here, and neither is a second kernel:
 *
 *   1. The machine's memory: a sparse 32-bit word store, so a 1e process
 *      can keep its stack just below USTKTOP = 0x80000000 and its text at
 *      0x1020 without a 2 Gbyte array or an address fold.
 *
 *   2. A *replayer* for the kernel's work.  tools/p9run.py runs the same
 *      binary on the reference model and records every kernel entry (a
 *      system call, or the unimplemented-instruction handler for floating
 *      point): the id and arguments it saw, the bytes it stored into the
 *      process, and the result.  This file checks that the Bluespec
 *      machine arrives with the same id and arguments, stores the same
 *      bytes, and hands back the same result.  What a `write` call writes
 *      is taken from the *model's* memory, not from the recording, so the
 *      files this run produces are the model's own output.
 *
 * The recording (`p9.rec`, text, hex fields) is described in
 * tools/p9run.py (`Recorder`).  Its records, in order:
 *
 *   L lo hi                 a legal address range [lo, hi)
 *   M addr word             an initial memory word
 *   S pc sp psw isp vb      the start state
 *   G go rdy res flag       the stub's device words
 *   E kind id n a0 a1 a2 a3 a kernel entry: kind K (system call, id = its
 *                           number) or F (floating point, id = the PC the
 *                           sequence saved); n arguments are compared
 *   B addr hexbytes         bytes the kernel stores (little-endian lanes)
 *   O name offset addr n    a write: n bytes at addr go to file `name`
 *                           at `offset` ("-" is the console, appended)
 *   R result flag done      the entry's result, the PSW.F the stub
 *                           leaves, and done = 1 for exits
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

#define PAGEBITS 12
#define PAGEWORDS (1u << (PAGEBITS - 2))
#define NBUCKET 4096

typedef struct Page Page;
struct Page {
	uint32_t base;
	uint32_t w[PAGEWORDS];
	Page *next;
};

typedef struct {
	uint32_t lo, hi;
} Range;

static Page *bucket[NBUCKET];
static Range range[32];
static int nrange;
static FILE *rec;
static char line[1 << 20];
static int have_line;
static uint32_t start[5];
static uint32_t dev[4];		/* go, rdy, res, flag */
static int initialised;
static int failed;
static unsigned long events, unmapped_reads;
static char outdir[512] = "p9.out";

static Page *
page(uint32_t addr, int make)
{
	uint32_t base = addr >> PAGEBITS;
	Page *p;

	for (p = bucket[base % NBUCKET]; p; p = p->next)
		if (p->base == base)
			return p;
	if (!make)
		return 0;
	p = calloc(1, sizeof *p);
	if (!p) {
		fprintf(stderr, "p9host: out of memory\n");
		exit(2);
	}
	p->base = base;
	p->next = bucket[base % NBUCKET];
	bucket[base % NBUCKET] = p;
	return p;
}

static int
legal(uint32_t addr)
{
	int i;

	for (i = 0; i < nrange; i++)
		if (addr >= range[i].lo && addr < range[i].hi)
			return 1;
	return 0;
}

static uint32_t
rd(uint32_t addr)
{
	Page *p = page(addr, 0);

	return p ? p->w[(addr >> 2) & (PAGEWORDS - 1)] : 0;
}

static void
wr(uint32_t addr, uint32_t v)
{
	page(addr, 1)->w[(addr >> 2) & (PAGEWORDS - 1)] = v;
}

/* 1e data is little-endian: BYTE0 is bits 7:0 (PRM Figure 1-3). */
static unsigned
rdbyte(uint32_t addr)
{
	return (rd(addr) >> (8 * (addr & 3))) & 0xFF;
}

static void
wrbyte(uint32_t addr, unsigned b)
{
	unsigned sh = 8 * (addr & 3);

	wr(addr, (rd(addr) & ~(0xFFu << sh)) | ((uint32_t)(b & 0xFF) << sh));
}

static void
fail(const char *why)
{
	if (!failed)
		printf("P9HOST FAIL event %lu: %s\n", events, why);
	failed = 1;
}

static int
next_line(void)
{
	if (have_line)
		return 1;
	if (!rec || !fgets(line, sizeof line, rec))
		return 0;
	have_line = 1;
	return 1;
}

static void
init(void)
{
	const char *path = getenv("P9REC");
	const char *out = getenv("P9OUT");
	uint32_t a, b;

	if (initialised)
		return;
	initialised = 1;
	if (!path)
		path = "p9.rec";
	if (out)
		snprintf(outdir, sizeof outdir, "%s", out);
	rec = fopen(path, "r");
	if (!rec) {
		fprintf(stderr, "p9host: cannot open %s\n", path);
		exit(2);
	}
	while (next_line()) {
		if (line[0] == 'L' && sscanf(line + 1, "%x %x", &a, &b) == 2) {
			if (nrange == 32) {
				fprintf(stderr, "p9host: too many ranges\n");
				exit(2);
			}
			range[nrange].lo = a;
			range[nrange++].hi = b;
		} else if (line[0] == 'M' && sscanf(line + 1, "%x %x", &a, &b) == 2)
			wr(a, b);
		else if (line[0] == 'S') {
			if (sscanf(line + 1, "%x %x %x %x %x", &start[0], &start[1],
			    &start[2], &start[3], &start[4]) != 5) {
				fprintf(stderr, "p9host: bad S record\n");
				exit(2);
			}
		} else if (line[0] == 'G') {
			if (sscanf(line + 1, "%x %x %x %x", &dev[0], &dev[1],
			    &dev[2], &dev[3]) != 4) {
				fprintf(stderr, "p9host: bad G record\n");
				exit(2);
			}
		} else
			break;		/* the first E record stays buffered */
		have_line = 0;
	}
}

/* ---- memory, as the testbench's HobbitMem sees it ------------------ */

uint32_t
p9h_read(uint32_t addr)
{
	init();
	if (!legal(addr)) {
		/* a wrong-path fetch may do this; $P9UNMAPPED=n prints the first n */
		static long show = -1;

		if (show < 0) {
			const char *e = getenv("P9UNMAPPED");

			show = e ? strtol(e, 0, 10) : 0;
		}
		if ((long)unmapped_reads < show)
			printf("P9HOST unmapped read 0x%08x\n", addr);
		unmapped_reads++;
	}
	return rd(addr);
}

void
p9h_write(uint32_t addr, uint32_t v)
{
	init();
	if (!legal(addr)) {
		char why[96];

		snprintf(why, sizeof why,
		    "the machine wrote 0x%08x to 0x%08x, outside every segment",
		    v, addr);
		fail(why);
		return;
	}
	wr(addr, v);
}

/* which: 0 pc, 1 sp, 2 psw, 3 isp, 4 vb */
uint32_t
p9h_start(uint32_t which)
{
	init();
	return start[which % 5];
}

/* ---- the kernel entry ---------------------------------------------- */

static int
hexval(int c)
{
	if (c >= '0' && c <= '9')
		return c - '0';
	if (c >= 'a' && c <= 'f')
		return c - 'a' + 10;
	return -1;
}

static void
put_file(const char *name, uint32_t off, uint32_t addr, uint32_t n)
{
	char path[1024];
	FILE *f;
	uint32_t i;

	if (strcmp(name, "-") == 0) {
		snprintf(path, sizeof path, "%s/console", outdir);
		f = fopen(path, "ab");
	} else {
		char *q;

		snprintf(path, sizeof path, "%s/%s", outdir, name);
		/* the file may be in a subdirectory of the tree: make the way */
		for (q = path + strlen(outdir) + 1; *q; q++)
			if (*q == '/') {
				*q = 0;
				mkdir(path, 0777);
				*q = '/';
			}
		f = fopen(path, "r+b");
		if (!f)
			f = fopen(path, "w+b");
		if (f)
			fseek(f, (long)off, SEEK_SET);
	}
	if (!f) {
		fail("cannot open an output file");
		return;
	}
	for (i = 0; i < n; i++)
		fputc((int)rdbyte(addr + i), f);
	fclose(f);
}

/*
 * Called every clock.  Returns 0 while the stub has not rung, 1 when a
 * floating-point entry has been served, 4 when a system call has (the
 * testbench then does KRET's PSW and ISP), 2 when the served entry was
 * exits, 3 on any disagreement with the recording (the run must stop).
 */
uint32_t
p9h_poll(uint32_t sp)
{
	uint32_t go, id, n, a[4], result, flag, done, addr, off, cnt;
	char kind, name[512];
	int i, k;

	init();
	if (failed)
		return 3;
	go = rd(dev[0]);
	if (go == 0)
		return 0;
	events++;
	if (!next_line() || line[0] != 'E') {
		fail("the machine entered the kernel but the recording has ended");
		return 3;
	}
	if (sscanf(line + 1, " %c %x %x %x %x %x %x", &kind, &id, &n,
	    &a[0], &a[1], &a[2], &a[3]) != 7) {
		fail("bad E record");
		return 3;
	}
	have_line = 0;
	if ((kind == 'K') != (go == 1)) {
		fail("system call / floating-point entry does not match the recording");
		return 3;
	}
	if (kind == 'K') {
		/* the id is the word KCALL stored at ISP-12 (p. 3-29) */
		uint32_t got = rd(start[3] - 12);

		if (got != id) {
			char why[96];

			snprintf(why, sizeof why,
			    "system call %u, the recording has %u", got, id);
			fail(why);
			return 3;
		}
	} else if (rd(sp) != id) {
		char why[96];

		snprintf(why, sizeof why,
		    "trap PC 0x%08x at *(SP), the recording has 0x%08x",
		    rd(sp), id);
		fail(why);
		return 3;
	}
	for (i = 0; i < (int)n && i < 4; i++)
		if (rd(sp + 4 + 4 * i) != a[i]) {
			char why[128];

			snprintf(why, sizeof why,
			    "argument %d is 0x%08x, the recording has 0x%08x "
			    "(%c id 0x%x)", i, rd(sp + 4 + 4 * i), a[i], kind, id);
			fail(why);
			return 3;
		}
	for (;;) {
		if (!next_line()) {
			fail("the recording ends inside an entry");
			return 3;
		}
		have_line = 0;
		if (line[0] == 'B') {
			char *p;

			addr = (uint32_t)strtoul(line + 1, &p, 16);
			while (*p == ' ')
				p++;
			for (k = 0; hexval(p[0]) >= 0 && hexval(p[1]) >= 0; p += 2, k++) {
				if (!legal(addr + k)) {
					fail("the kernel's store is outside every segment");
					return 3;
				}
				wrbyte(addr + k, hexval(p[0]) * 16 + hexval(p[1]));
			}
		} else if (line[0] == 'O') {
			if (sscanf(line + 1, "%511s %x %x %x", name, &off, &addr,
			    &cnt) != 4) {
				fail("bad O record");
				return 3;
			}
			put_file(name, off, addr, cnt);
		} else if (line[0] == 'R') {
			if (sscanf(line + 1, "%x %x %x", &result, &flag, &done) != 3) {
				fail("bad R record");
				return 3;
			}
			break;
		} else {
			fail("unexpected record inside an entry");
			return 3;
		}
	}
	wr(dev[2], result);
	wr(dev[3], flag);
	wr(dev[0], 0);
	wr(dev[1], 1);
	return failed ? 3 : (done ? 2 : (kind == 'K' ? 4 : 1));
}

/* 1 when every recorded entry has been served. */
uint32_t
p9h_finished(void)
{
	init();
	return !next_line();
}

/* The clock budget, in thousands of clocks ($P9KCLOCKS, default 400000). */
uint32_t
p9h_kclocks(void)
{
	const char *s = getenv("P9KCLOCKS");

	return s ? (uint32_t)strtoul(s, 0, 10) : 400000;
}

uint32_t
p9h_events(void)
{
	return (uint32_t)events;
}

uint32_t
p9h_unmapped_reads(void)
{
	return (uint32_t)unmapped_reads;
}
