/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

#include <Xm/Form.h>
#include "gui.h"
#include "dbt.h"
#include "messages.h"
#include "commands.h"

#define VC_INIT_LABEL "              "

Widget viewListW[POS_NUM];
Widget vsVW[POS_NUM];
Widget vsSW[POS_NUM];
Widget vsOrderW[POS_NUM], vsOrderOldW[POS_NUM], vsOrderNewW[POS_NUM];
Widget viewSetW[POS_NUM];

GuiCallback(VsVcCancelCB)
{
  int i,pos;

  pos = (int)client_data;
  XtDestroyWidget(vsVW[pos]);
}

GuiCallback(VsVcSelectCB)
{
  int i,pos;
  int max;

  pos = (int)client_data;
  GuiMacro(ComSendViewCandidate( (COMCHAR)((int)client_data),
	     (COMSTRING)allViewCList[((XmListCallbackStruct *)call_data)->item_position-1]));

  /* OKだったら receive view candidateがきているはずなので
     価値観設定ウインドウを書き変える */
  XmListDeleteAllItems(viewListW[pos]);
  ComListMax(MessageD,arg2,max);
  GuiXmListAddItems(viewListW[pos], GuiCm(MessageD)->arg2, max, 0);

  XtDestroyWidget(vsVW[pos]);
}
  
GuiCallback(viewSetVcCB)
/* 価値観設定ウインドウのViewCandidateボタンのCB
   全ての価値観候補を持つポップアップウインドウが開く */
{
  int pos,i;
  Widget formB;
  Widget frameB, cancelB;
  Widget listL;
  Widget vsListW;

  pos = (int)client_data;

  GuiSt();
  vsVW[pos] = GuiXmCreateFormDialog(dbtform[pos], "View Candidate");

/* 価値観候補表示領域 */

  GuiSt();
  GuiXmAttachForm(5,10,10,-1);
  GuiMakeAndSetLabel("View Candidate List",GUI_F_ITAL14);
  listL = GuiXmCreateLabel(vsVW[pos],NULL);

  GuiSt();
  GuiSa(XmNvisibleItemCount,10);
  GuiXmAttachForm(-1, 10, 10, -1);
  GuiXmAttachWidget(GuiREG, listL, 5,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  GuiSa(XmNscrollingPolicy, XmAUTOMATIC);
  GuiSa(XmNlistSizePolicy, XmRESIZE_IF_POSSIBLE);
  GuiSa(XmNscrollBarDisplayPolicy,XmAS_NEEDED);
  vsListW = (Widget)GuiXmCreateScrolledList(vsVW[pos],allViewCList_num,
					      allViewCList);
  XtAddCallback(vsListW, XmNdefaultActionCallback, VsVcSelectCB,
		(XtPointer)pos);

/* アクションエリア */

  GuiSt();
  GuiXmAttachForm(-1,0,0,0);
  GuiXmAttachWidget(GuiREG,vsListW, 10,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  frameB = GuiXmCreateFrame(vsVW[pos]);

  GuiSt();
  GuiXmAttachForm(0,0,0,0);
  formB = GuiXmCreateForm(frameB, "form");

  GuiXmAttachForm(2,-1,5,2);
  cancelB = GuiXmCreateButton(formB, "Cancel");
  XtAddCallback(cancelB, XmNactivateCallback, VsVcCancelCB, (XtPointer)pos);

  XtManageChild(vsVW[pos]);
}

GuiCallback(VsSpCancelCB)
{
  int i,pos;

  pos = (int)client_data;
  XtDestroyWidget(vsSW[pos]);
}

GuiCallback(VsSpSelectCB)
{
  int i,pos;
  char **tmp_i;
  int tmp_n;

  pos = (int)client_data;
  GuiXmListAddItem(viewListW[pos],
		   allStandPoint[((XmListCallbackStruct *)call_data)->item_position-1],
		   0);

  XtDestroyWidget(vsSW[pos]);
}

GuiCallback(viewSetSpCB)
/* 価値観設定ウインドウのStandpointボタンのCB
   全ての判断基準を持つポップアップウインドウが開く */
{
  int pos,i;
  Widget formB;
  Widget frameB, cancelB;
  Widget listL;
  Widget vsListSW;

  pos = (int)client_data;

  GuiSt();
  vsSW[pos] = GuiXmCreateFormDialog(dbtform[pos], "Standpoint");

/* 価値観候補表示領域 */

  GuiSt();
  GuiXmAttachForm(5,10,10,-1);
  GuiMakeAndSetLabel("View Candidate List",GUI_F_ITAL14);
  listL = GuiXmCreateLabel(vsSW[pos],NULL);

  GuiSt();
  GuiSa(XmNvisibleItemCount,10);
  GuiXmAttachForm(-1, 10, 10, -1);
  GuiXmAttachWidget(GuiREG, listL, 5,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  GuiSa(XmNscrollingPolicy, XmAUTOMATIC);
  GuiSa(XmNlistSizePolicy, XmRESIZE_IF_POSSIBLE);
  GuiSa(XmNscrollBarDisplayPolicy,XmAS_NEEDED);
  vsListSW = (Widget)GuiXmCreateScrolledList(vsSW[pos],allStandPoint_num,
					      allStandPoint);
  XtAddCallback(vsListSW, XmNdefaultActionCallback, VsSpSelectCB,
		(XtPointer)pos);

/* アクションエリア */

  GuiSt();
  GuiXmAttachForm(-1,0,0,0);
  GuiXmAttachWidget(GuiREG,vsListSW, 10,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  frameB = GuiXmCreateFrame(vsSW[pos]);

  GuiSt();
  GuiXmAttachForm(0,0,0,0);
  formB = GuiXmCreateForm(frameB, "form");

  GuiXmAttachForm(2,-1,5,2);
  cancelB = GuiXmCreateButton(formB, "Cancel");
  XtAddCallback(cancelB, XmNactivateCallback, VsSpCancelCB, (XtPointer)pos);

  XtManageChild(vsSW[pos]);
}

GuiCallback(viewSetCancelCB)
{
  int i,pos;

  pos = (int)client_data;
  XtDestroyWidget(viewSetW[pos]);
}

GuiCallback(viewSetClearCB)
{
  int i,pos;

  pos = (int)client_data;
  XmListDeleteAllItems(viewListW[pos]);
}

GuiCallback(viewSetDoneCB)
{
  int i,pos;
  char **view;
  XmString *items;
  int max;

  pos = (int)client_data;
  GuiSt();
  GuiSa(XmNitemCount, &max);
  GuiSa(XmNitems, &items);
  GuiSg(viewListW[pos]);
  view = (char **)XtCalloc(max+1,sizeof(char *));
  for(i = 0; i < max; i++) {
    XmStringGetLtoR(items[i], XmSTRING_DEFAULT_CHARSET, &view[i]);
  }
  view[max] = (char *)NULL;
  GuiMacroP(viewSetW[pos], ComSetStandpointList((COMCHAR)pos,(COMLIST)view));

  /* OKだったら 価値観を更新して価値観設定ウインドウを閉じる */
  for(i = 0; i < currentView_num[pos]; i++) {
    XtFree(currentView[pos][i]);
  }
  XtFree((char *)currentView[pos]);
  currentView[pos] = (char **)XtCalloc(max, sizeof(char *));
  currentView_num[pos] = max;
  for(i = 0; i < currentView_num[pos]; i++) {
    GuiStrCp(currentView[pos][i],view[i]);
  }

  XtDestroyWidget(viewSetW[pos]);
  for(i = 0 ; i < max+1; i++) {
    XtFree(view[i]);
  }
  XtFree((char *)view);

  /* posの論争ウインドウのViewエリアを更新する */
  GuiDisplayCurrentView(pos);
}

GuiCallback(VsOrderSlctCB)
{
  int i,pos;
  int tmp,max;
  XmString *items;
  char *sp;
  char **it;

  pos = (int)client_data;
  tmp = ((XmListCallbackStruct *)call_data)->item_position;;
  GuiSt();
  GuiSa(XmNitemCount, &max);
  GuiSa(XmNitems, &items);
  GuiSg(vsOrderOldW[pos]);

  XmStringGetLtoR(items[tmp-1], XmSTRING_DEFAULT_CHARSET, &sp);
  GuiXmListAddItem(vsOrderNewW[pos],
		   sp,
		   0);
  XmListDeletePos(vsOrderOldW[pos], tmp);


  if(max == 1) {
    /* 順序替え終了処理 */
    GuiSt();
    GuiSa(XmNitemCount, &max);
    GuiSa(XmNitems, &items);
    GuiSg(vsOrderNewW[pos]);
    it = (char **)XtCalloc(max, sizeof(char *));
    for(i = 0; i < max; i++) {
      XmStringGetLtoR(items[i], XmSTRING_DEFAULT_CHARSET, &it[i]);
    }
    /* 価値観選定ウインドウの表示領域を更新する */
    XmListDeleteAllItems(viewListW[pos]);
    GuiXmListAddItems(viewListW[pos], it, max, 0);
    XtDestroyWidget(vsOrderW[pos]);
  }
}

GuiCallback(VsOrderCancelCB)
{
  int i,pos;

  pos = (int)client_data;
  XtDestroyWidget(vsOrderW[pos]);
}

GuiCallback(viewSetOrderCB)
{
  int pos,i;
  Widget formB;
  Widget frameB, cancelB;
  Widget listL;
  Widget formL, formR;
  Dimension width;
  Widget listR;
  int item_num;
  XmString *items;
  char **it;

  pos = (int)client_data;

  GuiSt();
  GuiSa(XmNitemCount, &item_num);
  GuiSa(XmNitems, &items);
  GuiSg(viewListW[pos]);
  it = (char **)XtCalloc(item_num, sizeof(char *));
  for(i = 0; i < item_num; i++) {
    XmStringGetLtoR(items[i], XmSTRING_DEFAULT_CHARSET, &it[i]);
  }

  GuiSt();
  vsOrderW[pos] = GuiXmCreateFormDialog(dbtform[pos], "View Ordering");

/* 価値観候補表示領域 */

  GuiSt();
  GuiXmAttachForm(5,5,-1,-1);
  formL = GuiXmCreateForm(vsOrderW[pos], "form");
  GuiSt();
  GuiXmAttachForm(0,0,-1,-1);
  GuiMakeAndSetLabel("Old View",GUI_F_ITAL14);
  listL = GuiXmCreateLabel(formL,NULL);

  GuiSt();
  GuiSa(XmNvisibleItemCount,10);
  GuiXmAttachForm(-1, 0, 0, 0);
  GuiXmAttachWidget(GuiREG, listL, 5,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  GuiSa(XmNscrollingPolicy, XmAUTOMATIC);
  GuiSa(XmNlistSizePolicy, XmRESIZE_IF_POSSIBLE);
  GuiSa(XmNscrollBarDisplayPolicy,XmAS_NEEDED);
  vsOrderOldW[pos] = (Widget)GuiXmCreateScrolledList(formL, item_num, it);

  XtAddCallback(vsOrderOldW[pos], XmNdefaultActionCallback, VsOrderSlctCB,
		(XtPointer)pos);
  GuiSt();
  GuiSa(XmNwidth,&width);
  GuiSg(vsOrderOldW[pos]);

  GuiSt();
  GuiXmAttachForm(5,-1,5,-1);
  GuiXmAttachWidget(NULL,NULL,NULL,
		    GuiREG, formL, 10,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  formR = GuiXmCreateForm(vsOrderW[pos], "form");
  GuiSt();
  GuiXmAttachForm(0,0,-1,-1);
  GuiMakeAndSetLabel("New View",GUI_F_ITAL14);
  listR = GuiXmCreateLabel(formR,NULL);

  GuiSt();
  GuiSa(XmNwidth, width);
  GuiSa(XmNvisibleItemCount,10);
  GuiXmAttachForm(-1, 0, 0, 0);
  GuiXmAttachWidget(GuiREG, listR, 5,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  GuiSa(XmNscrollingPolicy, XmAUTOMATIC);
  GuiSa(XmNlistSizePolicy, XmRESIZE_IF_POSSIBLE);
  GuiSa(XmNscrollBarDisplayPolicy,XmAS_NEEDED);
  vsOrderNewW[pos] = (Widget)GuiXmCreateScrolledList(formR,0,(char **)NULL);

/* アクションエリア */

  GuiSt();
  GuiXmAttachForm(-1,0,0,0);
  GuiXmAttachWidget(GuiREG,formL, 10,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  frameB = GuiXmCreateFrame(vsOrderW[pos]);

  GuiSt();
  GuiXmAttachForm(0,0,0,0);
  formB = GuiXmCreateForm(frameB, "form");

  GuiXmAttachForm(2,-1,5,2);
  cancelB = GuiXmCreateButton(formB, "Cancel");
  XtAddCallback(cancelB, XmNactivateCallback, VsOrderCancelCB, (XtPointer)pos);

  XtManageChild(vsOrderW[pos]);
}

GuiCallback(vsSlctCB)
{
  int i,pos;
  int tmp;

  pos = (int)client_data;
  tmp = ((XmListCallbackStruct *)call_data)->item_position - 1;
  XmListDeletePos(viewListW[pos], tmp+1);
}

GuiCallback(viewCB)
/* viewボタンのCB 
   価値観設定ウインドウを開く*/
{
  int pos,i;
  Widget formL, formR, formB;
  Widget frameB, actKSW, orderB, cancelB, doneB, clearB;
  Widget vaB;
  Widget listL;
  Dimension dim;
  Widget spB; /* Standpoint Button */
  Widget currentViewLabel; 
  int l;
  char *vc;

  pos = (int)client_data;

  GuiMacro(ComSendCurrentView((char)pos));
  ComListMax(MessageD,arg2,currentView_num[pos]);
  ComListCp(currentView[pos],currentView_num[pos],MessageD,arg2);
  if (currentView_num[pos] != 0) {
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

  GuiSt();
  viewSetW[pos] = GuiXmCreateFormDialog(dbtform[pos], "View Set");

/* 指定領域 */

  GuiSt();
  GuiXmAttachForm(5,5,5,-1);
  formL = GuiXmCreateForm(viewSetW[pos], "form");

  GuiSt();
  GuiXmAttachForm(10,5,-1,-1);
  vaB = GuiXmCreateButton(formL, "View Candidate");
  XtAddCallback(vaB,XmNactivateCallback, (XtCallbackProc)viewSetVcCB,
		(XtPointer)pos);

  GuiSt();
  GuiXmAttachForm(10,-1,-1,-1);
  GuiXmAttachWidget(NULL,NULL,NULL,
		    GuiREG, vaB, 10,
		    NULL,NULL,NULL,
		    GuiOPP, vaB, 0);
  currentViewLabel = GuiXmCreateLabel(formL,VC_INIT_LABEL);

  GuiSt();
  GuiXmAttachForm(-1,5,-1,5);
  GuiXmAttachWidget(GuiREG, vaB, 10,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  spB = GuiXmCreateButton(formL, "Standpoint");
  XtAddCallback(spB,XmNactivateCallback, (XtCallbackProc)viewSetSpCB,
		(XtPointer)pos);

/* 価値観表示領域 */

  GuiSt();
  GuiXmAttachForm(-1,5,5,-1);
  GuiXmAttachWidget(GuiREG, formL, 0,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  formR = GuiXmCreateForm(viewSetW[pos], "form");
  
  GuiSt();
  GuiXmAttachForm(10,5,-1,-1);
  GuiMakeAndSetLabel("Standpoint List",GUI_F_ITAL14);
  listL = GuiXmCreateLabel(formR,NULL);

  GuiSt();
  GuiSa(XmNvisibleItemCount,10);
  GuiXmAttachForm(-1, -1, 5, 10);
  GuiXmAttachWidget(GuiREG, listL, 5,
		    GuiOPP,listL,10,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  GuiSa(XmNscrollingPolicy, XmAUTOMATIC);
  GuiSa(XmNlistSizePolicy, XmRESIZE_IF_POSSIBLE);
  GuiSa(XmNscrollBarDisplayPolicy,XmAS_NEEDED);
  viewListW[pos] = (Widget)GuiXmCreateScrolledList(formR,currentView_num[pos],
					      currentView[pos]);
  XtAddCallback(viewListW[pos], XmNdefaultActionCallback, vsSlctCB,
		(XtPointer)pos);

/* アクションエリア */

  GuiSt();
  GuiXmAttachForm(-1,0,0,0);
  GuiXmAttachWidget(GuiREG,formR, 0,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  frameB = GuiXmCreateFrame(viewSetW[pos]);

  GuiSt();
  GuiXmAttachForm(0,0,0,0);
  formB = GuiXmCreateForm(frameB, "form");

  GuiSt();
  GuiXmAttachForm(0,0,-1, 0);
  GuiSa(XmNorientation, XmHORIZONTAL);
  actKSW = GuiXmCreateRowColumn(formB);
  GuiSt();
  orderB = GuiXmCreateButton(actKSW, "Order");
  XtAddCallback(orderB,XmNactivateCallback, (XtCallbackProc)viewSetOrderCB,
		(XtPointer)pos);
  GuiSt();
  cancelB = GuiXmCreateButton(actKSW, "Cancel");
  XtAddCallback(cancelB,XmNactivateCallback, (XtCallbackProc)viewSetCancelCB,
		(XtPointer)pos);
  GuiSt();
  clearB = GuiXmCreateButton(actKSW, "Clear");
  XtAddCallback(clearB,XmNactivateCallback, (XtCallbackProc)viewSetClearCB,
		(XtPointer)pos);
  GuiSt();
  GuiSa(XmNmarginHeight, &dim);
  GuiSg(actKSW);
  GuiSt();
  GuiXmAttachForm((int)dim,-1,5,-1);
  doneB = GuiXmCreateButton(formB, "Done");
  XtAddCallback(doneB,XmNactivateCallback, (XtCallbackProc)viewSetDoneCB,
		(XtPointer)pos);

  XtManageChild(viewSetW[pos]);
}
