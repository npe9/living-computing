/*
 * p9kern.c -- the host side of bsv/P9KernTb.bsv (Bluesim BDPI): the board
 * on which the Bluespec core boots the shipped 1e kernel, s9term.
 *
 * Nothing here is a second device model.  tools/p9coreboot.py runs the
 * reference boot (tools/p9boot.py on sem/hobbit_sem.py with a System) and
 * records, besides the retirement trace:
 *
 *   M addr word        the boot memory (the loaded image, the ROM page)
 *   S pc               the entry
 *   D n pa value       the n-th record's instruction read `value` from the
 *                      device register at physical `pa`
 *   W n pa value mask  the n-th record's instruction wrote a device register
 *   I n level pc       after record n the board raised an interrupt
 *   E n                the reference stopped after record n
 *
 * The machine's physical memory is a sparse 32-bit store: RAM is
 * [0x80000000, 0x80800000) (p9boot CHOICES memsize); every other address
 * is a device.  A device *read* is answered from the recording: the
 * request is matched to the earliest unused D record for the same address
 * whose record number lies within WINDOW of the records the core has
 * retired (the instruction making the request is at most a few slots
 * younger than the last one retired).  A request that matches nothing is
 * a read the reference never made -- an operand fetch on a mispredicted
 * path (docs/conformance_1to1.md 1c; PRM p. 2-3 lets the part make it) --
 * and is answered with 0 and counted; it cannot retire, and if it did the
 * trace would differ.  A device *write* is compared with the next W
 * record (address and value) and its byte, when it is Quart channel 0's
 * transmit holding register, goes to the console: the console is the
 * core's own output, not the recording's.
 *
 * The MMU's table walk reads this same memory (pk_peek): the kernel
 * builds its segment and page tables in RAM (raml.s _stbinit, mmu.c).
 */

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PAGEBITS 12
#define PAGEWORDS (1u << (PAGEBITS - 2))
#define NBUCKET 4096
#define RAMLO 0x80000000u
#define RAMHI 0x80800000u
#define WINDOW 8

typedef struct Page Page;
struct Page {
	uint32_t base;
	uint32_t w[PAGEWORDS];
	Page *next;
};

typedef struct {
	uint32_t n, pa, v, mask;
	int used;
} Dev;

typedef struct {
	uint32_t n, level, pc;
} Irq;

static Page *bucket[NBUCKET];
static int initialised;
static uint32_t start_pc;
static uint32_t end_n = 0xFFFFFFFFu;
static Dev *rd_rec, *wr_rec;
static size_t nrd, nwr, ard, awr;
static size_t rd_lo;		/* every D record below this is used */
static size_t wr_next;
static Irq *irq;
static size_t nirq, airq;
static unsigned long spec_reads, wr_bad, rd_dup;
static FILE *console;
static int failed;
static uint32_t retired;	/* records the core has presented (pk_retired) */

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
		fprintf(stderr, "p9kern: out of memory\n");
		exit(2);
	}
	p->base = base;
	p->next = bucket[base % NBUCKET];
	bucket[base % NBUCKET] = p;
	return p;
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

static int
ram(uint32_t a)
{
	return a >= RAMLO && a < RAMHI;
}

static void *
grow(void *p, size_t *cap, size_t n, size_t size)
{
	if (n < *cap)
		return p;
	*cap = *cap ? 2 * *cap : 1024;
	p = realloc(p, *cap * size);
	if (!p) {
		fprintf(stderr, "p9kern: out of memory\n");
		exit(2);
	}
	return p;
}

static void
init(void)
{
	const char *path = getenv("P9KREC");
	const char *cons = getenv("P9KCONSOLE");
	char line[256];
	FILE *f;
	uint32_t a, b, c, d;

	if (initialised)
		return;
	initialised = 1;
	if (!path)
		path = "boot.rec";
	f = fopen(path, "r");
	if (!f) {
		fprintf(stderr, "p9kern: cannot open %s\n", path);
		exit(2);
	}
	while (fgets(line, sizeof line, f)) {
		switch (line[0]) {
		case 'M':
			if (sscanf(line + 1, "%x %x", &a, &b) == 2)
				wr(a, b);
			break;
		case 'S':
			sscanf(line + 1, "%x", &start_pc);
			break;
		case 'D':
			if (sscanf(line + 1, "%x %x %x", &a, &b, &c) == 3) {
				rd_rec = grow(rd_rec, &ard, nrd, sizeof *rd_rec);
				rd_rec[nrd++] = (Dev){a, b, c, 0, 0};
			}
			break;
		case 'W':
			if (sscanf(line + 1, "%x %x %x %x", &a, &b, &c, &d) == 4) {
				wr_rec = grow(wr_rec, &awr, nwr, sizeof *wr_rec);
				wr_rec[nwr++] = (Dev){a, b, c, d, 0};
			}
			break;
		case 'I':
			if (sscanf(line + 1, "%x %x %x", &a, &b, &c) == 3) {
				irq = grow(irq, &airq, nirq, sizeof *irq);
				irq[nirq++] = (Irq){a, b, c};
			}
			break;
		case 'E':
			sscanf(line + 1, "%x", &end_n);
			break;
		}
	}
	fclose(f);
	console = fopen(cons ? cons : "console", "wb");
	printf("P9KERN boot: entry %08x, %zu device reads, %zu device writes, "
	    "%zu interrupts, reference ends at record %u\n",
	    start_pc, nrd, nwr, nirq, end_n);
}

static uint32_t
dev_read(uint32_t pa, uint32_t retired)
{
	size_t i;

	while (rd_lo < nrd && rd_rec[rd_lo].used)
		rd_lo++;
	for (i = rd_lo; i < nrd && rd_rec[i].n <= retired + WINDOW; i++)
		if (!rd_rec[i].used && rd_rec[i].pa == pa &&
		    rd_rec[i].n > retired) {
			rd_rec[i].used = 1;
			return rd_rec[i].v;
		}
	/* The same instruction asking again: a used record still ahead. */
	for (i = rd_lo; i > 0 && rd_rec[i - 1].n > retired; i--)
		if (rd_rec[i - 1].pa == pa) {
			rd_dup++;
			return rd_rec[i - 1].v;
		}
	spec_reads++;
	if (getenv("P9KSPEC"))
		printf("P9KERN unrecorded device read %08x after record %u\n",
		    pa, retired);
	return 0;
}

/* ---- memory, as the testbench's HobbitMem sees it ------------------ */

static uint32_t latched_pa = 0xFFFFFFFFu, latched_v;

/*
 * Called by the memory's fetch rule every clock with the registered read
 * address; `fresh` is 1 on the clock after a readReq (one request), when a
 * device register is answered from the recording and the answer latched.
 */
uint32_t
pk_fetch(uint32_t addr, uint32_t fresh)
{
	init();
	addr &= ~3u;
	if (ram(addr))
		return rd(addr);
	if (fresh) {
		latched_pa = addr;
		latched_v = dev_read(addr, retired);
	}
	return latched_pa == addr ? latched_v : 0;
}

void
pk_write(uint32_t addr, uint32_t v)
{
	init();
	addr &= ~3u;
	if (ram(addr)) {
		wr(addr, v);
		return;
	}
	/*
	 * Past the reference's last record the testbench is only draining the
	 * pipeline: there is nothing to check a device write against, and its
	 * byte is not part of the compared console.
	 */
	if (retired >= end_n)
		return;
	if (wr_next < nwr && wr_rec[wr_next].pa == addr &&
	    wr_rec[wr_next].v == v) {
		wr_next++;
	} else {
		wr_bad++;
		if (!failed)
			printf("P9KERN FAIL: device write %08x to %08x after record "
			    "%u; the recording's next is %08x to %08x (record %u)\n",
			    v, addr, retired,
			    wr_next < nwr ? wr_rec[wr_next].v : 0,
			    wr_next < nwr ? wr_rec[wr_next].pa : 0,
			    wr_next < nwr ? wr_rec[wr_next].n : 0);
		failed = 1;
	}
	/* Quart channel 0's transmit holding register (io.h Duart.txfifo). */
	if (addr == 0xB000010Cu && console) {
		fputc((int)(v & 0xFF), console);
		fflush(console);
	}
}

/* The testbench tells the board, every clock, how many records retired. */
void
pk_retired(uint32_t n)
{
	retired = n;
}

/* The MMU's table walk: a combinational read of physical memory. */
uint32_t
pk_peek(uint32_t addr)
{
	init();
	return rd(addr & ~3u);
}

void
pk_poke(uint32_t addr, uint32_t v)
{
	init();
	if (ram(addr & ~3u))
		wr(addr & ~3u, v);
}

uint32_t
pk_start(void)
{
	init();
	return start_pc;
}

/* The reference's last record, or $P9KLIMIT if smaller. */
uint32_t
pk_end(void)
{
	const char *s = getenv("P9KLIMIT");
	uint32_t lim;

	init();
	if (s) {
		lim = (uint32_t)strtoul(s, 0, 0);
		if (lim < end_n)
			return lim;
	}
	return end_n;
}

/* The clock budget, in thousands ($P9KCLOCKS, default 50,000,000 clocks). */
uint32_t
pk_kclocks(void)
{
	const char *s = getenv("P9KCLOCKS");

	return s ? (uint32_t)strtoul(s, 0, 10) : 50000;
}

uint32_t
pk_failed(void)
{
	return failed;
}

/* Interrupts: the next one's record number (0xFFFFFFFF: none), level, PC. */
static size_t irq_next;

uint32_t
pk_irq_at(void)
{
	init();
	return irq_next < nirq ? irq[irq_next].n : 0xFFFFFFFFu;
}

uint32_t
pk_irq_level(void)
{
	return irq_next < nirq ? irq[irq_next].level : 7;
}

uint32_t
pk_irq_pc(void)
{
	return irq_next < nirq ? irq[irq_next].pc : 0;
}

void
pk_irq_taken(void)
{
	if (irq_next < nirq)
		irq_next++;
}

void
pk_report(void)
{
	size_t i, used = 0, unused = 0;

	init();
	for (i = 0; i < nrd; i++) {
		if (rd_rec[i].used)
			used++;
		else if (rd_rec[i].n <= retired)
			unused++;
	}
	printf("P9KERN devices: %zu of %zu recorded reads replayed, %lu "
	    "repeated, %lu unrecorded (mispredicted path), %zu recorded reads "
	    "up to record %u never requested; %zu of %zu writes matched, "
	    "%lu differed\n",
	    used, nrd, rd_dup, spec_reads, unused, retired, wr_next, nwr,
	    wr_bad);
}
