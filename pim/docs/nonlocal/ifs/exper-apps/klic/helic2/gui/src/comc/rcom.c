/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*
 *      File Name  : rcom.c
 *      Function   : receive message processing
$*      History    :
$*      1995/ 1/12 : extensional functions
$*      1994/11/29 : ComErrReadSock, ComErrWriteSock
$*      1994/11/15 : spec change : free message struct
$*      1994/11/10 : receive justification list message args change
$*      1994/11/ 8 : bug : getCommand
$*      1994/11/ 8 : bug : change getStringList to getListOfString
$*      1994/11/ 8 : bye
$*      1994/11/ 7 : messages for server to receive for debug
$*      1994/11/ 7 : ng
$*      1994/11/ 7 : error handling
$*      1994/10/31 : crank in
 *
 */

/*
 *
 * メッセージを読みだし、メッセージ構造体に格納する。
 * メッセージ構造体のアドレスとメッセージタイプを
 * グローバル変数 ComMessageInfo メッセージ情報構造体にセットする。
 *
 * 処理が無事に終った場合は、戻り値として ComNoError (0)(エラーなし) を返す。
 * もし、処理中にエラーがあった場合は、グローバル変数 
 * ComErrorDest, ComErrorType, ComErrorMessage にエラー
 * 情報をセットし、戻り値として ComHasError (-1)(エラーあり) を返す。
 *
 */
#include <stdio.h>

#include "commands.h"
#include "messages.h"
#include "comerrs.h"

int getMessageA(COMSHORT command);
int getMessageB(COMSHORT command);
int getMessageC(COMSHORT command);
int getMessageD(COMSHORT command);
int getMessageE(COMSHORT command);
int getMessageF(COMSHORT command);
int getMessageG(COMSHORT command);
/* int getMessageH(COMSHORT command); */
int getMessageI(COMSHORT command);
/* int getMessageJ(COMSHORT command); */
int getMessageK(COMSHORT command);
int getMessageL(COMSHORT command);
int getMessageM(COMSHORT command);
int getMessageN(COMSHORT command);
int unknownMessage(COMSHORT command);


/* DDD : for debug */

int ComInterpret()
{
  int error;
  short command;

  if( (error = getCommand( &command )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }

  switch( command )
  {
    /* A : no arguments */
    case CmdOk :		/* ok */
    case CmdCompleteDebate	:	/* complete debate */
    case CmdStartDebate	:	/* DDD start debate */
    case CmdEndDebate	:	/* DDD end debate */
    case CmdBye		:	/* DDD bye */
    case CmdEnterBrowse	:	/* DDD enter browse */
    case CmdExitBrowse	:	/* DDD exit browse */
    case CmdStartSolve	:	/* DDD start solve */
      error = getMessageA( command );
      break;

    /* B : CCS */
    case CmdNg :		/* ng */
      error = getMessageB(command);
      break;

    /* C : CC */
    case CmdRecvLoadFlag :	/* receive load flag */
    case CmdSetSolver	 :	/* DDD set solver */
    case CmdSetExpMode	 :	/* DDD set explanation mode */
      error = getMessageC(command);
      break;

    /* D : CL */
    case CmdRecvSPL :	/* receive standpoint list */
    case CmdRecvVCL :	/* receive view candidate list */
    case CmdRecvCU  :	/* receive current unit */
    case CmdRecvCV  :	/* receive current view */
    case CmdRecvVC  :	/* receive view candidate */
    case CmdRecvRL  :	/* receive reason list */
    case CmdSetSPL  :	/* DDD set standpoint list */
    case CmdSetUL   :	/* DDD set unit list */
      error = getMessageD(command);
      break;

    /* E : CHL */
    case CmdRecvGCL :	/* receive goal candidate list */
      error = getMessageE(command);
      break;

    /* F : CLL */
    case CmdRecvAL :		/* receive argument list */
    case CmdRecvCounter :	/* receive counter list */
    case CmdRecvCL :		/* receive claimlist */
      error = getMessageF(command);
      break;

    /* G : CLSHLLS */
    case CmdRecvArg :	/* receive argument */
    case CmdShowArg :	/* show argument */
      error = getMessageG(command);
      break;

    /* H : CLHLLS */
    /* obsolete : show argument move to type G */
    /*
    case CmdShowArg :
      error = getMessageH(command);
      break;
     */

    /* I : CS */
    case CmdRecvExp	:	/* receive explanation */
    case CmdLoadType	:	/* DDD load type */
    case CmdLoadCommand	:	/* DDD load command */
    case CmdLoadRule	:	/* DDD load rule */
    case CmdLoadView	:	/* DDD load view */
    case CmdLoadQuery	:	/* DDD load query */
    case CmdSendVC	:	/* DDD send view candidate */
    case CmdCheckUnit	:	/* DDD check unit */
    case CmdJump	:	/* DDD jump */
      error = getMessageI(command);
      break;

    /* J : CHS */
    /* obsolete */

    /* K : CLL */
    case CmdRecvJL :	/* receive justification list */
      error = getMessageK(command);
      break;

    /* L : I */
    case CmdSetPID :	/* DDD set pid */
      error = getMessageL(command);
      break;

    /* M : C */
    case CmdSendSPL  :	/* DDD send standpoint list */
    case CmdSendVCL  :	/* DDD send view candidate list */
    case CmdSendCU   :	/* DDD send current unit */
    case CmdSendGCL  :	/* DDD send goal candidate list */
    case CmdSendCV   :	/* DDD send current view */
    case CmdSendRL   :	/* DDD send reason list */
    case CmdPose     :	/* DDD pose */
    case CmdCancel   :	/* DDD cancel */
    case CmdFinish   :	/* DDD finish */
    case CmdJustify  :	/* DDD justify */
    case CmdBackward :	/* DDD backward */
    case CmdForward  :	/* DDD forward */
    case CmdNext     :	/* DDD next */
    case CmdPrevious :	/* DDD previous */
    case CmdFocus    :	/* DDD focus */
    case CmdSendCL   :	/* DDD send claimlist */
    case CmdSendExp  :	/* DDD send explanation */
      error = getMessageM(command);
      break;

    /* N : CH */
    case CmdSetGoal	:	/* DDD set goal */
    case CmdNotice	:	/* DDD notice */
    case CmdSetJust	:	/* DDD set justification */
    case CmdSendArg	:	/* DDD send argument */
    case CmdSendCounter	:	/* DDD send counter list */
    case CmdSendRebut	:	/* DDD send rebuttal */
    case CmdJumpClaim	:	/* DDD jump claim */
    case CmdSetDepth	:	/* DDD set depth */
      error = getMessageN(command);
      break;

    default :
    /* unknown command */
      error = unknownMessage(command);
  }
  return( error );
}

/*
 *
 * process commands by type
 *
 */
int getMessageA(COMSHORT command)
{
  MessageA	*message;

  message = (MessageA *) malloc( sizeof( MessageA ) );
  if( message == (MessageA*)NULL )
  {
    /* malloc fail */
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, ComErrMallocFail);
    return ( ComHasError );
  }

  message->command = command;

  ComSetMessageInfo(MessageTypeA, message);
  ComSetErrorInfo(ComNoError, ComNoError);
  return( 0 );
}

int getMessageB(COMSHORT command)
{
  COMCHAR	dest;
  COMCHAR	etype;
  COMSTRING	emessage;
  int error;

  if( (error = getChar( &dest )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }

  if( (error = getChar( &etype )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }

  if( (error = getString( &emessage )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    return ( ComHasError );
  }

  /*
   * Set message type in order to free memory at the next Com function call.
   * We set NULL for ComMessageInfo.message because we handle ng message
   * as a special case for error handling and we set error info to
   * the global variables to notify GUI.
   * When Type B, we will free ComErrorMessage, not ComMessageInfo.message
   * because we don't allocate any memory for MessageB type struct as stated
   * above. See mesfree.c.
   */
  ComSetMessageInfo(MessageTypeB, NULL);

  /* Set server error info and notify it */
  ComErrorDest = dest;
  ComErrorType = etype;
  ComErrorMessage = emessage;
  return( ComHasError );
}

int getMessageC(COMSHORT command)
{
  MessageC	*message;
  COMCHAR	arg1, arg2;
  int error;

  message = (MessageC *) malloc( sizeof( MessageC ) );
  if( message == (MessageC *)NULL )
  {
    /* malloc fail. We have nothing to be freed. */
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, ComErrMallocFail);
    return ( ComHasError );
  }

  if( (error = getChar( &arg1 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }

  if( (error = getChar(&arg2)) != 0)
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }

  message->command = command;
  message->arg1 = arg1;
  message->arg2 = arg2;

  ComSetMessageInfo(MessageTypeC, message);
  ComSetErrorInfo(ComNoError, ComNoError);
  return(ComNoError);
}

int getMessageD(COMSHORT command)
{
  MessageD	*message;
  COMCHAR	arg1;
  COMLIST	arg2;
  int error;

  message = (MessageD *) malloc( sizeof( MessageD ) );
  if( message == (MessageD *)NULL )
  {
    /* malloc fail */
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, ComErrMallocFail);
    return(ComHasError);
  }

  if( (error = getChar( &arg1 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }
  if( (error = getListOfString( &arg2 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }

  message->command = command;
  message->arg1 = arg1;
  message->arg2 = arg2;

  ComSetMessageInfo(MessageTypeD, message);
  ComSetErrorInfo(ComNoError, ComNoError);
  return(ComNoError);
}

int getMessageE(COMSHORT command)
{
  MessageE	*message;
  COMCHAR	arg1;
  COMSHORT	arg2;
  COMLIST	arg3;
  int error;

  message = (MessageE *) malloc( sizeof( MessageE ) );
  if( message == (MessageE *)NULL )
  {
    /* malloc fail */
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, ComErrMallocFail);
    return(ComHasError);
  }

  if( (error = getChar( &arg1 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }
  if( (error = getShort( &arg2 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }
  if( (error = getListOfString( &arg3 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }

  message->command = command;
  message->arg1 = arg1;
  message->arg2 = arg2;
  message->arg3 = arg3;

  ComSetMessageInfo(MessageTypeE, message);
  ComSetErrorInfo(ComNoError, ComNoError);
  return(ComNoError);
}

int getMessageF(COMSHORT command)
{
  MessageF	*message;
  COMCHAR	arg1;
  COMLIST	arg2;
  COMLIST	arg3;
  int error;

  message = (MessageF *) malloc( sizeof( MessageF ) );
  if( message == (MessageF *)NULL )
  {
    /* malloc fail */
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, ComErrMallocFail);
    return(ComHasError);
  }

  if( (error = getChar( &arg1 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }
  if( (error = getListOfString( &arg2 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }
  if( (error = getListOfString( &arg3 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    freeListOfString(arg2);
    free(message);
    return(ComHasError);
  }

  message->command = command;
  message->arg1 = arg1;
  message->arg2 = arg2;
  message->arg3 = arg3;

  ComSetMessageInfo(MessageTypeF, message);
  ComSetErrorInfo(ComNoError, ComNoError);
  return(ComNoError);
}

int getMessageG(COMSHORT command)
{
  MessageG	*message;
  COMCHAR	arg1;
  COMLIST	arg2;
  COMSTRING	arg3;
  COMSHORT	arg4;
  COMLIST	arg5;
  COMLIST	arg6;
  COMSTRING	arg7;
  int error;

  message = (MessageG *) malloc( sizeof( MessageG ) );
  if( message == (MessageG *)NULL )
  {
    /* malloc fail */
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, ComErrMallocFail);
    return(ComHasError);
  }

  if( (error = getChar( &arg1 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }
  if( (error = getListOfString( &arg2 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }
  if( (error = getString( &arg3 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    freeListOfString(arg2);
    free(message);
    return(ComHasError);
  }
  if( (error = getShort( &arg4 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    freeListOfString(arg2);
    freeString(arg3);
    free(message);
    return(ComHasError);
  }
  if( (error = getListOfString( &arg5 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    freeListOfString(arg2);
    freeString(arg3);
    free(message);
    return(ComHasError);
  }
  if( (error = getListOfString( &arg6 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    freeListOfString(arg2);
    freeString(arg3);
    freeListOfString(arg5);
    free(message);
    return(ComHasError);
  }
  if( (error = getString( &arg7 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    freeListOfString(arg2);
    freeString(arg3);
    freeListOfString(arg5);
    freeListOfString(arg6);
    free(message);
    return(ComHasError);
  }

  message->command = command;
  message->arg1 = arg1;
  message->arg2 = arg2;
  message->arg3 = arg3;
  message->arg4 = arg4;
  message->arg5 = arg5;
  message->arg6 = arg6;
  message->arg7 = arg7;

  ComSetMessageInfo(MessageTypeG, message);
  ComSetErrorInfo(ComNoError, ComNoError);
  return(ComNoError);
}

/* obsolete */
/* int getMessageH(COMSHORT command); */

int getMessageI(COMSHORT command)
{
  MessageI	*message;
  COMCHAR	arg1;
  COMSTRING	arg2;
  int error;

  message = (MessageI *) malloc( sizeof( MessageI ) );
  if( message == (MessageI *)NULL )
  {
    /* malloc fail */
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, ComErrMallocFail);
    return(ComHasError);
  }

  if( (error = getChar( &arg1 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }
  if( (error = getString( &arg2 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }

  message->command = command;
  message->arg1 = arg1;
  message->arg2 = arg2;

  ComSetMessageInfo(MessageTypeI, message);
  ComSetErrorInfo(ComNoError, ComNoError);
  return(ComNoError);
}

/* obsolete */
/* int getMessageJ(COMSHORT command); */

int getMessageK(COMSHORT command)
{
  MessageK	*message;
  COMCHAR	 arg1;
  COMLIST	 arg2;
  COMLIST	*arg3;
  int error;

  message = (MessageK *) malloc( sizeof( MessageK ) );
  if( message == (MessageK *)NULL )
  {
    /* malloc fail */
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, ComErrMallocFail);
    return(ComHasError);
  }

  if( (error = getChar( &arg1 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }

  if( (error = getListOfString(&arg2)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }
  if( (error = getListOfListOfString(&arg3)) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }

  message->command = command;
  message->arg1 = arg1;
  message->arg2 = arg2;
  message->arg3 = arg3;

  ComSetMessageInfo(MessageTypeK, message);
  ComSetErrorInfo(ComNoError, ComNoError);
  return(ComNoError);
}

int unknownMessage(COMSHORT command)
{

  ComSetMessageInfo(NoMessage, NULL);
  ComSetErrorInfo(NEITHER, ComErrUnknown);
  return(ComHasError);
}

/*
 * for debug
 */
int getMessageL(COMSHORT command)
{
  MessageL	*message;
  COMINT	arg1;
  int error;

  message = (MessageL *) malloc( sizeof( MessageL ) );
  if( message == (MessageL *)NULL )
  {
    /* malloc fail */
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, ComErrMallocFail);
    return(ComHasError);
  }

  if( (error = getInt( &arg1 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }

  message->command = command;
  message->arg1 = arg1;

  ComSetMessageInfo(MessageTypeL, message);
  ComSetErrorInfo(ComNoError, ComNoError);
  return(ComNoError);
}

int getMessageM(COMSHORT command)
{
  MessageM	*message;
  COMCHAR	arg1;
  int error;

  message = (MessageM *) malloc( sizeof( MessageM ) );
  if( message == (MessageM *)NULL )
  {
    /* malloc fail */
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, ComErrMallocFail);
    return(ComHasError);
  }

  if( (error = getChar( &arg1 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }

  message->command = command;
  message->arg1 = arg1;

  ComSetMessageInfo(MessageTypeM, message);
  ComSetErrorInfo(ComNoError, ComNoError);
  return(ComNoError);
}

int getMessageN(COMSHORT command)
{
  MessageN	*message;
  COMCHAR	arg1;
  COMSHORT	arg2;
  int error;

  message = (MessageN *) malloc( sizeof( MessageN ) );
  if( message == (MessageN *)NULL )
  {
    /* malloc fail */
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, ComErrMallocFail);
    return(ComHasError);
  }

  if( (error = getChar( &arg1 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }

  if( (error = getShort( &arg2 )) != 0 )
  {
    ComSetMessageInfo(NoMessage, NULL);
    ComSetErrorInfo(NEITHER, error);
    free(message);
    return(ComHasError);
  }

  message->command = command;
  message->arg1 = arg1;
  message->arg2 = arg2;

  ComSetMessageInfo(MessageTypeN, message);
  ComSetErrorInfo(ComNoError, ComNoError);
  return(ComNoError);
}
