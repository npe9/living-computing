/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*
 *      File Name  : server.c
 *      Function   : server socket setup
 *                   for debug use
$*      History    :
$*      1994/11/29 : change socket variable name from soc to ComCSocket
$*      1994/11/22 : ifdef for debug print
$*      1994/10/31 : crank in
 *
 */

/*
 *
 * This file contains socket initialization for server
 *
 */
#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <stropts.h>
#include "comerrs.h"

/*
 * Socket object is defined in lower socket access module, socacc.c.
 */
extern int ComCSocket;

/*
 *
 * Socket initialization
 * The members sin_family, sin_port and sin_addr of the arguement server
 *   are expected to have been set the following value before calling
 *   this function.
 *      server.sin_family : AF_INET
 *      server.sin_port   : server port (9000)
 *      server.sin_addr   : server host address
 *
 */
int ComSetupServer(struct sockaddr_in *server)
{
  int s,s_waiting;

  if((s_waiting = socket(AF_INET, SOCK_STREAM, 0)) < 0)
  {
#ifdef	NETDEBUG
    fprintf(stderr, "COMC:socket allocation failed.\n");
#endif
    return( ComErrSocAllocFail );
  }

  if(bind(s_waiting, server, sizeof(struct sockaddr_in)) == -1)
  {
#ifdef	NETDEBUG
    fprintf(stderr, "COMC:cannot bind.\n");
#endif
    return( ComErrBindFail );
  }

  listen(s_waiting, 1);
  s = accept(s_waiting, NULL, NULL);
  close(s_waiting);

  /* man streamio  */
/*  if( ioctl(s, I_SRDOPT, RMSGN) != 0 )
  {
    printf("COMC:cannot change read mode\n");
  }
*/
  /* save socket in global variable */
  ComCSocket = s;

  return( 0 );
}

int ComSetupServerByName(char *hostname, unsigned short port)
{
  struct hostent *host;
  struct sockaddr_in server;
  int s,s_waiting,error;

#ifdef	NETDEBUG
  printf("hostname:%s, port:%d\n", hostname, port);
#endif
  if((host = gethostbyname(hostname)) == NULL)
  {
#ifdef	NETDEBUG
    fprintf(stderr, "COMC:bad hostname!\n");
#endif
    return( ComErrBadHostname );
  }

  bzero((char *)&server, sizeof(server));
  server.sin_family = AF_INET;
  server.sin_port = port;
  bcopy(host->h_addr, (char *)&server.sin_addr, host->h_length);
  error = ComSetupServer( &server );
  return( error );
}

void ComCloseServer(void)
{
  close( ComCSocket );
}
