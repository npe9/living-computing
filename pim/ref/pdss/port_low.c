/* PORT: keep every address PDSS can store in a 32-bit cell below 2 GB.
 * PDSS keeps pointers in `int` (cell.h).  The program is linked low
 * (no PIE, small __PAGEZERO); this file gives it a low heap and a low
 * stack.  x86_64 only (Linux: build with -m32 instead and drop this). */
#ifndef PDSS_NO_LOW
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <sys/mman.h>

#define LOW_BASE  ((char *)0x20000000)
#define LOW_SIZE  (0x50000000UL)          /* 1.25 GB reserved, lazily used */
#define STACK_SIZE (64UL << 20)

static char *low_next, *low_end;

static void low_init(void)
{
    char *p = mmap(LOW_BASE, LOW_SIZE, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANON | MAP_FIXED, -1, 0);
    if (p != LOW_BASE) { perror("pdss: low mmap"); exit(1); }
    low_next = p;
    low_end = p + LOW_SIZE;
}

void *pdss_malloc(size_t n)
{
    char *p;
    if (!low_next) low_init();
    n = (n + 15) & ~(size_t)15;
    if (low_next + n + 16 > low_end) return NULL;
    *(size_t *)low_next = n;
    p = low_next + 16;
    low_next = p + n;
    return p;
}

void pdss_free(void *p) { (void)p; }      /* bump allocator: never reused */

void *pdss_realloc(void *p, size_t n)
{
    void *q = pdss_malloc(n);
    if (p && q) {
        size_t old = *(size_t *)((char *)p - 16);
        memcpy(q, p, old < n ? old : n);
    }
    return q;
}

void *pdss_calloc(size_t a, size_t b)
{
    void *p = pdss_malloc(a * b);
    if (p) memset(p, 0, a * b);
    return p;
}

extern int pdss_main(int, char **);
static int g_argc; static char **g_argv; static int g_rc;

static void *run(void *x) { (void)x; g_rc = pdss_main(g_argc, g_argv); return NULL; }

int main(int argc, char **argv)
{
    pthread_t t; pthread_attr_t a; int i;
    char *stk;
    /* copy argv low: option.c keeps pointers into it */
    g_argv = pdss_malloc((argc + 1) * sizeof(char *));
    for (i = 0; i < argc; i++) {
        g_argv[i] = pdss_malloc(strlen(argv[i]) + 1);
        strcpy(g_argv[i], argv[i]);
    }
    g_argv[argc] = NULL; g_argc = argc;
    stk = pdss_malloc(STACK_SIZE);
    pthread_attr_init(&a);
    pthread_attr_setstack(&a, stk, STACK_SIZE);
    if (pthread_create(&t, &a, run, NULL)) { perror("pdss: thread"); return 1; }
    pthread_join(t, NULL);
    return g_rc;
}

#endif /* PDSS_NO_LOW */

#include <stddef.h>
/* PORT: BSD re_comp/re_exec over POSIX basic regular expressions. */
#include <regex.h>
static regex_t re_cur; static int re_have;
char *re_comp(const char *s)
{
    if (!s || !*s) return re_have ? NULL : "No previous regular expression";
    if (re_have) { regfree(&re_cur); re_have = 0; }
    if (regcomp(&re_cur, s, REG_NOSUB)) return "Invalid regular expression";
    re_have = 1;
    return NULL;
}
int re_exec(const char *s)
{
    if (!re_have) return -1;
    return regexec(&re_cur, s, 0, NULL, 0) == 0;
}
