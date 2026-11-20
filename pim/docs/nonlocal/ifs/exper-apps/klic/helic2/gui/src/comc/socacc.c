/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*
 *      File Name  : socacc.c
 *      Function   : low level socket access and buffering
$*      History    :
$*      1994/11/30 : syscall interruption
$*      1994/11/29 : ComErrReadSock, ComErrWriteSock
$*      1994/11/29 : change socket variable name from soc to ComCSocket
$*      1994/11/15 : debug print
$*      1994/10/31 : crank in
 *
 */

/*
 *
 * This file contains low level functions of socket operations.
 *
 */
#include <stdio.h>
#include <sys/errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include "comparams.h"
#include "comerrs.h"

/*
 * For debug
 */
#ifdef NETDEBUG
#include "comdebug.h"
#endif

extern errno;

int ComCSocket;	/* socket object */

static unsigned char rbuf[RBUFSIZE];	/* receive buffer */
static int rpos = 0;	/* current position of receive buffer (0 origin) */
static int rlen = 0;	/* current size of chars contained in receive buffer */

static unsigned char sbuf[SBUFSIZE];	/* send buffer */
static int spos = 0;	/* current position of send buffer (0 origin) */

/*
 *
 * Low layer access methods
 *
 */

/*
 * Receive buffering function
 */
int readBytesFromSocket()
{
  int result;

 readagain:
  result = read(ComCSocket, rbuf, RBUFSIZE);
  if( result == 0 )
  {
    /* EOF detected */
    rlen = 0;
    rpos = 0;
    return(ComErrEOFDetect);
  }
  else if( result > 0 )
  {
    /* normally read */
    rlen = result;
    rpos = 0;
  }
  else if( errno == EINTR )
  {
    /* interrupt while read syscall */
#ifdef	NETDEBUG
    printf("COMC:interrupt while read. try again\n");
#endif
    goto readagain;
  }
  else
  {
#ifdef	NETDEBUG
    fprintf(stderr, "COMC:read error. errno(hex):%x\n",errno);
#endif
    rlen =  0;		/* for safety */
    rpos = 0;		/* for safety */
    return(ComErrReadSock);
  }

#ifdef NETDEBUG
  DebugPrintReadBuf(rlen, PSRECV);
#endif

  return(0);
}

/*
 * Get one byte from the receive buffer.
 * If Pos >= Len then read at most BUFLEN size of bytes from socket
 * into receive buffer.
 */
int getOneByte(unsigned char *c)
{
  int error;

  if ( rpos >= rlen )
  {
    if( (error = readBytesFromSocket()) != 0 )
      return(error);
  }
  *c = rbuf[rpos];
  rpos++;

  return( 0 );
}

/*
 * Two bytes access
 * This is chiefly used to get element size of string and list type structure.
 */
int get2Bytes(short *j)
{
  unsigned char	work[2];
  int error;

  /* get element size */
  if( (error = getOneByte( &work[0] )) != 0 )
    return(error);
  if( (error = getOneByte( &work[1] )) != 0 )
    return(error);

  *j = work[0] << 8 | work[1];
  *j = ntohs( *j );

  return( 0 );
}


/*
 * Send buffer flushing
 */
int flushSendBuffer()
{
  int result;

#ifdef	NETDEBUG
  DebugPrintWriteBufPos(spos, PSSEND);
#endif

  while( spos > 0 )
  {
  writeagain:
    result = write(ComCSocket, sbuf, spos);
#ifdef NETDEBUG
    DebugPrintWriteBuf(result, PSSEND);
#endif
    if( result >= 0 )
    {
      /* normally written */
      spos -= result;
    }
    else if( errno == EINTR )
    {
      /* interrupt while write syscall */
#ifdef	NETDEBUG
    printf("COMC:interrupt while write. try again\n");
#endif
      goto writeagain;
    }
    else
    {
#ifdef	NETDEBUG
      printf("COMC:write error. errno(hex):%x\n",errno);
#endif
      return(ComErrWriteSock);
    }
  }

  /* here spos should be 0 */
#ifdef	NETDEBUG
  DebugPrintWriteBufPos(spos, PSSEND);
#endif
  return(0);
}

/*
 * Put one byte to the send buffer.
 * If spos >= BUFSIZE then write the contents of send buffer
 * into socket.
 */
int putOneByte(unsigned char c)
{
  int error;

  if ( spos >= SBUFSIZE ) {
    if( (error = flushSendBuffer()) != 0 )
      return(error);
  }
  sbuf[spos] = c;
  spos++;
  return( 0 );
}

/*
 * Two bytes access
 */
int put2Bytes(short h)
{
  short i;
  unsigned char  work[2];
  int error;

  i = htons( h );
  work[0] =  i >> 8;
  work[1] =  0x00ff & i;
  if( (error = putOneByte(work[0])) != 0 )
    return(error);
  if( (error = putOneByte(work[1])) != 0 )
    return(error);

  return( 0 );
}
