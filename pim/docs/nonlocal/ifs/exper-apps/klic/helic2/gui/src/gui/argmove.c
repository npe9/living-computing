/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

#include <Xm/Form.h>
#include "gui.h"
#include "dbt.h"
#include "err.h"
#include "messages.h"
#include "commands.h"

Widget jumpW;
static int claimSideFlag;
Widget clW;
int space; /* used in claimCB*/

GuiCallback(backwardCB)
{
  int pos;

  pos = (int)client_data;
  GuiMacroP( dbtform[pos],  ComBackward((COMCHAR)pos) );

  /* エラーがないのでPendingありとする。*/
  GuiPendingOn();
}
  
GuiCallback(forwardCB)
{
  int pos;

  pos = (int)client_data;
  GuiMacroP( dbtform[pos], ComForward((COMCHAR)pos) );

  /* エラーがないのでPendingありとする。*/
  GuiPendingOn();
}

GuiCallback(previousCB)
{
  int pos;

  pos = (int)client_data;
  GuiMacroP( dbtform[pos], ComPrevious((COMCHAR)pos) );

  /* エラーがないのでPendingありとする。*/
  GuiPendingOn();
}

GuiCallback(nextCB)
{
  int pos;

  pos = (int)client_data;
  GuiMacroP( dbtform[pos], ComNext((COMCHAR)pos) );

  /* エラーがないのでPendingありとする。*/
  GuiPendingOn();
}
  
GuiCallback(focusCB)
{
  int pos;

  pos = (int)client_data;
  GuiMacroP( dbtform[pos], ComFocus((COMCHAR)pos) );

  /* エラーがないのでPendingありとする。*/
  GuiPendingOn();
}
  
GuiCallback(jumpDoneCB)
{
  int pos;
  char *argid;

  pos = (int)client_data;
  XmStringGetLtoR(((XmSelectionBoxCallbackStruct *)call_data)->value,
		  XmSTRING_DEFAULT_CHARSET,
		  &argid);

  GuiMacroP( dbtform[pos],ComJump((COMCHAR)pos, (COMSTRING)argid));

  /* エラーがないのでPendingありとする。*/
  GuiPendingOn();

/*  XtDestroywidget(jumpW);*/
}

GuiCallback(jumpCB)
{
  int pos;

  pos = (int)client_data;
  GuiSt();
  GuiSa(XmNselectionLabelString, 
	XmStringCreateLtoR("Argument ID", XmSTRING_DEFAULT_CHARSET));
  GuiSa(XmNokLabelString,
	XmStringCreateLtoR("Jump", XmSTRING_DEFAULT_CHARSET));
  jumpW = (Widget)XmCreatePromptDialog(dbtform[pos], "Jump", GuiXArg, 
				       GuiXArgNum);
  XtUnmanageChild( (Widget)XmSelectionBoxGetChild(jumpW, XmDIALOG_HELP_BUTTON) );

  XtAddCallback(jumpW, XmNokCallback, jumpDoneCB, (XtPointer)pos);

  XtManageChild(jumpW);
}


GuiCallback(ClProSlctCB)
{
  int tmp,pos;

  pos = (int)client_data;
  tmp = ((XmListCallbackStruct *)call_data)->item_position - 1;

  GuiMacroP( dbtform[pos],ComJumpClaim((COMCHAR)pos, (COMSHORT)tmp));

  XtDestroyWidget(clW);
}

GuiCallback(ClDefSlctCB)
{
  int tmp,pos;

  pos = (int)client_data;
  tmp = ((XmListCallbackStruct *)call_data)->item_position + space;

  GuiMacroP( dbtform[pos],ComJumpClaim((COMCHAR)pos, (COMSHORT)tmp));

  XtDestroyWidget(clW);
}

GuiCallback(ClCancelCB)
{
  int i,pos;

  pos = (int)client_data;
  XtDestroyWidget(clW);
}

GuiCallback(claimCB)
{
  int pos,i;
  int max;
  Widget formB;
  Widget frameB, cancelB;
  Widget listL;
  Widget formL, formR;
  Dimension width;
  Widget listR;
  Widget clProW, clDefW;
  int pro_n, def_n;
  char **pro, **def;

  pos = (int)client_data;

  GuiMacroP( dbtform[pos], ComSendClaimlist((COMCHAR)pos) );
  ComListMax(MessageF,arg2,max);

  for(i = 0; i < max; i++) 
    if ( (GuiCm(MessageF)->arg2)[i][0] == ' ' ) 
      space = i; /* Spaceの位置 */

  pro = GuiCm(MessageF)->arg2;
  def = &(GuiCm(MessageF)->arg2[space+1]);
  pro_n = space;
  def_n = max - space - 1;

  GuiSt();
  clW = GuiXmCreateFormDialog(dbtform[pos], "Claim List");

/* 価値観候補表示領域 */

  GuiSt();
  GuiXmAttachForm(5,5,-1,-1);
  formL = GuiXmCreateForm(clW, "form");
  GuiSt();
  GuiXmAttachForm(0,0,-1,-1);
  GuiMakeAndSetLabel("Prosecutor",GUI_F_ITAL14);
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
  clProW = (Widget)GuiXmCreateScrolledList(formL, pro_n, pro);

  XtAddCallback(clProW, XmNdefaultActionCallback, ClProSlctCB,
		(XtPointer)pos);

  if( def_n == 0 ) {
    GuiSt();
    GuiSa(XmNwidth,&width);
    GuiSg(clProW);
  }

  GuiSt();
  GuiXmAttachForm(5,-1,5,-1);
  GuiXmAttachWidget(NULL,NULL,NULL,
		    GuiREG, formL, 10,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  formR = GuiXmCreateForm(clW, "form");
  GuiSt();
  GuiXmAttachForm(0,0,-1,-1);
  GuiMakeAndSetLabel("Defendant",GUI_F_ITAL14);
  listR = GuiXmCreateLabel(formR,NULL);

  GuiSt();
  if (def_n == 0) 
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
/*
  clDefW = (Widget)GuiXmCreateScrolledList(formR,def_n,def);
*/
  if (def_n != 0) 
    clDefW = (Widget)GuiXmCreateScrolledList(formR,def_n,def);
  else
    clDefW = (Widget)GuiXmCreateScrolledList(formR,0,NULL);
  XtAddCallback(clDefW, XmNdefaultActionCallback, ClDefSlctCB,
		(XtPointer)pos);

/* アクションエリア */

  GuiSt();
  GuiXmAttachForm(-1,0,0,0);
  GuiXmAttachWidget(GuiREG,formL, 20,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  frameB = GuiXmCreateFrame(clW);

  GuiSt();
  GuiXmAttachForm(0,0,0,0);
  formB = GuiXmCreateForm(frameB, "form");

  GuiXmAttachForm(2,-1,5,2);
  cancelB = GuiXmCreateButton(formB, "Cancel");
  XtAddCallback(cancelB, XmNactivateCallback, ClCancelCB, (XtPointer)pos);

  XtManageChild(clW);
}

GuiCallback(explainCloseCB)
{
  XtDestroyWidget((Widget)client_data);
}

GuiCallback(explainCB)
{
  Widget tmp;
  int pos;
  Widget textW, label;
  char *text;
  Widget expW, closeB;

  pos = (int)client_data;
  GuiMacroP(dbtform[pos],ComSendExplanation((COMCHAR)pos));
  if ( (GuiCm(MessageI))->command != CmdRecvExp ) {
    GuiErrorStopPopup(BUG_FINDED);
    return;
  }
  GuiSt();
  expW = GuiXmCreateFormDialog(dbtform[pos], "Explanation");

  GuiSt();
  GuiXmAttachForm(15,10,-1,-1);
  text = XtMalloc(strlen(EXPLANATION_LABEL)+40);
  sprintf(text, "%s%s", displayedArgId[pos], EXPLANATION_LABEL);
  label = GuiXmCreateLabel(expW, text);
  
  GuiSt();
  GuiXmAttachForm(-1, -1, 10, -1);
  GuiXmAttachWidget(GuiREG, label, 5,
		    GuiOPP,label,10,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  GuiSa(XmNwidth, EXP_WIDTH);
  GuiSa(XmNheight, EXP_HEIGHT);
  GuiSa(XmNscrollBarDisplayPolicy,XmAS_NEEDED);
  textW = (Widget)GuiXmCreateText(expW);
  XmTextSetString(textW, (GuiCm(MessageI))->arg2);

  GuiSt();
  GuiXmAttachForm(-1,-1,5,5);
  GuiXmAttachWidget(GuiREG, textW, 5,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL,
		    NULL,NULL,NULL);
  closeB = GuiXmCreateButton(expW, "Close");
  XtAddCallback(closeB,XmNactivateCallback, (XtCallbackProc)explainCloseCB,
		(XtPointer)expW);

  XtManageChild(expW);
}



