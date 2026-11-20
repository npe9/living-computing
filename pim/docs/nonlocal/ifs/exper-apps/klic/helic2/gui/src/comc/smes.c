/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*
 *      File Name  : smes.c
 *      Function   : send message to socket according to message type
 *                 : chiefly for debug use
$*      History    :
$*      1995/ 1/12 : obsolete putMessageH : extensional functions
$*      1994/11/29 : ComErrReadSock, ComErrWriteSock
$*      1994/11/10 : bug : arg3 type is string, not short in putMessageH
$*      1994/11/10 : putListOfListOfString instead of putJustification
$*      1994/11/10 : crank in
 *
 */

#include <stdio.h>
#include "comtypes.h"

int putMessageA(COMSHORT command)
{
  int error;

  if( (error = putCommand(command)) != 0 )
    return(error);

  if( (error = flushSendBuffer()) != 0 )
    return(error);

  return(0);
}

int putMessageB(COMSHORT command, COMCHAR arg1, COMCHAR arg2, COMSTRING arg3)
{
  int error;

  if( (error = putCommand(command)) != 0 )
    return(error);
  if( (error = putChar(arg1)) != 0 )
    return(error);
  if( (error = putChar(arg2)) != 0 )
    return(error);
  if( (error = putString(arg3)) != 0 )
    return(error);
  if( (error = flushSendBuffer()) != 0 )
    return(error);

  return(0);
}

int putMessageC(COMSHORT command, COMCHAR arg1, COMCHAR arg2)
{
  int error;

  if( (error = putCommand(command)) != 0 )
    return(error);
  if( (error = putChar(arg1)) != 0 )
    return(error);
  if( (error = putChar(arg2)) != 0 )
    return(error);
  if( (error = flushSendBuffer()) != 0 )
    return(error);

  return(0);
}

int putMessageD(COMSHORT command, COMCHAR arg1, COMLIST arg2)
{
  int error;

  if( (error = putCommand(command)) != 0 )
    return(error);
  if( (error = putChar(arg1)) != 0 )
    return(error);
  if( (error = putListOfString(arg2)) != 0 )
    return(error);
  if( (error = flushSendBuffer()) != 0 )
    return(error);

  return(0);
}

int putMessageE(COMSHORT command, COMCHAR arg1, COMSHORT arg2, COMLIST arg3)
{
  int error;

  if( (error = putCommand(command)) != 0 )
    return(error);
  if( (error = putChar(arg1)) != 0 )
    return(error);
  if( (error = putShort(arg2)) != 0 )
    return(error);
  if( (error = putListOfString(arg3)) != 0 )
    return(error);
  if( (error = flushSendBuffer()) != 0 )
    return(error);

  return(0);
}

int putMessageF(COMSHORT command, COMCHAR arg1, COMLIST arg2, COMLIST arg3)
{
  int error;

  if( (error = putCommand(command)) != 0 )
    return(error);
  if( (error = putChar(arg1)) != 0 )
    return(error);
  if( (error = putListOfString(arg2)) != 0 )
    return(error);
  if( (error = putListOfString(arg3)) != 0 )
    return(error);
  if( (error = flushSendBuffer()) != 0 )
    return(error);

  return(0);
}

int putMessageG(COMSHORT command, COMCHAR arg1, COMLIST arg2, COMSTRING arg3,
		COMSHORT arg4, COMLIST arg5, COMLIST arg6, COMSTRING arg7)
{
  int error;

  if( (error = putCommand(command)) != 0 )
    return(error);

  if( (error = putChar(arg1)) != 0 )
    return(error);

  if( (error = putListOfString(arg2)) != 0 )
    return(error);

  if( (error = putString(arg3)) != 0 )
    return(error);

  if( (error = putShort(arg4)) != 0 )
    return(error);
  if( (error = putListOfString(arg5)) != 0 )
    return(error);
  if( (error = putListOfString(arg6)) != 0 )
    return(error);
  if( (error = putString(arg7)) != 0 )
    return(error);
  if( (error = flushSendBuffer()) != 0 )
    return(error);

  return(0);
}

/* obsolete
int putMessageH(COMSHORT command, COMCHAR arg1, COMLIST arg2, COMSTRING arg3,
		COMLIST arg4, COMLIST arg5, COMSTRING arg6)
{
  int error;

  if( (error = putCommand(command)) != 0 )
    return(error);
  if( (error = putChar(arg1)) != 0 )
    return(error);
  if( (error = putListOfString(arg2)) != 0 )
    return(error);
  if( (error = putString(arg3)) != 0 )
    return(error);
  if( (error = putListOfString(arg4)) != 0 )
    return(error);
  if( (error = putListOfString(arg5)) != 0 )
    return(error);
  if( (error = putString(arg6)) != 0 )
    return(error);
  if( (error = flushSendBuffer()) != 0 )
    return(error);

  return(0);
}
*/

int putMessageI(COMSHORT command, COMCHAR arg1, COMSTRING arg2)
{
  int error;

  if( (error = putCommand(command)) != 0 )
    return(error);
  if( (error = putChar(arg1)) != 0 )
    return(error);
  if( (error = putString(arg2)) != 0 )
    return(error);
  if( (error = flushSendBuffer()) != 0 )
    return(error);

  return(0);
}

/* putMessageJ(); */

int putMessageK(COMSHORT command, COMCHAR arg1, COMLIST arg2, COMLIST *arg3)
{
  int error;

  if( (error = putCommand(command)) != 0 )
    return(error);
  if( (error = putChar(arg1)) != 0 )
    return(error);
  if( (error = putListOfString(arg2)) != 0 )
    return(error);
  if( (error = putListOfListOfString(arg3)) != 0 )
    return(error);
  if( (error = flushSendBuffer()) != 0 )
    return(error);

  return(0);
}

int putMessageL(COMSHORT command, COMINT arg1)
{
  int error;

  if( (error = putCommand(command)) != 0 )
    return(error);
  if( (error = putInt(arg1)) != 0 )
    return(error);
  if( (error = flushSendBuffer()) != 0 )
    return(error);

  return(0);
}

int putMessageM(COMSHORT command, COMCHAR arg1)
{
  int error;

  if( (error = putCommand(command)) != 0 )
    return(error);
  if( (error = putChar(arg1)) != 0 )
    return(error);
  if( (error = flushSendBuffer()) != 0 )
    return(error);

  return(0);
}

int putMessageN(COMSHORT command, COMCHAR arg1, COMSHORT arg2)
{
  int error;

  if( (error = putCommand(command)) != 0 )
    return(error);
  if( (error = putChar(arg1)) != 0 )
    return(error);
  if( (error = putShort(arg2)) != 0 )
    return(error);
  if( (error = flushSendBuffer()) != 0 )
    return(error);

  return(0);
}
