/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

#include <Xm/Form.h>
#include <Xm/MessageB.h>
#include <Xm/SelectioB.h>
#include <string.h>
#include "gui.h"

#define DBTMAIN
#include "dbt.h"
#include "err.h"
#include "dbtwin.h" /* 95.1.13 for RBR-Window */
#include "messages.h"
#include "commands.h"

void DbtSensitivitySet(int pos, short flag)
{
  int i;

  for(i=0;i<SENS_NUM;i++) {
    if (sensBut[pos][i] != (Widget)NULL) 
      if (((flag>>i) & (short)0x1) == 0x1)
	XtSetSensitive(sensBut[pos][i], True);
      else
	XtSetSensitive(sensBut[pos][i], False);
  }
  XtSetSensitive((Widget)botB[pos][8], True);  /* 95.1.17 for Set Form */
  /* Set always Depth-Button sensitive */
  XtSetSensitive(topB[pos][4], True); /* 95.2.20 for Depth */
}

/* 95.2.20 Added for Depth */
void DbtSensitivitySet2(int pos, short flag)
/* nearly equal to DbtSensitivitySet2 except for Depth */
{
  int i;

  for(i=0;i<SENS_NUM;i++) {
    if (sensBut[pos][i] != (Widget)NULL) 
      if (((flag>>i) & (short)0x1) == 0x1)
	XtSetSensitive(sensBut[pos][i], True);
      else
	XtSetSensitive(sensBut[pos][i], False);
  }
  if (((flag>>6) & (short)0x1) == 0x1)
    XtSetSensitive((Widget)botB[pos][8], True);  /* 95.1.17 for Set Form */
}

void GuiDbtTopButSensitive(int pos, Boolean flag)
{
  int i;

  for( i = 0; i < TOP_NUM; i++) 
    XtSetSensitive(topB[pos][i], flag);
}

void GuiDbtMidButSensitive(int pos, Boolean flag)
{
  int i;

  for( i = 0; i < MID_NUM; i++) 
    XtSetSensitive(midB[pos][i], flag);
}

void GuiDbtBotButSensitive(int pos, Boolean flag)
{
  int i;

  for( i = 0; i < BOT_NUM; i++) 
    if (botB[pos][i] != (Widget)NULL) 
      XtSetSensitive(botB[pos][i], flag);
}

void GuiDisplayCurrentGoal(int pos)
{
    if (currentGoal[pos] != (short)-1) {
      if (pos == PROSECUTOR) {
	/* 論証ウインドウのGoal情報に記入 */
	XmTextSetString(dbtGoal[pos], goalCandidateList[currentGoal[pos]]);
      }
    }
}

void GuiDisplayCurrentView(int pos)
{
  int l,i;
  char *vc;

  /* 論証ウインドウのView情報に記入 */
  l = 0;
  for(i = 0; i < currentView_num[pos]; i++) 
    l += strlen((currentView[pos])[i]) + 3;
  l = l - 3 + 1; /* decrease for " > " and increase for '\0' */
  vc = XtMalloc(l); 
  vc[0] = '\0';
  for(i = 0; i < currentView_num[pos]-1; i++)  {
    vc = strcat(vc,(currentView[pos])[i]);
    vc = strcat(vc," > ");
  }
  vc = strcat(vc,(currentView[pos])[currentView_num[pos]-1]);
  XmTextSetString(dbtView[pos], vc);
}

void GuiDisplayCurrentIssue(int pos, char *issue)
{
  XmTextSetString(dbtIss[pos], issue);
}

GuiCallback(quitCB)
{
  int i;
  int pos;

  pos = (int)client_data;

  /* 現在 Browse Modeならばそこから脱出する */
  /* 95.1.17 for Browse */
  if (browseMode == True) {
    GuiMacroP(dbtform[pos], ComExitBrowse()); 
    browseMode = False;
  }

  for( i = 0; i < POS_NUM; i++) {
    if (dbtform[i] != (Widget)NULL)
      XtDestroyWidget(dbtform[i]); /* 95.1.13 for RBR */
  }

  XtSetSensitive( init_form, True ); /* 95.1.13 for RBR */
}

GuiCallback(startCB)
/* 論争ウインドウのStartボタンのCB */
{
  int i, j;
  int pos;

  pos = (int)client_data;
/*
   論争開始可能かのチェックを行なう 
*/

  /* ロードチェック→必要なし */
  /* 役割設定チェック→必要なし */
  /* ゴール設定チェック〜検察側のみ行なう */
  if (currentGoal[PROSECUTOR] == DB_INIT ) {
    /* ゴール設定されていない */
    GuiWarnA( NO_SET_GOAL );
    return;
  }
  /* 価値観チェック→必要なし。フラットでやる場合もあるから */

/* 現在 Browse Modeならばそこから脱出する */
  /* 95.1.17 for Browse */
  if (browseMode == True) {
    GuiMacroP(dbtform[pos], ComExitBrowse()); 
    browseMode = False;
    for( i = 0; i < POS_NUM ; i++ ) {
      GuiDbtMidButSensitive(i, False) ;
      GuiDbtBotButSensitive(i, False) ;
    }
  }

/*
  論争の開始を通達する
*/

  GuiMacroP(dbtform[pos],ComStartDebate());

  /* エラーがないのでPendingありとする。*/
  GuiPendingOn();

/*
   全ての論争ウインドウの上部操作ボタン列をinsensitiveにする
*/
  for( i = 0; i < POS_NUM ; i++ ) 
    GuiDbtTopButSensitive(i, False) ;

}

GuiCallback(argSlctEndCB1)
/* 論争を終了を確認するCB */
{
  Widget tmp;
  int pos;

  pos = (int)client_data;
  GuiSt();
  GuiSa(XmNmessageString,XmStringCreateLtoR(DEBATE_ENDING,
					    XmSTRING_DEFAULT_CHARSET));
  GuiSa(XmNokLabelString, XmStringCreateSimple("Yes"));
  GuiSa(XmNcancelLabelString, XmStringCreateSimple("No"));
  tmp = (Widget)XmCreateWarningDialog(dbtform[pos], "warning", GuiXArg, 
				      GuiXArgNum);
  XtUnmanageChild((Widget)XmMessageBoxGetChild(tmp, XmDIALOG_HELP_BUTTON));
  XtAddCallback(tmp, XmNokCallback, argSlctEndCB2, (XtPointer)pos);
  XtManageChild(tmp);
}

GuiCallback(argSlctEndCB2)
{
  int i;

  GuiMacro(ComEndDebate());

  XtDestroyWidget(argSlct);

/* 95.2.22 sensitive 動作はdriver.cのEndDebateCB内で行われるので削除した */

  GuiPendingOn();             /* 95.2.22 for Browse */
}  

GuiCallback(poseCB)
/* 論争ウインドウ ｐｏｓｅボタンのCB */
{
  int pos;

  pos = (int)client_data;
  GuiMacroP(dbtform[pos],ComPose((COMCHAR)pos));

  /* エラーがないのでPendingありとする */
  GuiDbtTopButSensitive(pos, False) ; /* 95.2.20 Added for Depth */
  GuiDbtMidButSensitive(pos, False);
  GuiDbtBotButSensitive(pos, False);
  GuiPendingOn();
}

void noticeDraw(int pos)
{
  Widget labelW,acFR,acFO,cancelB;

  /* エラーがないので優先通告ウインドウを開く */
  GuiSt();
  GuiSa(XmNmessageString, XmStringCreateLtoR(NOTICE_DRAW_MESSAGE, XmSTRING_DEFAULT_CHARSET));
  GuiSa(XmNokLabelString, XmStringCreateSimple("Yes"));
  GuiSa(XmNcancelLabelString, XmStringCreateSimple("No"));
  noticeSlct = XmCreateMessageDialog(dbtform[pos],"Notice Draw",
					     GuiXArg, GuiXArgNum);
  XtUnmanageChild(XmMessageBoxGetChild(noticeSlct, 
					       XmDIALOG_HELP_BUTTON));
  XtAddCallback(XmMessageBoxGetChild(noticeSlct, XmDIALOG_CANCEL_BUTTON)
		, XmNactivateCallback, noticeCancelCB, (XtPointer)pos);
  XtAddCallback(XmMessageBoxGetChild(noticeSlct, XmDIALOG_OK_BUTTON)
		, XmNactivateCallback, noticeOkCB, (XtPointer)pos);

  XtManageChild(noticeSlct);
}

GuiCallback(noticeCB)
{
  int pos;
  Widget acFR,acFO,cancelB;


  pos = (int)client_data;
  GuiMacro(ComSendReasonList((COMCHAR)pos));

  /* エラーがないので優先通告ウインドウを開く */
  ComListMax(MessageD,arg2,recvRSmax);
  if (recvRSmax == 0) {
    noticeDraw(pos);
    return;
  }

  GuiSt();
  noticeSlct = GuiXmCreateFormDialog(dbtform[pos],"Notice Selection");

  /* StandPointの表示 */
  GuiSt();
  GuiXmAttachForm(0,0,0,-1);
  GuiSa(XmNwidth, NTS_WIDTH);
  GuiSa(XmNvisibleItemCount,10);
  GuiSa(XmNscrollingPolicy, XmAUTOMATIC);
  GuiSa(XmNlistSizePolicy, XmCONSTANT);
  GuiSa(XmNscrollBarDisplayPolicy,XmAS_NEEDED);
  GuiSa(XmNscrollBarPlacement, XmBOTTOM_RIGHT);
  noticeSlctS = (Widget)GuiXmCreateScrolledList(noticeSlct,recvRSmax,
					  GuiCm(MessageD)->arg2);
  XtAddCallback(noticeSlctS, XmNdefaultActionCallback, 
		noticeLineCB, (XtPointer)pos);

  /* アクションエリアの生成 */
  GuiSt();
  GuiXmAttachForm(-1,0,0,0);
  GuiXmAttachWidget(GuiREG,noticeSlctS,5,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  acFR = (Widget)GuiXmCreateFrame(noticeSlct);
  GuiSt();
  GuiXmAttachForm(0,0,0,0);
  acFO = GuiXmCreateForm(acFR,"form");
  GuiSt();
  GuiXmAttachForm(2,-1,2,2);
  cancelB = GuiXmCreateButton(acFO, "Cancel");
  XtAddCallback(cancelB, XmNactivateCallback, noticeCancelCB, (XtPointer)pos);

  XtManageChild(noticeSlct);
}

GuiCallback(cancelCB)
/* 論争ウインドウ CancelボタンのCB */
{
  int pos;

  pos = (int)client_data;
  GuiMacro(ComCancel((COMCHAR)pos));

  /* エラーがないのでPendingありとする */
  GuiDbtTopButSensitive(pos, False) ; /* 95.2.20 Added for Depth */
  GuiDbtMidButSensitive(pos, False);
  GuiDbtBotButSensitive(pos, False);
  GuiPendingOn();
}

GuiCallback(finishCB)
/* 論争ウインドウ FinishボタンのCB */
{
  int pos;

  pos = (int)client_data;
  GuiMacro(ComFinish((COMCHAR)pos));

  /* エラーがないのでPendingありとする */
  GuiDbtTopButSensitive(pos, False) ; /* 95.2.20 Added for Depth */
  GuiDbtMidButSensitive(pos, False);
  GuiDbtBotButSensitive(pos, False);
  GuiPendingOn();
}

GuiCallback(justifyCB)
{
  int pos;
  Widget acFR,acFO,cancelB,doneB;


  pos = (int)client_data;
  GuiMacroP(dbtform[pos],ComJustify((COMCHAR)pos));

  /* エラーがないので価値観変更ウインドウを開く */
  GuiSt();
  spSlct = GuiXmCreateFormDialog(dbtform[pos],"View Justification");

  /* StandPointの表示 */
  ComListMax(MessageK,arg2,recvVCmax);
/*  ComListCp(recvVCtmp,recvVCmax,MessageK,arg2);*/
  GuiSt();
  GuiXmAttachForm(0,0,-1,-1);
  GuiSa(XmNwidth, JST_WIDTH);
  GuiSa(XmNvisibleItemCount,10);
  GuiSa(XmNscrollingPolicy, XmAUTOMATIC);
  GuiSa(XmNlistSizePolicy, XmCONSTANT);
  GuiSa(XmNscrollBarDisplayPolicy,XmAS_NEEDED);
  GuiSa(XmNscrollBarPlacement, XmBOTTOM_LEFT);
/*  spSlctS = (Widget)GuiXmCreateScrolledList(ctrSlct,recvVCmax,recvVCtmp);*/
  spSlctS = (Widget)GuiXmCreateScrolledList(spSlct,recvVCmax,
					  GuiCm(MessageK)->arg2);
  XmListSelectPos(spSlctS, 1, False); /* 1番目のStandPointを強調 */
  XtAddCallback(spSlctS, XmNbrowseSelectionCallback, spLineCB,
		(XtPointer)pos);

  /* Viewの表示 */
  /* 1番目のStandPointのViewを見る */
   
  recvVC2max = 0;
  while (((GuiCm(MessageK)->arg3)[0])[recvVC2max] != (char *)NULL) 
    recvVC2max++;
  GuiSt();
  GuiXmAttachForm(0,-1,0,-1);
  GuiXmAttachWidget(NULL,NULL,NULL,
		    GuiREG,spSlctS,3,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  GuiSa(XmNwidth, JST_WIDTH);
  GuiSa(XmNvisibleItemCount,10);
  GuiSa(XmNscrollingPolicy, XmAUTOMATIC);
  GuiSa(XmNlistSizePolicy, XmCONSTANT);
  GuiSa(XmNscrollBarDisplayPolicy,XmAS_NEEDED);
  GuiSa(XmNscrollBarPlacement, XmBOTTOM_RIGHT);
  spSlctV = (Widget)GuiXmCreateScrolledList(spSlct,recvVC2max,
					  (GuiCm(MessageK)->arg3)[0]);


  /* アクションエリアの生成 */
  GuiSt();
  GuiXmAttachForm(-1,0,0,0);
  GuiXmAttachWidget(GuiREG,spSlctV,5,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  acFR = (Widget)GuiXmCreateFrame(spSlct);
  GuiSt();
  GuiXmAttachForm(0,0,0,0);
  acFO = GuiXmCreateForm(acFR,"form");
  GuiSt();
  GuiXmAttachForm(2,-1,2,2);
  cancelB = GuiXmCreateButton(acFO, "Cancel");
  XtAddCallback(cancelB, XmNactivateCallback, spCancelCB, (XtPointer)pos);
  GuiSt();
  GuiXmAttachForm(2,2,-1,2);
  doneB = GuiXmCreateButton(acFO, "Done");
  XtAddCallback(doneB, XmNactivateCallback, spDoneCB, (XtPointer)pos);

  XtManageChild(spSlct);
}

GuiCallback(endCB)
{
  Widget tmp;
  int pos;

  pos = (int)client_data;
  GuiSt();
  GuiSa(XmNmessageString,XmStringCreateLtoR(DEBATE_ENDING,
					    XmSTRING_DEFAULT_CHARSET));
  GuiSa(XmNokLabelString, XmStringCreateSimple("Yes"));
  GuiSa(XmNcancelLabelString, XmStringCreateSimple("No"));
  tmp = (Widget)XmCreateWarningDialog(dbtform[pos], "warning", GuiXArg, 
				      GuiXArgNum);
  XtUnmanageChild((Widget)XmMessageBoxGetChild(tmp, XmDIALOG_HELP_BUTTON));
  XtAddCallback(tmp, XmNokCallback, endCB2, (XtPointer)pos);
  XtManageChild(tmp);
}

GuiCallback(endCB2)
{
  int i;

  GuiMacro(ComEndDebate());

/* 95.1.15 sensitive 動作はdriver.cのEndDebateCB内で行われるので削除した */

  GuiPendingOn();             /* 95.1.17 for Browse */
}  

GuiCallback(argLineCB)
/* 論争ウインドウ論証表示エリアのCB */
/* 反論選定ウインドウを生成する */
{
  int i;
  int pos;
  Widget slct,slct2,acFR,acFO,cancelB;

  if ( ((XmListCallbackStruct *)call_data)->item_position < 3 ) {
    /* 選択対象でない行なので戻す */
    return;
  }
  pos = (int)client_data;
  GuiMacro(
   ComSendCounterList(
       (COMCHAR)pos,
       (COMSHORT)(((XmListCallbackStruct *)call_data)->item_position - 3)));

  /* エラーがないので反論リストが帰ってきたことを期待する */
  if (GuiCm(MessageF)->command != CmdRecvCounter) {
    GuiErrSpA("System Error\n driver:GuiRecvCounter:1");
  }
  pos = GuiCm(MessageF)->arg1;

  /* 反論選定ウインドウを開く */
  GuiSt();
  ctrSlct = GuiXmCreateFormDialog(dbtform[pos],"Counter Selection");

  /* add infoの表示 */
  ComListMax(MessageF,arg3,recvCT2max);
  ComListCp(recvCT2tmp,recvCT2max,MessageF,arg3);
  GuiSt();
  GuiXmAttachForm(0,0,0,-1);
  GuiSa(XmNwidth, DBT_WIDTH);
  GuiSa(XmNvisibleItemCount,6);
  GuiSa(XmNscrollingPolicy, XmAUTOMATIC);
  GuiSa(XmNlistSizePolicy, XmRESIZE_IF_POSSIBLE);
  GuiSa(XmNscrollBarDisplayPolicy,XmAS_NEEDED);
  GuiSa(XmNscrollBarPlacement, XmTOP_RIGHT);
  slct2 = (Widget)GuiXmCreateScrolledList(ctrSlct,recvCT2max,recvCT2tmp);

  /* 反論リストの表示 */
  ComListMax(MessageF,arg2,recvCTmax);
  ComListCp(recvCTtmp,recvCTmax,MessageF,arg2);
  GuiSt();
  GuiXmAttachForm(-1,0,0,-1);
  GuiXmAttachWidget(GuiREG,slct2,0,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  GuiSa(XmNwidth, DBT_WIDTH);
  GuiSa(XmNvisibleItemCount,5);
  GuiSa(XmNscrollingPolicy, XmAUTOMATIC);
  GuiSa(XmNlistSizePolicy, XmRESIZE_IF_POSSIBLE);
  GuiSa(XmNscrollBarDisplayPolicy,XmAS_NEEDED);
  slct = (Widget)GuiXmCreateScrolledList(ctrSlct,recvCTmax,recvCTtmp);
  XtAddCallback(slct, XmNdefaultActionCallback, ctrLineCB, (XtPointer)pos);

  /* アクションエリアの生成 */
  GuiSt();
  GuiXmAttachForm(-1,0,0,0);
  GuiXmAttachWidget(GuiREG,slct,5,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  acFR = (Widget)GuiXmCreateFrame(ctrSlct);
  GuiSt();
  GuiXmAttachForm(0,0,0,0);
  acFO = GuiXmCreateForm(acFR,"form");
  GuiSt();
  GuiXmAttachForm(2,-1,2,2);
  cancelB = GuiXmCreateButton(acFO, "Cancel");
  XtAddCallback(cancelB, XmNactivateCallback, ctrCancelCB, (XtPointer)pos);

  XtManageChild(ctrSlct);
}

GuiCallback(ctrLineCB)
/* 反論選定ウインドウのリスト要素のCB */
{
  int i;
  int pos;

  pos = (int)client_data;
  GuiMacro(
   ComSendRebuttal(
       (COMCHAR)pos,
       (COMSHORT)(((XmListCallbackStruct *)call_data)->item_position - 1)));

  /* エラーがないのでPendingありとする */
  GuiPendingOn();

  /* 反論選定ウインドウの破壊と領域の解放 */
  XtDestroyWidget(ctrSlct);
  for(i = 0; i < recvCTmax; i++) {
    XtFree(recvCTtmp[i]);
  }
  XtFree((char *)recvCTtmp);
  for(i = 0; i < recvCT2max; i++) {
    XtFree(recvCT2tmp[i]);
  }
  XtFree((char *)recvCT2tmp);
}

GuiCallback(ctrCancelCB)
/* 反論選定ウインドウのCancelのCB */
{
  int i;

  /* 反論選定ウインドウの破壊と領域の解放 */
  XtDestroyWidget(ctrSlct);
  for(i = 0; i < recvCTmax; i++) {
    XtFree(recvCTtmp[i]);
  }
  XtFree((char *)recvCTtmp);
  for(i = 0; i < recvCT2max; i++) {
    XtFree(recvCT2tmp[i]);
  }
  XtFree((char *)recvCT2tmp);
}

GuiCallback(spDoneCB)
/* 価値観変更ウインドウのリスト要素のCB */
{
  int i,length;
  int pos;
  int slct_num;
  int *selects;
  int justno;
  COMLIST tmp;
  int tmp_max;
  char *vc;
  char **view;
  int view_num;

  pos = (int)client_data;
  (void)XmListGetSelectedPos(spSlctS,&selects,&slct_num);
  justno = selects[0]-1;

  /* 選択された価値観を退避させる */
  tmp = (GuiCm(MessageK)->arg3)[justno]; /* 新しい価値観の中身 */
  tmp_max = 0;
  while (tmp[tmp_max] != (char *)NULL) 
    tmp_max++;
  view = (char **)XtCalloc(tmp_max, sizeof(char *));
  for(i = 0; i < tmp_max; i++) {
    view[i] = XtMalloc(strlen(tmp[i])+1);
    strcpy(view[i],tmp[i]);
  }
  view_num = tmp_max; /* 退避終了 */

  GuiMacro( ComSetJustification( (COMCHAR)pos, (COMSHORT)justno ) );

  /* エラーがないのでPendingありとする */
  GuiDbtMidButSensitive(pos, False);
  GuiDbtBotButSensitive(pos, False);
  GuiPendingOn();

  /* データベースから古い価値観を削除する */
  for(i = 0; i < currentView_num[pos]; i++) 
    XtFree((currentView[pos])[i]);
  XtFree((char *)currentView[pos]);

  /* データベースの価値観を更新する */
  currentView[pos] = view;
  currentView_num[pos] = view_num;

  /* 論争ウインドウの価値観エリアを更新する */
  if (currentView_num[pos] != 0) {
    length = 0;
    for(i = 0; i < currentView_num[pos]; i++) 
      length += strlen((currentView[pos])[i]) + 3;
    length = length - 3 + 1; /* decrease for " > " and increase for '\0' */
    vc = XtMalloc(length); 
    vc[0] = '\0';
    for(i = 0; i < currentView_num[pos]-1; i++)  {
      vc = strcat(vc,(currentView[pos])[i]);
      vc = strcat(vc," > ");
    }
    vc = strcat(vc,(currentView[pos])[currentView_num[pos]-1]);
    XmTextSetString(dbtView[pos], vc);
  }

  /* 反論選定ウインドウの破壊と領域の解放 */
  /* ComMessageInfo.messageの指すMessageK構造体の破壊
     ただし、COM/Cが行なう場合は不用 */
  XtDestroyWidget(spSlct);
}

GuiCallback(spCancelCB)
/* 価値観変更ウインドウのCancelのCB */
{
  int i;
  int pos;

  /* 価値観変更ウインドウの破壊と領域の解放 */
  XtDestroyWidget(spSlct);
}

void GuiCreateDebateWindow(int pos,  /* 立場  検察(pos==PROSECUTOR)
				         弁護(pos==DEFENDANT) */
			   int role) /* 役割  システム(role==SYSTEM)
				         ユーザ(role==USER) */
{
  Widget formT, formM, formB;
  Widget frameT, frameM, frameB;
  Widget topR, midR, botR;
  Widget labelG, labelV, labelDH;
  Widget labelS, labelI, labelA;
  Widget posL;
  int i;
  Dimension dim;

  GuiSt();
  dbtform[pos] = GuiXmCreateFormDialog(toplevel, posS[pos]);

  GuiSt();
  GuiXmAttachForm(10,10,-1,-1);
  GuiMakeAndSetLabel(posS[pos],GUI_F_ITAL34);
  posL = GuiXmCreateLabel(dbtform[pos], NULL);

  /* Top Button Area */

  GuiSt();
  GuiXmAttachForm(-1, 0, 0, -1);
  GuiXmAttachWidget(GuiREG, posL, 5,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  frameT = GuiXmCreateFrame(dbtform[pos]);

  GuiSt();
  GuiXmAttachForm(0, 0, 0, 0);
  formT = GuiXmCreateForm(frameT);

  GuiSt();
  GuiXmAttachForm(0,0,-1, 0);
  GuiSa(XmNorientation, XmHORIZONTAL);
  topR = GuiXmCreateRowColumn(formT);

/* 論争ウインドウの上部操作ボタンの作成
  topB[pos][0] = "View", 
  topB[pos][1] = "Unit", 
  topB[pos][2] = "Goal", 
  topB[pos][3] = "Start", 
  topB[pos][4] = "Depth"
  topB[pos][5] = "Quit" */

  for(i = 0; i < (TOP_NUM-1) ; i++) { /* Quitは右端におくため別に設定する */
    GuiSt();
    topB[pos][i] = GuiXmCreateButton(topR, topS[i]);
  }
  GuiSt();
  GuiSa(XmNmarginHeight, &dim);
  GuiSg(topR);
  GuiSt();
  GuiXmAttachForm((int)dim,-1,5,-1);
  topB[pos][(TOP_NUM-1)] = GuiXmCreateButton(formT, topS[(TOP_NUM-1)]);
  for(i = 0; i < TOP_NUM ; i++) { 
    XtAddCallback(topB[pos][i], XmNactivateCallback, 
		  (XtCallbackProc)topC[i], (XtPointer)pos);
  }

  /* Top Browsing Area */

  /* Goal Browsing dbtGoal[pos] */
  GuiSt();
  GuiXmAttachForm(-1, 5, -1, -1);
  GuiXmAttachWidget(GuiREG, frameT, 16,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  GuiMakeAndSetLabel("Goal",GUI_F_ITAL14);
  labelG = GuiXmCreateLabel(dbtform[pos], NULL);

  GuiSt();
  GuiSa(XmNrows, 1);
  GuiSa(XmNcolumns, DBT_CLM);  
  GuiSa(XmNeditable, False);
  GuiXmAttachForm(-1, -1, 5, -1);
  GuiXmAttachWidget(GuiREG, frameT, 10,
		    GuiREG, labelG, 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  GuiSa(XmNscrollHorizontal, False);
  GuiSa(XmNwordWrap, True);
  dbtGoal[pos] = GuiXmCreateText(dbtform[pos]);

  /* View Browsing dbtView[pos] */
  GuiSt();
  GuiXmAttachForm(-1, 5, -1, -1);
  GuiXmAttachWidget(GuiREG, dbtGoal[pos], 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  GuiMakeAndSetLabel("View",GUI_F_ITAL14);
  labelV = GuiXmCreateLabel(dbtform[pos], NULL);

  GuiSt();
  GuiSa(XmNrows, 1);
  GuiSa(XmNcolumns, DBT_CLM);  
  GuiSa(XmNeditable, False);
  GuiXmAttachForm(-1, -1, 5, -1);
  GuiXmAttachWidget(GuiREG, dbtGoal[pos], 5,
		    GuiREG, labelV, 10,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  GuiSa(XmNscrollHorizontal, False);
  GuiSa(XmNwordWrap, True);
  dbtView[pos] = GuiXmCreateText(dbtform[pos]);


  /* Middle Button Area */

  GuiSt();
  GuiXmAttachForm(-1, 0, 0, -1);
  GuiXmAttachWidget(GuiREG, dbtView[pos], 5,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  frameM = GuiXmCreateFrame(dbtform[pos]);

  GuiSt();
  GuiXmAttachForm(0, 0, 0, 0);
  formM = GuiXmCreateForm(frameM, "form");

  GuiSt();
  GuiXmAttachForm(0,0,-1, 0);
  GuiSa(XmNorientation, XmHORIZONTAL);
  midR = GuiXmCreateRowColumn(formM);
  for(i = 0; i < (MID_NUM-1) ; i++) {
    GuiSt();
    midB[pos][i] = GuiXmCreateButton(midR, midS[i]);
  }
  GuiSt();
  GuiSa(XmNmarginHeight, &dim);
  GuiSg(topR);
  GuiSt();
  GuiXmAttachForm((int)dim,-1,5,-1);
  midB[pos][(MID_NUM-1)] = GuiXmCreateButton(formM, midS[(MID_NUM-1)]);

  for(i = 0; i < MID_NUM ; i++) { 
    XtAddCallback(midB[pos][i], XmNactivateCallback, 
		  (XtCallbackProc)midC[i], (XtPointer)pos);
  }

  /* Bottom Browsing Area */

/* 95.2.1 Moved from Top Browsing to here */
  GuiSt();
  GuiXmAttachForm(-1, 5, -1, -1);
  GuiXmAttachWidget(GuiREG, frameM, 5,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  GuiMakeAndSetLabel("Debate History",GUI_F_ITAL14);
  labelDH = GuiXmCreateLabel(dbtform[pos], NULL);

  GuiSt();
  GuiSa(XmNrows, DBT_HIST_ROW);
  GuiSa(XmNcolumns, DBT_CLM);  
  GuiSa(XmNeditable, False);
  GuiXmAttachForm(-1, 5, 5, -1);
  GuiXmAttachWidget(GuiREG, labelDH, 3,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  GuiSa(XmNscrollHorizontal, False);
  GuiSa(XmNwordWrap, True);
  dbtHis[pos] = GuiXmCreateText(dbtform[pos]);

  GuiSt();
  GuiXmAttachForm(-1, 5, -1, -1);
  GuiXmAttachWidget(GuiREG, dbtHis[pos], 5,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  GuiMakeAndSetLabel("Status",GUI_F_ITAL14);
  labelS = GuiXmCreateLabel(dbtform[pos], NULL);

  GuiSt();
  GuiSa(XmNrows, DBT_STAT_ROW);
  GuiSa(XmNcolumns, DBT_CLM);  
  GuiSa(XmNeditable, False);
  GuiXmAttachForm(-1, 5, 5, -1);
  GuiXmAttachWidget(GuiREG, labelS, 3,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  GuiSa(XmNscrollHorizontal, False);
  GuiSa(XmNwordWrap, True);
  dbtStat[pos] = GuiXmCreateText(dbtform[pos]);

  GuiSt();
  GuiXmAttachForm(-1, 5, -1, -1);
  GuiXmAttachWidget(GuiREG, dbtStat[pos], 5,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  GuiMakeAndSetLabel("Issue",GUI_F_ITAL14);
  labelI = GuiXmCreateLabel(dbtform[pos], NULL);

  GuiSt();
  GuiSa(XmNrows, 1);
  GuiSa(XmNcolumns, DBT_CLM);  
  GuiSa(XmNeditable, False);
  GuiXmAttachForm(-1, 5, 5, -1);
  GuiXmAttachWidget(GuiREG, labelI, 3,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  GuiSa(XmNscrollHorizontal, False);
  GuiSa(XmNwordWrap, True);
  dbtIss[pos] = GuiXmCreateText(dbtform[pos]);

  GuiSt();
  GuiXmAttachForm(-1, 5, -1, -1);
  GuiXmAttachWidget(GuiREG, dbtIss[pos], 5,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  GuiMakeAndSetLabel("Argument",GUI_F_ITAL14);
  labelA = GuiXmCreateLabel(dbtform[pos], NULL);

  GuiSt();
  GuiSa(XmNvisibleItemCount,DBT_LINE);
  GuiSa(XmNwidth, DBT_WIDTH);  
  GuiSa(XmNlistSizePolicy, XmCONSTANT);
  GuiXmAttachForm(-1, 5, 5, -1);
  GuiXmAttachWidget(GuiREG, labelA, 3,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  GuiSa(XmNscrollBarDisplayPolicy, XmSTATIC);
  dbtArg[pos] = GuiXmCreateScrolledList(dbtform[pos],0,(char **)NULL);
  XtAddCallback(dbtArg[pos], XmNdefaultActionCallback, 
		argLineCB, (XtPointer)pos);
  
  /* Buttom Button Area */

  GuiSt();
  GuiXmAttachForm(-1, 0, 0, -1);
  GuiXmAttachWidget(GuiREG, dbtArg[pos], 5,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL,
		    NULL, NULL, NULL);
  frameB = GuiXmCreateFrame(dbtform[pos]);

  GuiSt();
  GuiXmAttachForm(0, 0, 0, 0);
  formB = GuiXmCreateForm(frameB, "form");

  GuiSt();
  GuiXmAttachForm(0,0,-1, 0);
  GuiSa(XmNorientation, XmHORIZONTAL);
  botR = GuiXmCreateRowColumn(formB);
  for(i = 0; i < BOT_NUM ; i++) {
    GuiSt();
    botB[pos][i] = GuiXmCreateButton(botR, botS[i]);
    XtAddCallback(botB[pos][i], XmNactivateCallback, 
		  (XtCallbackProc)botC[i], (XtPointer)pos);
  }

  GuiDbtMidButSensitive(pos, False);
  GuiDbtBotButSensitive(pos, False);

  for(i = 0; i < MID_NUM; i++) 
    sensBut[pos][i] = midB[pos][i];
  for(i = 0; i < BOT_NUM - 1; i++) /* 95.1.17 for Set Form */
    sensBut[pos][i+MID_NUM] = botB[pos][i];

}

void GuiCreateDebateWindowDrv()
{
  int i;

  /* 論争とDRSの違いを設定 */
  GuiStrCp(topS[START_SOLVE], "Start");
  topC[START_SOLVE] = startCB;

  for( i = 0 ; i < POS_NUM ; i++) {
    GuiCreateDebateWindow(i, roleAssign[i]);
  }
}

GuiCallback(noticeCancelCB)
/* 優先通告ウインドウ CancelボタンのCB */
{
  int i;
  int pos;

  /* 反論選定ウインドウの破壊と領域の解放 */
  /* ComMessageInfo.messageの指すMessageD構造体の破壊
     ただし、COM/Cが行なう場合は不用 */
  XtDestroyWidget(noticeSlct);
}

GuiCallback(noticeLineCB)
/* 優先通告ウインドウのリスト要素のCB */
{
  int i,length;
  int pos;
  int slct_num;
  int *selects;
  int standpoint;

  pos = (int)client_data;
  (void)XmListGetSelectedPos(noticeSlctS,&selects,&slct_num);
  standpoint = selects[0]-1;

  GuiMacro( ComNotice( (COMCHAR)pos, (COMSHORT)standpoint ) );

  /* エラーがないのでPendingありとする */
  GuiDbtMidButSensitive(pos, False);
  GuiDbtBotButSensitive(pos, False);
  GuiPendingOn();

  /* 反論選定ウインドウの破壊と領域の解放 */
  /* ComMessageInfo.messageの指すMessageD構造体の破壊
     ただし、COM/Cが行なう場合は不用 */
  XtDestroyWidget(noticeSlct);
}

GuiCallback(noticeOkCB)
/* 優先通告ウインドウのリスト要素のCB */
{
  int pos;

  pos = (int)client_data;

  GuiMacro( ComNotice( (COMCHAR)pos, (COMSHORT)0 ) );

  /* エラーがないのでPendingありとする */
  GuiDbtTopButSensitive(pos, False) ; /* 95.2.20 Added for Depth */
  GuiDbtMidButSensitive(pos, False);
  GuiDbtBotButSensitive(pos, False);
  GuiPendingOn();

  /* 反論選定ウインドウの破壊と領域の解放 */
  /* ComMessageInfo.messageの指すMessageD構造体の破壊
     ただし、COM/Cが行なう場合は不用 */
  XtDestroyWidget(noticeSlct);
}

GuiCallback(spLineCB)
{
  int pos;
  int view_num;

  view_num = (int)(((XmListCallbackStruct *)call_data)->item_position - 1);
  XmListDeleteAllItems(spSlctV);
  recvVC2max = 0;
  while (((GuiCm(MessageK)->arg3)[view_num])[recvVC2max] != (char *)NULL) 
    recvVC2max++;
  GuiXmListAddItems(spSlctV, (GuiCm(MessageK)->arg3)[view_num],
		    recvVC2max, 0);
}

GuiCallback(formHCB) /* 95.1.17 for Extended Display Form */
{
  int pos;

  pos = (int)client_data;
  GuiMacro(ComSetExplanationMode( (COMCHAR)pos, (COMCHAR)0 ));
}  

GuiCallback(formNLCB) /* 95.1.17 for Extended Display Form */
{
  int pos;

  pos = (int)client_data;
  GuiMacro(ComSetExplanationMode( (COMCHAR)pos, (COMCHAR)1 ));
}  

GuiCallback(formCB) /* 95.1.17 for Extended Display Form */
{
  Widget tmp;
  int pos;

  pos = (int)client_data;
  GuiSt();
  GuiSa(XmNmessageString,XmStringCreateLtoR(SET_FORM,
					    XmSTRING_DEFAULT_CHARSET));
  GuiSa(XmNokLabelString, XmStringCreateSimple("H-term"));
  GuiSa(XmNcancelLabelString, XmStringCreateSimple("Natural Language"));
  tmp = (Widget)XmCreateMessageDialog(dbtform[pos], "message", GuiXArg, 
				      GuiXArgNum);
  XtUnmanageChild((Widget)XmMessageBoxGetChild(tmp, XmDIALOG_HELP_BUTTON));
  XtAddCallback(tmp, XmNokCallback, formHCB, (XtPointer)pos);
  XtAddCallback(tmp, XmNcancelCallback, formNLCB, (XtPointer)pos);
  XtManageChild(tmp);
}

GuiCallback(depthSetCB) /* 95.1.17 for Set Depth */
{
  int i,pos;
  char *text;

  pos = (int)client_data;
  XmStringGetLtoR(((XmSelectionBoxCallbackStruct *)call_data)->value,
			   XmSTRING_DEFAULT_CHARSET, &text);

  /* 95.2.24 Add for numeral check */
  if(strlen(text) != strspn(text,"1234567890"))
    if(strcmp(text,"-1")) {
      GuiWarningPopup(DEPTH_INPUT_ERROR);
      return;
    }

  i = atoi(text);
  GuiMacro(ComSetDepth( (COMCHAR)pos, (COMSHORT)i ));
  d_ahead[pos] = i; /* 95.2.25 Add for showing current level */
}  

GuiCallback(depthCB) /* 95.1.17 for Set Depth */
{
  Widget tmp;
  int pos;
  char *text;

  pos = (int)client_data;
  GuiSt();

  /* 95.2.25 Add for showing current level */
  text = XtMalloc(strlen(SET_DEPTH)+10);
  sprintf(text, "%s%d", SET_DEPTH, d_ahead[pos]);
  GuiSa(XmNselectionLabelString,XmStringCreateLtoR(text,
					    XmSTRING_DEFAULT_CHARSET));

  GuiSa(XmNokLabelString, XmStringCreateSimple("Done"));
  GuiSa(XmNcancelLabelString, XmStringCreateSimple("Cancel"));
  tmp = (Widget)XmCreatePromptDialog(dbtform[pos], "prompt", GuiXArg, 
				      GuiXArgNum);
  XtUnmanageChild((Widget)XmSelectionBoxGetChild(tmp, XmDIALOG_HELP_BUTTON));
  XtAddCallback(tmp, XmNokCallback, depthSetCB, (XtPointer)pos);
  XtManageChild(tmp);
  XtFree(text);
}

