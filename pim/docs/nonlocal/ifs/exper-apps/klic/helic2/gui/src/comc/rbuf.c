/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*
 *      File Name  : rbuf.c
 *      Function   : receive buffer access
$*      History    :
$*      1994/11/29 : ComErrReadSock, ComErrWriteSock
$*      1994/11/14 : debug print
$*      1994/11/10 : getListOfListOfString instead of getJustification
$*      1994/11/ 5 : getString arg type bug
$*      1994/11/ 4 : typo
$*      1994/10/31 : crank in
 *
 */

#include <stdio.h>

#include "comerrs.h"
#include "comtypes.h"

/*
 * For debug
 */
#ifdef NETDEBUG
#include "comdebug.h"
#define PSW PSRECV
#endif

/*
 * prototypes
 */
int getTag(char *c);
short getCommand(short *command);
int getChar(char *c);
int getUChar(unsigned char *c);
int getShort(short *h);
int getUShort(unsigned short *h);
int getInt(int *i);
int getUInt(unsigned int *i);
int getString(char **s);
int getListOfString(char ***l);
int getListOfListOfString(COMLIST **arg3);
char* makeString(int size);
void freeString(char *s);
char** makeListOfString(int size);
void freeListOfString(char **l);
void freeListOfListOfString(char ***l);

/*
 *
 */
int getTag(char *tag)
{
  int error;
  unsigned char uc;

  if( (error = getOneByte(&uc)) != 0)
    return( error );

  *tag = (char) uc;

#ifdef NETDEBUG
  DebugPrintTag(*tag, PSW);
#endif

  return( 0 );
}

short getCommand(short *command)
{
  int error;

  error = get2Bytes( command );

#ifdef NETDEBUG
  DebugPrintCommand(*command, PSW);
#endif

  return ( error );
}

int getChar(char *c)
{
  unsigned char uc;
  char tag;
  int error;


  if( (error = getTag(&tag)) != 0 )
    return( error );

  if( tag != TAGCHAR )
    /* received data does not match to the expected type of message argument */
    return( ComErrMisType );

  if( (error = getOneByte( &uc )) != 0 )
    return( error );

  *c = (char) uc;

#ifdef NETDEBUG
  DebugPrintChar(*c, PSW);
#endif

  return( 0 );
}

int getUChar(unsigned char *c)
{
  int error;
  char tag;

  if( (error = getTag(&tag)) != 0 )
    return( error );

  if( tag != TAGUCHAR )
    /* received data does not match to the expected type of message argument */
    return( ComErrMisType );

  error = getOneByte( c );

#ifdef NETDEBUG
  DebugPrintChar(*c, PSW);
#endif

  return( error );
}

int getShort(short *h)
{
  int error;
  char tag;

  if( (error = getTag(&tag)) != 0 )
    return(error);

  if( tag != TAGSHORT )
    /* received data does not match to the expected type of message argument */
    return( ComErrMisType );

  error = get2Bytes( h );

#ifdef NETDEBUG
  DebugPrintShort(*h, PSW);
#endif

  return( error );
}

int getUShort(unsigned short *h)
{
  int error;
  char tag;

  if( (error = getTag(&tag)) != 0 )
    return(error);

  if( tag != TAGUSHORT )
    /* received data does not match to the expected type of message argument */
    return( ComErrMisType );

  error = get2Bytes( h );

#ifdef NETDEBUG
  DebugPrintShort(*h, PSW);
#endif

  return( error );
}

int getInt(int *i)
{
  int error;
  unsigned char  work[4];
  char tag;

  if( (error = getTag(&tag)) != 0 )
    return(error);

  if( tag != TAGINT )
    /* received data does not match to the expected type of message argument */
    return( ComErrMisType );

  if( (error = getOneByte( &work[0] )) != 0 )
    return(error);
  if( (error = getOneByte( &work[1] )) != 0 )
    return(error);
  if( (error = getOneByte( &work[2] )) != 0 )
    return(error);
  if( (error = getOneByte( &work[3] )) != 0 )
    return(error);

  *i = work[0] << 24 | work[1] << 16 | work[2] << 8 | work[3];
  *i = ntohl( *i );

#ifdef NETDEBUG
  DebugPrintInt(*i, PSW);
#endif

  return( 0 );
}

int getUInt(unsigned int *i)
{
  int error;
  unsigned char  work[4];
  char tag;

  if( (error = getTag(&tag)) != 0 )
    return(error);

  if( tag != TAGUINT )
    /* received data does not match to the expected type of message argument */
    return( ComErrMisType );

  if( (error = getOneByte( &work[0] )) != 0 )
    return(error);
  if( (error = getOneByte( &work[1] )) != 0 )
    return(error);
  if( (error = getOneByte( &work[2] )) != 0 )
    return(error);
  if( (error = getOneByte( &work[3] )) != 0 )
    return(error);

  *i = work[0] << 24 | work[1] << 16 | work[2] << 8 | work[3];
  *i = (unsigned int) ntohl( *i );

#ifdef NETDEBUG
  DebugPrintInt(*i, PSW);
#endif

  return( 0 );
}


int getString(COMSTRING *s)
{
  int	i,error;
  short size;
  char *ss;
  char tag;

  if( (error = getTag(&tag)) != 0 )
    return(error);

  if( tag != TAGSTR )
    /* received data does not match to the expected type of message argument */
    return( ComErrMisType );

  /* get element size */
  if( (error = get2Bytes( &size )) != 0 )
    return(error);

#ifdef NETDEBUG
  DebugPrintSize(size, PSW);
#endif

  if( (*s = makeString( size )) == (char *) NULL )
    /* memory allocation failed */
    return( ComErrMallocFail );

  ss = *s;
  ss[0] = '\0';
  if ( size > 0 )
  {
    for ( i=0 ; i<size ; i++) {
      if( (error = getOneByte( &ss[i] )) != 0 )
      {
	freeString(ss);
	return(error);
      }
    }
    ss[i] = '\0';
  }

#ifdef NETDEBUG
  DebugPrintString(ss, PSW);
#endif

  return ( 0 );
}

int getListOfString(COMLIST *l)
{
  int i, error;
  short size;
  char **ll;
  char tag;

  if( (error = getTag(&tag)) != 0 )
    return(error);
  if( tag != TAGLIST )
    return( ComErrMisType );

  if( (error = get2Bytes( &size )) != 0 )
    return(error);

#ifdef NETDEBUG
  DebugPrintSize(size, PSW);
#endif

  if( (*l = makeListOfString( size )) == (char **)NULL )
    return( ComErrMallocFail );

  ll = *l;
  ll[0] = (char *) NULL;		/* sentinel */
  if ( size > 0 )
  {
    for ( i=0 ; i<size ; i++)
    {
      if( (error = getString( &ll[i] )) != 0 )
      {
	/* sentinel for free */
	ll[i] = (char *) NULL;
	freeListOfString(ll);
	return( error );
      }
    }
    ll[i] = (char *) NULL;	/* sentinel */
  }
  return ( 0 );
}

/*
 * This is the special function
 *   for receive justification list message.
 *
 */
int getListOfListOfString(COMLIST **arg3)
{
  int i, error;
  short size;
  COMLIST *l;
  char tag;

  if( (error = getTag(&tag)) != 0 )
    return(error);

  if( tag != TAGLIST )
    return( ComErrMisType );

  if( (error = get2Bytes( &size )) != 0 )
    return(error);

#ifdef NETDEBUG
  DebugPrintSize(size, PSW);
#endif

  /* make list of list of string */
  /* size+1 for sentinel */
  *arg3 = (COMLIST *) malloc( (size+1) * sizeof(COMLIST) );
  l = *arg3;
  if( l == (COMLIST *) NULL )
  {
    return( ComErrMallocFail );
  }

  l[0]  = (COMLIST) NULL;	/* sentinel */
  if ( size > 0 )
  {
    for ( i=0 ; i<size ; i++)
    {
      if( (error = getListOfString(&l[i])) != 0 )
      {
	/* set sentinel for free */
	l[i]  = (COMLIST) NULL;
	freeListOfListOfString(l);
	return( error );
      }
    }
    l[i]  = (COMLIST) NULL;	/* sentinel */
  }
  return ( 0 );
}

char* makeString(int size)
{
  char *s;

  /* size+1 for sentinel */
  s = (char *) malloc( size+1 );

  return (s);
}

void freeString(char *s)
{
  free( s );
}

char** makeListOfString(int size)
{
  char **l;

  /* size+1 for sentinel */
  l = (char **) malloc( (size+1) * sizeof(char *) );

  return (l);
}

void freeListOfString(char **l)
{
  int i;

  i = 0;
  while( l[i] != (char *) NULL )
  {
    free( l[i] );
    i++;
  }
  free( l );
  return;
}

void freeListOfListOfString(char ***l)
{
  int i;

  i = 0;
  while( l[i] != (char **) NULL )
  {
    freeListOfString( l[i] );
    i++;
  }
  free( l );
  return;
}
