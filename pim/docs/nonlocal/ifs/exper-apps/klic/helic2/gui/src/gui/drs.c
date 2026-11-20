/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

#include <Xm/Form.h>
#include <Xm/MessageB.h>
#include <Xm/SelectioB.h>
#include <string.h>
#include "gui.h"

#include "dbt.h"
#include "err.h"
#include "dbtwin.h" /* 95.1.13 for RBR-Window */
#include "messages.h"
#include "commands.h"

GuiCallback(solveCB)
/* DRSウインドウのSolveボタンのCB */
{
  int i, j;
  int pos;

  pos = (int)client_data;
/*
   推論開始可能かのチェックを行なう 
*/

  /* ロードチェック→必要なし */
  /* 役割設定チェック→必要なし */
  /* ゴール設定チェック */
  if (currentGoal[pos] == DB_INIT ) {
    /* ゴール設定されていない */
    GuiWarnA( NO_SET_GOAL );
    return;
  }
  /* 価値観チェック→必要なし。フラットでやる場合もあるから */

/* 現在 Browse Modeならばそこから脱出する */
  if (browseMode == True) {
    GuiMacroP(dbtform[pos], ComExitBrowse()); 
    browseMode = False;
    GuiDbtBotButSensitive(pos, False) ;
  }
  browseMode = True; /* ブラウズ機能が推論部にない時はQuit,Solve時に
			ExitBrowseを発行するためにbrowseModeをTrueに
			しておく */

/*
  推論の開始を通達する
*/

  GuiMacroP(dbtform[pos],ComStartSolve());

  /* エラーがないのでPendingありとする。*/
  GuiPendingOn();

/* ブラウズモードができたらGuiDbtTopButSensitiveは復活して下さい */
/*
   全ての論争ウインドウの上部操作ボタン列をinsensitiveにする
  GuiDbtTopButSensitive(pos, False) ;
*/

}

void GuiCreateDRSWindow()
{
  int pos = DRS;
  Widget formT, formM, formB;
  Widget frameT, frameM, frameB;
  Widget topR, midR, botR;
  Widget labelG, labelV, labelDH;
  Widget labelS, labelI, labelA;
  Widget posL;
  int i;
  Dimension dim;

  /* 論争とDRSの違いを設定 */
  GuiStrCp(topS[START_SOLVE], "Solve");
  topC[START_SOLVE] = solveCB;

  GuiSt();
  dbtform[pos] = GuiXmCreateFormDialog(toplevel, posS[pos]);

  GuiSt();
  GuiXmAttachForm(10,10,-1,-1);
  GuiMakeAndSetLabel(DRS_NAME,GUI_F_ITAL34);
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


  /* Bottom Browsing Area */

  GuiSt();
  GuiXmAttachForm(-1, 5, -1, -1);
  GuiXmAttachWidget(GuiREG, dbtView[pos], 10,
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

  for(i = 0; i < MID_NUM; i++) 
    sensBut[pos][i] = (Widget)NULL;

  XtUnmanageChild(botB[pos][4]);
  XtUnmanageChild(botB[pos][6]);
  botB[pos][4] = (Widget)NULL;
  botB[pos][6] = (Widget)NULL;
  for(i = 0; i < BOT_NUM - 1; i++) /* 95.1.17 for Set Form */
    sensBut[pos][i+MID_NUM] = botB[pos][i];

  GuiDbtBotButSensitive(pos, False);

  dbtStat[pos] = (Widget)NULL;
  dbtHis[pos] = (Widget)NULL;
  for( i = 0; i < POS_NUM; i++) 
    if (i != DRS)
      dbtform[i] = (Widget)NULL;
}

