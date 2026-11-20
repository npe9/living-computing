/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*
 *      File Name  : comtypes.h
 *      Function   : com/c type definition
$*      History    :
$*      1994/11/ 4 : typo
$*      1994/10/31 : crank in
 *
 */

/*
 * types used in COM/C
 */

#ifndef COMTYPES

typedef char	COMCHAR;
typedef short	COMSHORT;
typedef int	COMINT;
typedef char   *COMSTRING;
typedef char  **COMLIST;

typedef unsigned char	COMUCHAR;
typedef unsigned short	COMUSHORT;
typedef unsigned int	COMUINT;


/*
 * TAG definition
 */

#define	TAGCHAR		1
#define	TAGUCHAR	2
#define	TAGSHORT	3
#define	TAGUSHORT	4
#define	TAGINT		5
#define	TAGUINT		6
#define	TAGSTR		7
#define	TAGLIST		8

#define COMTYPES

#endif
