/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*
 *      File Name  : comdebug.h
 *      Function   : debug
$*      History    :
$*      1994/11/15 : add debug print for low level buffer access
$*      1994/11/14 : debug print
$*      1994/11/ 7 : crank in
 *
 */

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
#define PSSEND 0x01
#define PSRECV 0x02
#define PSBOTH 0x03

#define DPNAME	0x01
#define DPARGS	0x02
#define DPBUF	0x04

extern int ComDebugFlag;	/* defined in comdebug.c */
