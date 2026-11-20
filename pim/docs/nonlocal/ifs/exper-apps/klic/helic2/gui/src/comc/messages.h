/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*
 *      File Name  : messages.h
 *      Function   : message info and message structure definition
$*      History    :
$*      1995/ 1/23 : move ComError* global variables from comerrs.h
$*      1995/ 1/12 : obsolete MessageTypeH : extensional function
$*      1994/11/15 : spec change : add NoMessage for memory free
$*      1994/11/ 8 : bug : arg3 of MessageH is string
$*      1994/11/ 7 : messages for server to receive for debug
$*      1994/11/ 4 : change messagetypeB for ng and delete typeJ
$*      1994/10/31 : crank in
 *
 */

#ifdef MAIN
#define EXTERN
#else
#define EXTERN extern
#endif MAIN

#include "comtypes.h"



/*
 *
 * global variables for passing receive information from COM/C to GUI
 *
 */

/*
 * message info structure
 */
typedef struct MessageInfo {
  char *message;	/* pointer to message structure
			 * casted to each message type */
  short type;		/* message type */
} MessageInfo;


/*
 * message info (defined in GUI main)
 */
EXTERN MessageInfo ComMessageInfo;

#define ComSetMessageInfo(t,m)\
		{ComMessageInfo.type = t;\
		 ComMessageInfo.message = (char*)m;}

/*
 * Globals for GUI-COM/C error info interface
 */
EXTERN short  ComErrorDest;
EXTERN short  ComErrorType;
EXTERN char  *ComErrorMessage;

/*
 *
 * message structures
 *   messages common to server and client
 * [N.B.]
 *   We implement an argument of list data structure as char **.
 *   We put NULL as the sentinel in the last element
 *   as is the case of string implementation by char * and '\0'.
 *   If we have no element of a list (id. nil), we have one element of
 *   char*  which contains (char *) NULL.
 *
 */

/*
 * No memory for message allocated
 */
#define	NoMessage	0

/*
 * Type A
 */
#define MessageTypeA	1
typedef struct MessageA {
  COMSHORT command;
} MessageA;

/*
 * Type B
 */
#define MessageTypeB	2
typedef struct MessageB {
  COMSHORT command;
  COMCHAR   arg1;    /* agent */
  COMCHAR   arg2;    /* error type */
  COMSTRING arg3;    /* error message */
} MessageB;

/*
 * Type C
 */
#define MessageTypeC	3
typedef struct MessageC {
  COMSHORT command;
  COMCHAR arg1;    /* agent */
  COMCHAR arg2;    /* loadflag */
} MessageC;

/*
 * Type D
 */
#define MessageTypeD	4
typedef struct MessageD {
  COMSHORT command;
  COMCHAR arg1;    /* agent */
  COMLIST arg2;    /* unitlist | standpointlist
                      | viewcandidatelist | reasonlist */
} MessageD;

/*
 * Type E
 */
#define MessageTypeE	5
typedef struct MessageE {
  COMSHORT command;
  COMCHAR  arg1;    /* agent */
  COMSHORT arg2;    /* goalno */
  COMLIST  arg3;    /* goallist */
} MessageE;

/*
 * Type F
 */
#define MessageTypeF	6
typedef struct MessageF {
  COMSHORT command;
  COMCHAR  arg1;    /* agent */
  COMLIST  arg2;    /* argumentlist | counterlist | claimlist */
  COMLIST  arg3;    /* addinfo */
} MessageF;

/*
 * Type G
 */
#define MessageTypeG	7
typedef struct MessageG {
  COMSHORT  command;
  COMCHAR   arg1;    /* agent */
  COMLIST   arg2;    /* aidpair */
  COMSTRING arg3;    /* issue */
  COMSHORT  arg4;    /* buttonstate */
  COMLIST   arg5;    /* argument */
  COMLIST   arg6;    /* status */
  COMSTRING arg7;    /* history */
} MessageG;

/*
 * obsolete
 * Type H
 *   show argument : change to Type G
 */
/*
#define MessageTypeH	8
typedef struct MessageH {
  COMSHORT  command;
  COMCHAR   arg1;
  COMLIST   arg2;
  COMSTRING arg3;
  COMLIST   arg4;
  COMLIST   arg5;
  COMSTRING arg6;
} MessageH;
*/

/*
 * Type I
 */
#define MessageTypeI	9
typedef struct MessageI {
  COMSHORT  command;
  COMCHAR   arg1;    /* agent */
  COMSTRING arg2;    /* explanation */
} MessageI;

/*
 * Type J
 * obsolete
 * receive error info message has been integrated to ng.
 */

/*
 * Type K
 */
#define MessageTypeK	11
typedef struct MessageK {
  COMSHORT  command;
  COMCHAR   arg1;    /* agent */
  COMLIST   arg2;    /* standpoint list */
  COMLIST  *arg3;    /* pointer to view list */
} MessageK;


/*
 * For debug
 *   messages for server to receive
 */
/*
 * Type L
 *   set pid
 */
#define MessageTypeL	12
typedef struct MessageL {
  COMSHORT  command;
  COMINT    arg1;    /* pid */
} MessageL;

/*
 * Type M
 *   send standpoint list, send view candidate list,
 *   send current unit, send goal candidate list,
 *   send current view, pose, send reason list,
 *   cancel, finish, justify, backward, forward,
 *   next, previous, focus, send claimlist, send explanation
 */
#define MessageTypeM	13
typedef struct MessageM {
  COMSHORT  command;
  COMCHAR   arg1;    /* agent */
} MessageM;

/*
 * Type N
 *   set goal, notice, set justification, send argument
 *   send counter list, send rebuttal, jump claim,
 *   set depth
 */
#define MessageTypeN	14
typedef struct MessageN {
  COMSHORT  command;
  COMCHAR   arg1;    /* agent */
  COMSHORT  arg2;
} MessageN;
