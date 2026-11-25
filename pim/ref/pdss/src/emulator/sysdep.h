/*************************************************************************
*  PDSS modernisation (living-computing): the operating-system layer.	 *
*  Not part of the 1992 sources.  ICOT Free Software terms (COPYRIGHT).	 *
*************************************************************************/

/* Everything PDSS needs beyond ISO C comes from POSIX, and only through
   this header and sysdep.c: getcwd, chdir, unlink, getpid, alarm, pause,
   getrusage, getpwnam, the directory calls, sigprocmask and kill, the
   signals beyond ISO C's (SIGQUIT, SIGTSTP, SIGALRM), and the BSD
   regular-expression calls the 1992 code used, supplied over POSIX
   <regex.h>.  No other source file includes a POSIX header (checked by
   ../../tools/posixcheck.py).  A port to a system without POSIX
   (Windows, for one) replaces this header and sysdep.c. */

#ifndef PDSS_SYSDEP_H
#define PDSS_SYSDEP_H

#include <stddef.h>
#include <signal.h>		/* ISO C; sigset_t below is POSIX */

/* The signals PDSS uses beyond ISO C's SIGINT, SIGTERM and SIGFPE. */
#define PDSS_SIGQUIT	SIGQUIT
#define PDSS_SIGTSTP	SIGTSTP
#define PDSS_SIGALRM	SIGALRM

/* Call-for-call wrappers of the POSIX functions PDSS calls. */
int  pdss_getpid(void);
void pdss_pause(void);				/* pause(2) */
unsigned pdss_alarm(unsigned seconds);		/* alarm(2) */
int  pdss_chdir(const char *dir);		/* 0 on success */
int  pdss_unlink(const char *file);		/* 0 on success */
const char *pdss_home_of(const char *user);	/* getpwnam(3)->pw_dir, or NULL */

/* CPU time used so far (getrusage(2), RUSAGE_SELF), as it reports it. */
typedef struct { long user_sec, user_usec, sys_sec, sys_usec; } PDSS_CPUTIME;
void pdss_cputime(PDSS_CPUTIME *t);

/* Directory reading (opendir(3) and friends); readdir gives the next
   entry's name, NULL at the end. */
typedef struct pdss_dir PDSS_DIR;
PDSS_DIR   *pdss_opendir(const char *path);
const char *pdss_readdir(PDSS_DIR *d);
void        pdss_closedir(PDSS_DIR *d);

/* BSD sigblock/sigsetmask, over POSIX sigprocmask: block one signal
   (saving the previous mask in *OLD unless OLD is NULL), put a saved
   mask back, unblock one signal. */
typedef sigset_t PDSS_SIGMASK;
void pdss_sig_block(int sig, PDSS_SIGMASK *old);
void pdss_sig_restore(const PDSS_SIGMASK *old);
void pdss_sig_unblock(int sig);

/* Stop the process (job control, as on SIGTSTP); returns when continued. */
void pdss_stop_self(void);

/* BSD: compile a regular expression (NULL on success) and match one. */
char *re_comp(const char *s);
int   re_exec(const char *s);

/* getwd(3) (removed from POSIX): the current directory into the array
   BUF (PDSS's callers pass arrays, so their size is known here). */
char *pdss_getwd(char *buf, size_t size);
#define getwd(buf) pdss_getwd((char *)(buf), sizeof(buf))

/* Test hook: with PDSS_WORLD set, a directory under the one PDSS started
   in is reported with that prefix replaced by PDSS_WORLD (Micro PIMOS's
   "World is" line; see ../../conformance.sh).  Unset, nothing changes. */
void pdss_world(char *path);

#endif
