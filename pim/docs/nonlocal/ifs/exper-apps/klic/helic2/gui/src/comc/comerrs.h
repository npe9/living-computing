/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*
 *      File Name  : comerrs.h
 *      Function   : error code definition
$*      History    :
$*      1995/ 1/23 : move ComError* global variables to messages.h
$*      1994/11/30 : ComErrEOFDetect
$*      1994/11/29 : ComErrReadSock, ComErrWriteSock
$*      1994/11/15 : add ComNoError
$*      1994/11/ 7 : unknown message
$*      1994/10/31 : crank in
 *
 */


#define ComNoError	0
#define ComHasError	-1

/*
 * メッセージのデータ型が一致しない
 */ 
#define	ComErrMisType	1

/*
 * メモリの allocation に失敗
 */
#define	ComErrMallocFail	2

/*
 * socket の allocation に失敗
 */
#define ComErrSocAllocFail	3

/*
 * サーバへの接続に失敗
 *   - connect に失敗
 *   - 接続確認のための初期メッセージの送受信に失敗
 *
 */
#define ComErrConnectFail	4

/* Just for debug */
#define ComErrBindFail		5
#define ComErrBadHostname	6

/*
 * unknown message
 */
#define ComErrUnknown		7

/* 
 * socket read/write
 */
#define ComErrReadSock		8
#define ComErrWriteSock		9

/* EOF detected while reading socket */
#define ComErrEOFDetect		10

/*
 * COM/C error table structure type
 */
typedef struct ComErrorInfo {
  short type;
  char  message[60];
} ComErrorInfo;

extern ComErrorInfo ComErrorTable[];

#define ComSetErrorInfo(dest,eid)\
		{ComErrorDest = dest;\
		 ComErrorType = ComErrorTable[eid].type;\
		 ComErrorMessage = ComErrorTable[eid].message;}

/*
 * target to display error window
 */
#define PROSECUTE	0
#define DEFENSE		1
#define NEITHER		-1
