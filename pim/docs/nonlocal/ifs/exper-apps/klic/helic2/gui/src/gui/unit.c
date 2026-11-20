/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

#include <Xm/Form.h>
#include "gui.h"
/*
#include "dbt.h"
*/
#include "messages.h"
#include "commands.h"

Widget unitSetW[POS_NUM];
Widget unitListW[POS_NUM];
Widget unitT[POS_NUM];

GuiCallback(unitSetCancelCB)
{
  int i,pos;

  pos = (int)client_data;
  XtDestroyWidget(unitSetW[pos]);
}

GuiCallback(unitSetClearCB)
{
  int i,pos;

  pos = (int)client_data;
  XmListDeleteAllItems(unitListW[pos]);
}

GuiCallback(unitSetDoneCB)
{
  int i,pos;
  char **unit;
  XmString *items;
  int item_count;

  pos = (int)client_data;
  GuiSt();
  GuiSa(XmNitems, &items);
  GuiSa(XmNitemCount, &item_count);
  GuiSg(unitListW[pos]);

  unit = (char **)XtCalloc(item_count+1,sizeof(char *));
  for(i = 0; i < item_count; i++) {
    XmStringGetLtoR(items[i], XmSTRING_DEFAULT_CHARSET, &unit[i]);
  }
  unit[item_count] = (char *)NULL;
  GuiMacro(ComSetUnitList((COMCHAR)pos,(COMLIST)unit));

  /* OKだったら 使用ユニット情報を更新して使用ユニット設定ウインドウを閉じる */
  for(i = 0; i < currentUnitList_num[pos]; i++) {
    XtFree(currentUnitList[pos][i]);
  }
  XtFree((char *)currentUnitList[pos]);
  currentUnitList[pos] = (char **)XtCalloc(item_count, sizeof(char *));
  currentUnitList_num[pos] = item_count;
  for(i = 0; i < currentUnitList_num[pos]; i++) {
    GuiStrCp(currentUnitList[pos][i],unit[i]);
  }

  XtDestroyWidget(unitSetW[pos]);
  for(i = 0 ; i < item_count; i++) {
    XtFree(unit[i]);
  }
  XtFree((char *)unit);
}

GuiCallback(unSlctCB)
{
  int i,pos;
  int tmp;

  pos = (int)client_data;
  XmListDeletePos(unitListW[pos], 
		  ((XmListCallbackStruct *)call_data)->item_position);
}

GuiCallback(unitCheckCB)
{
  int i,pos;
  char *unit;
  int result;
  

  pos = (int)client_data;
  unit = (char *)XmTextFieldGetString(unitT[pos]);
  GuiMacro(ComCheckUnit((COMCHAR)pos, (COMSTRING)unit));

  XmTextFieldSetString(unitT[pos],"");
  GuiXmListAddItem(unitListW[pos], unit, 0);
  XtFree(unit);
}
 

GuiCallback(unitCB)
/* unitボタンのCB 
   価値観設定ウインドウを開く*/
{
  int pos,i;
  Widget formB;
  Widget frameB, actKSW, cancelB, doneB, clearB;
  Widget unitL;
  Widget listL;
  Dimension dim;

  pos = (int)client_data;

  GuiSt();
  unitSetW[pos] = GuiXmCreateFormDialog(dbtform[pos], "Unit Set");

/* 指定領域 */

  GuiSt();
  GuiXmAttachForm(15,10,-1,-1);
  GuiMakeAndSetLabel("Unit Name", GUI_F_ITAL14);
  unitL = GuiXmCreateLabel(unitSetW[pos], NULL);


  GuiSt();  
  GuiXmAttachForm(10,-1,10,-1);
  GuiXmAttachWidget(NULL,NULL,NULL,
		    GuiREG,unitL,5,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  GuiSa(XmNwidth, 200);
  unitT[pos] = GuiXmCreateTextField(unitSetW[pos]);
  XtAddCallback(unitT[pos],XmNactivateCallback, (XtCallbackProc)unitCheckCB,
		(XtPointer)pos);

/* 使用ユニット表示領域 */

  GuiSt();
  GuiXmAttachForm(-1,10,-1,-1);
  GuiXmAttachWidget(GuiREG, unitL, 20,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  GuiMakeAndSetLabel("Assigned Unit List",GUI_F_ITAL14);
  listL = GuiXmCreateLabel(unitSetW[pos],NULL);
  
  GuiSt();
  GuiXmAttachForm(-1, -1, 10, -1);
  GuiXmAttachWidget(GuiREG, listL, 5,
		    GuiOPP,listL,10,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  GuiSa(XmNscrollingPolicy, XmAUTOMATIC);
  GuiSa(XmNlistSizePolicy, XmRESIZE_IF_POSSIBLE);
  GuiSa(XmNscrollBarDisplayPolicy,XmAS_NEEDED);
  GuiSa(XmNvisibleItemCount,10);
  unitListW[pos] = (Widget)GuiXmCreateScrolledList(unitSetW[pos],
					      currentUnitList_num[pos],
					      currentUnitList[pos]);
  XtAddCallback(unitListW[pos], XmNdefaultActionCallback, unSlctCB,
		(XtPointer)pos);

/* アクションエリア */

  GuiSt();
  GuiXmAttachForm(-1,0,0,0);
  GuiXmAttachWidget(GuiREG,unitListW[pos], 10,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  frameB = GuiXmCreateFrame(unitSetW[pos]);

  GuiSt();
  GuiXmAttachForm(0,0,0,0);
  formB = GuiXmCreateForm(frameB, "form");

  GuiSt();
  GuiXmAttachForm(0,0,-1, 0);
  GuiSa(XmNorientation, XmHORIZONTAL);
  actKSW = GuiXmCreateRowColumn(formB);
  GuiSt();
  cancelB = GuiXmCreateButton(actKSW, "Cancel");
  XtAddCallback(cancelB,XmNactivateCallback, (XtCallbackProc)unitSetCancelCB,
		(XtPointer)pos);
  GuiSt();
  clearB = GuiXmCreateButton(actKSW, "Clear");
  XtAddCallback(clearB,XmNactivateCallback, (XtCallbackProc)unitSetClearCB,
		(XtPointer)pos);
  GuiSt();
  GuiSa(XmNmarginHeight, &dim);
  GuiSg(actKSW);
  GuiSt();
  GuiXmAttachForm((int)dim,-1,5,-1);
  doneB = GuiXmCreateButton(formB, "Done");
  XtAddCallback(doneB,XmNactivateCallback, (XtCallbackProc)unitSetDoneCB,
		(XtPointer)pos);

  XtManageChild(unitSetW[pos]);
}
