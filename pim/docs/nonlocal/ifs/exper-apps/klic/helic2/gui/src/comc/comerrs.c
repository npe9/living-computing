/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*
 *      File Name  : comerrs.c
 *      Function   : error message table
$*      History    :
$*      1994/11/30 : ComErrEOFDetect
$*      1994/11/29 : ComErrReadSock, ComErrWriteSock
$*      1994/11/ 7 : crank in
 *
 */

#include "comerrs.h"

#define FATAL	0
#define	ERROR	1
#define	WARNING	2

ComErrorInfo ComErrorTable[] = {
  0,     "",
/* ComErrMisType */
  FATAL, "Protocol Error: message type mismatch.",
/* ComErrMallocFail */
  FATAL, "Com Error: cannot allocate memory.",
/* ComErrSocAllocFail */
  FATAL, "Com Error: cannot allocate socket.",
/* ComErrConnectFail */
  FATAL, "Com Error: cannot connect to server.",
/* ComErrBindFail */
  FATAL, "Com Error: cannot bind socket.",
/* ComErrBadHostname */
  FATAL, "Com Error: cannot get host by name.",
/* ComErrUnknown */
  FATAL, "Protocol Error: unknown message.",
/* ComErrReadSock */
  FATAL, "Com Error: cannot read socket.",
/* ComErrWriteSock */
  FATAL, "Com Error: cannot write socket.",
/* ComErrEOFDetect */
  FATAL, "Protocol Error: EOF detected while reading socket.",
  0,	 ""
};
