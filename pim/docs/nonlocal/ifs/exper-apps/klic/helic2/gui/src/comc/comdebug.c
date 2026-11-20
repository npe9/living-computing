/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*
 *      File Name  : comdebug.c
 *      Function   : debug
$*      History    :
$*      1995/ 1/13 : bug fix : print error for complete debate
$*      1995/ 1/12 : add commands for extensional functions
$*      1994/11/30 : add DebugPrintWriteBufPos
$*      1994/11/29 : add ComCSocket print
$*      1994/11/25 : stop char type debug print
$*      1994/11/15 : add debug print for low level buffer access
$*      1994/11/14 : debug print
$*      1994/11/ 7 : crank in
 *
 */

#include <stdio.h>

/*
 * Debug Flag : short
 *   debug level  : upper byte
 *       0 : no debug
 *       1 : print only command names
 *       2 : print only arguments of command
 *       3 : print command names and arguments
 *       4 : print low level buffer access status
 *   print switch : lower byte
 *       0 : no print
 *       1 : print message sending to server
 *       2 : print message received from server
 *       3 : print message both sending to and received from server
 *
 *  default setting : 0x0103
 *       print only command names of sending and received messages
 *
 */

int ComDebugFlag = 0x0103;


#ifdef NETDEBUG

extern int ComCSocket;

#include "commands.h"
#include "comtypes.h"
#include "comdebug.h"

char *TagTable[] = {
  "no assign",
  "char",	/* TAGCHAR */
  "uchar",	/* TAGUCHAR */
  "short",	/* TAGSHORT */
  "ushort",	/* TAGUSHORT */
  "int",	/* TAGINT */
  "uint",	/* TAGUINT */
  "str",	/* TAGSTR */
  "list"	/* TAGLIST */
};


/*
 */
int printCommandName(COMSHORT command);

/*
 */
int DebugPrintTag(unsigned char tag, int psw)
{
  if( psw & ComDebugFlag )
    if( ComDebugFlag & (DPARGS << 8) )
      printf("TAG : dec:%d, hex:%x (%s)\n",tag, tag, TagTable[tag]);
  return(0);
}

int DebugPrintCommand(COMSHORT command, int psw)
{
  if( psw & ComDebugFlag )
    if( ComDebugFlag & (DPNAME << 8) )
    {
      printf("COMMAND : dec:%d, hex:%x, (", command, command);
      printCommandName(command);
      printf(")\n");
    }
  return(0);
}

int printCommandName(COMSHORT command)
{
  switch(command)
  {
  case CmdSetPID:
    printf("set pid");
    break;
  case CmdOk:
    printf("ok");
    break;
  case CmdNg:
    printf("ng");
    break;
  case CmdLoadType:
    printf("load type");
    break;
  case CmdLoadCommand:
    printf("load command");
    break;
  case CmdLoadRule:
    printf("load rule");
    break;
  case CmdLoadView:
    printf("load view");
    break;
  case CmdLoadQuery:
    printf("load query");
    break;
  case CmdRecvLoadFlag:
    printf("receive load flag");
    break;
  case CmdSetSolver:
    printf("set solver");
    break;
  case CmdSendSPL:
    printf("send standpoint list");
    break;
  case CmdRecvSPL:
    printf("receive standpoint list");
    break;
  case CmdSendVCL:
    printf("send view candidate list");
    break;
  case CmdRecvVCL:
    printf("receive view candidate list");
    break;
  case CmdSendCU:
    printf("send current unit");
    break;
  case CmdRecvCU:
    printf("receive current unit");
    break;
  case CmdSendGCL:
    printf("send goal candidate list");
    break;
  case CmdRecvGCL:
    printf("receive goal candidate list");
    break;
  case CmdSendCV:
    printf("send current view");
    break;
  case CmdRecvCV:
    printf("receive current view");
    break;
  case CmdSendVC:
    printf("send view candidate");
    break;
  case CmdRecvVC:
    printf("receive view candidate");
    break;
  case CmdSetSPL:
    printf("set standpoint list");
    break;
  case CmdCheckUnit:
    printf("check unit");
    break;
  case CmdSetUL:
    printf("set unit list");
    break;
  case CmdSetGoal:
    printf("set goal");
    break;
  case CmdStartDebate:
    printf("start debate");
    break;
  case CmdEndDebate:
    printf("end debate");
    break;
  case CmdPose:
    printf("pose");
    break;
  case CmdSendRL:
    printf("send reason list");
    break;
  case CmdRecvRL:
    printf("receive reason list");
    break;
  case CmdNotice:
    printf("notice");
    break;
  case CmdCancel:
    printf("cancel");
    break;
  case CmdFinish:
    printf("finish");
    break;
  case CmdJustify:
    printf("justify");
    break;
  case CmdRecvJL:
    printf("receive justification list");
    break;
  case CmdSetJust:
    printf("set justification");
    break;
  case CmdRecvAL:
    printf("receive argument list");
    break;
  case CmdSendArg:
    printf("send argument");
    break;
  case CmdRecvArg:
    printf("receive argument");
    break;
  case CmdShowArg:
    printf("show argument");
    break;
  case CmdSendCounter:
    printf("send counter list");
    break;
  case CmdRecvCounter:
    printf("receive counter list");
    break;
  case CmdSendRebut:
    printf("send rebuttal");
    break;
  case CmdBackward:
    printf("backward");
    break;
  case CmdForward:
    printf("forward");
    break;
  case CmdNext:
    printf("next");
    break;
  case CmdPrevious:
    printf("previous");
    break;
  case CmdFocus:
    printf("focus");
    break;
  case CmdJump:
    printf("jump");
    break;
  case CmdSendCL:
    printf("send claimlist");
    break;
  case CmdRecvCL:
    printf("receive claimlist");
    break;
  case CmdJumpClaim:
    printf("jump claim");
    break;
  case CmdSendExp:
    printf("send explanation");
    break;
  case CmdRecvExp:
    printf("receive explanation");
    break;

/* add extensional functions after demo version */
  case CmdEnterBrowse:
    printf("enter browse");
    break;
  case CmdExitBrowse:
    printf("exit browse");
    break;
  case CmdCompleteDebate:
    printf("complete debate");
    break;
  case CmdStartSolve:
    printf("start solve");
    break;
  case CmdSetExpMode:
    printf("set explanation mode");
    break;
  case CmdSetDepth:
    printf("set depth");
    break;

/* obsolete */
  case CmdSendErrInfo:
    printf("obsolete command : send error info");
    break;
  case CmdRecvErrInfo:
    printf("obsolete command : receive error info");
    break;

  case CmdBye:
    printf("bye");
    break;

  default:
    printf("unknown command");
  }

  return(0);
}

int DebugPrintChar(COMCHAR c, int psw)
{
  if( psw & ComDebugFlag )
    if( ComDebugFlag & (DPARGS << 8) )
      printf("CHAR : dec:%d, hex:%x\n", c, c);
  return(0);
}

int DebugPrintShort(COMSHORT i, int psw)
{
  if( psw & ComDebugFlag )
    if( ComDebugFlag & (DPARGS << 8) )
      printf("SHORT : dec:%d, hex:%x\n", i, i);
  return(0);
}

int DebugPrintInt(COMINT i, int psw)
{
  if( psw & ComDebugFlag )
    if( ComDebugFlag & (DPARGS << 8) )
      printf("INT : dec:%d, hex:%x\n", i, i);
  return(0);
}

int DebugPrintSize(int size, int psw)
{
  if( psw & ComDebugFlag )
    if( ComDebugFlag & (DPARGS << 8) )
      printf("size : dec:%d, hex:%x\n", size, size);
  return(0);
}

int DebugPrintString(char *s, int psw)
{
  if( psw & ComDebugFlag )
    if( ComDebugFlag & (DPARGS << 8) )
      printf("string : \"%s\"\n", s);
  return(0);
}

int DebugPrintReadBuf(int size, int psw)
{
  if( psw & ComDebugFlag )
    if( ComDebugFlag & (DPBUF << 8) )
      printf("Read %d bytes from socket %d\n", size, ComCSocket);
  return(0);
}

int DebugPrintWriteBuf(int size, int psw)
{
  if( psw & ComDebugFlag )
    if( ComDebugFlag & (DPBUF << 8) )
      printf("Write %d bytes to socket %d\n", size, ComCSocket);
  return(0);
}

int DebugPrintWriteBufPos(int pos, int psw)
{
  if( psw & ComDebugFlag )
    if( ComDebugFlag & (DPBUF << 8) )
      printf("spos : %d\n", pos);
  return(0);
}
#endif
