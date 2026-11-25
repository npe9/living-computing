/*************************************************************************
*  PDSS modernisation (living-computing): the operating-system layer.	 *
*  Not part of the 1992 sources.  ICOT Free Software terms (COPYRIGHT).	 *
*************************************************************************/

/* Everything PDSS needs beyond ISO C comes from POSIX, through this
   header: <unistd.h> (getcwd, chdir, unlink, getpid, alarm, pause), the
   signals PDSS catches (SIGINT, SIGQUIT, SIGTERM, SIGTSTP, SIGALRM), and
   the BSD regular-expression calls the 1992 code used, supplied by
   sysdep.c over POSIX <regex.h>.  A port to a system without POSIX
   (Windows, for one) replaces this header and sysdep.c. */

#ifndef PDSS_SYSDEP_H
#define PDSS_SYSDEP_H

#include <stddef.h>
#include <unistd.h>
#include <signal.h>

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
