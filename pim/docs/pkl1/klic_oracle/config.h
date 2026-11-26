/* hand-written replacement for Configure output (macOS arm64, clang) */
#define Unknown_cpu
#define KLICBIN "PREFIXDIR/prefix/bin"
#define KLICLIB "PREFIXDIR/prefix/lib"
#define KLICINCLUDE "PREFIXDIR/prefix/include"
#define KLIC_COMPILER "PREFIXDIR/prefix/lib/klic/kl1cmp"
#define KLIC_DBMAKER "PREFIXDIR/prefix/lib/klic/klicdb"
#define CC "cc"
#define LD "cc"
#define RANLIB "ranlib"
#define UOPTFLAGS ""
#define LIBRARIES "-lklic -lm"
#define LIBRARIES_T "-lklict -lm"
#define LIBRARIES_D "-lklicd -lm"
#define LIBRARIES_S "-lklics -lm"
#define KLIC_CC_OPTIONS "-std=gnu89 -w -Wno-error -Wno-implicit-function-declaration -Wno-int-conversion -Wno-incompatible-pointer-types -Wno-return-type -Wno-implicit-int -fcommon"
#define KLIC_LD_OPTIONS ""
#undef ASYNCIO
#define STRINGH
#define STDDEFH
#define SETLINEBUF
#define USELOCKF
#define USESIG
#define GETRUSAGE
#define USEBCMP
#define USEBCOPY
#define USEBZERO
#define USESTRCHR
#define USEUSLEEP
#undef USEULIMIT
#define USEGETDTABLESIZE
#define USETIMER
#define NRAND48
#define USESTREAMINCLUDEDIR
#undef USEPROCBIND
#undef XTERM
#ifdef USEBCMP
#define BCMP(x,y,len)		bcmp(x,y,len)
#else
#define BCMP(x,y,len)		memcmp(x,y,len)
#endif
#ifdef USEBCOPY
#define BCOPY(from,to,len)	bcopy(from,to,len)
#else
#define BCOPY(from,to,len)	memcpy(to,from,len)
#endif
#ifdef USEBZERO
#define BZERO(from,len)		bzero(from,len)
#else
#define BZERO(from,len)		memset(from,0,len)
#endif
#ifdef USESTRCHR
#define STRCHR			strchr
#else
#define STRCHR			index
#endif
