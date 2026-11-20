/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*
 *      File Name  : scom.c
 *      Function   : gui-com/c function interface
 *                   send one message and receive one message
$*      History    :
$*      1995/ 1/12 : function extensions
$*      1994/11/30 : ComErrReadSock, ComErrWriteSock
$*      1994/11/15 : spec change : free message struct memory before sending
$*      1994/11/14 : move ComOk check in ComSetPID to ComInit
$*      1994/11/10 : ComBye for debug returns ComInterpreted value
$*      1994/11/10 : bug : setPID in ComInit
$*      1994/11/10 : change to use putMessageX in smes.c
$*      1994/11/ 9 : bug : add flushSendBuffer in setPID
$*      1994/11/ 8 : bug : add flushSendBuffer
$*      1994/11/ 8 : add bye in ComClose
$*      1994/11/ 7 : server message for debug
$*      1994/11/ 7 : ok message check in ComInit
$*      1994/11/ 7 : error handling
$*      1994/10/31 : crank in
 *
 */

/*
 *
 * The members sin_family, sin_port and sin_addr of the arguement server
 *   are expected to have been set the following value before calling
 *   this function.
 *      server.sin_family : AF_INET
 *      server.sin_port   : server port (9000)
 *      server.sin_addr   : server host address
 *
 */

#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>

#include "commands.h"
#include "comerrs.h"
#include "messages.h"
#include "comdebug.h"

/*
 * ソッケット獲得後、最初に pid をサーバに送り、
 * サーバから ok メッセージを受けとることで、
 * コネクション確立の検査とする。
 */
int ComInit(struct sockaddr_in *server, int debug)
{
  MessageA *msgA;
  int pid, error;

  /* save debug flag in global variable */
  ComDebugFlag = debug;

  /* Initialize MessageInfo as no message set */
  ComSetMessageInfo(NoMessage, NULL);

  if( (error = ComSetupClient( server )) != 0)
  {
    ComSetErrorInfo(NEITHER, error);
    return(ComHasError);
  }

  /* Initial message negotiation */
  pid = getpid();
  if( ComSetPID(pid) != 0 )
  {
    return(ComHasError);
  }

  if( ComMessageInfo.type != MessageTypeA )
  {
    ComSetErrorInfo(NEITHER, ComErrConnectFail);
    return(ComHasError);
  }

  msgA = (MessageA *) ComMessageInfo.message;
  if( msgA->command != CmdOk )
  {
    ComSetErrorInfo(NEITHER, ComErrConnectFail);
    return(ComHasError);
  }

  return(ComNoError);
}

int ComSetPID(int pid)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageL(CmdSetPID, pid)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }

  return( ComInterpret() );
}

int ComClose()
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageA(CmdBye)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  ComCloseClient();
  return(ComNoError);
}

int ComLoadType(COMCHAR agent, COMSTRING pathname)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageI(CmdLoadType, agent, pathname)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComLoadCommand(COMCHAR agent, COMSTRING pathname)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageI(CmdLoadCommand, agent, pathname)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComLoadRule(COMCHAR agent, COMSTRING pathname)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageI(CmdLoadRule, agent, pathname)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComLoadView(COMCHAR agent, COMSTRING pathname)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageI(CmdLoadView, agent, pathname)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComLoadQuery(COMCHAR agent, COMSTRING pathname)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageI(CmdLoadQuery, agent, pathname)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSetSolver(COMCHAR agent, COMCHAR role)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageC(CmdSetSolver, agent, role)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComOk(void)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageA(CmdOk)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSendStandpointList(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdSendSPL, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSendViewCandidateList(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdSendVCL, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSendCurrentUnit(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdSendCU, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSendGoalCandidateList(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdSendGCL, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSendCurrentView(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdSendCV, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSendViewCandidate(COMCHAR agent, COMSTRING view)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageI(CmdSendVC, agent, view)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSetStandpointList(COMCHAR agent, COMLIST standpointlist)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageD(CmdSetSPL, agent, standpointlist)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComCheckUnit(COMCHAR agent, COMSTRING unitname)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageI(CmdCheckUnit, agent, unitname)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSetUnitList(COMCHAR agent, COMLIST unitlist)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageD(CmdSetUL, agent, unitlist)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSetGoal(COMCHAR agent, COMSHORT goal)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageN(CmdSetGoal, agent, goal)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComStartDebate(void)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageA(CmdStartDebate)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComEndDebate(void)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageA(CmdEndDebate)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComPose(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdPose, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSendReasonList(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdSendRL, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComNotice(COMCHAR agent, COMSHORT standpoint)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageN(CmdNotice, agent, standpoint)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComCancel(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdCancel, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComFinish(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdFinish, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComJustify(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdJustify, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSetJustification(COMCHAR agent, COMSHORT justno)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageN(CmdSetJust, agent, justno)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSendArgument(COMCHAR agent, COMSHORT argno)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageN(CmdSendArg, agent, argno)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSendCounterList(COMCHAR agent, COMSHORT issueno)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageN(CmdSendCounter, agent, issueno)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSendRebuttal(COMCHAR agent, COMSHORT rebutno)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageN(CmdSendRebut, agent, rebutno)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComBackward(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdBackward, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComForward(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdForward, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComNext(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdNext, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComPrevious(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdPrevious, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComFocus(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdFocus, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComJump(COMCHAR agent, COMSTRING argid)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageI(CmdJump, agent, argid)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSendClaimlist(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdSendCL, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComJumpClaim(COMCHAR agent, COMSHORT claimno)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageN(CmdJumpClaim, agent, claimno)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSendExplanation(COMCHAR agent)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageM(CmdSendExp, agent)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

/*
 * For debug
 *   messages to be sent from server
 */
int ComNg(COMCHAR agent, COMCHAR errortype, COMSTRING errormessage)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageB(CmdNg, agent, errortype, errormessage)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComReceiveLoadFlag(COMCHAR agent, COMCHAR loadflag)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageC(CmdRecvLoadFlag, agent, loadflag)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComReceiveStandpointList(COMCHAR agent, COMLIST splist)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageD(CmdRecvSPL, agent, splist)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComReceiveViewCandidateList(COMCHAR agent, COMLIST vclist)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageD(CmdRecvVCL, agent, vclist)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}


int ComReceiveCurrentUnit(COMCHAR agent, COMLIST culist)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageD(CmdRecvCU, agent, culist)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComReceiveGoalCandidateList(COMCHAR agent, COMSHORT goal, COMLIST gclist)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageE(CmdRecvGCL, agent, goal, gclist)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComReceiveCurrentView(COMCHAR agent, COMLIST splist)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageD(CmdRecvCV, agent, splist)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComReceiveViewCandidate(COMCHAR agent, COMLIST splist)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageD(CmdRecvVC, agent, splist)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComReceiveReasonList(COMCHAR agent, COMLIST reasonlist)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageD(CmdRecvRL, agent, reasonlist)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComReceiveJustificationList(COMCHAR agent, COMLIST sp, COMLIST *view)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageK(CmdRecvJL, agent, sp, view)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComReceiveArgumentList(COMCHAR agent, COMLIST arglist, COMLIST addinfo)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageF(CmdRecvAL, agent, arglist, addinfo)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComReceiveArgument(COMCHAR agent, COMLIST aidinfo, COMSTRING issue,
		       COMSHORT button, COMLIST arg,
		       COMLIST status, COMSTRING history)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageG(CmdRecvArg, agent, aidinfo,
			   issue, button, arg, status, history)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComShowArgument(COMCHAR agent, COMLIST aidinfo, COMSTRING issue,
		    COMSHORT button, COMLIST arg,
		    COMLIST status, COMSTRING history)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageG(CmdShowArg, agent, aidinfo,
			   issue, button, arg, status, history)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComReceiveCounterList(COMCHAR agent, COMLIST counter, COMLIST add)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageF(CmdRecvCounter, agent, counter, add)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComReceiveClaimList(COMCHAR agent, COMLIST claimlist, COMLIST add)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageF(CmdRecvCL, agent, claimlist, add)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComReceiveExplanation(COMCHAR agent, COMSTRING exp)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageI(CmdRecvExp, agent, exp)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComBye()
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageA(CmdBye)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

/*
 * extensional functions after demo version
 */
int ComEnterBrowse(void)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageA(CmdEnterBrowse)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComExitBrowse(void)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageA(CmdExitBrowse)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComCompleteDebate(void)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageA(CmdCompleteDebate)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComStartSolve(void)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageA(CmdStartSolve)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSetExplanationMode(COMCHAR agent, COMCHAR mode)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageC(CmdSetExpMode, agent, mode)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}

int ComSetDepth(COMCHAR agent, COMSHORT depth)
{
  int error;

  /* Free current set message if any before send message. */
  freeMessage();

  if( (error = putMessageN(CmdSetDepth, agent, depth)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }
  return( ComInterpret() );
}
