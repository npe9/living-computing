/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

#include <Xm/Form.h>
#include <Xm/List.h>
#include "gui.h"
#include "dbt.h"
#include "err.h"
#include "dbtwin.h"
#include "messages.h"
#include "commands.h"

void GuiCmdRecvAL()
{
  int i,max;
  int pos;
  Widget upper,label,goal;
  XmStringTable mlist;
  Widget slct,acFR,acFO,endB;
  
  if (GuiCm(MessageF)->command != CmdRecvAL) {
    GuiErrSpA("System Error\n driver:GuiRecvAL:1");
  }
  pos = GuiCm(MessageF)->arg1;
  
  /* 主張選定ウインドウを作る */
  GuiSt();
  argSlct = GuiXmCreateFormDialog(dbtform[pos],"Argument Selection");

  GuiSt();
  GuiXmAttachForm(0,0,0,-1);
  upper = GuiXmCreateForm(argSlct, "form");

  GuiSt();
  GuiXmAttachForm(0,0,-1,0);
  label = GuiXmCreateLabel(upper, "Goal");

  GuiSt();
  GuiXmAttachForm(0,-1,0,0);
  GuiXmAttachWidget(NULL,NULL,NULL,
		    GuiREG,label,5,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  GuiSa(XmNeditable, False);
  GuiSa(XmNrows, 1);
  GuiSa(XmNscrollHorizontal, False);
  GuiSa(XmNwordWrap, True);
  goal = GuiXmCreateText(upper);
  XmTextSetString(goal, (GuiCm(MessageF)->arg3)[0]); /* ゴール表示 */

  ComListMax(MessageF,arg2,max);
  GuiSt();
  GuiXmAttachForm(-1,0,0,-1);
  GuiXmAttachWidget(GuiREG,upper,5,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  GuiSa(XmNwidth, DBT_WIDTH);
  GuiSa(XmNvisibleItemCount,5);
  GuiSa(XmNmaxWidth,500);
  GuiSa(XmNscrollingPolicy, XmAUTOMATIC);
  GuiSa(XmNlistSizePolicy, XmRESIZE_IF_POSSIBLE);
  GuiSa(XmNscrollBarDisplayPolicy,XmAS_NEEDED);
  slct = (Widget)GuiXmCreateScrolledList(argSlct,max,
					 GuiCm(MessageF)->arg2);
  XtAddCallback(slct, XmNdefaultActionCallback, slctArgCB, (XtPointer)pos);

  GuiSt();
  GuiXmAttachForm(-1,0,0,0);
  GuiXmAttachWidget(GuiREG,slct,5,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  acFR = (Widget)GuiXmCreateFrame(argSlct);
  GuiSt();
  GuiXmAttachForm(0,0,0,0);
  acFO = GuiXmCreateForm(acFR,"form");
  GuiSt();
  GuiXmAttachForm(2,-1,2,2);
  endB = GuiXmCreateButton(acFO, "End");
  XtAddCallback(endB, XmNactivateCallback, argSlctEndCB1, (XtPointer)pos);

  XtManageChild(argSlct);
}

GuiCallback(slctArgCB)
{
  int i;

  GuiMacroP(argSlct, ComSendArgument(
	     (COMCHAR)((int)client_data),
	     (COMSHORT)(((XmListCallbackStruct *)call_data)->item_position - 1)));
  /* OKだったら receive argumentがきているはずなのでPendingありとする。*/
  GuiPendingOn();

  XtDestroyWidget(argSlct);
}

void GuiCmdRecvArg()
{
  int i,max;
  int pos;
  
  if (GuiCm(MessageG)->command != CmdRecvArg) {
    GuiErrSpA("System Error\n driver:GuiRecvArg:1");
  }

  /* Agentの獲得 */
  pos = GuiCm(MessageG)->arg1;

  /* 95.2.22 Added for Limited Browsing Mode.
             If browsing mode is complited, please delete here */
  if ( GuiCm(MessageG)->arg4 == 0x0 ) { 
    GuiMacroP(dbtform[pos], ComExitBrowse()); 
    browseMode = False;
    for( i = 0; i < POS_NUM ; i++ ) {
      GuiDbtMidButSensitive(i, False) ;
      GuiDbtBotButSensitive(i, False) ;
    }
    return;
  }

  /* 論証IDの獲得 */
  if(displayedArgId[pos] != (char *)NULL)
    XtFree(displayedArgId[pos]);
  if(parentArgId[pos] != (char *)NULL)
    XtFree(parentArgId[pos]);
  if(focusArgId[pos] != (char *)NULL)
    XtFree(focusArgId[pos]);
  displayedArgId[pos] =
    strcpy(XtMalloc(strlen((GuiCm(MessageG))->arg2[0])+1),
	   ((GuiCm(MessageG))->arg2)[0]);

  parentArgId[pos] =
    strcpy(XtMalloc(strlen((GuiCm(MessageG))->arg2[1])+1),
	   ((GuiCm(MessageG))->arg2)[1]);
  
  focusArgId[pos] =
    strcpy(XtMalloc(strlen((GuiCm(MessageG))->arg2[2])+1),
	   ((GuiCm(MessageG))->arg2)[2]);

  /* 争点の表示 */
  GuiDisplayCurrentIssue(pos, (GuiCm(MessageG))->arg3);

  /* 論争ウインドウのボタンのsensitivityの設定 */
  DbtSensitivitySet(pos, (GuiCm(MessageG))->arg4);

  /* ルール名、ルール関係、論証の表示 */
  XmListDeleteAllItems(dbtArg[pos]);
  ComListMax(MessageG,arg5,max);
  for(i = 0; i < max; i++) 
    GuiXmListAddItem(dbtArg[pos],(GuiCm(MessageG)->arg5)[i],0);

  /* ステータス情報の印字 */
  GuiXmTextAddString(dbtStat[pos], (GuiCm(MessageG))->arg6[0]);

  /* ヒストリ情報の印字 */
  GuiXmTextAddString(dbtHis[pos], (GuiCm(MessageG))->arg7);
}

void GuiCmdShowArg()
{
/* 95.1.17 Changed from MessageTypeH to MessageTypeG */
  int i,max;
  int pos;
  
  if (GuiCm(MessageG)->command != CmdShowArg) {
    GuiErrSpA("System Error\n driver:GuiShowArg:1");
  }

  /* Agentの獲得 */
  pos = GuiCm(MessageG)->arg1;

  /* 論証IDの獲得 */
  if(displayedArgId[pos] != (char *)NULL)
    XtFree(displayedArgId[pos]);
  if(parentArgId[pos] != (char *)NULL)
    XtFree(parentArgId[pos]);
  if(focusArgId[pos] != (char *)NULL)
    XtFree(focusArgId[pos]);
  displayedArgId[pos] =
    strcpy(XtMalloc(strlen((GuiCm(MessageG))->arg2[0])+1),
	   ((GuiCm(MessageG))->arg2)[0]);

  parentArgId[pos] =
    strcpy(XtMalloc(strlen((GuiCm(MessageG))->arg2[1])+1),
	   ((GuiCm(MessageG))->arg2)[1]);
  
  focusArgId[pos] =
    strcpy(XtMalloc(strlen((GuiCm(MessageG))->arg2[2])+1),
	   ((GuiCm(MessageG))->arg2)[2]);

  /* 争点の表示 */
  if ( strlen((GuiCm(MessageG))->arg3) != 0 )
    GuiDisplayCurrentIssue(pos, (GuiCm(MessageG))->arg3);

  /* 論争ウインドウのボタンのsensitivityの設定 */
  DbtSensitivitySet2(pos, (GuiCm(MessageG))->arg4); /* 95.1.17 for Change Spec */

  /* ルール名、ルール関係、論証の表示 */
  ComListMax(MessageG,arg5,max);
  if (max > 0) {
    XmListDeleteAllItems(dbtArg[pos]);
    for(i = 0; i < max; i++) 
      GuiXmListAddItem(dbtArg[pos],(GuiCm(MessageG)->arg5)[i],0);
  }

  /* ステータス情報の印字 */
  GuiXmTextAddString(dbtStat[pos], (GuiCm(MessageG))->arg6[0]);

  /* ヒストリ情報の印字 */
  GuiXmTextAddString(dbtHis[pos], (GuiCm(MessageG))->arg7);

  GuiMacroP(dbtform[pos],ComOk());

  GuiPendingOn();
}

GuiCallback(EndDebateCB)
{
  int i;

/*
   全ての論争ウインドウの上部操作ボタン列をsensitiveにする
*/
  for( i = 0; i < POS_NUM ; i++ ) 
    GuiDbtTopButSensitive(i, True) ;

/*
   全ての論争ウインドウの中部操作ボタン列および下部操作ボタン列
   をinsensitiveにする
*/
  for( i = 0; i < POS_NUM ; i++ ) 
    GuiDbtBotButSensitive(i, False) ;
  for( i = 0; i < POS_NUM ; i++ ) 
    GuiDbtMidButSensitive(i, False) ;

/* ブラウズモードに入る */
  GuiMacro(ComEnterBrowse()); /* 95.1.13 for Browse */
  browseMode = True;          /* 95.1.17 for Browse */
  GuiPendingOn();             /* 95.1.13 for Browse */
}  

void GuiCmdCompleteDebate()
{
  Widget tmp;
  int pos;

  pos = PROSECUTOR;
  GuiSt();
  GuiSa(XmNmessageString,XmStringCreateLtoR(DEBATE_ENDED,
					    XmSTRING_DEFAULT_CHARSET));
  GuiSa(XmNokLabelString, XmStringCreateSimple("Ok"));
  tmp = (Widget)XmCreateInformationDialog(dbtform[pos], "informing", GuiXArg, 
				      GuiXArgNum);
  XtUnmanageChild((Widget)XmMessageBoxGetChild(tmp, XmDIALOG_HELP_BUTTON));
  XtUnmanageChild((Widget)XmMessageBoxGetChild(tmp, XmDIALOG_CANCEL_BUTTON));
  XtAddCallback(tmp, XmNokCallback, EndDebateCB, (XtPointer)pos);
  XtManageChild(tmp);
}

void GuiRunData()
/**
   論争中のサーバーからの要求に応じるドライバー
      帰ってくる可能性のあるプロトコル
       receive argument list
       receive argument
       show argument
       ok
**/
{
  /* MessageInfoを見に行く */
  switch( (int)GuiCt ) {
  case MessageTypeA:
    /* CmdCompleteDebateしかない */
    GuiCmdCompleteDebate();
    break;
  case MessageTypeF:
    /* CmdRecvALしかない */
    GuiCmdRecvAL();
    break;
  case MessageTypeG:
    /* CmdRecvArgまたはCmdShowArg */
    if ((GuiCm(MessageG))->command == CmdRecvArg)
      /* CmdRecvArg */
      GuiCmdRecvArg();
    else
      GuiCmdShowArg(); /* 95.1.17 for Change Specification of CmdShowArg */
    break;
  }
  return;
}


