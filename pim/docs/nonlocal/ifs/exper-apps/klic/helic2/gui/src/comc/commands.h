/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*
 *      File Name  : commands.h
 *      Function   : command identifier definition
$*      History    :
$*      1995/ 1/12 : function extensions
$*      1994/11/ 8 : bye
$*      1994/11/ 7 : obsolete send/receive error info
$*      1994/10/31 : crank in
 *
 */

/*
 *
 * Command id definition
 *
 */

#define	CmdSetPID	10	/* set pid */
#define CmdOk		20	/* ok */
#define CmdNg		30	/* ng */

#define CmdLoadType	40	/* load type */
#define CmdLoadCommand	41	/* load command */
#define CmdLoadRule	42	/* load rule */
#define CmdLoadView	43	/* load view */
#define CmdLoadQuery	44	/* load query */

#define CmdRecvLoadFlag	45	/* receive load flag */

#define CmdSetSolver	50	/* set solver */

#define CmdSendSPL	60	/* send standpoint list */
#define CmdRecvSPL	61	/* receive standpoint list */

#define CmdSendVCL	70	/* send view candidate list */
#define CmdRecvVCL	71	/* receive view candidate list */

#define CmdSendCU	80	/* send current unit */
#define CmdRecvCU	81	/* receive current unit */

#define CmdSendGCL	90	/* send goal candidate list */
#define CmdRecvGCL	91	/* receive goal candidate list */

#define CmdSendCV	100	/* send current view */
#define CmdRecvCV	101	/* receive current view */

#define CmdSendVC	110	/* send view candiate */
#define CmdRecvVC	111	/* receive view candidate */

#define CmdSetSPL	120	/* set standpoint list */

#define CmdCheckUnit	130	/* check unit */

#define CmdSetUL	140	/* set unit list */

#define CmdSetGoal	150	/* set goal */

#define CmdStartDebate	160	/* start debate */
#define CmdEndDebate	161	/* end debate */

#define CmdPose		170	/* pose */

#define CmdSendRL	180	/* send reason list */
#define CmdRecvRL	181	/* receive reason list */
#define CmdNotice	182	/* notice */

#define CmdCancel	190	/* cancel */

#define CmdFinish	200	/* finish */

#define CmdJustify	210	/* justify */
#define CmdRecvJL	211	/* receive justification list */
#define CmdSetJust	212	/* set justification */

#define CmdRecvAL	220	/* receive argument list */

#define CmdSendArg	230	/* send argument */
#define CmdRecvArg	231	/* receive argument */
#define CmdShowArg	232	/* show argument */

#define CmdSendCounter	240	/* send counter list */
#define CmdRecvCounter	241	/* receive counter list */

#define CmdSendRebut	250	/* send rebuttal */

#define CmdBackward	260	/* backward */
#define CmdForward	270	/* forward */
#define CmdNext		280	/* next */
#define CmdPrevious	290	/* previous */
#define CmdFocus	300	/* focus */
#define CmdJump		310	/* jump */

#define CmdSendCL	320	/* send claimlist */
#define CmdRecvCL	321	/* receive claimlist */
#define CmdJumpClaim	322	/* jump claim */

#define CmdSendExp	330	/* send explanation */
#define CmdRecvExp	331	/* receive explanation */

/* obsolete */
#define CmdSendErrInfo	340	/* send error info */
#define CmdRecvErrInfo	341	/* receive error info */

#define CmdBye		350	/* bye */

/* additional functions after demo version */
#define	CmdEnterBrowse	360	/* enter browse */
#define	CmdExitBrowse	361	/* exit browse */

#define	CmdCompleteDebate	370	/* complete debate */

#define	CmdStartSolve	380	/* start solve */

#define	CmdSetExpMode	390	/* set explanation mode */

#define	CmdSetDepth	400	/* set depth */
