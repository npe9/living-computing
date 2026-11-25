/*************************************************************************
*  PDSS modernisation (living-computing): the operating-system layer	 *
*  (sysdep.h).  ICOT Free Software terms (COPYRIGHT).			 *
*************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <regex.h>
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
