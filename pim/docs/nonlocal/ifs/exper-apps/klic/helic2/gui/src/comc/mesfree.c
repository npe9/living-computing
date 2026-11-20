/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*
 *      File Name  : mesfree.c
 *      Function   : free memory of message structure according to message type
 *                 : message structure memory is forced to be freed
 *                 : just before sending a message to server.
$*      History    :
$*      1995/ 1/12 : obsolete freeMessageH : extensional functions
$*      1994/11/22 : bug : didnot free message structure
$*      1994/11/15 : typo in freeMessageK
$*      1994/11/15 : crank in
 *
 */

#include <stdio.h>
#include "messages.h"
#include "comerrs.h"

void freeMessageA(void);
void freeMessageB(void);
void freeMessageC(void);
void freeMessageD(void);
void freeMessageE(void);
void freeMessageF(void);
void freeMessageG(void);
/* void freeMessageH(void); */
void freeMessageI(void);
void freeMessageK(void);
void freeMessageL(void);
void freeMessageM(void);
void freeMessageN(void);


int freeMessage(void)
{
  switch( ComMessageInfo.type )
  {
  case NoMessage :
    break;

  case MessageTypeA :
    freeMessageA();
    break;
  case MessageTypeB :
    freeMessageB();
    break;
  case MessageTypeC :
    freeMessageC();
    break;
  case MessageTypeD :
    freeMessageD();
    break;
  case MessageTypeE :
    freeMessageE();
    break;
  case MessageTypeF :
    freeMessageF();
    break;
  case MessageTypeG :
    freeMessageG();
    break;
/* obsolete
  case MessageTypeH :
    freeMessageH();
    break;
 */
  case MessageTypeI :
    freeMessageI();
    break;
/* obsolete
  case MessageTypeJ :
    printf("COMC:Warning: Can't free obsolete message type J structure\n");
    break;
 */
  case MessageTypeK :
    freeMessageK();
    break;
  case MessageTypeL :
    freeMessageL();
    break;
  case MessageTypeM :
    freeMessageM();
    break;
  case MessageTypeN :
    freeMessageN();
    break;

  default :
    printf("COMC:Warning: Can't free unknown message structure (TYPE:%d)\n",
	   ComMessageInfo.type);
  }
  return(0);
}

void freeMessageA(void)
{
  MessageA *message;
  message = (MessageA *) ComMessageInfo.message;
  free(message);
  return;
}

void freeMessageB(void)
{
  /* Free error message */
  freeString(ComErrorMessage);
  return;
}

void freeMessageC(void)
{
  MessageC *message;
  message = (MessageC *) ComMessageInfo.message;
  free(message);
  return;
}

void freeMessageD(void)
{
  MessageD *message;

  message = (MessageD *) ComMessageInfo.message;
  freeListOfString(message->arg2);
  free(message);
  return;
}

void freeMessageE(void)
{
  MessageE *message;

  message = (MessageE *) ComMessageInfo.message;
  freeListOfString(message->arg3);
  free(message);
  return;
}

void freeMessageF(void)
{
  MessageF *message;

  message = (MessageF *) ComMessageInfo.message;
  freeListOfString(message->arg2);
  freeListOfString(message->arg3);
  free(message);
  return;
}

void freeMessageG(void)
{
  MessageG *message;

  message = (MessageG *) ComMessageInfo.message;
  freeListOfString(message->arg2);
  freeString(message->arg3);
  freeListOfString(message->arg5);
  freeListOfString(message->arg6);
  freeString(message->arg7);
  free(message);
  return;
}


/* obsolete
void freeMessageH(void)
{
  MessageH *message;

  message = (MessageH *) ComMessageInfo.message;
  freeListOfString(message->arg2);
  freeString(message->arg3);
  freeListOfString(message->arg4);
  freeListOfString(message->arg5);
  freeString(message->arg6);
  free(message);
  return;
}
*/

void freeMessageI(void)
{
  MessageI *message;

  message = (MessageI *) ComMessageInfo.message;
  freeString(message->arg2);
  free(message);
  return;
}

void freeMessageK(void)
{
  MessageK *message;

  message = (MessageK *) ComMessageInfo.message;
  freeListOfString(message->arg2);
  freeListOfListOfString(message->arg3);
  free(message);
  return;
}

void freeMessageL(void)
{
  MessageL *message;

  message = (MessageL *) ComMessageInfo.message;
  free(message);
  return;
}

void freeMessageM(void)
{
  MessageM *message;

  message = (MessageM *) ComMessageInfo.message;
  free(message);
  return;
}

void freeMessageN(void)
{
  MessageN *message;

  message = (MessageN *) ComMessageInfo.message;
  free(message);
  return;
}
