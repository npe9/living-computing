/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*
 *      File Name  : sbuf.c
 *      Function   : send buffer access
$*      History    :
$*      1994/11/29 : ComErrReadSock, ComErrWriteSock
$*      1994/11/14 : debug print
$*      1994/11/10 : putListOfListOfString instead of putJustification
$*      1994/11/ 7 : putJustification for debug
$*      1994/11/ 4 : typo
$*      1994/10/31 : crank in
 *
 */

#include <stdio.h>
#include "comtypes.h"

/*
 * For debug
 */
#ifdef NETDEBUG
#include "comdebug.h"
#define PSW PSSEND
#endif

int putTag(char tag)
{
  int error;
  error = putOneByte( (unsigned char) tag );

#ifdef NETDEBUG
  DebugPrintTag(tag, PSW);
#endif

  return( error );
}

int putCommand(short command)
{
  int error;

  error = put2Bytes( command );

#ifdef NETDEBUG
  DebugPrintCommand(command, PSW);
#endif

  return( error );
}

int putChar(char c)
{
  int error;

  if( (error = putTag( TAGCHAR )) != 0 )
    return(error);

  if( (error = putOneByte( (unsigned char) c )) != 0 )
    return(error);

#ifdef NETDEBUG
  DebugPrintChar(c, PSW);
#endif

  return( 0 );
}

int putUChar(unsigned char c)
{
  int error;

  if( (error = putTag( TAGUCHAR )) != 0 )
    return(error);

  if( (error = putOneByte( c )) != 0 )
    return(error);

#ifdef NETDEBUG
  DebugPrintChar(c, PSW);
#endif

  return( 0 );
}

int putShort(short h)
{
  int error;

  if( (error = putTag( TAGSHORT )) != 0 )
    return(error);

  if( (error = put2Bytes( h )) != 0 )
    return(error);

#ifdef NETDEBUG
  DebugPrintShort(h, PSW);
#endif

  return( 0 );
}

int putUShort(unsigned short h)
{
  int error;

  if( (error = putTag( TAGUSHORT )) != 0 )
    return(error);

  if( (error = put2Bytes( (short) h )) != 0 )
    return(error);

#ifdef NETDEBUG
  DebugPrintShort(h, PSW);
#endif

  return( 0 );
}

int putInt(int i)
{
  unsigned int j;
  int error;
  unsigned char  work[4];


  if( (error = putTag( TAGINT )) != 0 )
    return(error);

  j = (unsigned int) htonl( i );
  work[0] =  j >> 24;
  work[1] = (j >> 16) & 0x000000ff;
  work[2] = (j >>  8) & 0x000000ff;
  work[3] =  j        & 0x000000ff;
  if( (error = putOneByte(work[0])) != 0 )
    return(error);
  if( (error = putOneByte(work[1])) != 0 )
    return(error);
  if( (error = putOneByte(work[2])) != 0 )
    return(error);
  if( (error = putOneByte(work[3])) != 0 )
    return(error);

#ifdef NETDEBUG
  DebugPrintInt(i, PSW);
#endif

  return( 0 );
}

int putUInt(unsigned int i)
{
  unsigned int j;
  int error;
  unsigned char  work[4];

  if( (error = putTag( TAGUINT )) != 0 )
    return(error);

  j = (unsigned int) htonl( i );
  work[0] =  j >> 24;
  work[1] = (j >> 16) & 0x000000ff;
  work[2] = (j >>  8) & 0x000000ff;
  work[3] =  j        & 0x000000ff;
  if( (error = putOneByte(work[0])) != 0 )
    return(error);
  if( (error = putOneByte(work[1])) != 0 )
    return(error);
  if( (error = putOneByte(work[2])) != 0 )
    return(error);
  if( (error = putOneByte(work[3])) != 0 )
    return(error);

#ifdef NETDEBUG
  DebugPrintInt(i, PSW);
#endif

  return( 0 );
}

/*
 * string is encoded as follows.
 *    "abc" : 'a','b','c','\0'  -> 0x0003616263
 *
 */
int putString(char *s)
{
  int error;
  short size, i;

  /* string tag */
  if( (error = putTag( TAGSTR )) != 0 )
    return(error);

  /* length of string */
  size = strlen(s);
  if( (error = put2Bytes( size )) != 0 )
    return(error);

#ifdef NETDEBUG
  DebugPrintSize(size, PSW);
#endif

  /* body of string */
  if ( size > 0 )
  {
    for ( i=0 ; i<size ; i++)
    {
      if( (error = putOneByte( s[i] )) != 0 )
	return(error);
    }
  }

#ifdef NETDEBUG
  DebugPrintString(s, PSW);
#endif

  return( 0 );
}

/*
 * string list is encoded as follows.
 *    ["a","bc"] : "a","bc", (STRING *) NULL
 *      -> 0x080002070001610700026263
 *
 */
int putListOfString(char **l)
{
  short size, i;
  int error;

  /* list tag */
  if( (error = putTag( TAGLIST )) != 0 )
    return(error);

  /* count of element of list */
  size = 0;
  while ( l[size] != (char *) NULL )
  {
    size++;
  }
  if( (error = put2Bytes( size )) != 0 )
    return(error);

#ifdef NETDEBUG
  DebugPrintSize(size, PSW);
#endif

  /* body of list */
  if ( size > 0 )
  {
    for ( i=0 ; i<size ; i++)
    {
      if( (error = putString( l[i] )) != 0 )
	return(error);
    }
  }
  return(0);
}

/*
 * For debug
 *
 * This is the special function
 *   for sending justification list message.
 *
 */
int putListOfListOfString(COMLIST *l)
{
  int i, error;
  short size;

  /* list tag */
  if( (error = putTag( TAGLIST )) != 0 )
    return(error);

  /*
   * count of element of list
   */
  size = 0;
  while ( l[size] != (COMLIST) NULL )
  {
    size++;
  }
  if( (error = put2Bytes( size )) != 0 )
    return(error);

#ifdef NETDEBUG
  DebugPrintSize(size, PSW);
#endif

  /* body of list */
  if ( size > 0 )
  {
    for ( i=0 ; i<size ; i++)
    {
      if( (error = putListOfString(l[i])) != 0 )
	return(error);
    }
  }
  return(0);
}
