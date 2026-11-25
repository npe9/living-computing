/*************************************************************************
*  PDSS modernisation (living-computing): the operating-system layer	 *
*  (sysdep.h).  ICOT Free Software terms (COPYRIGHT).			 *
*************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>
#include <unistd.h>
#include <dirent.h>
#include <pwd.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/resource.h>
#include "sysdep.h"

static regex_t re_cur;
static int re_have;

char *re_comp(const char *s)
{
    if(!s || !*s) return re_have ? NULL : "No previous regular expression";
    if(re_have){ regfree(&re_cur); re_have = 0; }
    if(regcomp(&re_cur, s, REG_NOSUB)) return "Invalid regular expression";
    re_have = 1;
    return NULL;
}

int re_exec(const char *s)
{
    if(!re_have) return -1;
    return regexec(&re_cur, s, 0, NULL, 0) == 0;
}

char *pdss_getwd(char *buf, size_t size)
{
    if(!getcwd(buf, size)){
	strcpy(buf, ".");
	return NULL;
    }
    return buf;
}

void pdss_world(char *path)
{
    static char start[1024];
    const char *w = getenv("PDSS_WORLD");
    size_t n;
    char buf[1024];
    if(!w) return;
    if(!start[0] && !getcwd(start, sizeof start)) return;
    n = strlen(start);
    if(strncmp(path, start, n) == 0 && (path[n] == 0 || path[n] == '/')){
	snprintf(buf, sizeof buf, "%s%s", w, path + n);
	strcpy(path, buf);
    }
}

void pdss_sig_block(int sig, PDSS_SIGMASK *old)
{
    sigset_t s;
    sigemptyset(&s);
    sigaddset(&s, sig);
    sigprocmask(SIG_BLOCK, &s, old);
}

void pdss_sig_restore(const PDSS_SIGMASK *old)
{
    sigprocmask(SIG_SETMASK, old, NULL);
}

void pdss_sig_unblock(int sig)
{
    sigset_t s;
    sigemptyset(&s);
    sigaddset(&s, sig);
    sigprocmask(SIG_UNBLOCK, &s, NULL);
}

/* The 1992 stop_pdss: let SIGTSTP through with its default action, stop,
   and ignore it again once continued. */
void pdss_stop_self(void)
{
    signal(SIGTSTP, SIG_DFL);
    pdss_sig_unblock(SIGTSTP);
    kill(getpid(), SIGTSTP);
    pdss_sig_block(SIGTSTP, NULL);
    signal(SIGTSTP, SIG_IGN);
}

int pdss_getpid(void) { return (int)getpid(); }
void pdss_pause(void) { pause(); }
unsigned pdss_alarm(unsigned seconds) { return alarm(seconds); }
int pdss_chdir(const char *dir) { return chdir(dir); }
int pdss_unlink(const char *file) { return unlink(file); }

const char *pdss_home_of(const char *user)
{
    struct passwd *pw = getpwnam(user);
    return pw ? pw->pw_dir : NULL;
}

void pdss_cputime(PDSS_CPUTIME *t)
{
    struct rusage u;
    getrusage(RUSAGE_SELF, &u);
    t->user_sec = (long)u.ru_utime.tv_sec;
    t->user_usec = (long)u.ru_utime.tv_usec;
    t->sys_sec = (long)u.ru_stime.tv_sec;
    t->sys_usec = (long)u.ru_stime.tv_usec;
}

struct pdss_dir { DIR *d; };

PDSS_DIR *pdss_opendir(const char *path)
{
    PDSS_DIR *r;
    DIR *d = opendir(path);
    if(!d) return NULL;
    r = malloc(sizeof *r);
    if(!r){ closedir(d); return NULL; }
    r->d = d;
    return r;
}

const char *pdss_readdir(PDSS_DIR *d)
{
    struct dirent *e = readdir(d->d);
    return e ? e->d_name : NULL;
}

void pdss_closedir(PDSS_DIR *d)
{
    closedir(d->d);
    free(d);
}
