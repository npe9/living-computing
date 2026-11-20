/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

#include <Xm/Form.h>
#include <Xm/List.h>
#include <stdio.h>
#include <errno.h>

#include "gui.h"
#include "err.h"
#include "messages.h"
#include "commands.h"

Widget goalSetW;
Widget goalListW;

GuiCallback(goalLoadCancelCB)
{
  XtDestroyWidget((Widget)client_data);
}

void goalLoadLoadCB(Widget w, XtPointer client_data, 
		XmFileSelectionBoxCallbackStruct *call_data)
/* ロードウインドウのLoadボタンのCB */
{
  char *tmp;
  char *file;
  int pos,i;
  char *tmpfile, *tmppath, *command;

  if (call_data->length == call_data->dir_length)
    return; /* no file selected */

  XmStringGetLtoR(call_data->value, XmSTRING_DEFAULT_CHARSET, &file);

  if (strcmp(&file[strlen(file)-strlen("goal")],"goal") == 0) {
    tmpfile = tmpnam((char *)NULL);

/* Advanced Version ** included bugs 
    if (fork() == 0) {
      if (execlp("gtrans", "goal", file, tmpfile, (char *)0))
	if (errno == ENOENT) {
	  GuiWarningPopup(NO_PATH);
	  exit(0);
	} else {
	  tmp = XtMalloc(strlen(UNKNOWN_ERROR)+5);
	  sprintf(tmp, "%s%d", UNKNOWN_ERROR, errno);
	  GuiWarningPopup(tmp);
	  XtFree(tmp);
	  exit(0);
	}
      exit(0);
    }
*/
/* Temporary Version Begin*/
    command = XtMalloc(strlen("gtrans goal ")+strlen(file)+1+strlen(tmpfile)+1);
    sprintf(command, "gtrans goal %s %s", file, tmpfile);
    printf("command = %s\n",command);
    system(command);
/* Temporary Version End */
    
    GuiMacro(ComLoadQuery(PROSECUTOR,tmpfile));
  } else
    GuiMacro(ComLoadQuery(PROSECUTOR,file));

/* 現在設定しているゴールおよびゴール候補を求める */ 
  for(pos = 0; pos < POS_NUM; pos++) 
    currentGoal[pos] = DB_INIT;

  for(i = 0 ; i < goalCandidateList_num ; i++)
    XtFree(goalCandidateList[i]);
  GuiMacro(ComSendGoalCandidateList(PROSECUTOR));
  ComListMax(MessageE,arg3,goalCandidateList_num);
  ComListCp(goalCandidateList,goalCandidateList_num,MessageE,arg3);

  XmListDeleteAllItems(goalListW);
  GuiXmListAddItems(goalListW, goalCandidateList, goalCandidateList_num, 0);

  XtDestroyWidget((Widget)client_data);
}

GuiCallback(goalLoadCB)
/* ゴールロードウインドウの作成 */
{
  int pos;
  Widget goalLoadW, tmp;

  pos = (int)client_data;

  /* Form Widet */
  GuiSt();
  goalLoadW = GuiXmCreateFormDialog(dbtform[pos], "GoalLoad");

  /* File Selection Box */
  GuiSt();
  GuiSa(XmNokLabelString, XmStringCreateSimple("Load"));
  GuiSa(XmNapplyLabelString, XmStringCreateSimple("Filter"));
  GuiSa(XmNselectionLabelString, XmStringCreateSimple("Loading File"));
  GuiSa(XmNcancelLabelString, XmStringCreateSimple("Cancel"));
  GuiSa(XmNlistLabelString, XmStringCreateSimple("File"));
  GuiSa(XmNdirListLabelString, XmStringCreateSimple("Directory"));
  GuiSa(XmNfileListLabelString, XmStringCreateSimple("File"));
  GuiSa(XmNfilterLabelString, XmStringCreateSimple("Filter"));
  GuiSa(XmNdirMask, XmStringCreateSimple(QUERY_SUFFIX));
  GuiXmAttachForm(5,5,5,5);
  tmp = (Widget)XmCreateFileSelectionBox(goalLoadW, "file_slct_b", 
						 GuiXArg, GuiXArgNum);
  XtUnmanageChild(
      (Widget)XmFileSelectionBoxGetChild( tmp, XmDIALOG_HELP_BUTTON ));
  XtAddCallback(tmp, XmNokCallback, (XtCallbackProc)goalLoadLoadCB, 
		(XtPointer)goalLoadW);
  XtAddCallback(tmp, XmNcancelCallback, (XtCallbackProc)goalLoadCancelCB, 
		(XtPointer)goalLoadW);
  XtManageChild( tmp );
  XtManageChild( goalLoadW );
}

GuiCallback(goalSetCancelCB)
{
  int i,pos;

  pos = (int)client_data;
  XtDestroyWidget(goalSetW);
}

GuiCallback(goalSlctCB)
{
  int i,pos;
  char **goal;
  XmString *items;
  int item_count;
  int tmp;

  pos = (int)client_data;

  tmp = ((XmListCallbackStruct *)call_data)->item_position - 1;

  GuiMacro(ComSetGoal((COMCHAR)pos,(COMSHORT)tmp));

  /* OKだったら ゴール情報を更新して使用ユニット設定ウインドウを閉じる */
  currentGoal[pos] = tmp;
  GuiDisplayCurrentGoal(pos);

  XtDestroyWidget(goalSetW);
}

GuiCallback(goalCB)
/* goalボタンのCB 
   ゴール設定ウインドウを開く*/
{
  int pos,i;
  Widget formB;
  Widget frameB, cancelB, loadB;
  Widget listL;

  pos = (int)client_data;

  GuiSt();
  goalSetW = GuiXmCreateFormDialog(dbtform[pos], "Goal Set");

/* 指定領域 */

  GuiSt();
  GuiXmAttachForm(15,10,-1,-1);
  GuiMakeAndSetLabel("Goal List",GUI_F_ITAL14);
  listL = GuiXmCreateLabel(goalSetW,NULL);
  
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
  goalListW = (Widget)GuiXmCreateScrolledList(goalSetW,
					      goalCandidateList_num,
					      goalCandidateList);
  if (currentGoal[pos] != -1) {
    XmListSelectPos(goalListW, currentGoal[pos] + 1, False);
  }
  XtAddCallback(goalListW, XmNdefaultActionCallback, goalSlctCB,
		(XtPointer)pos);

/* アクションエリア */

  GuiSt();
  GuiXmAttachForm(-1,0,0,0);
  GuiXmAttachWidget(GuiREG,goalListW, 10,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  frameB = GuiXmCreateFrame(goalSetW);

  GuiSt();
  GuiXmAttachForm(0,0,0,0);
  formB = GuiXmCreateForm(frameB, "form");

  GuiSt();
  GuiXmAttachForm(3,-1,5,3);
  cancelB = GuiXmCreateButton(formB, "Cancel");
  XtAddCallback(cancelB,XmNactivateCallback, (XtCallbackProc)goalSetCancelCB,
		(XtPointer)pos);

  GuiSt();
  GuiXmAttachForm(3,-1,-1,3);
  GuiXmAttachWidget(NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    GuiREG, cancelB, 5,
		    NULL,NULL,NULL);
  loadB = GuiXmCreateButton(formB, "Load");
  XtAddCallback(loadB,XmNactivateCallback, (XtCallbackProc)goalLoadCB,
		(XtPointer)pos);

  XtManageChild(goalSetW);
}
